# Capability status — PM Decisions 001-R

Date: 1 Sep 2026

This matrix distinguishes capabilities that can be completed against PM Decisions 001-R from work whose normative inputs have not yet been issued.

| PM direction | Status | Evidence / boundary |
|---|---|---|
| Treat 001-R as superseding 001 | Complete | `PM-NOTES.md` records 001-R as controlling. No further DRAFT-1 review is underway. |
| Wait for full replacement DRAFT-3 | Compliant, waiting | DRAFT-3 has not been supplied. No replacement-spec assertions are being invented from the disposition summary. |
| Prioritize new DRAFT-3 recovery text | Ready, input-blocked | Review queue is re-spool disjointness, two-phase promote, duplicate `WRITE_IN_PROGRESS`, then superblock generation/recovery. Execution requires DRAFT-3. |
| Build crash-injection harness structure | Complete for the specification-independent layer | `tests/crash_harness.[ch]` traces a clean run and exhaustively replays every 0..512-byte block outcome and every flush failure through reset, power cut, remount, validation, and reporting callbacks. |
| Build fault-injecting block device | Complete | `tests/fault_block_device.[ch]` is allocation-free C99, works inside multi-block writes, supports both flush-required and write-through durability, models flush and power cut, and persists torn prefixes. |
| Develop Suite 3 invariant list | Complete at the PM-authorized pre-DRAFT-3 level | `tests/SUITE-3-INVARIANTS.md` covers consecutive runs, corrected reachability semantics, re-spool/promote invariants, parameterized geometry, generator/shrinker obligations, oracle independence, and exhaustive crash quantification. Exact field parsers await DRAFT-3. |
| Maintain on-request independent PR review | Complete and live | The watcher requires the exact marker in PR description/discussion and deduplicates by head SHA. It reviews tooling/firmware/docs, or engine behavior only after verifier-authored coverage lands. Otherwise it declines without reading the diff and requires PM for exceptions. |
| File directly where PM can read | Complete | Status and findings remain in this repository; `PM-NOTES.md` is the handoff log. |
| Implement WP-10/WP-11 acceptance tests | Input-blocked, not presently authorized to guess | `spec/acceptance.md` and DRAFT-3 remain owed by PM. |

## Verification of the infrastructure

The following pass with no output:

```sh
cc -std=c99 -Wall -Wextra -Werror -pedantic \
  tests/fault_block_device.c tests/test_fault_block_device.c \
  -o test_fault_block_device && ./test_fault_block_device

cc -std=c99 -Wall -Wextra -Werror -pedantic \
  tests/fault_block_device.c tests/crash_harness.c \
  tests/test_crash_harness.c -o test_crash_harness && ./test_crash_harness
```

The harness self-test observes two block writes and two flushes and runs 1,029 cases: one clean baseline, 513 outcomes per written block, and one failure at each flush.
