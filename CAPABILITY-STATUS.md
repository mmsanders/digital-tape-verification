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
