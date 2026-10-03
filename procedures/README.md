# Verification procedures and checks

The [advisory PR review procedure](independent-pr-review.md) is opt-in and separate
from Verification publication and exact-candidate disposition. Neither a marker nor
an advisory comment grants acceptance or automatic activation.

## CI map

All runners are pinned to `ubuntu-24.04`. PR checks are path-scoped except the
historical playback workflow, which is push/dispatch only. Closure replay workflows
retain PR/dispatch entry points; obsolete completed-issue push branches are removed.

| Workflow | Packages / retained checks |
|---|---|
| `verifier-package-selftests.yml` | `*_draft8`, `*_draft9`, `*_r44`: package self-tests; `make -C tests check-infrastructure` C helper self-tests |
| `playback-verifier.yml` | Early playback regeneration, hash/spec authentication, synthetic replay and controls |
| `verifier-wp06-closure-r52.yml` | WP-06 closure audit, self-test, retained-stream replay/regeneration |
| `verification-issue-100.yml` | WP-08 portability GCC/Clang evidence, replay, committed-evidence comparison |
| `verifier-closure-r53.yml` | All `*_r53`: audit, self-test, offline replay/regeneration |
| `verifier-closure-r54.yml` | All `*_r54`: audit, self-test, offline replay/regeneration |
| `verifier-wp10-packages.yml` | WP-10 backlog/final, strengthening, WP-08/09 reconciliation and capacity checks |
| `verifier-residue-d10.yml` | DRAFT-10 residue audit, self-test and full regenerated synthetic stream replay |
| `verifier-wp11-r63.yml` | Golden model/hashes, independent differential and paper-ledger audit; PR/main push/dispatch |

For an exact workflow locally, run its `run` blocks from the declared working
directory with the listed toolchain. Some audits import pinned siblings or findings;
use the whole repository. Generic local `check` is a compatibility alias for
`check-core`, not all 37 packages. Do not infer Product acceptance from self-tests.
WP-11 source-asset regeneration/publication is explicit manual dispatch only;
normal PR/main checks do not recreate assets or rerun network conversion.

## Historical replay tools

- `audit_mount_observations.py`: the 7 September DRAFT-8 mount-log replay; its
  default observations belong to Product. Fetch the exact retained input named in
  the [mount disposition](../findings/mount-observation-disposition-2026-09-11.md).
- [R25 re-spool replay](../tools/README.md): single-round evidence audit.

These scripts retain their original bytes and defaults. They are provenance tools,
not the current all-package runner or a Phase 2 assignment.
