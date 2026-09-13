# P1-R10-V — corrected complete-playback product-bundle disposition

**Date:** 13 September 2026 UTC  
**Issue:** `mmsanders/digital-tape-verification#9`  
**Disposition:** **ACCEPT — narrowly, for the ten recorded product-observation families**  
**Next owner:** PM

## Authority and exact inputs

This return performs only the bounded disposition assigned in issue #9. Verification
worked from the frozen public contracts, WP-08, the already-authored corrected
complete-playback package, and the committed raw evidence. Product engine/firmware
source, Software-owned adapter/probe source, Software's narrative return, private
tests, and the discarded diagnostic oracle were not inspected or executed.

- Product main: `d52730ffb4c9d8e634eded9caca208dcacb0d046`
- Verifier main/source commit: `62b18deb8b4fbe6e797b00d792ee9f46ac0a8059`
- Held product PR #64 head/evidence commit: `c18aa42579ef7c5ea92a4d70972d6a2daa6698bb`
- Code-under-test commit: `5f44b97fe9fb3342fce3b58236a75ea27b4898a6`
- Corrected package tree: `6dbb23bb4626238b0f22427031a551d2ece454fd`
- Evidence path: `docs/verification/runs/2026-09-13-r9/product-evidence/`
- Evidence tree: `34bad4611b6849ed586c7ec701fa7ddafef0cb12`
- Evidence manifest SHA-256: `02900981cbdd19cb4b0b8a92bd1e56687acad44cf69ef77233ac1eef950d5461`
- Raw observation SHA-256: `24a35a3cd5a8364d1909f0ee3e0a90d196b4c1afdedfb3bf9d38d34c775e7ce4`
- Saved result SHA-256: `1fb3437a3fffb668ce92e3e6391f4d06d1ead07b8b24889a0264c9fe0d75f742`
- Frozen DRAFT-8 SHA-256: TapeFS `3bffa0ec...47cbb`, Engine API
  `537eadc4...e3a1`, acceptance `7f78fba7...b6b7`
- WP-08 SHA-256: `ff519e960ed3db6e401baebd12f33d5527f83f0e4dfec12484f498470198a96a`

Issue #9 was open with the exact `verification-lead` label and had update timestamp
`2026-09-13T16:21:38Z` when taken. Its only comment was Verification's start notice;
there was no PM/Michael scope update.

## Identity and immutability authentication

The corrected package tree resolves to the same exact Git tree
`6dbb23bb4626238b0f22427031a551d2ece454fd` at product main, PR #64 head, and
verifier main. The evidence manifest names verifier source commit `62b18deb...` and
that same package tree. Every staged `input/package` file is byte- and mode-identical
to its corresponding file in that tree. The stage intentionally contains the
run/replay inputs, not verifier-only `Makefile`, `_synthetic_adapter.py`, `selftest.py`,
or retained synthetic evidence; no common file differs.

The complete evidence manifest binds all 30 non-manifest files. Independent
enumeration found neither an unbound file nor a missing file, and recomputed SHA-256
for every entry matched. Commit `5f44b97...` is the sole parent of evidence commit
`c18aa425...`, so the named code-under-test predates and is an ancestor of the
committed run without relying on implementation content.

Manifest and observation agree on `adapter.kind=product` and adapter ID
`software-lead-complete-playback-public-api-probe-v1`. Source/build declarations are
present and hash-bound. The retained execution is `outcome=exited`, exit code 0,
`output/adapter-exit.txt` is exactly `0\n`, and stderr is empty.

## Commands and results

Run from clean detached worktrees at the exact commits above:

