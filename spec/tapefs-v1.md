# spec/tapefs-v1.md — TAPEFS v1.0

**Revision:** DRAFT-4 · **Issued:** 2 Sep 2026 · **Status:** for adversarial review; not frozen
**Owner:** Program Manager. Changes require PM sign-off (escalation trigger #1).
**Supersedes:** DRAFT-3 (2 Sep). Incorporates all sixteen findings V3-001…V3-016 per PM Decisions 005.

This is the on-media format for a Digital Tape Player cartridge. It is normative and byte-exact. Where it is ambiguous, that is a defect — report it.

**Three findings were resolved by design decision rather than correction and are the least-scrutinised text here: §9.3 (promote's phase-1 double commit), §9.4 (per-pass disjointness) and the forbid-while-armed rule in `engine-api.md` §10. Attack those first.**

---

## 0. Three rules that govern everything below

**Rule 1 — The engine computes. The caller owns anything that needs entropy, hardware knowledge, or memory beyond the engine's budget.** The cartridge UUID, the format epoch, the warm-start buffer and the block device's geometry are all supplied by the caller. The engine never generates identity, never reads a clock, and never trusts `block_count`.

**Rule 2 — Identity and validity are written last**, after the content they describe. A cartridge interrupted mid-operation is recognisably unfinished, never silently wrong.

**Rule 3 — Ownership is not reference.** A side may *reference* chunks it does not *own*. It may only allocate and write within what it owns. This is the copy-on-write mechanism the whole format rests on, and DRAFT-3 contradicted it (V3-009).

---

## 1. Constants

| Name | Value |
|---|---|
| `SAMPLE_RATE` | 44 100 Hz |
| `CHANNELS` | 2, interleaved L then R |
| `SAMPLE_FORMAT` | signed 16-bit little-endian |
| `FRAME_BYTES` | 4 |
| `BYTE_RATE` | 176 400 B/s |
| `BLOCK_BYTES` | 512 |
| `CHUNK_BYTES` | 524 288 (512 KiB) |
| `CHUNK_FRAMES` | 131 072 |
| `CHUNK_BLOCKS` | 1 024 |
| `CHUNK_SECONDS` | 2.972154195… (= 131 072 / 44 100) |
| `INDEX_SLOT_BYTES` | 65 536 (128 blocks) |
| `INDEX_ENTRY_BYTES` | 12 |
| `TAPE_MAX_ENTRIES` | 4 096 (blocks 1–96 of a slot) |
| `TAPE_MAX_TOTAL_FRAMES` | 4 294 967 295 (2³² − 1) — see §5.4 |

All multi-byte integers are little-endian. All CRCs are CRC-32/ISO-HDLC: polynomial 0xEDB88320 (reflected), init 0xFFFFFFFF, reflect in and out, final XOR 0xFFFFFFFF.

---

## 2. Tape lengths

Length is a **format-time parameter**, not a format constant. Every region size derives from it.

**Normative formula.** Given `nominal_length_s`, computed in 64-bit with overflow check:

```
frames       = (uint64_t)nominal_length_s * SAMPLE_RATE
total_chunks = (frames + CHUNK_FRAMES - 1) / CHUNK_FRAMES      /* ceiling */
reject if total_chunks == 0 or total_chunks > UINT32_MAX
reject if frames > TAPE_MAX_TOTAL_FRAMES                        /* §5.4 */
```

The store must cover the **full** labelled duration. A cartridge that cannot hold the time printed on it is a defect.

| Designation | `nominal_length_s` | `total_chunks` | Side A store | Holds | Copy at high-speed 4-bit (~22 MB/s) |
|---|---|---|---|---|---|
| **C-60 — the standard cartridge** | 3 600 | **1 212** | 635.4 MB | 3 602.25 s | ~29 s |
| C-90 | 5 400 | 1 817 | 952.6 MB | 5 400.40 s | ~43 s |
| C-120 | 7 200 | **2 423** | 1 270.3 MB | 7 201.53 s | ~58 s |

> DRAFT-3 gave 1 211 and 2 422 — a truncation where the formula requires a ceiling. A "C-60" formatted to DRAFT-3 held 3 599.28 s, twenty-eight hundredths of a second short of its own label (V3-012).

**C-60 is the standard.** It meets the 30-second copy target on the plain 3.3 V high-speed interface with a write rate every V30 card guarantees. Longer cartridges are permitted, copy more slowly, and say so on the label. `nominal_length_s` is not a limit on Side B's timeline (§9.1); it is what the label says.

---

## 3. Media layout

MBR with two partitions. **Provisioning the MBR and partition 1 is `tapectl`'s job.** Every `tape_dev` the engine sees is a block view of partition 2 alone; LBA 0 below is that partition's first block. The engine never sees the MBR.

| # | Type | Size | Contents |
|---|---|---|---|
| 1 | 0x0C FAT32 | 16 MiB | `README.TXT`, optional label art. Never read by the device |
| 2 | 0xDA | remainder | TAPEFS |

| LBA | Blocks | Region |
|---|---|---|
| 0 | 8 | Superblock, primary. Block 0 used; 1–7 reserved, zero |
| 8 | 128 | Index slot **A0** |
| 136 | 128 | Index slot **A1** |
| 264 | 128 | Index slot **B0** |
| 392 | 128 | Index slot **B1** |
| 520 | 1 528 | Reserved, zero (alignment padding) |
| 2 048 | `total_chunks × 1024` | Chunk store. Chunk *N* at `lba_chunk_base + N × 1024` |
| *`block_count − 1`* | 1 | Superblock, mirror |

There is no preroll cache. Instant-on is not a format feature (§12).

---

## 4. Superblock (512 bytes)

| Offset | Size | Field | Notes |
|---|---|---|---|
| 0 | 8 | `magic` | `54 41 50 45 46 53 00 01` — `"TAPEFS\0\x01"` |
| 8 | 2 | `version_major` | 1 |
| 10 | 2 | `version_minor` | 0 |
| 12 | 4 | `sb_generation` | Incremented once per **logical** update; see §4.1 |
| 16 | 1 | `state` | 0 = `VALID`, 1 = `WRITE_IN_PROGRESS` |
| 17 | 3 | *reserved* | zero |
| 20 | 16 | `cartridge_uuid` | Caller-supplied. The engine only stores it |
| 36 | 4 | `sample_rate` | 44100 |
| 40 | 2 | `channels` | 2 |
| 42 | 2 | `bits_per_sample` | 16 |
| 44 | 4 | `chunk_bytes` | 524288 |
| 48 | 4 | `nominal_length_s` | Label value. §2 |
| 52 | 4 | `total_chunks` | Capacity of the chunk store |
| 56 | 4 | `a_high_water` | Chunk ids `[0, a_high_water)` are **owned by** Side A |
| 60 | 4 | `index_slot_bytes` | 65536 |
| 64 | 4 | `lba_index_a0` | 8 |
| 68 | 4 | `lba_index_a1` | 136 |
| 72 | 4 | `lba_index_b0` | 264 |
| 76 | 4 | `lba_index_b1` | 392 |
| 80 | 4 | `lba_chunk_base` | 2048 |
| 84 | 4 | `lba_superblock_mirror` | `block_count − 1` |
| 88 | 32 | `label` | UTF-8, NUL-padded. Advisory |
| 120 | 4 | `format_epoch` | Caller-supplied. Informational |
| 124 | 384 | *reserved* | zero |
| 508 | 4 | `crc32` | Over bytes 0…507 |

**Bytes 0–19 are frozen across all future major versions.** A v1 reader must be able to read magic, both version fields, `sb_generation` and `state` from v2 media in order to refuse it correctly.

### 4.1 Mount — selection, admission, then repair

DRAFT-3 ordered repair before the version check, which meant a v1 engine could write to v2 media it was forbidden to touch (V3-006). The three phases are now explicit and **only phase 3 writes**.

**Phase 1 — selection. No writes.**
Read both copies. A copy is *structurally valid* iff its magic matches and its CRC verifies.

- Neither valid → `TAPE_ERR_BAD_MAGIC` or `TAPE_ERR_CRC`. Mount ends.
- Exactly one valid → it is the candidate. Record that the partner needs repair.
- Both valid, different `sb_generation` → the higher is the candidate.
- Both valid, equal `sb_generation` → they must be byte-identical. If not, `TAPE_ERR_INCONSISTENT`.

**Phase 2 — admission. No writes.** In this order:

1. `version_major ≠ 1` → **`TAPE_ERR_VERSION`. Nothing is written. No repair. Mount ends.** An unsupported version is not corruption, and repairing it is how an old reader downgrades new media.
2. `version_minor > 0` → mount **read-only**; continue.
3. `state == WRITE_IN_PROGRESS` → `TAPE_ERR_INCOMPLETE`. Nothing written. The cartridge is an interrupted duplicate or format; the remedy is to re-run the operation.
4. Geometry, all in 64-bit:
   - `sample_rate`, `channels`, `bits_per_sample`, `chunk_bytes`, `index_slot_bytes` equal §1;
   - the six `lba_*` fields equal §3, and `lba_superblock_mirror == block_count − 1`;
   - `total_chunks ≥ 1` and `a_high_water ≤ total_chunks`;
   - `block_count > lba_chunk_base`;
   - **`lba_chunk_base + (uint64_t)total_chunks × CHUNK_BLOCKS ≤ (uint64_t)block_count − 1`.**
   - `total_chunks ≥ ⌈nominal_length_s × SAMPLE_RATE / CHUNK_FRAMES⌉` — the store must cover the label (§2). Without this check §2's guarantee is unenforced and a cartridge labelled C-60 with 100 chunks mounts clean.

   Any failure → `TAPE_ERR_GEOMETRY`. Nothing written.

> The final inequality subtracts one for the mirror. DRAFT-3 allowed equality, which put the last chunk's final block exactly on the mirror block — filling that chunk would destroy the mirror, and repairing the mirror would destroy referenced audio (V3-004). Exact-equality and one-block-short cases are required tests.

`block_count` is caller-supplied and **untrusted**. These checks exist to defend against it as much as against the media.

**Phase 3 — repair. The only phase that writes.**
Performed only if the candidate passed phase 2, exactly one copy was structurally valid, and `write != NULL`. Rewrite the invalid copy from the candidate; flush.

**`sb_generation` is not incremented by repair.** Repair restores a copy of an existing logical state; it does not create a new one. Generation increments once per logical update, and a logical update writes **mirror first, flush, then primary, flush**.

On a read-only device, repair is skipped and `tape_get_info` reports `needs_repair`. A recoverable cartridge still mounts in the source slot.

---

## 5. Index slot (65 536 bytes = 128 blocks)

**Block 0 is the header and nothing else.** Bytes 64–511 reserved, zero.

| Offset | Size | Field |
|---|---|---|
| 0 | 8 | `magic` = `"TAPEIDX\x01"` |
| 8 | 4 | `sequence` (u32) |
| 12 | 1 | `side` — 0 = A, 1 = B |
| 13 | 3 | *reserved*, zero |
| 16 | 4 | `entry_count` (≤ `TAPE_MAX_ENTRIES`) |
| 20 | 8 | `total_frames` (u64) |
| 28 | 32 | *reserved*, zero |
| 60 | 4 | `crc32` — over bytes 0…59 concatenated with the entry array |

**The entry array begins at byte 512 — block 1.** Entry *i* at `512 + 12 × i`. Bytes beyond `512 + 12 × entry_count` are undefined and not CRC-covered.

`sequence` is monotonic **per cartridge**, shared across all four slots, incremented on every commit to either side.

### 5.1 Entry — a run over consecutive chunks

| Offset | Size | Field |
|---|---|---|
| 0 | 4 | `first_chunk_id` |
| 4 | 4 | `start_frame` — 0 … 131 071 |
| 8 | 4 | `frame_count` — ≥ 1; may exceed `CHUNK_FRAMES` |

**The run extent is computed in checked 64-bit and narrowed only after the bounds test:**

```
span = (uint64_t)start_frame + (uint64_t)frame_count - 1
last = (uint64_t)first_chunk_id + span / CHUNK_FRAMES
```

> DRAFT-3 expressed this in u32. With `start_frame = 131071` and `frame_count = 0xFFFFFFFF` the intermediate `start_frame + frame_count − 1` is 4 295 098 365, which wraps to **131 069** and validates clean — admitting a run whose physical extent reaches into the sandbox or past the device (V3-001). Arithmetic maxima are normative invalid-media cases.

**Entry ranges must not overlap.** For any two entries, their chunk extents `[first_chunk_id, last]` may share chunks only where the frame ranges within those chunks are disjoint. Equivalently: `total_frames ≤ (free_next − a_high_water + chunks referenced below a_high_water) × CHUNK_FRAMES`. Without this, an index of two entries both fully referencing chunk 0 passes every other check while claiming `total_frames = 262144`, and §9.3's phase-2 reasoning breaks. This is a validity requirement, checked at mount.

Frames lie contiguously across the run: the first chunk contributes from `start_frame`, every intermediate chunk contributes all 131 072, the last is truncated by `frame_count`.

**A freshly re-spooled side is one entry; a freshly formatted side is zero entries.** Entries are consumed by edits, not by tape length. Each splice costs two entries, so a side starting as one entry has room for roughly 2 000 splices before re-spool.

Entries are ordered by timeline position; the position of entry *i* is the sum of `frame_count` over entries `0 … i−1`. A cached prefix-sum array is permitted and is not part of the on-media format.

### 5.2 Slot validity

A slot is **valid** iff all of:

- `magic` matches; `side` matches the slot's assignment; `entry_count ≤ TAPE_MAX_ENTRIES`; `crc32` verifies;
- `total_frames` equals the sum of `frame_count` over the entries, computed in 64-bit;
- `total_frames ≤ TAPE_MAX_TOTAL_FRAMES` (§5.4);
- every entry has `frame_count ≥ 1` and `start_frame < CHUNK_FRAMES`;
- every entry's `last` (§5.1) satisfies `last < total_chunks`;
- **for Side A only:** every entry's `last < a_high_water`.

There is deliberately **no Side B lower bound.** Side B may reference chunks owned by Side A — see Rule 3 and §7.

Validity is evaluated against the superblock already selected by §4.1.

### 5.3 Index-slot selection

DRAFT-1 had this rule; DRAFT-3 dropped it in restructuring, leaving implementations to invent one (V3-005). It is normative, it parallels §4.1, and **it performs no writes.**

For each side, classify both slots (A0/A1 or B0/B1) per §5.2, then:

- **Neither valid** → `TAPE_ERR_NO_VALID_INDEX` for that side.
- **Exactly one valid** → it is live. **The invalid partner is not repaired.** An invalid partner is the normal resting state after format (§9.6) and after every commit (§8) — repairing it would destroy the fallback the commit protocol depends on.
- **Both valid, different `sequence`** → the higher is live.
- **Both valid, equal `sequence`** → `TAPE_ERR_INCONSISTENT` for that side. Unreachable via §8; it means media fault or implementation bug, and it is not recovered from silently.

Side A in either error state: the cartridge is unusable. Side B in either: recoverable by `tape_reset_side_b`.

Promote's recovery (§9.3) depends on falling back from a newer-but-invalid A slot to the previous generation. That is this rule plus §5.2's Side A bound, and it is now implementable byte-exactly.

### 5.4 Timeline cap

`total_frames` is capped at `TAPE_MAX_TOTAL_FRAMES` = 2³² − 1, which is 27.05 hours of audio — far beyond any cartridge this format describes. The cap exists because playback position is a 64-bit fixed-point value with 32 fractional bits, leaving 32 bits of whole frames (`engine-api.md` §6). Media declaring more is rejected at mount rather than becoming unseekable later (V3-010).

---

## 6. Chunks

131 072 frames of raw interleaved PCM. No header, no padding. A partially written chunk still occupies a full slot; bytes beyond the referenced range are **undefined, not zero**.

> Any comparison of "Side A is unchanged" must be over *referenced frames*, reconstructed through the index. A raw region compare produces false failures on the tail chunk of a run.

---

## 7. Ownership, reference, and allocation

**Ownership** partitions the chunk store:

- `[0, a_high_water)` — **owned by Side A.** No runtime path writes here, with exactly one exception: **promote phase 2** (§9.3), which writes low only after both live indices have been committed away from that region and only after an explicit disjointness check. Nothing else, ever.
- `[a_high_water, free_next)` — **allocated to Side B.**
- `[free_next, total_chunks)` — unallocated.

**Reference is separate from ownership.** Side B's index **may reference chunks owned by Side A**. That is precisely what `tape_reset_side_b` (§9.2) and a completed promote (§9.3) produce, and it is the copy-on-write mechanism that makes "start over" instant and makes Side B nearly free until it is edited.

What Side B may not do is **allocate or write** below `a_high_water`.

> DRAFT-3's engine invariant 4 required every Side B run to lie entirely at or above `a_high_water`. That forbids the format's own centrepiece: no implementation could pass both reset-B and that invariant (V3-009). The distinction between referencing and owning is the fix, and it is now Rule 3.

**`free_next` is derived at mount, never stored:**

```
free_next = max( a_high_water,
                 max over live-B entries of (last + 1) )
```

Entries referencing only Side A chunks yield `last + 1 ≤ a_high_water` and so do not raise it. Allocation is a bump pointer over that value and hands out **contiguous runs**.

Because it is derived from the *committed* index, chunks written by an operation that never committed sit above `free_next` on the next mount and are silently reused. **The aborted-write leak class does not exist.**

Chunks superseded by an overwrite sit below the live maximum and remain allocated until re-spool reclaims them. That is the only leak source, it is bounded, and it is **expected** — see `acceptance.md` WP-10, which DRAFT-3 got wrong in the opposite direction (V3-014).

---

## 8. The commit protocol

An index slot is 128 blocks and cannot be written atomically. Atomicity is by ordering:

1. Write chunk data for the operation.
2. **Flush.**
3. Write the entry array into blocks 1 … ⌈`entry_count` × 12 / 512⌉ of the **inactive** slot for this side.
4. **Flush.**
5. Write block 0 of that slot — the 64-byte header zero-padded to 512 — with the new `sequence`, `entry_count`, `total_frames` and the CRC over the entries just written. **This is the commit point.**
6. **Flush.** `tape_commit` returns success only after this flush succeeds. On failure, `TAPE_ERR_IO`; the on-media state is indeterminate until remount, where §4.1 and §5.3 resolve it.

Before step 5 the inactive slot's block 0 holds the previous generation's header, whose CRC does not match the newly written entries — so a crash before step 5 leaves an invalid slot and §5.3 falls back to the other one. A crash during step 5 leaves a header failing its own CRC, with the same result.

**Flush** means the data has reached media: on SD, the card has left the busy state, not merely accepted the blocks.

**The assumption:** a 512-byte SD block write is atomic under power loss. True of essentially all cards in practice; not universally guaranteed. Tested against real media under *Media atomicity* in `acceptance.md`, not inherited. See §13.

---

## 9. Operations

### 9.1 Record — overwrite, overdub, splice

All three allocate fresh chunks and commit per §8. None modifies a chunk in place.

- **Overwrite** replaces the timeline from the current position. Entries wholly covered are dropped; a partially covered entry is trimmed.
- **Overdub** reads existing frames, adds input at `int32`, and **clamps** to `[−32768, 32767]` — saturating, never wrapping. Exact formula in `engine-api.md` §8.
- **Splice** inserts at the current position. The run containing the insertion point is split into two entries; new entries for the inserted material go between them.

`nominal_length_s` is not a limit; `total_chunks`, `TAPE_MAX_ENTRIES` and `TAPE_MAX_TOTAL_FRAMES` are.

**Cartridge full.** `tape_feed` reserves before accepting (`engine-api.md` §7) and returns `TAPE_ERR_CARTRIDGE_FULL` with a short accept. Frames already accepted remain owed and commit normally. **The child keeps everything recorded up to the moment it filled.**

**Index full.** An operation that would exceed `TAPE_MAX_ENTRIES` returns `TAPE_ERR_INDEX_FULL` and commits nothing. `tape_status` exposes `entries_free` so firmware can run the record light green → yellow → red; at red the record button does not hold. Recovery is re-spool.

### 9.2 Reset Side B

Copy the live Side A index into Side B's inactive slot with `side` = 1 and `sequence` + 1; commit per §8. **Moves no audio** — the resulting Side B references Side A's chunks, which Rule 3 permits. Sub-second.

Clears any device-side stored position for `(uuid, B)` (§11).

### 9.3 Promote Side B to Side A

The only destructive operation on Side A, and the only operation permitted to write below `a_high_water`. Incremental on the `block_budget` / `more_work` contract (`engine-api.md` §9), because a ~30 s blocking call in an engine that must service audio is not acceptable.

**Preconditions, checked before any write:**

- Side B is non-empty. `total_frames == 0` → `TAPE_ERR_INVALID_ARG`. Promoting an empty side would produce a zero-length entry, which §5.2 forbids, and would silently erase Side A.
- `total_chunks − free_next ≥ len`, where `len = ⌈total_frames / CHUNK_FRAMES⌉`. Insufficient → `TAPE_ERR_CARTRIDGE_FULL`, nothing written.

**Resume detection.** If Side A's live index is already a single run of exactly `len` chunks whose `first_chunk_id ≥ len`, and Side B's live index is identical to it, phase 1 has already completed — skip to phase 2. Without this, re-running an interrupted promote climbs another `len` chunks higher every time and never lands (a defect in DRAFT-4's first cut).

**Phase 1.**
1. Write B's timeline, compacted, to `[S, S+len)` where `S = free_next`.
2. Commit a new **A** index referencing `[S, S+len)` as one entry, `sequence` + 1.
3. **Commit a new B index referencing the same range**, `sequence` + 2.
4. Write the superblock with `a_high_water = S + len` — mirror, flush, primary, flush.

After step 4 the cartridge is valid, playable, and both sides reference only `[S, S+len)`.

**Phase 2.**
5. **Check that `[0, len)` is disjoint from the live set of both sides.** If it is not, promote stops here and returns `TAPE_OK` with the phase-1 layout in place — the cartridge is complete and correct, merely not compacted to the bottom. Space below `S` is stranded until the next promote or re-spool.
6. Write the timeline to `[0, len)`.
7. Commit a new A index referencing `[0, len)`.
8. Commit a new B index referencing `[0, len)`.
9. Write the superblock with `a_high_water = len`.
10. Clear the device-side stored positions for `(uuid, A)` and `(uuid, B)` (§11).

> **DRAFT-4's first cut proved step 5 unnecessary and the proof was wrong.** It argued that a compacted timeline of `len` chunks must reference at least `len` distinct chunks, so `free_next ≥ len` and `[0, len)` could not overlap `[S, S+len)`. That assumed entries never overlap each other — which §5.1 now requires, but which nothing checked at the time. An index with two entries both referencing chunk 0 would have made `S < len` and sent phase 2 straight through the only surviving copy. **The check replaces the proof.** A runtime test that costs one comparison is worth more than an argument that is correct only under an invariant stated two sections away.

**Recovery, by boundary.**

| Crash point | Result |
|---|---|
| Before step 2 commits | Nothing happened. Both sides at their previous generation |
| Between 2 and 3 | A references chunks ≥ `a_high_water` → §5.2 rejects it → §5.3 falls back to A's previous generation. **B is untouched and still at its previous generation.** Promote did not happen |
| Between 3 and 4 | A falls back as above. **B's new index is valid** — §5.2 imposes no Side B lower bound — so B is at the phase-1 generation while A is at its previous one. The cartridge mounts and plays; both sides' referenced audio is intact. Re-running promote detects this is *not* the resume state (A and B differ) and restarts phase 1 |
| Between 4 and 9 | Valid, playable cartridge, both sides at `[S, S+len)`. Re-running promote detects the resume state and completes phase 2 |
| After 9 | Complete |

> The "between 3 and 4" row above corrected a claim in DRAFT-4's first cut that both indices would fall back. They do not: B has no lower bound, by design. The state is mixed but every generation present is internally valid and every referenced byte is intact, which is what the guarantee actually requires.

**Invariant after a completed phase 2:** `a_high_water == len` and no allocated chunk is unreachable.

### 9.4 Re-spool

Rewrites Side B's timeline as one contiguous run and commits, reclaiming superseded chunks.

**The rule, stated per pass** — DRAFT-3 stated it once and applied it only to the first (V3-003):

> Re-spool performs **at most two passes**. Before **each** pass, the destination must be a contiguous run of `len` chunks that is **(a)** entirely at or above `a_high_water`, and **(b)** disjoint from the live set — the chunks referenced by the live index of *either* side at that moment. Pass 2 runs only if such a run exists whose start is **strictly lower** than the current layout's start. If none exists, re-spool stops and keeps the pass-1 layout.

Two things this wording fixes from DRAFT-4's first cut. It said "a **free** contiguous run… strictly lower", and "free" elsewhere in this document means `≥ free_next` — so nothing strictly lower could ever qualify and pass 2 was unsatisfiable by construction. And it omitted the `a_high_water` floor, so a pass-2 destination could have landed on an unreferenced chunk *owned by Side A*, which is disjoint from the live set and still forbidden. Condition (a) closes that.

Pass 1 achieves compaction, which is what re-spool exists for. **The downward pass is opportunistic space reclamation, not a correctness requirement.**

> Worked example. `a_high_water = 10`; Side B is one live entry spanning chunks 10–11 (`len = 2`), so `free_next = 12`. The low destination `[10, 12)` overlaps the live set, so pass 1 writes `[12, 14)` and commits. Chunks 10 and 11 are now unreferenced, contiguous, at or above `a_high_water`, and number exactly `len` — so `[10, 12)` **passes** both conditions and pass 2 runs, landing the timeline back at the bottom and reclaiming the two chunks.
>
> DRAFT-4's first cut gave this example with `free_next = 11`, which cannot occur: a two-chunk run ending at chunk 10 would need `frame_count > CHUNK_FRAMES` with `last = 10`, contradicting §5.1. It then concluded that pass 2 declines. Both the arithmetic and the conclusion were wrong, and `acceptance.md` WP-12 required reproducing a state that cannot exist. Corrected in both documents.

**Precondition:** a pass-1 destination satisfying (a) and (b) must exist, else `TAPE_ERR_CARTRIDGE_FULL` and nothing changes. Pass 2 has no precondition beyond the test it performs itself.

**Re-spool does not always reduce the leak.** If pass 2 declines, pass 1 has moved the timeline up and stranded its old chunks — strictly more allocated-but-unreachable space than before. That is acceptable because it is bounded and the next re-spool or promote reclaims it, but it is a real property and it should not be described as though re-spool always frees space.

Re-spool preserves rendered audio bit-exactly. It commits nothing until a destination is fully written, so an interrupted pass leaves the previous index live and partial work above `free_next` for reuse.

### 9.5 Duplicate

Copies **Side A** — the music — from the source slot to the work slot. The destination is erased and reformatted in the process; that is what dubbing over a tape does, and it is announced by the first block written.

**The destination is a `tape_dev`, not a mounted `tape`.** DRAFT-4's first cut took a mounted destination, which made its own recovery rule impossible to follow: a blank card cannot be mounted (§4.1 phase 1 → `TAPE_ERR_BAD_MAGIC`) and an interrupted duplicate cannot be mounted either (phase 2 → `TAPE_ERR_INCOMPLETE`), so "re-run to finish" could never be performed. `tape_dup` therefore takes a raw device, exactly as `tape_format` does, and works on blank, valid and interrupted destinations alike.

**Side B is not copied.** The destination's Side B is initialised to mirror its new Side A, as a freshly formatted cartridge would be. **Duplicate copies the music, not the sandbox** — you are handing someone the album, not their sibling's scribbles over it, and the recipient gets a clean side to work on. This is a deliberate product decision, not an omission.

**Preconditions, all checked before any write** (V3-007):

- The destination device must not alias the source. The engine compares `dev.ctx` and, where the port can report device identity, that too. A port that cannot distinguish two devices must not be handed the same one twice. Aliasing → `TAPE_ERR_INVALID_ARG`.
- The caller supplies the destination's `nominal_length_s`; `total_chunks` is derived from it and from the destination's own `block_count` via §2's formula. **Nothing about the destination's geometry or label length comes from the source** — copying a C-90's `nominal_length_s` onto a C-60 store would produce a cartridge that cannot hold the time printed on it, which §2 defines as a defect.
- **Capacity:** the source's Side A timeline must fit the destination's derived `total_chunks`. Insufficient → `TAPE_ERR_DEST_TOO_SMALL`. **Nothing is written** — the refusal precedes `WRITE_IN_PROGRESS`.

**Write order:**

1. Write the destination superblock with `state = WRITE_IN_PROGRESS`, `sb_generation` incremented if a valid one exists else 1 — mirror, flush, primary, flush. From here the destination does not mount as audio. *(On blank media there is nothing to invalidate; skip.)*
2. Write A1 and B1 block 0 as 512 zero bytes each; flush.
3. Write the source's Side A chunks to the destination, then commit A's index, then commit B's index identical to A, each under §8.
4. Write the destination superblock with `state = VALID`, the **caller-supplied fresh `cartridge_uuid`**, the caller-supplied `format_epoch`, and the destination's own geometry — mirror, flush, primary, flush. **This is the commit and the identity assignment, and it is last** (Rule 2).

A crash between 1 and 4 leaves `TAPE_ERR_INCOMPLETE` on mount, or `TAPE_ERR_BAD_MAGIC` if the destination was blank and crashed before step 4. Re-run `tape_dup` to finish — which is possible precisely because it takes a device rather than a mount.

A copy is a different cartridge. Reproducing the UUID would make two objects claim one identity and silently merge the device-side state keyed by it (§11).

### 9.6 Format

Destructive and ordered (V3-008). The caller supplies UUID, epoch, label and `nominal_length_s`; `total_chunks` comes from §2's formula.

1. **If a structurally valid superblock exists**, write it with `state = WRITE_IN_PROGRESS` and `sb_generation` incremented — **mirror, flush, then primary, flush**, matching §4.1 and §9.5. From here the cartridge does not mount. *On blank media there is nothing to invalidate — skip.*
2. Write A1 and B1 block 0 as 512 zero bytes each; flush.
3. Write A0 and B0 headers — valid, empty, `entry_count` 0, `total_frames` 0, `sequence` 1 and 2 respectively, CRC over the header alone; flush.
4. Write the **mirror** superblock: `state = VALID`, `sb_generation = 1`, `a_high_water = 0`; flush.
5. Write the **primary** superblock, byte-identical; flush. **This is the commit.**

**Resulting state.** Exactly one valid generation per side; A1 and B1 deliberately invalid. `TAPE_ERR_INCONSISTENT` therefore stays unreachable through normal operation, which is what makes it meaningful when it fires.

**Permitted remount outcomes after a crash:**

| Crash point | Result |
|---|---|
| Before 1 completes, reusable media | The old cartridge, unchanged |
| After 1, before 5 | `TAPE_ERR_INCOMPLETE`. Re-run format |
| Blank media, before 4 | **`TAPE_ERR_BAD_MAGIC`** — no valid superblock has ever existed. This is the one case where "remount succeeds" cannot hold, and `acceptance.md` WP-10 permits it explicitly |
| After 5 | The new empty cartridge |

---

## 10. Sequence exhaustion

`sequence` and `sb_generation` are u32. At one commit per second that is 136 years. On reaching 0xFFFFFFFE the engine returns `TAPE_ERR_SEQUENCE_EXHAUSTED` and refuses further commits. Neither wraps.

---

## 11. What the cartridge does not store

**Playback position.** The source slot is read-only, so a cartridge played there has no writable surface. Position lives in the **device's** flash as a table keyed by `(cartridge_uuid, side)` → `position_frames` (u32), holding the ~64 most recently used entries, LRU eviction. The engine reports position at unmount and accepts it at mount; it never writes it to media. Firmware checkpoints on a cadence and resumes 2 s early — see `acceptance.md`.

- Promote clears `(uuid, A)` and `(uuid, B)` — both timelines changed.
- Reset B clears `(uuid, B)`.
- Duplicate assigns a fresh UUID, so the destination simply has no entry.

**The position table is the UUID's only sanctioned consumer.** Adding another is an escalation, because every consumer is a new place where duplicate identities cause harm.

---

## 12. Instant-on is not a format feature

Two firmware mechanisms, neither on the card:

1. **Wake from sleep with a cartridge mounted.** The caller's play ring is retained across sleep and passed to `tape_mount` as a warm-start descriptor; rendering begins from it while `tape_service` re-establishes the card.
2. **Cold insert.** Card initialisation begins on the cartridge-detect switch, not on the play press.

**The warm-start descriptor carries `uuid`, `side`, `start_frame` and `valid_frames`** (`engine-api.md` §5). DRAFT-3 passed a bare pointer and length with no identity, so a ring retained from cartridge X side A could be rendered into a mount of cartridge Y side B with nothing to detect it (V3-016). **A mismatch disables warm start; it does not fail the mount** — a wrong buffer should cost instant-on, not the cartridge.

Guardrail 04 (wake to audio < 100 ms) is enforced, measured and tested in `firmware/`.

---

## 13. Assumptions this format inherits

1. A 512-byte SD block write is atomic under power loss (§8). Tested on real media under *Media atomicity* in `acceptance.md`, against the harness's torn-write mode.
2. A flush returning success means data has reached media.
3. Card wear from re-spool and promote is acceptable at family write volumes.
4. A cartridge is never mounted by two hosts concurrently.
5. `block_count` may be wrong; §4.1 phase 2 is the defence.

---

## 14. Open before freeze

- §9.3, §9.4 and the forbid-while-armed rule are design decisions, not corrections. They are the least-scrutinised text in this document.
- Whether `TAPE_ERR_INCOMPLETE` should distinguish an interrupted duplicate from an interrupted format. Both are recovered by re-running the operation, so the distinction may not earn its field.
- Michael's note that a child may lose patience with a 43-second C-90 copy — a firmware LED behaviour, not a format concern.
