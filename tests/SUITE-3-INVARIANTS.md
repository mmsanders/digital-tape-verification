# Suite 3 invariant checklist (DRAFT-3 review state)

Status: reconciled to DRAFT-3 field names and media layout. Operation adapters remain provisional until the crash-state and index-selection findings in `findings/spec-review-draft3.md` are dispositioned.

Generate arbitrary, parameterised cartridge geometries and arbitrary valid edit sequences. Do not assume a 90-minute cartridge.

After each successful operation, and after remount at every injected write/flush boundary, assert:

1. Timeline length equals the sum of every run's `frame_count`, using overflow-checked arithmetic.
2. Every run is structurally valid: nonzero length where required; start frame is within its first chunk; the number of occupied consecutive chunks is computed without truncation; and `first_chunk_id + occupied_chunks` neither wraps nor exceeds the chunk store.
3. Every chunk occupied by a Side A run is strictly below `a_high_water`; checking only `first_chunk_id` is insufficient.
4. Every Side B-owned allocation is at or above `a_high_water`. Side B may reference Side A runs below the mark, but must never write them.
5. `free_next` equals one past the greatest chunk referenced by live B entries, floored at `a_high_water`, using checked run-end arithmetic. Superseded, unreachable bytes below `free_next` and aborted-write bytes at or above it are permitted until re-spool; the format records no separate allocation bit.
6. Re-spool preserves rendered PCM bit-exactly and commits only after writing to a region disjoint from every chunk referenced by the live pre-operation index.
7. Re-spool refuses with `TAPE_ERR_CARTRIDGE_FULL` when free space is less than the timeline length, without changing the mounted cartridge state.
8. Any edit sequence followed by re-spool renders identically to the same sequence without re-spool.
9. After a completed promote, `a_high_water` equals the promoted timeline's occupied chunk count and no allocated space is unreachable.
10. Each crash point in either promote phase resolves to one complete, explicitly permitted generation; neither side is a mixture and every referenced frame is intact. The exact permitted set is blocked by V3-002 and V3-013.
11. Promote followed by reset B has the DRAFT-3-specified idempotent result.
12. Sequence and superblock-generation comparisons remain correct at their specified exhaustion boundary; neither counter wraps.
13. The chunk store ends before `lba_superblock_mirror`; equality is invalid geometry.
14. Mount performs no repair until a supported v1 candidate has passed version, state, and geometry checks.
15. Index-slot selection is deterministic across zero, one, and two valid slots once V3-005 is dispositioned.

Required generated edge cases include empty timelines, one-frame runs, exact chunk boundaries, maximum-length runs, final-chunk partial runs, arithmetic maxima, fragmented B layouts, runs whose first chunk is valid but last chunk is out of range, and run ends immediately below/at/above `a_high_water`.

## Generator obligations

- Seed must be explicit and printed/reported with every failure so a generated edit sequence is exactly replayable.
- Geometry is input data: `total_chunks`, `nominal_length_s`, high-water mark, entry capacity, and sequence/generation proximity to exhaustion are varied independently within the eventual valid bounds. C-60, C-90, and C-120 are named cases, never hard-coded global assumptions.
- Generated operations must include reset, overwrite, overdub, splice, re-spool, promote, remount, and no-op/boundary operations once their DRAFT-3 state matrix is available.
- Invalid-media generation is a separate family from valid edit sequences. It must mutate one invariant at a time, repair CRCs where needed, and assert rejection before out-of-range I/O or media repair.
- Shrinking must preserve the failure: first remove operations, then entries/runs, then frames/chunks, then geometry, while retaining the same violated invariant.

## Oracle separation

The property oracle must not call engine helpers or reuse engine parsing/arithmetic. It independently decodes little-endian fields, checks CRCs, expands run coverage with overflow-checked arithmetic, and renders reference PCM when audio equivalence is asserted. This prevents the same defect from appearing in both implementation and test oracle.

## Crash-state quantification

For each generated operation, use the clean trace to enumerate every block-write outcome: zero bytes landed, every torn prefix 1..511, and the full 512-byte block landed, plus every flush failure. After simulated power loss, remount only from durable media and run the complete invariant set. Sampling is not acceptable for the per-operation I/O trace.
