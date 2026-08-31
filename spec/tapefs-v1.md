# spec/tapefs-v1.md — TAPEFS v1.0

**Status:** DRAFT-1, issued for adversarial review. Not frozen.
**Owner:** Program Manager. Changes require PM sign-off.
**Issued:** 31 Aug 2026

This is the on-media format for a Digital Tape Player cartridge. It is normative and byte-exact. Where it is ambiguous, that is a defect — report it.

---

## 1. Constants

| Name | Value |
|---|---|
| `SAMPLE_RATE` | 44100 Hz |
| `CHANNELS` | 2 (interleaved, L then R) |
| `SAMPLE_FORMAT` | signed 16-bit little-endian |
| `FRAME_BYTES` | 4 |
| `BYTE_RATE` | 176 400 B/s |
| `BLOCK_BYTES` | 512 (one SD block; the addressable unit) |
| `CHUNK_BYTES` | 524 288 (512 KiB) |
| `CHUNK_FRAMES` | 131 072 |
| `CHUNK_BLOCKS` | 1024 |
| `CHUNK_SECONDS` | 2.97233… |
| `INDEX_SLOT_BYTES` | 65 536 (64 KiB, 128 blocks) |
| `TAPE_MAX_ENTRIES` | 4096 |

All multi-byte integers are little-endian. All CRCs are CRC-32/ISO-HDLC (IEEE 802.3): polynomial 0x04C11DB7 reflected to 0xEDB88320, init 0xFFFFFFFF, reflect in/out, final XOR 0xFFFFFFFF.

---

## 2. Media layout

A cartridge card carries an MBR with two partitions.

| # | Type | Size | Contents |
|---|---|---|---|
| 1 | 0x0C (FAT32 LBA) | 16 MiB | `README.TXT` explaining what the card is, plus optional label art. Never read by the device. Exists so a card plugged into a computer shows something human. |
| 2 | 0xDA (non-FS data) | remainder | TAPEFS. |

All LBAs below are relative to the start of partition 2.

| LBA | Blocks | Region |
|---|---|---|
| 0 | 8 | Superblock, primary (only block 0 is used; 1–7 reserved) |
| 8 | 128 | Index slot **A0** |
| 136 | 128 | Index slot **A1** |
| 264 | 128 | Index slot **B0** |
| 392 | 128 | Index slot **B1** |
| 520 | 1024 | Preroll cache |
| 1544 | 504 | Reserved (alignment padding) |
| 2048 | `total_chunks × 1024` | Chunk store. Chunk *N* begins at LBA `2048 + N × 1024`. |
| *last block of partition* | 1 | Superblock, mirror |

The chunk store base is at a 1 MiB offset, which is erase-block aligned on every card this device supports.

---

## 3. Superblock (512 bytes)

| Offset | Size | Field | Notes |
|---|---|---|---|
| 0 | 8 | `magic` | `54 41 50 45 46 53 00 01` — `"TAPEFS\0\x01"` |
| 8 | 2 | `version_major` | 1 |
| 10 | 2 | `version_minor` | 0 |
| 12 | 16 | `cartridge_uuid` | RFC 4122 v4 |
| 28 | 4 | `sample_rate` | 44100 |
| 32 | 2 | `channels` | 2 |
| 34 | 2 | `bits_per_sample` | 16 |
| 36 | 4 | `chunk_bytes` | 524288 |
| 40 | 4 | `nominal_length_s` | 5400. **Informational only** — the number on the label. Not a limit. |
| 44 | 4 | `total_chunks` | Capacity of the chunk store |
| 48 | 4 | `a_high_water` | Chunk ids `[0, a_high_water)` belong to Side A and are immutable |
| 52 | 4 | `preroll_frames` | Valid frames in the preroll cache |
| 56 | 4 | `index_slot_bytes` | 65536 |
| 60 | 4 | `lba_index_a0` | 8 |
| 64 | 4 | `lba_index_a1` | 136 |
| 68 | 4 | `lba_index_b0` | 264 |
| 72 | 4 | `lba_index_b1` | 392 |
| 76 | 4 | `lba_preroll` | 520 |
| 80 | 4 | `lba_chunk_base` | 2048 |
| 84 | 4 | `lba_superblock_mirror` | partition size − 1 |
| 88 | 32 | `label` | UTF-8, NUL-padded. Advisory; the physical label is authoritative |
| 120 | 4 | `format_epoch` | Unix time of format. Informational |
| 124 | 380 | *reserved* | Zero |
| 508 | 4 | `crc32` | Over bytes 0…507 |

