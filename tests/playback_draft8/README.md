# DRAFT-8 playback/golden tranche — P1-R2-V

Independent Verification package for exactly three observable playback families from the frozen DRAFT-8 public contract. It contains no product implementation code and was authored without inspecting product engine source, diffs, or private implementer tests.

## Covered families

1. `forward_1x`: exact 15-frame stereo s16le PCM at +1.0x across a deliberately non-constant three-run Side-A timeline.
2. `seek_boundaries`: `tape_seek(N)` then one rendered frame for `N = 0,1,4,5,6,8,9,10`, covering each run boundary and +/-1 where in range.
3. `reverse_neg1x`: exact 15-frame reverse-from-end PCM at -1.0x, long enough to reject the historical off-grid `max_pos-1` snap defect rather than checking only the first sample.

The candidate PCM files are verifier-derived oracle bytes. **They are not frozen/accepted WP-11 goldens yet:** Michael's human listening is a later separately issued step, and product-engine execution is also outside this assignment.

## Fixture and provenance

`fixtures/playback-three-run.vo08.gz` is a deterministic gzip (`mtime=0`) of a full TAPEFS-partition VO08 envelope. Side A has three physical runs in timeline order `(chunk 0,start 10,len 5)`, `(chunk 2,start 20,len 4)`, `(chunk 1,start 30,len 6)`. `package.json` binds the compressed fixture, raw VO08 bytes, metadata, candidate PCM and exact DRAFT-8 spec hashes.

Run `python3 tests/playback_draft8/selftest.py`. Run a public-API adapter with `runner.py`; recompute any saved bundle offline with `replay.py`. See `ADAPTER.md` and `COVERAGE.md`.

A green synthetic run proves only verifier plumbing. Product execution and Michael listening are separate later steps. This tranche does not complete all WP-08/WP-11.
