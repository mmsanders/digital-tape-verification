# P1-R18-V — VT8 fixture geometry and replay closure

**Date:** 19 September 2026 UTC  
**Assignment:** digital-tape-verification issue #14  
**Input verifier main:** `62630b8a1e6dea18d8c4b22057fce06577411896`  
**Product decision input only:** `44aeac087c5f970c30b75a001b95ca7d0c089da4`  
**Verifier source publication:** `eb5d7867c604b2c8a07e05597b8b9f07071b539e`  
**Source root tree:** `ed37ff38d3f44c5fd3349125b79326bd3ae16929`

## Disposition

The bounded verifier correction is complete with no residual blocker. Both VT8-001
fixtures are now valid frozen DRAFT-8 media, generator-side controls reject the two
invalid geometry classes before any adapter can run, and every verdict-affecting
adapter completion outcome is retained and recomputed by offline replay. Fresh
synthetic evidence from the immutable source passes both cases and exact replay.

This is verifier-package correctness only. No product candidate, product adapter,
PR #96 source/diff/discussion, or product implementation was inspected or run.

## Frozen geometry and fixture identities

The correction retains `nominal_length_s = 60` and derives:

```text
total_chunks = ceil(60 * 44100 / 131072) = 21
blocks_per_chunk = 524288 / 512 = 1024
block_count = 2048 + 21 * 1024 + 1 reserved block = 23553
chunk region = [2048, 23552)
reserved last block = 23552
```

Thus the complete derived chunk region ends exactly before the reserved last block.
Generator-side proof separately checks the stored/derived chunk count, sample/chunk
geometry, fixed index and chunk block layout, reserved-block placement, full-region
fit, exact structural sequences, live/degraded slot premises, source entries,
`a_high_water == free_next == 3`, and allocated chunk-3 bounds.

| Case | Input raw SHA-256 | Output raw SHA-256 | Case evidence tree |
|---|---|---|---|
| `VT8-001-RB-ALLSLOT` | `b39dd5a9aa0a160f1ab923ab76cdb9bbef54f042a525178cfff833b99377bd07` | `c1f12d43f12a65d99b06e6486abfa2a93a0945e26fdb4a18303978a2b5e08627` | `7c8de206ff77647349057be3c56923c9ae921a3c` |
| `VT8-001-REC-ALLOCSEQ` | `b3d87522ef3d8789b52916985beea8cdd25a517dc93063095be2abdbb6e7a4d7` | `3e447210d5207de737a335e15546501bb14e73642a46d1fbf0a8790d48870e7f` | `5830738a72bdc2665470f8c5b700e5da5343f96b` |

Targeted controls go red for the former stored `16` versus derived `21` mismatch
and for a 23,552-block medium whose chunk region overlaps its reserved last block.
All prior case intent, expected sequences, index assertions and exclusions remain.

## Runner/offline-replay closure

Evidence format `VT8-EVIDENCE-2` adds a per-case, manifest-bound
`VT8-ADAPTER-STATUS-1` record with one exact outcome: normal exit and integer code,
bounded timeout, or execution error. Runner and replay use the same strict outcome
schema to derive its verdict effect. Result evidence additionally binds the outcome
label and exit code.

The new nonzero control emits otherwise conforming observation/media evidence and
exits 7. The runner retains a failing two-case bundle; offline replay yields the same
two `adapter returned 7` failures. Separate controls reject a changed status file by
hash, a missing status file, and a relabeled status even when its descriptor hash is
updated. Zero-exit synthetic evidence replays exactly. Existing malformed-output,
spec authentication, missing/tampered evidence, diagnostics and nonempty-destination
retention behavior remains enforced.

## Trees, paths and evidence

The input verifier `tests/ops_draft8` tree was
`4a2ac719c2ca88840055499621be9af4ba7e9f9a`. The source-first publication changes it
to `12d2a95e879dd0b7b891387ebdc166f0be0c854e`. The complete package tree after adding
fresh retained evidence is `3667a2830ba80dbcedad03b97870d1127001ab59`.

Source changed paths:

- `tests/ops_draft8/ADAPTER.md`
- `tests/ops_draft8/COVERAGE.md`
- `tests/ops_draft8/README.md`
- `tests/ops_draft8/_synthetic_adapter_fail.py`
- `tests/ops_draft8/hardened.py`
- `tests/ops_draft8/oracle.py`
- `tests/ops_draft8/replay.py`
- `tests/ops_draft8/runner.py`
- `tests/ops_draft8/selftest.py`

Fresh evidence is the 19-file
`tests/ops_draft8/evidence/p1-r18-synthetic/` tree
`3a1320117d9d375367102d41b169010507a2ab58`. Its manifest is Git blob
`c5ea696d6a0d2a06f9123702d1ad2acf6947da2e`, SHA-256
`e30fa685181103de8080cb9a225af956cc4122a94d016d7f9697c4ccb577d872`.
The manifest-bound run log SHA-256 is
`10c7daec7f103c852feedcb015de97b221f044629a28ab54049b24dbb64bf411`.

The evidence authenticates the unchanged frozen DRAFT-8 bytes:

- TapeFS: `3bffa0ec46d7ba3779b02cbee6fac1edaf5094553f78270ee379759655147cbb`
- Engine API: `537eadc423e1a7bde726d689206b8fe93bef164d57e48e8ff71e07eaf8a7e3a1`
- Acceptance: `7f78fba7b66b4fc6e96d15399c62468249bb30fbccbb59bf9f57b4532f56b6b7`

## Commands and results

```text
python3 tests/ops_draft8/selftest.py
  PASS: 2 conforming + 2 geometry + 12 oracle + adapter-status/spec/evidence/replay controls

python3 tests/ops_draft8/runner.py --adapter tests/ops_draft8/_synthetic_adapter.py \
  --adapter-kind synthetic \
  --adapter-source 'eb5d7867c604b2c8a07e05597b8b9f07071b539e:tests/ops_draft8/_synthetic_adapter.py' \
  --adapter-build 'Python 3.12.3 direct executable; no build' \
  --verifier-source eb5d7867c604b2c8a07e05597b8b9f07071b539e \
  --evidence-dir tests/ops_draft8/evidence/p1-r18-synthetic
  PASS: 2 cases, 0 failed

python3 tests/ops_draft8/replay.py tests/ops_draft8/evidence/p1-r18-synthetic
  PASS: both cases; evidence complete, hash-bound, DRAFT-8 authenticated,
  verdicts recomputed offline

make -C tests check
  PASS: fault block device, crash harness, audio oracle, corrected ops package,
  three-family playback package and complete ten-family playback package

git diff --check
  PASS
```

## Exclusions and unchanged holds

No product import, PR #96 source review, product execution, candidate disposition,
engine acceptance or product acceptance occurred. Non-NULL warm start; overwrite and
overdub; zero-frame commit; stage clearing; reset timing; random/10,000-edit sequences;
promote, re-spool, duplicate and format; long-operation continuation/reentry; FAULTED
quarantine; crash/recovery; V7-001; timing/resources; hardware/media atomicity; PCM,
WP-11 goldens and listening all remain excluded.

PRs #20, #64 and #96, uncovered behavior, frozen-spec hashes, safety/fabrication/
charging holds, purchase approval, physical work, and all Michael-reserved approvals
remain unchanged. The next owner is PM for review and any separately issued Software
import/rerun direction.
