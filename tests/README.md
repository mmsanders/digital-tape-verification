# Verification tests and publication index

**3 October 2026 snapshot: Phase 1 complete, DRAFT-10 current in Product.**
All 37 package trees below are preserved at the cleanup input publication
`cdf89f5f0ab0aa8cc94c13fbf0f98fea484975a4`. This index updates status without changing
imported package identities. Package READMEs, fixtures, evidence and spec copies
remain records of their authoring/publication dates; old pending/held statements
must be read with this index and [current capability status](../CAPABILITY-STATUS.md).

Verification owns expectations and oracles; Product owns adapters and implementation.
An accepted work package is the union of the exact disposed tranches, not a claim
that every historical package individually proves the whole WP. The final WP-11
closure is in [the Stage 2 addendum](../findings/P1-R63-WP11-STAGE2-DISPOSITION-2026-10-03.md).

## Packages

Phase 2 additions: [wp14_r1](wp14_r1/README.md) is the #146 independent preflight
and **partial** WP14 publication. Contract recognition/loop conflicts block full
Stage1; no candidate acceptance or physical witness is claimed. Original Phase1
package bytes below remain unchanged.

Numbers below are Verification issues/PRs unless prefixed Product. Follow
[Product STATUS](https://github.com/mmsanders/Digital-Tape/blob/main/docs/STATUS.md) and [dated findings](../findings/README.md)
for exact hashes, evidence and exclusions.

| Publication tree | Scope | Phase 1 disposition / provenance |
|---|---|---|
| [allocator_cow_draft8](allocator_cow_draft8/README.md) | WP-07 | Accepted; PR #67 / Product #215 |
| [capacity_wp09_r52](capacity_wp09_r52/README.md) | WP-09 | Accepted capacity tranche; #107 / Product #311 |
| [crash_core_draft8](crash_core_draft8/README.md) | WP-10 | Accepted bounded core; PR #69 |
| [crossrun_wp08_r44](crossrun_wp08_r44/README.md) | WP-08 | Accepted cross-run; #95 / Product #287 |
| [embedded_readiness_draft8](embedded_readiness_draft8/README.md) | WP-13 | Historical DRAFT-8 predecessor; final DRAFT-9 acceptance #83 |
| [embedded_readiness_draft9](embedded_readiness_draft9/README.md) | WP-13 | Accepted six gates; #83 / Product #241; DRAFT-10 carry #361 |
| [format_dup_draft8](format_dup_draft8/README.md) | WP-06/10 | Accepted bounded refusals; R25 findings; final #138/#141 |
| [format_dup_identity_draft8](format_dup_identity_draft8/README.md) | WP-10 | Covered by final DRAFT-10 closure #141 |
| [golden](golden/README.md) | WP-08/09/11 | Stage 2 #143 PASS 10/10; Michael #367 approved all |
| [history_wp09_r44](history_wp09_r44/README.md) | WP-09 | Accepted 10,000-edit history; #96 / Product #288 |
| [mount_draft8](mount_draft8/README.md) | WP-06 | Accepted 289-case mount; final closure #138 |
| [notmounted_draft8](notmounted_draft8/README.md) | WP-06 | Accepted 34-case NOT_MOUNTED; final closure #138 |
| [ops_draft8](ops_draft8/README.md) | WP-06/09 | Early VT8 observations; final package state in #138/#143 |
| [playback_complete_draft8](playback_complete_draft8/README.md) | WP-08 | Accepted corrected-cadence tranche; synthetic PCM is historical |
| [playback_draft8](playback_draft8/README.md) | WP-08/11 | Historical early candidate PCM; accepted goldens are golden/ |
| [portability_wp08_r52](portability_wp08_r52/README.md) | WP-08 | Accepted 41 two-toolchain vectors; #122 / Product #327 |
| [promote_draft8](promote_draft8/README.md) | WP-10/12a | Accepted R29-A; #86 / Product #263; integration #267 |
| [record_draft8](record_draft8/README.md) | WP-09 | Accepted bounded structural observations; R25 findings |
| [respool_draft8](respool_draft8/README.md) | WP-12 | Accepted bounded 8-case observations; R25 findings |
| [respool_full_draft8](respool_full_draft8/README.md) | WP-10/12 | Accepted R29-C and composition; #81/#87 |
| [sequential_wp06_r44](sequential_wp06_r44/README.md) | WP-06 | Accepted corrected 38-case sequential; #98 / Product #297 |
| [slot_draft8](slot_draft8/README.md) | WP-36 | Accepted deterministic precursor; PR #57 |
| [strengthen_r55](strengthen_r55/README.md) | WP-06/09/10 | Accepted strengthening; R56 STRD / Product #343 |
| [transport_draft8](transport_draft8/README.md) | WP-08/36 | Accepted set-side/warm-start; R25 findings |
| [wp06_closure_r52](wp06_closure_r52/README.md) | WP-06 | Accepted 7 closure rows; #121 / Product #326; final #138 |
| [wp08_mapping_r56](wp08_mapping_r56/README.md) | WP-08 | Behavior reconciliation; R57 W89D; listening/L04 closed by #143/#367 |
| [wp09_gaps_r56](wp09_gaps_r56/README.md) | WP-09 | Behavior reconciliation; R57 W89D; listening closed by #143/#367 |
| [wp10_backlog_r53](wp10_backlog_r53/README.md) | WP-10 | Historical DRAFT-9 backlog; carried into final #141 ledger |
| [wp10_backlog_r54](wp10_backlog_r54/README.md) | WP-10 | Historical DRAFT-9 backlog; carried into final #141 ledger |
| [wp10_closure_r53](wp10_closure_r53/README.md) | WP-10 | Accepted closure tranches #119/#120; final #141 |
| [wp10_final_r54](wp10_final_r54/README.md) | WP-10 | Historical final DRAFT-9 ledger; superseded by residue DRAFT-10 |
| [wp10_residue_d10](wp10_residue_d10/README.md) | WP-10 | Final DRAFT-10 closure #141: 63 rows, zero open |
| [wp11_ledgers_r63](wp11_ledgers_r63/README.md) | WP-08/09/12/12a | Immutable Stage 1 ledger; Stage 2/listening closure in findings addendum |
| [wp11_portability_r63](wp11_portability_r63/README.md) | WP-11 | Stage 2 #143 accepted host/ARM/static-assert configurations |
| [wp12_closure_r53](wp12_closure_r53/README.md) | WP-12/12a | Accepted 7 gaps #123 / Product #328; final #143 ledger |
| [wp36_fuzz_draft8](wp36_fuzz_draft8/README.md) | WP-36 | Accepted 100,000-sequence campaign; PR #57 / Product #200 |
| [writability_draft8](writability_draft8/README.md) | WP-06 | Accepted 8-case writability; final closure #138 |

## Local checks and CI

`make -C tests check-core` runs the three generic C self-tests and the five legacy
package checks. `check` remains a compatibility alias for that subset; it is not
all-package validation. Package-specific commands remain in each README.

[Generic package CI](../.github/workflows/verifier-package-selftests.yml) covers
`*_draft8`, `*_draft9` and `*_r44`. Specialized workflows retain closure audits,
offline replay, two-toolchain checks and WP-11 checks. See
[the CI map](../procedures/README.md) for commands, filters and replay dependencies.
Synthetic self-tests establish verifier behavior, not new Product acceptance.

## Generic infrastructure and historical plans

- `fault_block_device.[ch]` models 512-byte blocks, volatile/durable media, both
  flush-required and write-through modes, and partial-write/flush faults.
- `crash_harness.[ch]` replays write/flush boundaries through scenario callbacks.
  Its early DRAFT-5 non-mounting support is infrastructure, not a current allowed-state oracle.
- `audio_oracle.[ch]` independently models saturation and interpolation with explicit
  floor division. The three `test_*.c` files self-test these helpers.
- [PLAN-STATUS](PLAN-STATUS.md) locates historical DRAFT-5/6 plans and the fulfilled
  early proposal. Derive new adapters and allowed states from authenticated current
  spec sections and independent package oracles.

Crash scenarios test both durability modes and remount from durable bytes only.
Product-only paths in historical findings (adapters, IMPORTS, fetch-evidence and
`tools/ci/`) belong to Digital-Tape, not this repository.
