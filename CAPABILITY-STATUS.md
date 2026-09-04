# Capability status — PM Decisions 002

Date: 2 Sep 2026

This matrix records the DRAFT-3 review and the verifier-owned work that can proceed before PM disposition.

| PM direction | Status | Evidence / boundary |
|---|---|---|
| Treat 001-R as superseding 001 | Complete | `PM-NOTES.md` records 001-R as controlling. No further DRAFT-1 review is underway. |
| Preserve full replacement inputs | Complete | PM Decisions 002, both DRAFT-3 specs, and DRAFT-1 acceptance criteria are stored under `pm/` and `spec/`. |
| Prioritize new DRAFT-3 recovery text | Complete | The review began with run extents, re-spool, promote, superblocks, duplicate, the state matrix, and exact arithmetic as directed. |
| Build crash-injection harness structure | Complete for the specification-independent layer | `tests/crash_harness.[ch]` traces a clean run and exhaustively replays every 0..512-byte block outcome and every flush failure through reset, power cut, remount, validation, and reporting callbacks. |
| Build fault-injecting block device | Complete | `tests/fault_block_device.[ch]` is allocation-free C99, works inside multi-block writes, supports both flush-required and write-through durability, models flush and power cut, and persists torn prefixes. |
| Develop Suite 3 invariant list | Complete at the current spec-stable boundary | `tests/SUITE-3-INVARIANTS.md` now uses DRAFT-3 names/layout and records the exact oracle points blocked by findings. |
| Maintain on-request independent PR review | Complete and live | The watcher requires the exact marker in PR description/discussion and deduplicates by head SHA. It reviews tooling/firmware/docs, or engine behavior only after verifier-authored coverage lands. Otherwise it declines without reading the diff and requires PM for exceptions. |
| File directly where PM can read | Complete | Status and findings remain in this repository; `PM-NOTES.md` is the handoff log. |
| Review DRAFT-3 and acceptance criteria | Complete for this PM pass | `findings/spec-review-draft3.md` contains 4 blockers, 11 majors, and 1 question, including explicit WP-10/WP-11 testability findings. |
| Implement WP-10 crash infrastructure | Complete below the operation-adapter seam | `fault_block_device.[ch]`, `crash_harness.[ch]`, self-tests, and `WP10-PLAN.md` provide exhaustive per-block/torn/flush enumeration. Final state oracles wait on the filed contradictions. |
| Implement WP-11 runner/golden structure | In progress at the spec-stable boundary | `tests/Makefile` gives the one-command strict-C99 runner and `WP11-PLAN.md` fixes fixture, diagnostic, golden-family, and mutation obligations. Fixtures/adapters wait on arithmetic/state dispositions. |

## Verification of the infrastructure

The following pass with no output:

```sh
make -C tests check
```

The harness self-test observes two block writes and two flushes and runs 1,029 cases: one clean baseline, 513 outcomes per written block, and one failure at each flush.

## PM Decisions 003 update — 3 Sep 2026

| PM direction | Status | Evidence / boundary |
|---|---|---|
| Preserve PM-003 and DRAFT-4 inputs | Complete | `pm/verification-lead-003.md` and all three `spec/` files are verifier-side copies of the supplied documents. |
| Run the last pre-freeze adversarial pass | Complete; freeze not recommended | `findings/spec-review-draft4.md`: 1 blocker, 12 majors, 1 question. |
| Attack entry non-overlap first | Complete | V4-002 proves the advertised scalar equivalence accepts overlapping physical frames and is circular for B validation. |
| Enumerate promote boundaries | Complete | V4-003 identifies the missing post-step-7 and post-step-8 states; V4-004 identifies the exact-tail rerun failure after phase-1 B commit. |
| Review re-spool and duplicate product semantics | Complete | V4-005 covers empty re-spool; V4-006 covers raw-device geometry. Side-A-only duplicate is accepted as coherent and testable. |
| Review state matrix and position arithmetic | Complete | V4-001 and V4-007…V4-013 cover effective read-only state, incremental continuation, commit/abort reachability, saturation, sample phase, warm-range arithmetic, invalid state admission, and signed-shift portability. |
| Confirm WP-10/WP-11 testability | Complete | Both plans now contain a DRAFT-4 testability verdict and exact remaining blockers. |
| Build WP-10 structure | Advanced | `crash_harness` now accepts a scenario-specific remount predicate, enabling the operation-specific `INCOMPLETE`/`BAD_MAGIC` outcomes while retaining strict default behavior. |
| Maintain test independence | Complete | No engine implementation, branch, diff, issue, or unlanded artifact was inspected. |

The DRAFT-4 documents are stable enough for generic harness and stable-operation oracle work, but not for freezing promote crash outcomes or byte-exact variable-rate playback fixtures.

## PM Decisions 004/007 update — 4 Sep 2026

| PM direction | Status | Evidence / boundary |
|---|---|---|
| Authenticate and preserve DRAFT-5 | Complete | `spec/VERSION.md` hashes match all three supplied files; exact verifier-side courtesy copies are under `spec/`. |
| Attack `promote_stage`, both-side mount, duplicate, and long-operation rows first | Complete | `findings/spec-review-draft5.md` begins with these state/crash paths and then records the whole-document pass. |
| Confirm WP-10/WP-11/WP-12a testability | Complete; all three need correction | The findings file gives separate mechanical verdicts and `tests/WP10-PLAN.md` / `tests/WP11-PLAN.md` map the remaining seams. |
| Phase 0 blocker gate | Clear, with majors | No blocker in `tapefs` §§1–8 or `engine-api` §§2–8/§12; eight major findings remain in or cross those sections. |
| Later behaviour freeze | Blocked | V5-001 and V5-002 are cartridge-corruption/loss paths; first-green WP-10 cannot gate the current text. |
| Advance independent WP-11 arithmetic work | Advanced | The oracle remains implementation-independent and now exhaustively covers all 131,071 sample deltas at five boundary phases. |
| Maintain test independence | Complete | No implementation source, implementation diff/branch/issue, or unlanded artifact was inspected. |

Canonical `Digital-Tape/main` had not yet received DRAFT-5 when checked; the verifier files are explicitly non-authoritative courtesy copies until it does.
