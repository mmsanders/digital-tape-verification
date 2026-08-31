# spec/engine-api.md — Tape Engine API v1.0

**Status:** DRAFT-1, issued for adversarial review. Not frozen.
**Owner:** Program Manager. Changes require PM sign-off.
**Issued:** 31 Aug 2026
**Companion:** `spec/tapefs-v1.md`, which is normative for everything on media.

C99. No operating system. No dynamic allocation, ever — not on firmware, not on desktop. No recursion. No libc file I/O. The only coupling to hardware is the block device in §2.

---

## 1. Error codes

```c
typedef enum {
  TAPE_OK = 0,
  TAPE_ERR_IO,                  /* block device returned failure */
  TAPE_ERR_BAD_MAGIC,
  TAPE_ERR_VERSION,             /* version_major != 1 */
  TAPE_ERR_CRC,
  TAPE_ERR_INCONSISTENT,        /* both slots valid, equal sequence */
  TAPE_ERR_NO_VALID_INDEX,
  TAPE_ERR_READ_ONLY,           /* write attempted against a device with write == NULL,
                                   or against Side A */
  TAPE_ERR_CARTRIDGE_FULL,
  TAPE_ERR_INDEX_FULL,
  TAPE_ERR_SEQUENCE_EXHAUSTED,
  TAPE_ERR_NOT_MOUNTED,
  TAPE_ERR_BUSY,                /* operation in progress that forbids this call */
  TAPE_ERR_UNDERRUN,            /* tape_render had insufficient buffered audio */
  TAPE_ERR_INVALID_ARG,
} tape_result;
```

Every call returns `tape_result`. There are no error strings in the engine.

---

## 2. Block device

```c
typedef struct {
  int (*read)(void *ctx, uint32_t lba, uint32_t count, void *dst);
  int (*write)(void *ctx, uint32_t lba, uint32_t count, const void *src);
  int (*flush)(void *ctx);
  void *ctx;
  uint32_t block_count;
} tape_dev;
```

Callbacks return 0 on success, non-zero on failure. `count` is in 512-byte blocks.

**`write` is `NULL` for a read-only device.** This is how the source slot is constructed, and it is the whole of the mechanism: there is no permission flag, no mode enum, no runtime check to forget. A write path that reaches a read-only device dereferences a null pointer and dies loudly in test rather than corrupting a cartridge in a child's hands.

`flush` must not return success until data has reached media. On SD that means the card has left the busy state.

Three implementations exist: a file-backed device for desktop, a fault-injecting simulator for the crash harness, and a real SD device for firmware. The engine cannot distinguish them, and that property is load-bearing — the same code is exercised by all three.

---

## 3. Memory

The caller owns all storage. The engine allocates nothing.

```c
size_t tape_instance_size(void);   /* compile-time constant */

tape_result tape_init(void *mem, size_t mem_len,
                      const tape_dev *dev,
                      void *play_ring,  size_t play_ring_len,
                      void *rec_ring,   size_t rec_ring_len,
                      tape **out);
```

| Buffer | Minimum | Purpose |
|---|---|---|
| `mem` | `tape_instance_size()` | Engine state: live index, scratch index, superblock, staging blocks |
| `play_ring` | 65 536 B | ~372 ms of playback headroom |
| `rec_ring` | 65 536 B | ~372 ms of capture headroom |

**Budget.** `tape_instance_size()` must be **≤ 200 KiB**, asserted in CI by a static assertion, and independently by checking that no allocator symbol links into the engine object. The dominant terms are two index arrays at `4096 × 12 + 64 ≈ 49 KiB` each. Ring buffers are caller-supplied and sit outside this budget.

`TAPE_MAX_ENTRIES` is 4096. That is an engine memory constraint, not a media one.

---

## 4. Lifecycle

```c
typedef enum { TAPE_SIDE_A = 0, TAPE_SIDE_B = 1 } tape_side;

tape_result tape_mount(tape *t, tape_side side, uint64_t resume_frame);
tape_result tape_unmount(tape *t, uint64_t *out_position_frame);
```

`tape_mount` executes §8 of the format spec, primes the preroll cache when `side` is A, and seeks to `resume_frame`. A `resume_frame` beyond the timeline clamps to the end.

`tape_unmount` returns the current position so the caller can store it. **The engine never writes position to media** — see format spec §10.

Mounting Side A on a device whose `write` is `NULL` is normal. Mounting Side B on such a device succeeds read-only; any subsequent write call returns `TAPE_ERR_READ_ONLY`.

```c
typedef struct {
  uint8_t  uuid[16];
  char     label[33];          /* NUL-terminated */
  uint64_t total_frames;
  uint32_t total_chunks;
  uint32_t free_chunks;
  uint32_t entry_count;
  uint32_t nominal_length_s;
  bool     writable;
} tape_info;

tape_result tape_get_info(const tape *t, tape_info *out);
tape_result tape_set_side(tape *t, tape_side side);
```

`tape_set_side` commits nothing and discards no pending state — it returns `TAPE_ERR_BUSY` if a recording is armed or uncommitted.

---

## 5. Transport

```c
tape_result tape_seek(tape *t, uint64_t frame);
uint64_t    tape_tell(const tape *t);
tape_result tape_set_rate(tape *t, int32_t rate_q16_16);
```

`rate_q16_16` is signed 16.16 fixed point. `0x00010000` is 1.0×. Negative values play in reverse. The transport uses 1.0× for play and ramps 4.0× → 12.0× while a scrub button is held, imitating a spool gaining momentum.

