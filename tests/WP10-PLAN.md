# WP-10 exhaustive crash-injection plan — DRAFT-4

Status: generic enumeration and scenario-specific remount handling are executable. Stable operation adapters can now be written; final promote/re-spool/format/duplicate oracles wait on `findings/spec-review-draft4.md`.

## Harness contract

For each operation and starting fixture:

1. Run once without faults and record the exact per-block write and flush trace.
2. Restore the byte-identical fixture before every case.
3. For each observed block write, cut power with 0, every prefix 1–511, and all 512 bytes durably landed.
4. Fail each observed flush in turn.
5. Repeat in flush-required and write-through durability modes.
6. Destroy volatile engine/device state and remount from durable bytes only.
7. Classify the remount through the operation-specific predicate. A non-zero mount result is a failure unless that operation explicitly permits it.
8. Decode mountable media with a verifier-owned parser; never call engine parsing, CRC, run, rendering, or allocation helpers from the oracle.
9. Report baseline writes, flushes, total injection cases, passed cases, failed cases, operation, starting fixture, durability mode, and replay seed.

`crash_scenario.remount_allowed` implements step 7. Its absence preserves the strict default that only a successful remount is accepted.

## Per-operation allowed-state matrix

| Operation | Required starting cases | Allowed result after injection | Current status |
|---|---|---|---|
| Play / seek / scrub | empty, one frame, every run boundary ±1, exact end/start, min/max rate | Both sides exactly unchanged; remount succeeds | Stable except render phase and max positive step, V4-009/V4-010 |
| Overwrite / overdub / splice / commit | t=0, mid-run, boundary, end, full/index-full, owed frames | A unchanged; B exact pre or post generation | Stable structure |
| Reset B | non-empty A; empty A; B fragmented/edited | A unchanged; B exact pre or A-mirroring post generation | Stable |
| Re-spool | corrected `[10,12) -> [12,14) -> [10,12)` case; no lower run; no pass-1 run; empty B | A unchanged; B bit-exact in a pre/pass-1/pass-2 layout | Empty result blocked by V4-005 |
| Promote | every boundary in both phases; exact-tail staging; low target overlap/non-overlap; empty B | Exact generation pair from recovery table; empty rejects with zero writes | Missing post-step-7/8 and exact-tail resume states, V4-003/V4-004 |
| Duplicate | blank/reusable/incomplete destination; equal/different geometry; exact/insufficient capacity; aliases | Source unchanged. Destination pre-copy, `INCOMPLETE`, blank `BAD_MAGIC`, or complete fresh UUID/A+B mirror | Raw geometry rejection incomplete, V4-006 |
| Format, reusable | C-60/C-90/C-120; exact/short geometry | Old, `INCOMPLETE`, or new empty cartridge | Short-geometry preflight blocked by V4-006 |
| Format, blank | same geometries | `BAD_MAGIC` before first valid final superblock, otherwise one-copy/two-copy new empty cartridge | One-copy boundary missing from criterion, V4-014 |
| Mount / repair | each superblock/index validity/ordering case; v1.1 writable callback; unknown state | Exact specified error or selected generation; no forbidden write | V4-001/V4-012 require correction |

## Universal checks for every mountable state

- Independently recompute CRCs, checked run endpoints, totals, geometry, slot selection, and sequence/generation ordering.
- Treat an entry as a checked half-open physical-frame interval and require pairwise disjointness; do not use DRAFT-4's false scalar equivalence.
- Reconstruct referenced PCM and compare it byte-exactly with the allowed generation.
- Assert no I/O range crosses `block_count` and the chunk store ends before the mirror.
- Assert Side B allocations/writes, rather than references, are never below `a_high_water`.
- Derive `free_next = max(a_high_water, max live-B last + 1)`; superseded unreachable chunks below it are permitted.
- Compare every re-spool/promote write destination with both sides' live sets at that exact write.
- Assert duplicate source receives zero writes and all alias/capacity/geometry refusals write nothing.
- Assert v1.1 and invalid-admission cases perform no repair or mutation.

## Integration seam

The operation adapter is linked only after the corresponding verifier tests land on `main`. Until then this repository contains no engine source and no implementation-derived expectations. The generic harness has already built unmodified in the Software Lead's CI.
