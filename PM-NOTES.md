# PM Notes

## 2026-08-31 — DRAFT-1 specifications received; adversarial review started

Received and preserved verifier-side copies of:

- `spec/tapefs-v1.md`
- `spec/engine-api.md`

Both documents identify themselves as **DRAFT-1, issued for adversarial review, not frozen**. I am therefore treating them as review inputs, not as final acceptance-test authority.

First-pass mechanical findings are in `findings/spec-review-draft1.md`. The current pass contains two blocker findings and multiple major/question findings. Highest-priority items for PM attention are:

1. Re-spool as currently described can overwrite chunks referenced by the still-live B index before commit, so interruption can corrupt a cartridge (`V-002`, blocker).
2. Duplicate has no destination precondition or crash protocol, so interruption can destroy a pre-existing destination cartridge (`V-003`, blocker).
3. Index entries are normatively placed starting at byte 64, but the commit protocol writes entries only to blocks 1–127 then zero-pads block 0 (`V-001`).
4. Promote's mutable superblock/high-water and single preroll cache do not have a complete two-copy/generation crash protocol (`V-007`, `V-009`).
5. Fresh UUID/format time generation is impossible through the current engine boundary because there is no entropy or clock input (`V-011`).
6. Recording commit/full-card semantics are underspecified across the interrupt-safe ring and service loop (`V-012`, `V-013`).

I have not inspected engine implementation, implementation PRs/diffs, or implementation issues while producing these findings.

### Still needed before WP test implementation

Please provide when available/frozen:

- WP-10 acceptance criteria
- WP-11 acceptance criteria
- revised/frozen TAPEFS and engine API specs after PM disposition of adversarial findings

No clarification from the user is required for the current spec-review pass.

## 2026-08-31 — Startup note (superseded)

At verification startup the required spec documents were not yet available. They have now been received as DRAFT-1 review copies; see above.

## 2026-09-01 — PM Decisions 001-R received and controlling

Received PM Decisions 001 and the superseding PM Decisions 001-R. I am treating 001-R as controlling. PM accepted all 22 DRAFT-1 findings in some form: sixteen as written, three with a different fix, two moot, and one as a charter defect rather than a spec defect. No finding was rejected.

Per 001-R, I have stopped reviewing DRAFT-1 and will wait for full replacement DRAFT-3 specs. When they arrive, review priority is: re-spool destination disjointness, two-phase promote, duplicate's WRITE_IN_PROGRESS protocol, and superblock generation/recovery. WP-10/WP-11 acceptance criteria remain outstanding and are expected in spec/acceptance.md with DRAFT-3.

Authorized pre-DRAFT-3 work has begun:

- tests/fault_block_device.[ch]: caller-owned C99 block simulator with per-block fault ordinals, unflushed-vs-durable media, power-cut rollback, before-block failure, torn-block persistence, and flush failure.
- tests/test_fault_block_device.c: strict-C99 self-test; compiled with -std=c99 -Wall -Wextra -Werror -pedantic and passed locally.
- tests/SUITE-3-INVARIANTS.md: parameterised run-based invariant scaffold, including corrected free-space semantics and the new re-spool/promote invariants.

Independent-review boundary remains in force: CI/tooling/host tooling/firmware/docs requests may be reviewed; engine behavior may be reviewed only after verifier-authored tests for that behavior have landed. A marked engine PR outside that boundary must be declined without reading its diff and escalated to PM.

## 2026-09-01 — Pre-DRAFT-3 capability completion audit

Completed every deliverable that PM Decisions 001-R authorizes before DRAFT-3. The initial block-device scaffold is now paired with a generic exhaustive crash runner. A clean trace is replayed for every individual block in batched writes with 0 through 512 landed bytes, and at every flush failure. Each case resets the fixture, simulates the operation and power cut, remounts, invokes independent invariant hooks, and emits a deterministic case record. The self-test's two writes/two flushes produce 1,029 passing cases.

The Suite 3 document now specifies parameterized geometry, consecutive-run bounds, generator/replay/shrinking obligations, independent-oracle rules, corrected free-space reachability, and re-spool/promote crash properties. Exact media decoding and operation adapters remain intentionally unimplemented until DRAFT-3 supplies their normative definitions.

See CAPABILITY-STATUS.md for the complete audit. The only remaining items are input-blocked: DRAFT-3 adversarial review and WP-10/WP-11 acceptance tests from spec/acceptance.md.
