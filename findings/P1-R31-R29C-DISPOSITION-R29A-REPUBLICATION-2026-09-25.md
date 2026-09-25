# P1-R31 Verification return — R29-C disposition and R29-A republication

Date: 2026-09-25 UTC  
Issue: [Digital-Tape-Verification #78](https://github.com/mmsanders/Digital-Tape-Verification/issues/78)  
Frozen authority: DRAFT-8  
Product input: `ac1f1bfb3efa636e3c22fff4febc7d08f7b6d026`  
Verification input: `50c47c1b9087de52f66d831ef2fe00cc02273087`

## Part 1 — exact R29-C head

### Mechanical authentication

The held [product PR #236](https://github.com/mmsanders/Digital-Tape/pull/236)
head is `175b8299efe59fe762fdc7fae2a371b318940abd`, tree
`2fb35a5737ffa8477bf70c36afd5ab87cd9ff04e`.

The branch order is authentic without inspecting engine implementation:

1. import commit
   [`375d55ff6bbf328e7ff434012258dd1a3c1fe98a`](https://github.com/mmsanders/Digital-Tape/commit/375d55ff6bbf328e7ff434012258dd1a3c1fe98a)
   has sole parent the issued product main and imports
   `tests/respool_full_draft8` tree
   `7e98b40c6aceb0a5759bfb1499091a4c9f541927`;
2. candidate head `175b8299...` has that import commit as sole parent;
3. [evidence-integrity run 36184043526](https://github.com/mmsanders/Digital-Tape/actions/runs/36184043526)
   is green at the exact head.

### Bounded behavioral observations

The corrected `WP10-RESPOOL-OBSERVATION-2` campaign is behaviorally green:

- [aggregate job 108236998695](https://github.com/mmsanders/Digital-Tape/actions/runs/36184043458/job/108236998695)
  downloaded exactly 48 shards and reported
  `PASS total=4209696 shards=48`;
- canonical planner digest:
  `02c52de7a7c51a6ffafe5c9d5afad9c23032b72fc11aaf206bb27a9c9506d3e1`;
- exact mode split: 2,104,848 flush-required and 2,104,848 write-through;
- exact pass split: 3,084 no-lower-run pass 1; 2,103,306 V3-003
  pass 1; 2,103,306 V3-003 pass 2;
- exact target split: 4,203,522 chunk-copy cuts, 3,078 entry-block
  cuts, 3,078 header-block cuts, and six cuts for each of the three
  relevant flush families;
- [aggregate artifact 10886032765](https://github.com/mmsanders/Digital-Tape/actions/runs/36184043458/artifacts/10886032765)
  ZIP SHA-256
  `adf497d98fdc1e3c88fd0f0e94fdef9884f310c08555a1b00935b75130a4d984`,
  retained aggregate SHA-256
  `b0db1248c67896e2a1612bb738d1a809a2ee843c138507dfae03cf8a7d999ebf`.

The [functional/WP-12a job 108233029922](https://github.com/mmsanders/Digital-Tape/actions/runs/36184043458/job/108233029922)
is green at the exact head. The public binding calls every small-budget
continuation with literal budget 1 and emits cumulative chronological raw
chunk-region write-LBA traces. The imported verifier independently requires:

- prefix continuity between every call, strict progress and no repeated LBA;
- BUSY/refusal rows with no block operations and unchanged traces;
- a following ordinary continuation that prefix-extends the prior trace;
- zero-budget INVALID_ARG with no work/state loss on initiation and continuation;
- terminal own-device write/flush failure to IO + FAULTED;
- the complete Faulted row, ring drain, abort cleanup and the stated exclusions.

This is bounded raw-observation credit only. It does not accept implementation
source, merge authority, stage-clear work already closed elsewhere, WP-11
listening/goldens, complete WP-10, complete WP-12, hardware media atomicity or
any unrelated hold.

### Provenance finding and disposition

The evidence bundles carry two false hard-coded identities copied from held PR
#227:

- `product_base = 8276d8f22da34a53f9f52dae8d3bd1acb3c763d9`, but the authenticated
  base is `ac1f1bfb3efa636e3c22fff4febc7d08f7b6d026`;
- `verifier_import_commit = 895351d17de9332e0804140858049d3608eeecd4`, but the authenticated
  product import commit is `375d55ff6bbf328e7ff434012258dd1a3c1fe98a`.

The stale constants are present in both
[`run_shard.py`](https://github.com/mmsanders/Digital-Tape/blob/175b8299efe59fe762fdc7fae2a371b318940abd/tests/respool_full_adapter/run_shard.py)
and
[`run_functional.py`](https://github.com/mmsanders/Digital-Tape/blob/175b8299efe59fe762fdc7fae2a371b318940abd/tests/respool_full_adapter/run_functional.py);
the aggregate artifact repeats them. GitHub run identity, product commit/tree,
verifier tree and Structural Rule 1 order are independently authentic, so this
does not erase the bounded behavioral observations above. It does make the
published evidence internally false and therefore unacceptable as the exact
R29-C evidence package.

**Disposition: RETURN.** Exact head `175b8299...` is behaviorally green at
the stated boundary but is not ready for acceptance or merge. Software must
correct only the evidence provenance identities, rerun the exact public
campaign on the resulting held head, and return the fresh artifacts. No engine
change is indicated by this finding. PR #236 remains held and unmerged.

## Part 2 — corrected R29-A verifier publication

Verifier source/publication commit:
[`4a206bcdc9b24db4cd47d2477c8229efb382040f`](https://github.com/mmsanders/Digital-Tape-Verification/commit/4a206bcdc9b24db4cd47d2477c8229efb382040f)  
Immutable package tree: `2eb707d7e8ea721085164b85f5e2f397e115a036`

The correction changes only the verifier-owned `tests/promote_draft8`
contract/oracle documentation and controls:

1. ordinary Promote-in-progress render now requires retained
   `rate_q16_16 == 0`, `TAPE_OK`, `rendered == 0`, empty PCM and empty
   device trace;
2. callback-nested render applies the same stopped-render rule;
3. own-device failure now requires the precondition **Promote in progress**,
   not Playing;
4. a separate Playing fixture may supply the Faulted ring-drain cell, which
   proves the frozen Faulted row but makes no Promote-while-Playing causal claim.

Four targeted red controls reject the superseded ordinary-render,
callback-render, failure-precondition and Faulted-row-causation expectations.

Planner membership is unchanged:

- crash cases: 44,204;
- contract/headroom/re-run cases: 107;
- total: 44,311;
- planner SHA-256:
  `8732af9434437d0411731b3e4909a2ca9a1278778e5d9c8947642cec7b793442`.

Verifier-owned execution:

```text
python3 tests/respool_full_draft8/selftest.py
python3 tests/promote_draft8/selftest.py
```

Both pass locally. R29-A prints the unchanged 44,204 + 107 = 44,311 census
and digest, all eleven recovery rows, two-interruption closure, the complete
107-case contract census, the new negative controls and the final all-selftests
PASS line.

No frozen DRAFT-8 byte, product import/adapter or product branch was edited.
The publication does not accept product PR #237, any known product fix,
WP-11, R29-B, R29-C, the previously accepted bounded core tranche, hardware
media atomicity or complete WP-10/WP-12a. The no-new-consumer/release hold
remains.

## Next owner

PM should review the exact verifier publication. If accepted, Software may
replace the held R29-A import with this immutable package tree and produce a
fresh binding/evidence return. Separately, Software owns the provenance-only
R29-C evidence correction and rerun. Product PRs #236 and #237 stay held.
