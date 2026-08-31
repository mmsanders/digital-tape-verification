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