**Rate change is unfiltered.** A fractional phase accumulator with linear interpolation, and no anti-aliasing, no pitch preservation, no crossfade. The aliasing artefact is the intended sound of the device. A change that smooths it is a regression, and a test asserting its presence is a correct test.

```c
tape_result tape_render(tape *t, int16_t *out, uint32_t frames, uint32_t *rendered);
tape_result tape_service(tape *t, uint32_t block_budget, bool *more_work);
```

This split is the concession to firmware reality and the most important structural point in the API.

- **`tape_render` is interrupt-safe.** It pulls from `play_ring` only. It never touches the block device, never blocks, never takes a lock that a service call could hold. If the ring is short it writes what it has, sets `*rendered` accordingly, and returns `TAPE_ERR_UNDERRUN`. The caller fills the remainder with silence.
- **`tape_service` does all card I/O.** It runs on the main loop, does at most `block_budget` blocks of work, and sets `*more_work` if it has more to do. This is what makes the engine usable from a 44.1 kHz audio interrupt without a real-time operating system underneath it.

A desktop harness may call `tape_service` until `*more_work` is false and then `tape_render` in a loop, which makes desktop behaviour deterministic and byte-reproducible. Firmware interleaves them. **Both must produce identical output** — this is the cross-target contract that golden fixtures enforce.

---

## 6. Recording

```c
typedef enum {
  TAPE_REC_OVERWRITE = 0,
  TAPE_REC_OVERDUB,
  TAPE_REC_SPLICE,
} tape_rec_mode;

tape_result tape_arm(tape *t, tape_rec_mode mode);
tape_result tape_feed(tape *t, const int16_t *in, uint32_t frames, uint32_t *accepted);
tape_result tape_commit(tape *t);
tape_result tape_abort(tape *t);
```

`tape_arm` fails with `TAPE_ERR_READ_ONLY` on Side A or a read-only device.

`tape_feed` is interrupt-safe and writes into `rec_ring`; `tape_service` drains it to the card. `*accepted` may be less than `frames` when the ring is full or the cartridge is full. A short accept with `TAPE_ERR_CARTRIDGE_FULL` means allocation has reached `total_chunks`; the caller should stop the transport and commit, and the child keeps what was captured.

Overdub sums at 32-bit and soft-clips to 16-bit. It never wraps.

**`tape_commit` is the only call that changes what is on the card.** It executes format spec §7 exactly: flush chunks, write entries to the inactive slot, flush, then write the single 512-byte header block. That last write is the commit. Nothing else in this API mutates media state.

`tape_abort` discards pending chunks without committing. The next mount reclaims them automatically, because `free_next` is derived rather than stored.

---

## 7. Cartridge operations

```c
typedef void (*tape_progress_fn)(void *user, uint32_t done, uint32_t total);

tape_result tape_reset_side_b(tape *t);
tape_result tape_promote(tape *t, tape_progress_fn cb, void *user);
tape_result tape_respool(tape *t, uint32_t block_budget, bool *more_work);
tape_result tape_dup(tape *src, tape *dst, tape_progress_fn cb, void *user);
tape_result tape_format(const tape_dev *dev, const char *label,
                        uint32_t nominal_length_s);
```

`tape_reset_side_b` copies the live A index into B and commits. Sub-second, moves no audio.

`tape_promote` implements format spec §9.3 and reports progress for the LED row. Expect ~15 s.

`tape_respool` is incremental and interruptible on the same `block_budget` / `more_work` contract as `tape_service`, so it can run during idle on USB power without blocking the transport.

`tape_dup` copies whole-cartridge, source → destination. It **assigns the destination a fresh `cartridge_uuid`**. Progress must reflect true bytes transferred — the LED row between the slots is specified as informative, not decorative. Target under 30 s for a 90-minute cartridge.

`tape_format` writes both superblocks, four empty index slots, and an empty preroll cache, and generates a fresh UUID.

---

## 8. Invariants

Assertable at any quiescent point, and the property-based suite should generate arbitrary edit sequences and check all of them:

1. `total_frames` equals the sum of `frame_count` over live entries.
2. No live entry has `chunk_id ≥ total_chunks`.
3. No Side A entry has `chunk_id ≥ a_high_water`.
4. Every Side B allocation has `chunk_id ≥ a_high_water`.
5. Every entry has `frame_count ≥ 1` and `start_frame + frame_count ≤ 131072`.
6. `sequence` strictly increases across successive commits on one cartridge.
7. Re-spool preserves rendered audio bit-exactly.
8. Any edit sequence followed by re-spool renders identically to the same sequence without it.
9. No allocator symbol links into the engine.
10. `tape_render` performs zero block-device calls. Verifiable by counting calls on the simulator across a full playback.

---

## 9. What the engine must never contain

- Any `#ifdef` naming a board, chip, or peripheral.
- Any reference to buttons, LEDs, solenoids, codecs, jacks, or volume.
- Any API returning a pointer the caller must free.
- Any dependency beyond freestanding libc — no allocator, no file I/O, no floating point in the audio path.
- Any codec, container, or metadata parsing. A cartridge holds raw PCM; that is the entire architecture.

If the engine appears to need one of these, the design is wrong and it is a PM escalation rather than a patch.

---

## 10. Open items before freeze

- The `render`/`service` split assumes the caller can guarantee `tape_service` runs often enough. The failure mode is audible underrun rather than corruption, but the required service cadence should be stated as a number here once measured on the bench build.
- `block_budget` units are blocks; whether that is the right knob versus a time budget is worth challenging.
- Whether `tape_set_side` should implicitly commit rather than returning `TAPE_ERR_BUSY`. Current answer is no — implicit commits are how a child loses work they did not mean to keep — but the alternative is arguable.