**There is no stored free-space pointer.** See §6.

The primary superblock is authoritative. The mirror is read only when the primary fails magic, version or CRC; on a successful fallback the engine rewrites the primary from the mirror. If both fail, the cartridge does not mount.

---

## 4. Index slot (65 536 bytes)

Header, 64 bytes:

| Offset | Size | Field |
|---|---|---|
| 0 | 8 | `magic` = `"TAPEIDX\x01"` |
| 8 | 4 | `sequence` (u32) |
| 12 | 1 | `side` — 0 = A, 1 = B |
| 13 | 3 | *reserved*, zero |
| 16 | 4 | `entry_count` (≤ `TAPE_MAX_ENTRIES`) |
| 20 | 8 | `total_frames` (u64) — sum of all `frame_count` values |
| 28 | 32 | *reserved*, zero |
| 60 | 4 | `crc32` |

`crc32` is computed over bytes 0…59 of this header **concatenated with** the entry array, `entry_count × 12` bytes beginning at offset 64. Bytes beyond the entry array are undefined and not covered.

Entry, 12 bytes, at offset `64 + 12 × i`:

| Offset | Size | Field |
|---|---|---|
| 0 | 4 | `chunk_id` |
| 4 | 4 | `start_frame` — 0 … 131071 |
| 8 | 4 | `frame_count` — 1 … 131072 |

Entries are ordered by timeline position. Timeline position of entry *i* is the sum of `frame_count` over entries 0…*i*−1. **Seek is therefore O(n) over a prefix sum**; implementations may cache the prefix array, which is not part of the on-media format.

`sequence` is monotonic **per cartridge**, shared across all four slots. It increments by one on every commit to either side.

---

## 5. Chunks

A chunk is 131 072 frames of raw interleaved PCM. No header, no footer, no padding.

A chunk written partially — the last one of a recording — still occupies a full chunk slot. Bytes beyond the referenced range are **undefined, not zero**.

> **Consequence for testing.** "Side A is byte-identical" must be evaluated over *referenced frames only*, reconstructed through the index. A raw region compare will produce false failures on the tail chunk. This is the correct definition, not a concession.

---

## 6. Allocation, and why nothing tracks free space

Chunk ids partition as follows:

- `[0, a_high_water)` — Side A. Immutable. No runtime code path writes here.
- `[a_high_water, free_next)` — allocated to Side B.
- `[free_next, total_chunks)` — free.

**`free_next` is derived at mount time, never stored:**

```
free_next = max(entry.chunk_id + 1  for entry in B_live_index)
            floored at a_high_water
```

This is the single most important structural decision in the format, and it is worth stating why. Because allocation is a bump pointer over a value derived from the *committed* index, chunks written during an operation that never committed are, by construction, above `free_next` on the next mount — and are silently reused. **The aborted-write leak class does not exist.** There is nothing to reclaim and nothing to garbage-collect.

One leak source remains and is bounded: chunks superseded by an overwrite, which sit below the live maximum and stay allocated. These are reclaimed by re-spool (§9), which rewrites Side B compactly from `a_high_water` upward.

---

## 7. The commit protocol

This is the load-bearing mechanism of the whole design.

An index slot is 128 blocks and **cannot** be written atomically. Atomicity is achieved by ordering, not by size:

