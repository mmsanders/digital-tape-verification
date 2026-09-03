# spec/engine-api.md — Tape Engine API v1.0

**Revision:** DRAFT-4 · **Issued:** 2 Sep 2026 · **Status:** for adversarial review; not frozen
**Owner:** Program Manager. Changes require PM sign-off.
**Supersedes:** DRAFT-3 (2 Sep). Incorporates V3-001…V3-016 per PM Decisions 005.
**Companion:** `spec/tapefs-v1.md` DRAFT-4, normative for everything on media.

C99. No operating system. No dynamic allocation, ever. No recursion. No libc file I/O. No floating point in the audio path. No clock. The only coupling to the outside world is the block device in §3.

---

## 1. The principles

> **1 — The engine computes. The caller owns anything that needs entropy, hardware knowledge, or memory beyond the engine's budget.**
> **2 — Identity and validity are written last**, after the content they describe.
> **3 — Ownership is not reference.** A side may reference chunks it does not own; it may only allocate and write within what it owns.

Principle 1 has now decided the warm-start buffer, the cartridge UUID, the format epoch, and the absence of any clock or timeout. Apply it before asking.

---

## 2. Error codes

```c
typedef enum {
  TAPE_OK = 0,
  TAPE_ERR_IO,                 /* block device returned failure */
  TAPE_ERR_BAD_MAGIC,
  TAPE_ERR_CRC,
  TAPE_ERR_VERSION,            /* version_major != 1; nothing written, no repair */
  TAPE_ERR_GEOMETRY,           /* fails tapefs §4.1 phase 2 */
  TAPE_ERR_INCOMPLETE,         /* superblock state == WRITE_IN_PROGRESS */
  TAPE_ERR_INCONSISTENT,       /* two valid copies that cannot be ordered: equal sb_generation and
                                  not byte-identical (superblock), or equal sequence at all (index) */
  TAPE_ERR_NO_VALID_INDEX,
  TAPE_ERR_READ_ONLY,          /* write against write == NULL, or against Side A */
  TAPE_ERR_CARTRIDGE_FULL,
  TAPE_ERR_INDEX_FULL,
  TAPE_ERR_DEST_TOO_SMALL,     /* tape_dup: destination cannot hold the source timeline */
  TAPE_ERR_SEQUENCE_EXHAUSTED,
  TAPE_ERR_NOT_MOUNTED,
  TAPE_ERR_BUSY,               /* the state matrix in §10 forbids this call now */
  TAPE_ERR_UNDERRUN,           /* tape_render had less than requested */
  TAPE_ERR_INVALID_ARG,        /* includes tape_dup aliasing */
} tape_result;
```

Every call returns `tape_result`. There are no error strings, no timeouts, and no clock.

---

## 3. Block device

```c
typedef struct {
  int (*read)(void *ctx, uint32_t lba, uint32_t count, void *dst);
  int (*write)(void *ctx, uint32_t lba, uint32_t count, const void *src);
  int (*flush)(void *ctx);
  void *ctx;
  uint32_t block_count;
} tape_dev;
```

Callbacks return **0 on success, non-zero on failure** — never engine error codes. `count` is in 512-byte blocks. **Every `tape_dev` is a block view of TAPEFS partition 2**; LBA 0 is that partition's first block. The engine never sees the MBR, and `tape_format` cannot create one — card provisioning belongs to `tapectl`.

**`write` is `NULL` for a read-only device.** There is no separate permission flag and no mode enum — the absence of the function *is* the permission. The engine tests `write != NULL` in exactly two places, both inside `dev.h`: `dev_write` itself, and the read-only predicate `tape_get_info` and the §10 matrix consult. Any write path that slips past both dereferences null and dies loudly in test rather than corrupting a cartridge in the field.

