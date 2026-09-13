# P1-R8-V corrected complete-playback package return

**Status: Ready for PM review.** Verification completed issue #8's bounded F-1/F-2/F-3
package correction. The result is an independently re-derived verifier publication and
saved synthetic plumbing evidence only. No product implementation, product adapter,
Software return, held product observation, diagnostic scratch oracle, or PR #64 source
was inspected or run.

## Immutable inputs and identities

- Product decision main: `mmsanders/Digital-Tape@add1a255607720d71f62688ece8d9036d40fba82`.
- Input verifier main: `121f5f7ab03c9ce08c38329e518c49a1ca9b65a5`; input complete
  publication tree: `863b3a49c421bda1bebcf1a9760149bec7051048`.
- Corrected pre-evidence source commit: `1c1489a5b1c10f2baa8425557fd7bdfde3225575`;
  `tests/playback_complete_draft8/` source tree:
  `43ca6f6bbc1990d5ced6de3b2ce0d04f00aa7519`.
- Corrected retained synthetic evidence tree:
  `d867fc68c80a2217508868c4b339d160b55ec2cc`; complete published package tree:
  `6dbb23bb4626238b0f22427031a551d2ece454fd`.
- Frozen SHA-256 remain TapeFS
  `3bffa0ec46d7ba3779b02cbee6fac1edaf5094553f78270ee379759655147cbb`,
  Engine API `537eadc423e1a7bde726d689206b8fe93bef164d57e48e8ff71e07eaf8a7e3a1`,
  and acceptance `7f78fba7b66b4fc6e96d15399c62468249bb30fbccbb59bf9f57b4532f56b6b7`.
  PM WP-08 remains
  `ff519e960ed3db6e401baebd12f33d5527f83f0e4dfec12484f498470198a96a`.
- The earlier `tests/playback_draft8/` tree remains
  `ff810814dbc8079c6903e6f85ed7ee312abd3076`. The prior complete publication and
  P1-R6 evidence remain preserved in Git history; their evidence tree remains
  `c67ea8fa128e06393839f968ae3cc949d84e5f2a` at its existing path.

The final publication commit is the commit containing this return. Its exact hash is
recorded in issue #8's immutable return comment together with the tree identities above.

## Exact corrections and targeted controls

- **F-1:** `intmin` now expects two emitted stereo frames, frame 1 followed by frame 0,
  then tell 0 and `at_start = true`. The named control
  `F-1 dropped frame 0 / at_start set on landing step` rejects the one-frame trace
  produced by either dropping frame 0 or setting `at_start` on the landing step.
- **F-2:** reverse scrub now starts at `((total_frames - 1) << 32)`. The named control
  `F-2 DRAFT-5 off-grid reverse snap candidate` reconstructs the old `max_pos - 1`
  candidate and proves that the corrected oracle rejects it byte-for-byte.
- **F-3:** both short pre-service side renders now require
  `TAPE_ERR_UNDERRUN = 18`. Separate Playing and idle controls substitute integer 6
  (`TAPE_ERR_GEOMETRY`) and are caught.

No unrelated expected value, tolerance, case, assertion, frozen input, fixture, or
earlier-package byte changed. Supporting source, adapter-contract, coverage, package,
runner/replay identity, and synthetic-model text changed only to implement and bind
these three corrections and their P1-R8 provenance.

## Generated-file before/after hashes

All six generated candidate/fixture paths were regenerated deterministically. Only the
PM-authorized reverse candidate changed.

| Generated path | Before SHA-256 | After SHA-256 | Disposition |
|---|---|---|---|
| `candidate/scrub-forward.pcm` | `41e882e74e3c64d929fcc76ad47b52f72ce9ed1541e971497b3c9a04fb46006b` | same | unchanged |
| `candidate/scrub-reverse.pcm` | `faae5cf894f9a7b2d84e9f9c99a36184ddd776e3cdc6de734e935c4f35f4f5d6` | `5f1794e8dcd7c1b3e2c390a1aef33039f5b88b20f682c56c4aa6f94051bd8fa1` | authorized grid-snap regeneration |
| `fixtures/empty.vo08.gz` | `95cc2ee3d7c72d42a53ffae9b74c52b21733b492eaa80a4cf06ae0c68655c6af` | same | unchanged |
| `fixtures/fixture.json` | `625d215b97168c06875c9f263582673bcc44f0463cedec2875cf8e004bbb4859` | same | unchanged |
| `fixtures/long.vo08.gz` | `39603c2c6b44a12a82cf8df9dd43cf529cdc3bad8bcebd642b29ba863cb40c2b` | same | unchanged |
| `fixtures/one.vo08.gz` | `985dd4e22beb9671be88b1d94695cfb28beae7949245195d0810e392d76bf73f` | same | unchanged |

The corrected synthetic `intmin.pcm` is two frames with SHA-256
`d844e1554b5c802b4cc27c59d7503f3117296f7928d3d24dc87679a3e32a27dd`.
The saved evidence manifest is
`1dc7ae2fa44d95403dd410b10ea7872e2b84aa2d0c2a8e45c3dfb3d8974f198d`;
saved result is
`1fb3437a3fffb668ce92e3e6391f4d06d1ead07b8b24889a0264c9fe0d75f742`.

## Reproduction

- `python3 tests/playback_complete_draft8/generate_fixture.py`: PASS; all six checked-in
  generated paths match deterministic regeneration.
- `python3 tests/playback_complete_draft8/selftest.py`: PASS; all ten corrected families,
  20 behavioral controls including named F-1/F-2/F-3 controls, retained P1-R4 three
  families and 18 controls, and evidence identity/tamper/exit/timeout/retention controls.
- `python3 tests/playback_draft8/selftest.py`: PASS; retained earlier package unchanged.
- `python3 tests/playback_complete_draft8/replay.py
  tests/playback_complete_draft8/evidence/p1-r8-synthetic`: PASS; saved offline replay.
- `make -C tests check`: PASS; full verifier suite.

The saved observation covers all ten families and records zero adapter exit. All
candidate PCM and evidence in this return are **synthetic, unlistened, and unaccepted**.

## Exclusions, holds, and next owner

This return makes no product-conformance, engine, adapter, PCM-golden, listening,
WP-08, WP-11, card, hardware, purchase, fabrication, charging, or safety acceptance.
PR #20 and PR #64 remain draft and held. Frozen specifications, test-strengthening,
golden/listening, purchase/qualification, fabrication, charging, and Michael-reserved
approval holds remain unchanged.

PM is the next owner: authenticate and disposition the corrected verifier publication,
then decide whether Software receives a fresh rerun issue. Issue closure records only
that Verification stopped at its assigned boundary.