1. Allocate chunks by bumping `free_next` in memory. Write chunk data to the card.
2. **Flush** — chunk data must reach media before step 3 begins. On SD this means waiting for the card to leave the busy state, not merely for the controller to accept the blocks.
3. Write the entry array into blocks 1…127 of the **inactive** slot for this side.
4. **Flush.**
5. Write block 0 of that slot — the 64-byte header, zero-padded to 512 — carrying the new `sequence`, `entry_count`, `total_frames`, and the CRC covering the entries just written.

**Step 5 is the commit.** It is a single 512-byte block write.

Before step 5, block 0 still holds the previous generation's header, whose stored CRC will not match the newly written entries. A crash at any point before step 5 therefore leaves a slot that fails validation, and mount falls back to the other slot — which is untouched and still describes the pre-operation state. A crash *during* step 5 leaves a header that fails its own CRC, with the same result.

**The assumption this rests on:** that a 512-byte SD block write is atomic under power loss — it either lands entirely or not at all. This is true of essentially every SD card in practice and is not universally guaranteed by the specification. It should be tested against real media, not inherited. See §12.

---

## 8. Mount

1. Read the primary superblock. Validate magic, `version_major`, CRC. On failure read the mirror; on success from the mirror, rewrite the primary. If both fail → `TAPE_ERR_BAD_MAGIC` / `TAPE_ERR_CRC`.
2. `version_major` ≠ 1 → refuse, `TAPE_ERR_VERSION`. `version_minor` > 0 → mount **read-only**.
3. For each side, read both slots. A slot is **valid** iff all of:
   - `magic` matches;
   - `side` matches the slot's assignment;
   - `entry_count` ≤ `TAPE_MAX_ENTRIES`;
   - `crc32` verifies;
   - `total_frames` equals the sum of `frame_count` across entries;
   - every entry satisfies `frame_count ≥ 1`, `start_frame + frame_count ≤ 131072`, `chunk_id < total_chunks`;
   - **for side A only:** every `chunk_id < a_high_water`.
4. The **live** slot is the valid slot with the higher `sequence`.
5. If both slots for a side are valid **with equal `sequence`** → that side does not mount; `TAPE_ERR_INCONSISTENT`. This state is unreachable via §7 and indicates a media fault or an implementation bug. It is not recovered from silently, on purpose.
6. If neither slot is valid → `TAPE_ERR_NO_VALID_INDEX` for that side. Side A in this state means the cartridge is unusable. Side B in this state is recoverable by `tape_reset_side_b`.
7. Derive `free_next` per §6.

**Sequence exhaustion.** `sequence` is u32. At one commit per second that is 136 years. On reaching 0xFFFFFFFE the engine returns `TAPE_ERR_SEQUENCE_EXHAUSTED` and refuses further commits. It does not wrap.

---

## 9. Operations

### 9.1 Record — overwrite, overdub, splice

All three allocate fresh chunks and commit per §7. None modifies a chunk in place.

- **Overwrite** replaces the timeline from the current position with new input. Index entries wholly covered are dropped; a partially covered entry is trimmed by adjusting `start_frame`/`frame_count`.
- **Overdub** reads existing frames, adds the input sample-wise, and writes the result to new chunks. Addition is performed at 32-bit and **soft-clipped** to 16-bit — never wrapped. Wraparound in headphones on a child is a safety issue, not an audio-quality one.
- **Splice** inserts at the current position, pushing everything after it later. The entry containing the insertion point is split into two; new entries for the inserted material go between them.

`nominal_length_s` is not a limit. Splice may extend the timeline past 90 minutes. The real limits are `total_chunks` and `TAPE_MAX_ENTRIES`.

**Cartridge full mid-recording.** When allocation reaches `total_chunks`, `tape_feed` accepts fewer frames than offered and returns `TAPE_ERR_CARTRIDGE_FULL`. Chunks already written stay pending until the caller calls `tape_commit`. The intended firmware behaviour is to stop the transport, pop the buttons, and commit — **the child keeps everything they recorded up to the moment it filled.**