```text
git rev-parse <ref>:tests/playback_complete_draft8
# product main, PR #64 head, verifier main -> 6dbb23bb...54fd

git rev-parse c18aa425...:docs/verification/runs/2026-09-13-r9/product-evidence
# 34bad4611b6849ed586c7ec701fa7ddafef0cb12

git merge-base --is-ancestor 5f44b97... c18aa425...
# exit 0

diff -qr <evidence>/input/package tests/playback_complete_draft8
# only verifier-only Makefile, _synthetic_adapter.py, selftest.py, and evidence/
# are absent from the staged input; no shared-file difference

python3 tests/playback_complete_draft8/generate_fixture.py
# PASS deterministic corrected P1-R8 fixture/candidate regeneration

python3 tests/playback_complete_draft8/selftest.py
# SELFTEST PASS: 10 corrected families; 20 behavioral controls including
# F-1/F-2/F-3; retained 18-control P1-R4 package; evidence controls

python3 tests/playback_complete_draft8/replay.py \
  <product>/docs/verification/runs/2026-09-13-r9/product-evidence
# REPLAY PASS
```

An independent raw-JSON audit, separate from `replay.py`, enumerated and rehashed
the complete manifest, checked product adapter agreement and retained exit, checked
all callback indices/records, and walked every scrub row, service sequence and render
subdivision. It passed. Forward scrub used 16 rates, 116 service calls and 698 render
calls; reverse scrub used 16 mirrored rates, 24 service calls and 698 render calls.
Both rendered 88,200 frames. Every callback was a successful positive-count read
associated only with `tape_mount` or `tape_service`; none was associated with render,
seek, rate, status, info, tell, side-switch, or unmount.

## Ten-family raw disposition

| Family | Public calls | Callbacks | Rendered frames | Narrow observation result |
|---|---:|---:|---:|---|
| `empty_zero` | 6 | 8 | 0 | requested 4, `TAPE_OK`, position 0, end only |
| `empty_nonzero` | 6 | 8 | 0 | requested 4 at +1x, `TAPE_OK`, position 0, end only |
| `nonempty_zero` | 7 | 14 | 0 | interior position 1234 retained, neither endpoint |
| `one_intmax` | 7 | 12 | 1 | one-frame clamp at `INT32_MAX`, end only |
| `reverse_zero` | 7 | 15 | 1 | frame 0 emitted, position 0, start only |
| `intmin` | 8 | 15 | 2 | frames 1 then 0 at `INT32_MIN`, position 0, start only |
| `scrub_forward` | 832 | 110,698 | 88,200 | exact 16-row positive WP-08 schedule and PCM match |
| `scrub_reverse` | 741 | 8,608 | 88,200 | exact mirrored schedule/end snap and corrected PCM match |
| `side_playing` | 14 | 16 | 2 | A endpoint then B frame 0; pre-service result 18/0 frames |
| `side_idle` | 11 | 15 | 1 | B reset then B frame 0; pre-service result 18/0 frames |

For the seven PCM-bearing families, the saved result has `match=true`, exact expected
and actual SHA-256 equality, and frame counts 1, 1, 2, 88,200, 88,200, 2 and 1,
respectively. The saved result is byte-for-byte equal to a fresh oracle result.
The three stopped/empty families correctly produce no PCM and are accepted from their
raw call/state observations. No finding identifier is opened.

## Separated conclusions

- **Verifier-package correctness:** remains green for the exact corrected tree:
  deterministic regeneration, all ten synthetic families, 20 current controls,
  retained P1-R4 package and 18 controls, evidence controls, and saved replay pass.
- **Product-result correctness:** **accepted only for the ten families and exact raw
  evidence above.** The recorded public observations, callback legality, state,
  results and seven PCM byte streams satisfy the corrected independent oracle.
- **PCM/golden status:** scrub PCM remains verifier-derived candidate material,
  unlistened and not a WP-11 golden. This return does not authorize listening or
  golden acceptance; WP-11 remains red.
- **Implementation/merge status:** no source review or implementation-wide acceptance
  occurred. PR #20 and PR #64 remain draft and held. This return grants no merge.

Uncovered recording, crash/recovery, warm-start, state/operation, performance and
hardware/card behavior remain excluded. Frozen hashes and test-first order remain.
Card purchase/qualification, fabrication, charging, safety and Michael-reserved
approvals remain held. PM is the next owner for review and any separately authorized
routing; issue closure records Verification's stop, not PM acceptance.
