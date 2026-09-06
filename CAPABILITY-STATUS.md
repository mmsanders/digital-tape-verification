# Capability status — DRAFT-7 / PM Decisions 006 and 009

Date: 6 Sep 2026

This is the current Verification Lead status snapshot. Historical pass details remain in `PM-NOTES.md` and the versioned files under `findings/`.

| Area | Status | Evidence / boundary |
|---|---|---|
| Verification publication point | **Corrected** | PR #1 and the completed DRAFT-6 publication PR #2 are merged. `README.md` now requires completed findings/status to land on `main`; review branches are not authoritative publication points. |
| DRAFT-7 source authentication | **Complete** | The supplied TapeFS, engine API, and acceptance files hash exactly to canonical `mmsanders/Digital-Tape` `main` `spec/VERSION.md`: `94f385…a95f`, `cbf34c…4724`, `021372…00a8`. |
| DRAFT-7 adversarial review | **Complete; freeze not recommended** | `findings/spec-review-draft7.md` records **1 blocker, 3 majors, and 1 documentation question** after the PM-directed pass and a clean whole-document pass. |
| Phase-0 freeze gate | **Not met** | `V7-001` is a blocker and `V7-002` is a major in/crossing the candidate. The gate requires zero blockers and zero majors in candidate sections. |
| §5.5 running `next_sequence` | **Clean in directed traces** | FRESH allocating, FRESH adopt-in-place, all RESUME entries, and two-pass re-spool use distinct successive commit values. No collision was found after the DRAFT-7 running-counter fix. |
| §4.5 branch-exact headroom | **Counts correct; boundary predicate defective** | Every branch count matches the §9 write sequence, but `V7-002` shows `needed == 0` still rejects stored FE/FF counter values despite the promised zero-write/no-op result. |
| Raw format/duplicate barrier | **Partially specified** | Normal/selectable destinations now use the safe non-selectable-first ordering and `max(existing,1)+1`. `V7-003` identifies structurally valid raw inputs for which “selected candidate” or the barrier bytes are undefined. `V7-004` identifies an undefined successful duplicate label. |
| Degraded-B / FAULTED matrix overrides | **Mechanically coherent** | Degraded-B overrides Playing/idle correctly; FAULTED overrides every media-touching call. One stale prose sentence says service is “always allowed” (`V7-005`), but the matrix, §7.2, and acceptance oracle agree on `TAPE_ERR_FAULTED`. |
| Promote superblock crash closure | **Blocked by V7-001** | A first interruption can leave a newer mirror plus stale structurally-valid primary; because mount does not restore that stale partner, a second mirror-first logical update can tear the only current copy and roll back to water-line metadata that rejects both current A indices. |
| WP-10 | **Mechanically executable, not sufficient as the final safety/freeze gate** | The literal DRAFT-7 suite can be implemented, but it lacks the two-interruption closure needed to expose `V7-001`; final green/freeze authority must wait for that closure plus dispositions of `V7-002`–`V7-004`. |
| WP-11 | **Testable as written** | DRAFT-7 leaves §§6.2, 6.3 and 8 unchanged. The independent arithmetic oracle and golden-fixture policy remain valid; implementation output is never the oracle. |
| WP-12a | **Testable as written** | DRAFT-7 resolves callback exemptions and BUSY persistence; the 45-cell/33-B accounting, underlying-transport termination, and FAULTED behavior now form one executable oracle. |
| Hardware safety audit | **Contract auditable; no result yet** | Acceptance now requires procedure, instrument/calibration, conditions, raw readings, derivation, and stated measurement uncertainty. No hardware measurement package was supplied in this round, so no hardware pass/fail audit is claimed. |
| Crash-injection infrastructure | **Complete below the implementation adapter seam** | `tests/fault_block_device.[ch]` and `tests/crash_harness.[ch]` retain exhaustive 0…512-byte torn outcomes, flush failures, reset/power-cut/remount, and both flush-required/write-through durability modes. |
| Implementation blindness | **Preserved** | This pass did not inspect `engine/`, implementation branches/diffs/issues, or unlanded implementation artifacts. Only canonical specs and verifier-owned material were used. |

## Current verifier work that may proceed

- Keep WP-11 golden/arithmetic work moving from independent expectations and the existing human-listening/PM-approval fixture policy.
- Implement all literal DRAFT-7 WP-10 cases, while adding a verifier-owned two-interruption closure scenario as a proposed safety extension rather than pretending the current acceptance text contains it.
- Exercise WP-12a's 45 state-matrix cells, callback re-entry exemptions, destination-failure return-to-Playing behavior, and FAULTED override.
- Prepare the hardware-safety audit checklist so the eventual raw measurement package can be audited independently.

## Current stop conditions

- **Do not recommend Phase-0 signature** while `V7-001` or `V7-002` remains blocker/major in the candidate.
- **Do not treat a literal green WP-10 as sufficient freeze evidence** until the repeated-interruption closure exposed by `V7-001` is mechanically covered and the remaining DRAFT-7 WP-10 ambiguities are dispositioned.
- **Do not unblock or merge `Digital-Tape` PR #20** from verification; PM Decisions 006/009 keep it draft and structural Rule 1 remains outstanding.
- Do not inspect engine implementation to resolve any normative ambiguity above.
