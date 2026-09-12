# P1-R4-V — playback evidence identity and retention correction

## Disposition

Issue #5's bounded verifier correction is **ready for PM review**. Replay now binds
the manifest adapter kind/ID to the observation, requires declared adapter
source/build provenance and a retained zero-exit record, and the runner no longer
deletes a pre-existing evidence directory. Adapter execution is time-bounded and
timeout/nonzero-exit diagnostics are retained. No playback assertion, fixture,
candidate PCM, spec byte, family, or exclusion changed.

| Provenance | Exact value |
|---|---|
| Issue | `mmsanders/digital-tape-verification#5`, observed update `2026-09-12T22:34:49Z` |
| PM-assigned product input | `91268789cc5a5026baa9bb7e3120671626897a74` |
| Activation-time product main used for current role/workflow docs only | `20aa6bbcf886d8f87b4e34c4af4afb0c091703fc` |
| Assigned verifier input | `48be424c5b5959c6e87c645a49ecc33a7026a30a` |
| Corrected verifier source commit | `d565403907ecea331a5dcf63efbd1c08d8bd732e` |
| Corrected `tests/playback_draft8/` source tree | `aaa6dde86c9a0bdffa2b375361049ac670e26467` |
| Saved synthetic evidence | `tests/playback_draft8/evidence/p1-r4-synthetic/` |
| Saved evidence manifest SHA-256 | `b915e44b65e293fe9765b3437b2491ee297136cf6561e2010cc50c3d048d61ed` |

The publication commit containing this return and saved evidence is recorded in
the immutable issue return because a Git commit cannot contain its own hash.

## Corrected contract and controls

- Evidence schema is `playback-draft8-evidence-v2`, assignment `P1-R4-V`. The old
  P1-R2 v1 bundle remains historical and is not silently upgraded.
- Runner arguments require nonempty adapter command, ID, source declaration, build
  declaration, verifier source commit, and verifier source tree. The manifest
  records the synthetic/product kind, adapter ID, source/build declarations,
  timeout, outcome, and exit code. A readable adapter source file also gets a
  SHA-256 record.
- Source/build/commit/tree strings are **declared provenance**, not authenticated
  commits merely because they are nonempty. The immutable repository commit and
  tree above are the external verifier-source evidence for this return.
- Replay requires a valid synthetic/product kind, nonempty adapter ID/source/build,
  successful execution with exit code zero, exact `output/adapter-exit.txt` value
  `0\n`, complete file hashes, and exact manifest/observation adapter kind and ID
  agreement before recomputing all three family verdicts.
- The runner accepts only a missing or empty evidence destination. A nonempty
  directory fails before any write; a byte-bearing sentinel control proves the
  original directory remains the only entry with identical bytes.
- Adapter execution defaults to a finite 60-second timeout. Actual nonzero-exit
  and timeout controls retain stdout, stderr, `adapter-exit.txt`, `result.json`,
  execution metadata, and the hash-bound manifest, return failure, and cannot pass
  replay.

The reproduced manifest-only `synthetic` to `product` relabel and adapter-ID change
now both fail replay. Missing adapter source/build, missing exit, nonzero exit,
timeout, missing evidence, tampered evidence, and verifier-source hash drift also
fail. A conforming synthetic bundle still replays all three families PASS.

## Executed verification

From repository root:

```text
python3 tests/playback_draft8/generate_fixture.py
  PASS checked-in fixture and candidate PCM equal deterministic generator

python3 tests/playback_draft8/selftest.py
  PASS three families + identity/exit/provenance/replay/retention controls

make -C tests check
  PASS strict-C99 fault-block, crash-harness, and audio-oracle tests
  PASS existing VT8 operation package and controls
  PASS corrected playback package and controls

python3 tests/playback_draft8/replay.py \
  tests/playback_draft8/evidence/p1-r4-synthetic
  REPLAY PASS: forward_1x, seek_boundaries, reverse_neg1x
```

The generated source evidence records zero exit and `outcome: exited`. It is
explicitly synthetic; no product adapter or engine ran.

## Byte preservation and scope

`package.json`, the compressed/raw VO08 fixture, fixture metadata, all three
candidate PCM files, and authenticated DRAFT-8 spec copies are byte-identical to
verifier input `48be424c...`. Key retained hashes are:

| Artifact | SHA-256 |
|---|---|
| Raw VO08 | `c2ef07b3c35f45a46564c8fc10ed37d31c555ef09b2cb8effab848c76ba9672b` |
| Deterministic VO08 gzip | `c32431807fe713a3054d15283dc81ec2a0d3d08eabe3fd50e3feeaccc98b7ac4` |
| Forward PCM | `750b7dfb75de2d9b75ba337393e3285e2ca02de23d7be609303505b096a424f8` |
| Seek PCM | `a79ea302572d626d46dbf2662f3fb18666b2ddb03843c2b1ef51042736597cda` |
| Reverse PCM | `15e64de5ceb9cf99ad87ea45db0b1ce7ceba65594506d8e2634d9471247049d7` |

Coverage remains exactly +1.0x forward, first-frame-after-seek for the eight issued
targets, and -1.0x reverse from end. Rate ramps; zero/one-frame/extreme rates; side
switching; warm descriptors; recording; crash/recovery; long operations/state;
performance; product execution; and human listening remain excluded.

No product engine/source/diff/private tests, product import, implementation-based
oracle material, or product observation was inspected or executed. This correction
does not accept the candidate PCM, WP-08/WP-11 as a whole, PR #20, or any hardware,
card, fabrication, charging, purchase, safety, or Michael-reserved decision.

Next owner is PM: reproduce the immutable package/evidence and review the bounded
correction. Issue closure records that Verification stopped, not correctness or
acceptance.
