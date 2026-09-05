# Capability status — DRAFT-6 / PM Decisions 005 and 008

Date: 5 Sep 2026

This file is the current verifier capability/status snapshot. Historical pass details remain in `PM-NOTES.md` and the versioned findings files.

| Area | Status | Evidence / boundary |
|---|---|---|
| DRAFT-6 source authentication | Complete | The three supplied DRAFT-6 files hash exactly to canonical `mmsanders/Digital-Tape` `main` `spec/VERSION.md`. Canonical `main` is the authority; the older verifier-side DRAFT-5 courtesy bundle is retained as historical input rather than silently overwritten. |
| DRAFT-6 adversarial review | Complete; freeze not recommended | `findings/spec-review-draft6.md` records **0 blockers and 9 majors** after the PM-directed pass and clean whole-document pass. |
| Phase-0 freeze gate | **Not met** | Six majors (`V6-001`…`V6-006`) touch the candidate. PM-005 requires zero blockers **and zero majors** in candidate sections. |
| `engine-api` §§6.2, 6.3, 8 | Clean in this pass | Independent transport/interpolation traces found no defect. The arithmetic/phase prerequisite for golden PCM is clear, subject to the existing human-listening and PM-approval fixture policy. |
| WP-10 | **Not testable as written** | `V6-002`, `V6-003`, `V6-007`, `V6-008` prevent one mechanical headroom/crash-state oracle. `tests/WP10-PLAN.md` preserves all executable infrastructure and isolates the blocked predicates. |
| WP-11 | **Testable as written** | `tests/WP11-PLAN.md` now maps the finite 1,572,852-boundary-pair + 10,000,000-seeded-pair portability gate, two-toolchain requirement, independent arithmetic oracle, golden families, and mutation obligations. |
| WP-12a | **Not testable as written** | `V6-009` makes callback re-entry contradictory; `tests/WP12A-PLAN.md` isolates that predicate while retaining the executable 45-cell/33-B, zero-budget and FAULTED tests. |
| Crash-injection harness | Complete below the implementation adapter seam | `tests/fault_block_device.[ch]` and `tests/crash_harness.[ch]` support every 0…512-byte torn outcome, flush failures, reset/power-cut/remount, and both flush-required/write-through durability modes. |
| Audio oracle | Ready for DRAFT-6 WP-11 | `tests/audio_oracle.c` independently widens arithmetic and implements mathematical floor without relying on engine helpers. |
| Independent PR review lane | Live | `procedures/independent-pr-review.md` remains separate from pre-test verification; implementation details learned there must not shape unwritten verifier expectations. |
| Implementation-blindness | Preserved | This DRAFT-6 pass did not open `engine/`, implementation branches/diffs/issues, or unlanded implementation artifacts. Only the canonical spec publication point was consulted to establish authority and hashes. |
| PM handoff index | Current | `PM-NOTES.md` now includes the DRAFT-6 result and testability verdicts; PM-005 and PM-008 are preserved under `pm/`. |

## Current verifier work that may proceed

- Build and run the DRAFT-6 WP-11 portability/golden machinery from independent expectations.
- Prepare WP-10 fixtures and enumeration for all non-contradictory states, including the new DRAFT-6 counter/durability regressions, without encoding the four disputed predicates as truth.
- Build the WP-12a callback driver and state/I/O recorder, but do not assert a final callback result oracle until `V6-009` is dispositioned.
- Continue independent PR review only under `procedures/independent-pr-review.md` and its implementation-separation rules.

## Current stop conditions

- Do **not** recommend the Phase-0 signature while any of `V6-001`…`V6-006` remains major or blocker.
- Do **not** claim a green final WP-10 while `V6-002`, `V6-003`, `V6-007`, or `V6-008` remains unresolved.
- Do **not** claim a green final WP-12a while `V6-009` remains unresolved.
- Do **not** inspect engine implementation to resolve any normative ambiguity above.
