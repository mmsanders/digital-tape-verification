# WP-10 exhaustive crash-injection plan — DRAFT-6

Status: **WP-10 is not testable as written for final acceptance.** The verifier-owned enumeration, torn-write block device, dual durability modes, remount hooks, and independent media-oracle structure remain executable. Final operation predicates are blocked only where DRAFT-6 itself has contradictory or undefined allowed states: `V6-002`, `V6-003`, `V6-007`, and `V6-008`.

This plan is implementation-independent. No engine parsing, CRC, allocation, generation-selection, or operation helper is used by the oracle.

## Harness contract

For each operation and starting fixture:

1. Run once without faults and record the exact per-block write and flush trace.
2. Restore the byte-identical fixture before every injected case.
3. For each observed block write, cut power with 0, every prefix 1–511, and all 512 bytes durably landed.
4. Fail each observed flush in turn.
5. Repeat every boundary in both **flush-required** and **write-through** durability modes.
6. Destroy all volatile engine/device state and remount from durable bytes only.
7. Classify remount through the operation-specific predicate. A non-zero mount result fails unless the operation expressly permits it.
8. Decode mountable media with a verifier-owned parser and recompute every CRC, checked endpoint, generation selection, live run, and ownership predicate independently.
9. Report operation, fixture, durability mode, baseline writes/flushes, injection ordinal, torn-byte count, permitted-state classification, seed, and replay command.

`crash_scenario.remount_allowed` remains the scenario-specific hook for step 7; absence means successful remount is mandatory.

## DRAFT-6 per-operation matrix

| Operation | Required starting cases | Allowed result after injection | DRAFT-6 status |
|---|---|---|---|
| Play / seek / scrub | empty, one frame, every run boundary ±1, exact end/start, min/max rate | Both sides exactly unchanged; remount succeeds | Testable |
| Overwrite / overdub / splice / commit | t=0, mid-run, boundary, end, full/index-full, owed frames, zero-frame commit | A unchanged; B exact pre/post generation; zero-frame commit zero-write/disarms | Counter base/headroom blocked by `V6-003` where crafted unequal live sequences apply |
| Reset B | normal B, empty B, fragmented B, degraded-B/no-valid-index, degraded-B/equal-sequence | A unchanged; B exact pre or A-mirroring post generation | Equal-sequence recovery has a spec defect (`V6-001`), exercised as a separate spec regression rather than accepted as WP-10 final oracle |
| Re-spool | pass-1/pass-2 cases, no lower run, no pass-1 run, empty B, counter boundaries | A unchanged; B exact pre/pass-1/pass-2 layout | Empty/no-op counter boundary conflicts with §4.5 (`V6-002`) |
| Promote | all FRESH/RESUME rows; step-5 overlap decline; phase-2 decline; exact-tail staging; empty/absent B; every counter boundary | Exact generation pair or specified decline/no-op state | Branch headroom and undefined shared sequence base blocked by `V6-002`/`V6-003` |
| Duplicate | blank/reusable/incomplete destination; empty/non-empty A; aliases; geometry/capacity; one-valid-superblock reusable destination; high-generation fallback | Source unchanged; destination pre-copy, `INCOMPLETE`, blank `BAD_MAGIC`, or complete fresh-UUID copy as specified | Final-primary durability and boundary fallback contradict tables (`V6-007`, `V6-008`) |
| Format, reusable | C-60/C-90/C-120; exact/short geometry; one/both valid superblocks; high-generation fallback | Old, `INCOMPLETE`, or new empty cartridge | Final-primary durability and one-valid-copy fallback blocked by `V6-007`, `V6-008` |
| Format, blank | same geometries and both durability modes | `BAD_MAGIC` until a valid final superblock is durable, then new empty cartridge | Final-primary table still incomplete under `V6-007` |
| Mount / repair | superblock/index validity/ordering; version-minor read-only; stage rows; degraded-B states; repair-needed | Exact specified result; every failing phase performs zero writes | Mechanically testable apart from the reset recovery follow-on in `V6-001` |
| FAULTED transition | every own-device write/flush failure; mount phase-4 repair exclusion; duplicate destination exclusion | Quarantine permits only the specified safe calls until unmount/remount; exclusions do not poison source | Mechanically testable; source-playing duplicate post-error transport semantics are separately defective under `V6-006` |

## Universal checks for every mountable state

- Recompute superblock and index CRCs independently.
- Perform checked run-end arithmetic in 64-bit and reject every out-of-range or overlapping physical interval.
- Reconstruct referenced PCM byte-for-byte and compare it with the exact permitted generation.
- Require the chunk store to end before the mirror and every I/O to remain within `block_count`.
- Assert Side B **allocations/writes**, not references, are never below `a_high_water`.
- Derive `free_next = max(a_high_water, max live-B last + 1)`; superseded unreachable chunks below it remain permitted.
- At every re-spool/promote data write, compare the destination against both sides' live physical sets at that instant.
- Assert duplicate source receives zero writes and every alias/capacity/geometry refusal writes nothing.
- Assert unsupported/admission-failure mounts perform no repair or mutation.
- After an own-device ambiguous write/flush failure, prove the `FAULTED` zero-write barrier until unmount/remount; test the two normative exclusions separately.
- Drive `sequence` and `sb_generation` to each specified operation boundary, but do not encode the contradictory DRAFT-6 rows in `V6-002`/`V6-003` as verifier truth.

## New DRAFT-6 regression fixtures

The verifier-side fixture set must include these even before final WP-10 predicates are unblocked:

1. **Unequal live A/B sequences:** e.g. A=10, B=500, to force an explicit shared counter base (`V6-003`).
2. **Empty re-spool at sequence `0xFFFFFFFD`:** expected zero-write/no-op semantics versus §4.5's two-sequence reservation (`V6-002`).
3. **Promote RESUME step-5 overlap decline at `0xFFFFFFFC`:** no index commit remains, so any two-sequence reservation is observable (`V6-002`).
4. **FRESH promote phase-2 decline at `0xFFFFFFFB`:** exactly two phase-1 index commits are needed, not four (`V6-002`).
5. **Final primary superblock write:** cut with every torn prefix and both durability modes after the final mirror is already durable; completed media must be distinguishable from `INCOMPLETE` (`V6-007`).
6. **Reusable high-generation media with only mirror valid:** exercise fallback ordering at `sb_generation >= 0xFFFFFFFD` (`V6-008`).

## Integration seam

The operation adapter is linked only after the corresponding verifier-authored tests and expectations exist independently. Until that boundary is crossed, this repository contains no engine source and no implementation-derived oracle. The generic crash infrastructure remains suitable for linkage once PM dispositions make the four blocked DRAFT-6 predicates mechanically singular.
