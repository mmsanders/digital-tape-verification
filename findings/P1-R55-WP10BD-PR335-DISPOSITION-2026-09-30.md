# P1-R55-V-WP10BD: disposition of Product PR #335 (WP-10 backlog rows 1–3, corrected rebind)

**Verdict: PASS** for exact Product head `d5540f111101eca03be1c90135888fa262363bf6`, tree
`78cce05e375e0d41b39a0d42c887024d09f50630`, **79,820 / 79,820**.

**Ruling:** taking the v2 pre/post digests from the accepted C69 worker's snapshots **binds the corrected row
soundly**. It does not let the binding supply its own expectation.

## Inputs

- Issue: Verification #127, body as of 2026-09-30T21:42:06Z, with no scope comments.
- Issuer: PM Product #305, pass 7.
- #335 supersedes #329.
- Product main was `2e54e0fc74a7c30df51a2cf232c7cb893cf9950a` at the time of this disposition. The candidate's base is `b05f6afc`, engine `81ad8ec2`.
- `engine/` was built and executed, never opened.

## Identities

| Object | Value | How checked |
|---|---|---|
| Import `71f24ac944d586f8ead70d6928d3d4e259ac6dce` | `tests/wp10_backlog_r53` = `caae666068e05c2c5e010e9b3e16e8583d3c707b`. That is my #124 publication `f327599` (2026-09-30T18:00:43Z), which precedes the import (19:58:51Z). Parent `b05f6afc`. Touches only that tree and `tests/IMPORTS.json`. | `rev-parse`, `diff-tree` |
| Binding `d5540f1` | Touches only `tests/wp10_backlog_adapter/` and one CI job. No `engine/`, `spec/` or `firmware/` change. | `diff --stat` |
| `wp10b_c69_worker.c` | The accepted `crash_core_adapter/wp10_core_worker.c` (SHA-256 `46ec919d…c0f`, taken from base `b05f6afc`) plus one public `tape_get_info` after remount. `diff` shows no other change. | `diff` |
| Retained evidence | JSONL `720db7ad…4742` (64,020,485 B), gzip `7c6f81519c65454f54731bcfc4dbc96b4d0bf93beceb35b17f7d790449a69729`, build identity `07c0eeac…2a35`, adapter aggregate `9b07d631…e268` | `SHA256SUMS` |

## Runs (Linux, GCC 13.3.0)

1. **Fresh canonical run at the exact head, with `--retained`.** The JSONL and gzip are **byte-identical** to the retained Windows evidence. Its replay passes 79,820.
2. **Independent replay** of the retained gzip, using my `oracle.py` at `f327599` (subtree `caae6660`), passes **79,820**:
   - row 1: 24,660 crash cases plus 2 completions;
   - row 2: 28,760 C69 and 26,392 R29-B;
   - row 3: 6 groups, 9,240 injections, enumerated from this binding's own flushes.

   The manifest is in `evidence/P1-R55-WP10BD/replay-manifest.json`.
3. **Product controls: 10 / 10 killed.**
   - Row 1: a chunk ≥ `total_chunks`, a layout-preserving copy, a changed source, and a wrong `free_chunks`.
   - Row 2: the frontier off by one, a different post-crash metadata state, and a changed chunk-store digest.
   - Row 3: metadata changed before commit, a wrong remount, and an extra service write.
4. **My own control, echo-pre-as-post.** I replaced `post_metadata_sha256` with `pre_metadata_sha256` in every real C69 record whose durable metadata changed. It is rejected in **28,456 / 28,456**.
5. **Row-2 C69 census** of the retained evidence:
   - All 6,168 `record_commit` records carry a `pre_chunk_sha256["2"]` that differs from the fixture (lawful setup audio). That is the state the v1 binding wrongly failed. All 22,592 `reset_b` and `stage_clear` records keep chunk 2 at the fixture value.
   - 304 records leave metadata unchanged: 12 `record_commit`, 28 `reset_b`, 264 `stage_clear`.
   - No C69 record carries `post_snapshot_sha256`.

I could not read CI runs from this session, which has no Digital-Tape API access by design. The steps above reproduce them.

## Ruling: the digests come from the accepted worker's snapshots

The binding is sound. Each part of the v2 check has a source the binding cannot steer:

- **The digests are observations, not predictions.** `capture_snapshot` fills `pre` and `post` directly from the worker's durable device buffer: both superblocks, the first two blocks of each slot, and a per-chunk SHA-256. `pre` is taken after setup and before the crash-scoped operation. `post` is taken after the injected cut and before remount. `run_product.py` lines 235–239 only split those emitted snapshots into the v2 fields. `image_sha256` is dropped. The accepted model appears only at lines 100–103, where it restates the case plan, as my `row2_cases` does.
- **The expectation is the oracle's.** My check requires the following, with each expected value computed by the oracle alone:
  - pre metadata equals the fixture's digest;
  - only `record_commit` may change chunk 2;
  - post metadata equals `expected_snapshot` simulated from that pre-state;
  - post chunks equal pre chunks.

  An adapter can make these pass only by reporting durable bytes that match the model. It cannot make them pass by choosing an expected value.
- **The worker is unchanged.** Its device model and snapshot code are the independently accepted C69 worker's, byte for byte. Regeneration reproduces the evidence exactly on a second toolchain.
- **The residual risk is the one every binding carries:** an adapter that fabricates snapshots. The last point closes it. This row adds no new trust.

## Exclusions

Complete WP-10, V-R54-03 (PM #308 / DRAFT-10), WP-11, hardware and release. This PASS accepts no engine behaviour beyond these 79,820 observations.

**Next owner:** PM.