**Index full.** Splice that would exceed `TAPE_MAX_ENTRIES` returns `TAPE_ERR_INDEX_FULL`. Recovery is re-spool, which coalesces adjacent entries that are contiguous in the chunk store. If re-spool cannot bring the count below the cap, the cartridge has reached its edit limit — a defined, reportable state rather than a corruption.

### 9.2 Reset Side B

Copy the live Side A index content into Side B's inactive slot, with `side` = 1 and `sequence` + 1, and commit per §7. Touches no audio. Completes in well under a second.

### 9.3 Promote Side B to Side A

The only destructive operation in the format, and the only multi-step one.

1. Build a compacted copy of Side B's timeline into fresh chunks beginning at `free_next`; call that range `[S, E)`.
2. Write and commit a new Side A index referencing `[S, E)`, `sequence` + 1.
3. Write a new superblock with `a_high_water = E`. Single block, atomic.
4. Write and commit a new Side B index identical to the new A index, `sequence` + 2.
5. Regenerate the preroll cache.

**Recovery.** A crash between 2 and 3 leaves a Side A index referencing chunk ids ≥ `a_high_water`, which §8.3 rejects — so mount falls back to A's previous generation and the promote simply did not happen. A crash between 3 and 4 leaves A new and B stale; both are internally valid, so the cartridge mounts and plays. B's old chunks now sit below `a_high_water` and are immutable; the space is recovered on the next re-spool. This is inconsistent but not corrupt, and the spec accepts it.

### 9.4 Re-spool

Rewrites Side B's chunks into linear timeline order starting at `a_high_water`, coalescing adjacent entries, then commits a new index. Reclaims superseded chunks. Preserves audio bit-exactly — only layout changes.

Interruptible: it performs no commit until the rewrite is complete, so an interrupted re-spool leaves the previous index live and the partial work above `free_next`, to be reused.

### 9.5 Duplicate

Whole-cartridge copy, always source slot → work slot.

**The destination is assigned a freshly generated `cartridge_uuid`.** A copy is a different cartridge. Reproducing the UUID would make two physical objects claim one identity, and any device-side state keyed by UUID — including the resume-position table in §10 — would silently merge them.

---

## 10. What the cartridge does *not* store

**Playback position is not stored on the cartridge.** It cannot be: the source slot is read-only, so a cartridge played there has no writable surface. Resume position lives in the device's own flash as a table of `{cartridge_uuid → frame_position}` covering the most recently used ~64 cartridges, evicted least-recently-used. The engine exposes position as an in/out parameter at mount and unmount (`spec/engine-api.md` §5) and never writes it to media.

This is why §9.5 assigns a fresh UUID on copy.

---

## 11. Preroll cache

Holds the first `preroll_frames` frames of **Side A's** timeline, reconstructed through A's index, laid out linearly. Capacity 131 072 frames (2.97 s). Regenerated on format and on promote.

Its purpose is instant-on: playback begins from this region while the card completes initialisation, which costs 100–500 ms.

Side B has no preroll cache. Selecting Side B pays normal mount latency. The justification is that Side A is what a child presses play on cold, and Side B is what they are already in the middle of using — and that maintaining a B preroll would add a 512 KiB rewrite to every commit. **This is a judgement call and a reasonable thing to challenge.**

---

## 12. Assumptions this format inherits

Stated explicitly so they can be attacked rather than assumed.

1. A 512-byte SD block write is atomic under power loss (§7). Needs testing against real media, not just simulation.
2. A flush that returns success means data has reached media, not merely the card's controller.
3. Card wear from re-spool and promote is acceptable at family-use write volumes.
4. A cartridge is never mounted by two hosts concurrently.
5. `total_chunks` fits in u32 — true to 2 TiB of chunk store.

---

## 13. Open items before freeze

- The resume-position resolution in §10 and the fresh-UUID rule in §9.5 are a **proposal**, not a decision. Both are open for challenge.
- The Side-B-has-no-preroll decision in §11.
- `TAPE_MAX_ENTRIES` = 4096 is set by the engine's static memory budget, not by any media constraint. If review shows heavy splicing exhausts it in ordinary use, the budget is the thing to revisit.
