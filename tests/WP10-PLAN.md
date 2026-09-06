# WP-10 exhaustive crash-injection plan — DRAFT-5

Status: generic enumeration and scenario-specific remount handling are executable. Final operation adapters wait on `findings/spec-review-draft5.md`; WP-10 is not testable as written until its duplicate, promote-stage, durability, degraded-B, and error-state oracles are corrected.

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
| Play / seek / scrub | empty, one frame, every run boundary ±1, exact end/start, min/max rate | Both sides exactly unchanged; remount succeeds | Reverse-from-end phase blocked by V5-005 |
| Overwrite / overdub / splice / commit | t=0, mid-run, boundary, end, full/index-full, owed frames | A unchanged; B exact pre or post generation | Stable structure |
| Reset B | non-empty A; empty A; B fragmented/edited | A unchanged; B exact pre or A-mirroring post generation | Stable |
| Re-spool | corrected `[10,12) -> [12,14) -> [10,12)` case; no lower run; no pass-1 run; empty B | A unchanged; B bit-exact in a pre/pass-1/pass-2 layout | Stable crash shapes; post-I/O-error state blocked by V5-001 |
| Promote | all eleven rows; exact-tail staging; stage clearing; low target overlap/non-overlap; empty/absent B | Exact generation pair; empty rejects; unmatched stage fails at the dispositioned API point | Mount/check location blocked by V5-003; absent-B result by V5-004; error state by V5-001 |
| Duplicate | blank/reusable/incomplete destination; empty/non-empty A; geometry/capacity/aliases | Source unchanged. Destination pre-copy, `INCOMPLETE`, blank `BAD_MAGIC`, or valid complete fresh UUID/A+B mirror | Empty source is destructive-invalid, V5-002; eager-durability rows blocked by V5-010 |
| Format, reusable | C-60/C-90/C-120; exact/short geometry; both durability modes | Old, `INCOMPLETE`, or new empty cartridge | Boundary wording blocked by V5-010 |
| Format, blank | same geometries and durability modes | `BAD_MAGIC` before any valid final superblock is durable, otherwise one-/two-copy new empty cartridge | Boundary wording blocked by V5-010 |
| Mount / repair | each superblock/index validity/ordering case; v1.1 writable callback; unknown/stage state | Exact specified error or selected generation; no forbidden write | Stage-row validation location blocked by V5-003 |

## Universal checks for every mountable state

- Independently recompute CRCs, checked run endpoints, totals, geometry, slot selection, and sequence/generation ordering.
- Treat an entry as a checked half-open physical-frame interval and require pairwise disjointness; the deleted scalar capacity test is not an oracle.
- Reconstruct referenced PCM and compare it byte-exactly with the allowed generation.
- Assert no I/O range crosses `block_count` and the chunk store ends before the mirror.
- Assert Side B allocations/writes, rather than references, are never below `a_high_water`.
- Derive `free_next = max(a_high_water, max live-B last + 1)`; superseded unreachable chunks below it are permitted.
- Compare every re-spool/promote write destination with both sides' live sets at that exact write.
- Assert duplicate source receives zero writes and all alias/capacity/geometry refusals write nothing.
- Assert v1.1 and invalid-admission cases perform no repair or mutation.
- After an ambiguous write/flush error, attempt every otherwise-idle mutator and require zero writes until remount/reselection (V5-001).
- Drive sequence and superblock generation to every operation's required headroom boundary once V5-015 defines it.

## Integration seam

The operation adapter is linked only after the corresponding verifier tests land on `main`. Until then this repository contains no engine source and no implementation-derived expectations. The generic harness has already built unmodified in the Software Lead's CI.
