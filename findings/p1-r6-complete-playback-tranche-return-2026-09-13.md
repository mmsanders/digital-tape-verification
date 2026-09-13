# P1-R6-V complete playback boundary and scrub tranche return

**Status: Ready for PM review.** Independent Verification completed the bounded
authorship assignment from verifier issue #7. This is a verifier package and saved
synthetic plumbing result only; no product implementation, product adapter, product
run, or listening result was inspected or produced.

## Authenticated inputs and package relationship

- Product input: `mmsanders/Digital-Tape@06f383d3901884a017d5c32316c71b575b6936bf`.
- PM table: `docs/PACKAGES/WP-08.md`, SHA-256
  `ff519e960ed3db6e401baebd12f33d5527f83f0e4dfec12484f498470198a96a`.
- Frozen hashes remain TapeFS `3bffa0ec46d7ba3779b02cbee6fac1edaf5094553f78270ee379759655147cbb`,
  Engine API `537eadc423e1a7bde726d689206b8fe93bef164d57e48e8ff71e07eaf8a7e3a1`,
  acceptance `7f78fba7b66b4fc6e96d15399c62468249bb30fbccbb59bf9f57b4532f56b6b7`.
- Preserved parent package: verifier publication `7a22cbb4447c40c51b7c8b2282a685ed30a46ba6`,
  `tests/playback_draft8/` tree `ff810814dbc8079c6903e6f85ed7ee312abd3076`. No existing source,
  fixture, evidence, candidate PCM or finding path was changed.
- New sibling source: commit `54789cc6e6bbfd942857374e2e0b3305d05d2f2c`,
  `tests/playback_complete_draft8/` tree
  `5527547b72b3e5c6d6fb91d41f3aa3bfa86fab7d`.

## Delivered coverage

Ten families cover zero-frame rendering at zero and nonzero rate; stopped non-empty
rendering without drift; one-frame `INT32_MAX`; reverse from zero; `INT32_MIN` without
wrap; exact forward and mirrored reverse scrubs; and side switch from Playing and
idle. The oracle verifies all public results, status/tell/info outputs, complete
callback traces, every table rate, 128-plus-remainder subdivision, finite
service-to-completion, endpoint state, retained rate, cleared position/flags/warm
state, invalidated ring, pre-service underrun and absence of stale-side PCM.

The long Side-A fixture has 1,100,000 frames. Each scrub candidate has 88,200 stereo
s16le frames. Key generated SHA-256 values:

- `long.vo08.gz`: `39603c2c6b44a12a82cf8df9dd43cf529cdc3bad8bcebd642b29ba863cb40c2b`;
  `one.vo08.gz`: `985dd4e22beb9671be88b1d94695cfb28beae7949245195d0810e392d76bf73f`;
  `empty.vo08.gz`: `95cc2ee3d7c72d42a53ffae9b74c52b21733b492eaa80a4cf06ae0c68655c6af`.
- forward scrub PCM: `41e882e74e3c64d929fcc76ad47b52f72ce9ed1541e971497b3c9a04fb46006b`;
  reverse scrub PCM: `faae5cf894f9a7b2d84e9f9c99a36184ddd776e3cdc6de734e935c4f35f4f5d6`.
- saved synthetic manifest: `30682e71f9b44debaff9d893d36b915ff201208ebffb74bc0dda0158528ea840`;
  saved result: `84df717b7ade7b0365428933c0ab4879f9653a967cb6edff8c17b2cc46243c75`; evidence tree:
  `c67ea8fa128e06393839f968ae3cc949d84e5f2a`.

## Reproduction and controls

- `python3 tests/playback_complete_draft8/generate_fixture.py`: PASS, deterministic
  fixture and PCM reproduction with exact product-input authentication.
- `python3 tests/playback_complete_draft8/selftest.py`: PASS, 10 families and 16
  new named behavioral mutations; retained P1-R4 three families and 18 controls;
  kind/identity, tamper, exit, timeout, retention and replay controls also pass.
- `python3 tests/playback_complete_draft8/replay.py
  tests/playback_complete_draft8/evidence/p1-r6-synthetic`: PASS.
- `make -C tests check`: PASS for the full verifier suite after registering the new
  package. CI workflow now includes the sibling package.

The named new mutations catch empty-check ordering, stopped-position drift,
`INT32_MAX` overshoot, reverse-zero skip, `INT32_MIN` wrap, wrong Q16.16 rate,
wrong row render count, wrong reverse start, service-time cadence drift,
Playing-side refusal, retained side position/endpoint/warm state, lost retained
rate, stale Side-A PCM and render-time I/O.

## Exclusions, holds and next owner

No product implementation/adapter/run inspection or execution; no product result,
golden/listening acceptance, warm-descriptor negative, recording, crash/recovery,
long-operation/state-matrix completion, performance, hardware/card, purchase,
fabrication, charging or frozen-spec change. Candidate PCM remains unaccepted.
All existing safety, coverage, purchase and Michael-reserved holds remain in force.

PM owns authentication/disposition and any exact mechanical import. Software may
later plumb the public adapter and produce held product evidence; independent
Verification and Michael's separately issued listening step remain required before
any WP-11 golden acceptance.
