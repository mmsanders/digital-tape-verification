# P1-R2-V — first DRAFT-8 playback/golden tranche return

## Disposition

The bounded Verification assignment from issue #4 is **ready for PM review**. The independently authored package covers exactly the three assigned playback families. This return proves verifier-package integrity and replay plumbing; it does not claim a product-engine run, accepted WP-11 goldens, or broader product acceptance.

| Provenance | Exact value |
|---|---|
| Assigned product input | `7fe9942a847c6decfa40ea75aa08d16ea730bb39` |
| Assigned verifier input | `7ca24853ed32ddd327461594a31021cba4a408f3` |
| Resumed partial-work baseline | `435ccd6a41dccd540297da0ddfff65ed6f680b99` |
| Completed verifier source | `afa7f280efa5d2dfeb966c44a2eff369b3e30f73` |
| Completed source `tests/playback_draft8/` tree | `8293d51cae969ae044aa33872708dffe2fff9c3a` |
| Package manifest SHA-256 | `04fb8faee7575f5cb1ce5e00bbaa601b1d7c5281e0df0a76ebf05a41fac93d66` |

The evidence/publication commit containing this return is recorded in the immutable issue #4 return comment because a Git commit cannot contain its own hash.

## Completed package

- `forward_1x`: byte-exact 15-frame stereo s16le output at +1.0x across the non-constant three-run timeline.
- `seek_boundaries`: `tape_seek(N)` followed by one rendered frame, with frame N first for `N = 0,1,4,5,6,8,9,10`.
- `reverse_neg1x`: byte-exact 15-frame reverse-from-end output at -1.0x on the exact 32.32 frame grid.
- Public call/result/rate/seek/render/service ordering and the complete callback trace are persisted and checked. Reads are permitted only during mount/service; render-time I/O is rejected.
- Offline evidence replay authenticates the complete file set, every file hash, the package and fixed DRAFT-8 hashes, and generator/oracle/runner/replay source identities before recomputing the verdict.

The resumed partial package contained a corrupt/truncated gzip archive. `generate_fixture.py` now reconstructs the full VO08, metadata, and all candidate PCM from explicit constants. Its 3,146,248 raw bytes hash to `c2ef07b3c35f45a46564c8fc10ed37d31c555ef09b2cb8effab848c76ba9672b`; deterministic gzip is 3,496 bytes and hashes to `c32431807fe713a3054d15283dc81ec2a0d3d08eabe3fd50e3feeaccc98b7ac4`. These are the hashes the existing authenticated manifest already declared, so the repair restored intended bytes without changing the oracle or golden expectations.

## Verification of the verifier

`make -C tests/playback_draft8 check` passes deterministic regeneration, DRAFT-8/package authentication, fixture-derived candidate PCM, all three conforming synthetic observations, and offline replay. Targeted controls reject:

- wrong first frame after seek;
- run-boundary off-by-one;
- reverse `max_pos-1`/grid drift;
- callback I/O during render;
- wrong public `tape_seek` target;
- altered fixture, candidate PCM, or authenticated spec bytes;
- missing/tampered evidence; and
- tampered verifier source identity.

The saved bundle at `tests/playback_draft8/evidence/p1-r2-synthetic/` replays 3/3 PASS. It is explicitly synthetic and establishes only that the independent package and evidence path work.

## Boundary, holds, and next owner

No product engine source, implementation diff, private implementer tests, or uncovered PR discussion was inspected. No product adapter was executed. Rate ramps; zero/one-frame/extreme-rate cases; side switching; warm descriptors; recording; crash/recovery; long operations/state; performance; and human listening are excluded.

The candidate PCM is not a frozen or accepted WP-11 golden until Michael performs the separately issued human-listening step. PR #20 remains held for uncovered behavior. WP-10 operations, remaining WP-11, WP-12a, hardware/card qualification, fabrication, charging, purchases, and Michael-approval holds remain unchanged.

Next owner is PM: review this immutable verifier return. Any product execution/import and Michael listening require separate workflow assignments; Verification stops here.