*(DRAFT-4's first cut said "no permission check" while simultaneously requiring `TAPE_ERR_READ_ONLY` returns, a read-only column in the state matrix, and a `write != NULL` condition on superblock repair. Those are permission checks. The claim is now what the design actually does: one mechanism, two call sites, both in one file.)*

`block_count` is caller-supplied and **untrusted**; `tapefs` §4.1 phase 2 validates the superblock's geometry against it in 64-bit and refuses on mismatch.

`flush` must not return success until data has reached media.

**All indirect calls go through three `static inline` wrappers in one file** — `dev_read`, `dev_write`, `dev_flush` in `engine/src/dev.h`. Nothing else dereferences a `tape_dev` member, with one declared exception: `tape_dup`'s aliasing check compares `dev.ctx` and lives in `dev.h` alongside the wrappers. CI checks this at source level and the exception is in the allowlist by name. `dev_write` asserts non-`NULL` **in debug builds only**; in release it dereferences.

Three implementations exist and the engine cannot distinguish them: file-backed (desktop), fault-injecting (crash harness — power-loss-after-N-writes and torn writes, the Verification Lead's, single injector per ADR-025), real SD (firmware).

---

## 4. Memory

The caller owns all storage. The engine allocates nothing, ever.

```c
size_t tape_instance_size(void);   /* compile-time constant */

tape_result tape_init(void *mem, size_t mem_len,
                      const tape_dev *dev,
                      void *play_ring, size_t play_ring_len,
                      void *rec_ring,  size_t rec_ring_len,
                      tape **out);
```

| Buffer | Minimum | Purpose |
|---|---|---|
| `mem` | `tape_instance_size()` | Live index, scratch index, superblock, staging blocks, all engine state |
| `play_ring` | 65 536 B | ~372 ms of playback. Retained across sleep by the caller for warm start |
| `rec_ring` | 65 536 B | ~372 ms of capture |

**Nothing engine-owned lives in `.bss`.** All per-instance state is inside `mem`, so two mounted cartridges — which `tape_dup` requires — cannot overwrite each other's index. This is not a style preference; it is a reentrancy requirement.

**Two budgets, both asserted in CI:**

| Budget | Ceiling | Counts |
|---|---|---|
| RAM | 200 KiB | `.data` + `.bss` + `tape_instance_size()`, summed. This is the single gate; `acceptance.md` WP-13 states the same sum |
| Flash | 32 KiB | `.rodata` |

`TAPE_MAX_ENTRIES` = 4 096 is an engine memory constraint, not a media one. **Stack:** maximum depth ≤ 8 KiB, asserted in CI from `-fstack-usage` and the call graph; this subsumes "no recursion".

---

## 5. Lifecycle

```c
typedef enum { TAPE_SIDE_A = 0, TAPE_SIDE_B = 1 } tape_side;

typedef struct {
  const void *data;        /* frames, same layout as tape_render output */
  uint32_t    valid_frames;
  uint32_t    start_frame; /* timeline frame the first sample represents */
  uint8_t     uuid[16];
  tape_side   side;
} tape_warm_start;

tape_result tape_mount(tape *t, tape_side side, uint64_t resume_frame,
                       const tape_warm_start *warm);   /* warm may be NULL */
tape_result tape_unmount(tape *t, uint64_t *out_position_frame);
```

`tape_mount` runs `tapefs` §4.1 in full — selection, admission, then repair — then §5.3 index-slot selection, then derives `free_next`, then seeks to `resume_frame` clamped to the timeline.

**The warm-start descriptor is validated, and a mismatch disables warm start rather than failing the mount** (V3-016). Warm start is used only if all of: `warm != NULL`; `warm->uuid` equals the mounted cartridge's UUID; `warm->side` equals the mounted side; and `[start_frame, start_frame + valid_frames)` contains `resume_frame`. Otherwise the field is ignored, `tape_get_info` reports `warm_start_used = false`, and the mount proceeds normally. A wrong buffer costs instant-on, never correctness.

`tape_unmount` returns the current position in **whole frames, truncated**. The engine never writes position to media.

Mounting a read-only device succeeds for either side; subsequent write calls return `TAPE_ERR_READ_ONLY`, and repair is skipped.

```c
typedef struct {
  uint8_t  uuid[16];
  char     label[33];
  uint32_t nominal_length_s;
  uint64_t total_frames;        /* of the mounted side */
  uint32_t total_chunks, free_chunks;
  uint32_t entry_count, entries_free;
  bool     writable;
  bool     needs_repair;        /* one superblock copy invalid; device read-only */
  bool     warm_start_used;
} tape_info;

tape_result tape_get_info(const tape *t, tape_info *out);
tape_result tape_set_side(tape *t, tape_side side);
```

`tape_set_side` commits nothing and discards nothing; `TAPE_ERR_BUSY` if a recording is armed or frames are owed. It does not implicitly commit — implicit commits are how a child loses work they did not mean to keep.

---

## 6. Transport

```c
tape_result tape_seek(tape *t, uint64_t frame);   /* beyond end clamps; TAPE_OK */
uint64_t    tape_tell(const tape *t);             /* whole frames, truncated */
tape_result tape_set_rate(tape *t, int32_t rate_q16_16);

tape_result tape_render(tape *t, int16_t *out, uint32_t frames, uint32_t *rendered);
tape_result tape_service(tape *t, uint32_t block_budget, bool *more_work);

typedef struct {
  bool     at_end, at_start;
  bool     recording_armed, frames_owed;
  uint32_t entries_free;         /* drives the record light's green/yellow/red */
  uint32_t free_chunks;
} tape_status_t;
tape_result tape_status(const tape *t, tape_status_t *out);
```

`rate_q16_16` is signed 16.16 fixed point; `0x00010000` is 1.0×; negative plays in reverse. **The engine accepts instantaneous rates only.** The scrub spool-up ramp is owned by firmware and specified as a rate-versus-time schedule in `acceptance.md`, so it can be golden-tested by driving `tape_set_rate` from a table.

**Position representation.** Position is `uint64_t` with 32 fractional bits, so the whole part holds 32 bits of frames — which is why `tapefs` §5.4 caps `total_frames` at 2³² − 1. The step and the endpoint clamp are computed as follows, and this is normative because DRAFT-3's `(int64_t)rate << 16` was undefined behaviour on negative rates and its unsigned addition could wrap at either end (V3-010):

```c
const uint64_t max_pos = ((uint64_t)total_frames) << 32;   /* fits: (2^32-1)<<32 < 2^64 */
const int64_t  step    = (int64_t)rate_q16_16 * 65536;     /* 16.16 -> 32.32, defined for negatives */

if (step >= 0) {
    uint64_t s = (uint64_t)step;
    if (position > max_pos - s) { position = max_pos; at_end = true; }
    else                          position += s;
} else {
    uint64_t s = (uint64_t)(-step);
    if (position < s) { position = 0; at_start = true; }
    else               position -= s;
}
```

The clamp is evaluated **before** each sample is fetched, not after.

`position == max_pos` means the playhead is one past the last frame. In that state `tape_render` fetches nothing, sets `*rendered = 0` and reports `at_end` (§11); the `i = position >> 32` indexing in §8 is never evaluated there. So §8's `b = a` rule covers `i` at the last frame, and `i` beyond it is unreachable rather than undefined — DRAFT-4's first cut left that gap open between §6, §8 and §11.

**`tape_render` is interrupt-safe.** It pulls from `play_ring` only, never touches the block device, never blocks. On a short ring it writes what it has, sets `*rendered`, returns `TAPE_ERR_UNDERRUN`; the caller fills the rest with silence. **`tape_service` does all card I/O**, at most `block_budget` blocks per call, setting `*more_work` if more remains.

A desktop harness services to completion then renders, making output deterministic; firmware interleaves them. **Both produce identical bytes** — the cross-target contract. `tape_render` performs zero block-device calls; the simulator counts them and the suite asserts zero across a full playback.

---

## 7. Recording

```c
typedef enum { TAPE_REC_OVERWRITE = 0, TAPE_REC_OVERDUB, TAPE_REC_SPLICE } tape_rec_mode;

tape_result tape_arm(tape *t, tape_rec_mode mode);
tape_result tape_feed(tape *t, const int16_t *in, uint32_t frames, uint32_t *accepted);
tape_result tape_commit(tape *t);
tape_result tape_abort(tape *t);
```

`tape_arm` fails with `TAPE_ERR_READ_ONLY` on Side A or a read-only device, and `TAPE_ERR_INDEX_FULL` if `entries_free` is insufficient for the requested mode.

**The recording cursor is fixed at arm time.** `tape_arm` captures the current position as the edit point, and §10 forbids `tape_seek` and `tape_set_rate` while armed — so there is exactly one position the edit can apply at, and no reading of the spec produces a different one (V3-011).

**`tape_feed` reserves before it accepts.** It computes remaining capacity from `total_chunks` and the in-memory bump pointer **without I/O**, and accepts only frames it can guarantee a chunk for. `*accepted < frames` with `TAPE_ERR_CARTRIDGE_FULL` means the cartridge is full *now*, reported in the call that hit the wall; `tape_service` never discovers fullness on its own. Accepted frames are **owed** by the engine and will be committed.

**`tape_commit` refuses while frames are owed.** If `rec_ring` is non-empty it returns `TAPE_ERR_BUSY`; the caller runs `tape_service` until `frames_owed` clears, then commits. Once `tape_commit` has been called, `tape_feed` returns `TAPE_ERR_BUSY` until the commit completes or is aborted. `tape_commit` executes `tapefs` §8 exactly, including the final flush.

`tape_abort` discards owed frames and pending chunks. The next mount reclaims them, because `free_next` is derived.

---

## 8. Exact audio arithmetic

Both formulas are normative; independent implementations must produce identical bytes.

**Overdub — a saturating clamp.** Not a curve, not a wrap.

```c
int32_t s = (int32_t)e + (int32_t)x;
if (s >  32767) s =  32767;
if (s < -32768) s = -32768;
out = (int16_t)s;
```

**Variable-rate playback.** Let `i = position >> 32`, `f = (uint32_t)position`, `a` = frame `i`, `b` = frame `i + 1` per channel. If `i + 1` is beyond the last frame, `b = a`.

```c
out = (int16_t)( a + (int32_t)( ((int64_t)(b - a) * (int64_t)f) >> 32 ) );
```

Arithmetic shift; truncation toward negative infinity; no rounding; channels independent with the same `f`. No anti-aliasing, no pitch preservation, no crossfade — the aliasing is the intended sound.

---

## 9. Cartridge operations

```c
typedef void (*tape_progress_fn)(void *user, uint32_t blocks_done, uint32_t blocks_total);

tape_result tape_reset_side_b(tape *t);
tape_result tape_promote(tape *t, uint32_t block_budget, bool *more_work,
                         tape_progress_fn cb, void *user);
tape_result tape_respool(tape *t, uint32_t block_budget, bool *more_work);
tape_result tape_dup(tape *src, const tape_dev *dst_dev,
                     const uint8_t new_uuid[16], uint32_t epoch,
                     uint32_t dst_nominal_length_s,
                     uint32_t block_budget, bool *more_work,
                     tape_progress_fn cb, void *user);
tape_result tape_format(const tape_dev *dev, const uint8_t uuid[16], uint32_t epoch,
                        const char *label, uint32_t nominal_length_s);
```

Progress callbacks carry **counts only**. Rates and ETAs belong to the caller, because only the caller knows what a second is. `tape_respool`, `tape_promote` and `tape_dup` share one incremental contract: each call does at most `block_budget` blocks of work and sets `*more_work` while any remains. **Do not add `timeout_ms` to any engine call** — it will look like a bug fix during SD bring-up and it is a principle-1 violation.

- `tape_reset_side_b` — `tapefs` §9.2. Sub-second, moves no audio, and the resulting Side B references Side A's chunks, which Rule 3 permits.
- `tape_promote` — `tapefs` §9.3, two phases with B committed in phase 1, incremental on `block_budget` / `more_work`. Roughly 30 s of wall time in total, driven across many calls.
- `tape_respool` — `tapefs` §9.4, incremental on the `block_budget` contract, at most two passes, second pass optional.
- `tape_dup` — `tapefs` §9.5, incremental. Takes the destination as a **`tape_dev *`, not a mounted `tape`**, so a blank or interrupted destination can be written and a failed copy can be re-run. **Rejects aliasing and insufficient capacity before any write.** Destination geometry derives from the destination's own `block_count` and the caller's `dst_nominal_length_s`. Copies Side A only; the destination's Side B is initialised to mirror it.
- `tape_format` — `tapefs` §9.6, an ordered destructive transaction; `total_chunks` from §2's formula.

---

## 10. State matrix

**Normative.** The grouped `seek/rate/render` column of DRAFT-3 is split, and `tape_service` and the query calls are present (V3-011).

**B** = `TAPE_ERR_BUSY`; **✓** = allowed; **W** = requires a writable **device** (`write != NULL`), else `TAPE_ERR_READ_ONLY`.

> **W is about the device, not the mounted side.** DRAFT-4's first cut marked these RO and defined `TAPE_ERR_READ_ONLY` as "write against `write == NULL`, **or against Side A**" — which forbade `tape_promote` from a Side-A mount and forbade `tape_dup` outright, since duplicating writes the destination's Side A by definition. The Side-A rule applies to `tape_arm` and `tape_feed` only: those write *the mounted side*. `reset_b`, `promote` and `dup` write regions chosen by the operation, not by what is mounted.

`tape_dup` takes a source `tape *` and a destination `tape_dev *`, so only the source's row applies; the destination is a raw device with no state in this table. Its own preconditions are in `tapefs` §9.5.

| State ↓ / Call → | seek | set_rate | render | service | status / info / tell | arm | feed | commit | abort | set_side | reset_b | promote | respool | dup (as src) | unmount |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Mounted, idle | ✓ | ✓ | ✓ | ✓ | ✓ | W+SideB | B | B | B | ✓ | W | W | W | ✓ | ✓ |
| Playing (rate ≠ 0) | ✓ | ✓ | ✓ | ✓ | ✓ | W+SideB | B | B | B | B | B | B | B | ✓ | ✓ |
| Armed, no frames owed | **B** | **B** | ✓ | ✓ | ✓ | B | ✓ | ✓ | ✓ | B | B | B | B | B | B |
| Armed, frames owed | **B** | **B** | ✓ | ✓ | ✓ | B | ✓ | **B** | ✓ | B | B | B | B | B | B |
| Commit in progress | B | B | ✓ | ✓ | ✓ | B | B | B | **✓** | B | B | B | B | B | B |
| Respool / promote / dup in progress | B | B | ✓ | ✓ | ✓ | B | B | B | B | B | B | B | B | B | B |
| Not mounted | `TAPE_ERR_NOT_MOUNTED` for all except `tape_mount`, `tape_format`, `tape_init`, and `tape_dup` on the destination device |

**`tape_arm` is the only call gated on the mounted side** — `W+SideB` means a writable device and `TAPE_SIDE_B`; Side A gives `TAPE_ERR_READ_ONLY`.

**`tape_abort` is permitted during a commit** and takes effect if the index header block (`tapefs` §8 step 5) has not yet been written; after that the commit has happened and `tape_abort` returns `TAPE_ERR_BUSY`. DRAFT-4's first cut said `tape_feed` unblocks when a commit "completes or is aborted" while forbidding abort in that row, which made the second clause unreachable.

**Long operations and the in-progress rows.** `tape_respool`, `tape_promote` and `tape_dup` all take `block_budget` / `more_work` and are driven to completion by repeated calls. The in-progress row is the state between those calls, and `tape_render` and `tape_service` stay allowed throughout so audio never stops. DRAFT-4's first cut gave only `tape_respool` a budget while specifying a "~30 s" blocking `tape_promote` in an engine with a hard audio-servicing requirement and no clock; all three now share one contract.

**`tape_seek` and `tape_set_rate` are forbidden while armed.** The recording cursor is fixed at arm time (§7). This resolves the ambiguity by removing it rather than documenting it, and it matches the object: you cannot seek a tape deck while it is recording, because the head is where the head is.

**`tape_render` stays allowed while armed** so firmware can monitor, and `tape_service` is always allowed because it is the call that clears owed frames and advances every long operation.

**`tape_unmount` while armed is refused.** The caller must commit or abort first, so a child's recording is never silently dropped by a firmware path that forgot to ask.

---

## 11. Boundary semantics

| Situation | Result |
|---|---|
| `tape_seek` beyond end | Clamp to end, `TAPE_OK` |
| Forward render at exact end | `*rendered` = 0, `TAPE_OK`, `at_end` set |
| Reverse render at frame 0 | `*rendered` = 0, `TAPE_OK`, `at_start` set |
| Splice into an empty side | Creates the first entry at position 0 |
| Splice at exact end | Append |
| Overwrite at end | Append |
| Overdub at end | Append; input passes through unchanged |
| Any edit beyond end | Unreachable — position is always clamped |

End of tape is not an error. Firmware turns `at_end` into the play button popping up.

---

## 12. Invariants

Assertable at any quiescent point. The property suite generates arbitrary edit sequences and checks all of them.

1. `total_frames` equals the sum of `frame_count` over live entries, computed in 64-bit.
2. `total_frames ≤ TAPE_MAX_TOTAL_FRAMES`.
3. No live entry's `last` (tapefs §5.1) is ≥ `total_chunks`.
4. No **Side A** entry's `last` is ≥ `a_high_water`.
5. **Every chunk Side B *allocates or writes* has id ≥ `a_high_water`.** Side B *referencing* chunks below the mark is correct and expected — it is what reset-B and a completed promote produce. *(DRAFT-3's invariant 4 forbade the reference and was unsatisfiable; V3-009.)*
6. Every entry has `frame_count ≥ 1` and `start_frame < CHUNK_FRAMES`.
7. `sequence` and `sb_generation` strictly increase across successive **logical** updates; superblock repair does not increment `sb_generation`.
8. Re-spool preserves rendered audio bit-exactly; after a completed pass, the side is one entry.
9. Any edit sequence followed by re-spool renders identically to the same sequence without it.
10. **Every re-spool and promote write destination is disjoint from the live set of both sides at the moment of that write.**
11. After a completed promote, `a_high_water` equals the timeline's chunk count and no allocated chunk is unreachable.
12. `free_next` equals `max(a_high_water, max over live-B entries of last + 1)` — recomputed at mount, never stored.
13. No allocator symbol links into the engine.
14. `tape_render` performs zero block-device calls.
15. No indirect call exists outside the three `dev_*` wrappers.
16. Maximum stack depth ≤ 8 KiB.
17. `tape_dup` writes the destination's `state = VALID` and `cartridge_uuid` in the final superblock write, after all chunks and both indices.
18. `tape_dup` performs zero writes when it rejects for aliasing or insufficient capacity.
19. No engine-owned state lives outside the caller's `mem` block.
20. Entry chunk extents within one index do not overlap except where their frame ranges are disjoint (`tapefs` §5.1). Promote's phase-2 safety check assumes nothing about this, but mount rejects media violating it.
21. Promote writes below `a_high_water` only in phase 2, only after both live indices reference `[S, S+len)`, and only after the explicit disjointness check in `tapefs` §9.3 step 5 passes.
22. `tape_promote` on a Side B with `total_frames == 0` returns `TAPE_ERR_INVALID_ARG` and writes nothing.

---

## 13. What the engine must never contain

Any `#ifdef` naming a board, chip or peripheral. Any reference to buttons, LEDs, solenoids, codecs, jacks or volume. Any API returning a pointer the caller must free. Any dependency beyond freestanding libc. Any clock, timer or timeout. Any entropy source. Any codec, container or metadata parsing. Any static buffer holding per-instance state.

If the engine appears to need one of these, apply §1 first; if it still does, escalate.

---

## 14. Open before freeze

- The required `tape_service` cadence, as a number, once the bench build measures it. The failure mode is audible underrun, not corruption.
- Whether `tape_status` should expose `sb_generation`/`sequence` for `tapectl verify`. Cheap; not needed by firmware.
- Whether `block_budget` should be blocks or bytes. Blocks matches what the device does.
