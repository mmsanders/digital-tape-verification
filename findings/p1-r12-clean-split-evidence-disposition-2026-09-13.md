# P1-R12-V clean-split evidence disposition

**Disposition: BLOCKED for playback; narrowly ACCEPTED for the exact mount
observations.** Ready for PM review. One finding, `P1-R12-V01`, prevents acceptance
of the playback observation and exposes a verifier-package coverage defect. No
product, adapter or probe source was inspected.

## Inputs and identity

- Issue: `digital-tape-verification` #10, observed open with label
  `verification-lead`, updated `2026-09-13T20:21:04Z` before work began.
- Current product main at activation: `26d7cebc735b897cccec4185d75c5c64100b81fd`.
  Product main named by the issue: `f1213430d10d4c0b62d173af532135daf56aca58`.
- Verifier input/main: `17d345ef23a9bbdb3e781f3451f4a8797a1a6f1c`.
- Exact evidence commit: `f100937aed1437401218003db3edbb07d8e4f543`,
  with sole parent `86eb3b77756042c365e2d0353018b981c39c99e8`.
  That pre-run commit has sole parent / assigned clean base
  `6a8b2fb481cf43a8d84aad6c74336fc4a2a50d96`. Git timestamps place the
  pre-run commit at `2026-09-13T17:28:08Z` and the evidence child at
  `2026-09-13T17:31:40Z`. Neither held head `2e0e8a4b...` (#20) nor
  `c18aa425...` (#64) is an ancestor of the pre-run commit.
- The exact run, product-evidence and staged-package trees reproduce as
  `a6c1dfeb1e35399301adcabf5adc90ef0e067307`,
  `1671bcb37abccb21cb59234792ba35e984a3eb5f`, and
  `b097c2a91fabf55677c9a7f866020d22d83ee90e`. Product
  `tests/playback_complete_draft8/` and verifier publication
  `62b18deb8b4fbe6e797b00d792ee9f46ac0a8059` both resolve to tree
  `6dbb23bb4626238b0f22427031a551d2ece454fd`.
- All 18 staged verifier files agree with that publication by mode and blob.
  The evidence manifest binds exactly 30 files: no bound path is missing, no
  unbound path is present, and every file hash matches.
- Manifest, observation, result and mount-log SHA-256 values match the issue:
  `c243b1dd...37a`, `24a35a3c...7ce4`, `1fb3437a...f742`, and
  `0d753bf8...319d`. The three frozen DRAFT-8 hashes and WP-08
  `ff519e96...a96a` also match.

## Verifier-package correctness

The unmodified corrected package authenticates and its existing self-test, 20
named controls, retained P1-R4 controls and saved synthetic replay all pass. The
unmodified offline replay of the exact product bundle also reports `REPLAY PASS`.
Those green results do not establish package correctness because the current scrub
oracle implements a weaker call schedule than authenticated WP-08.

### P1-R12-V01 — scrub oracle and evidence omit per-render service

**Acceptance blocker; verifier-owned package defect and product-observation defect.**

Authenticated `input/WP-08.md` requires, within every scrub row, a
`tape_service(block_budget=1024)` sequence ending in `more_work == false` **before
every render request**. Each direction contains 698 render requests: 35 in each of
rows 0–14 and 173 in row 15.

The package oracle instead accepts one completed service sequence after each rate
change and then all of that row's render requests. The exact product trace follows
that weaker schedule:

| Family | Rate rows | Service calls | Render calls | Rendered frames | Render calls without an immediately preceding completed service |
|---|---:|---:|---:|---:|---:|
| `scrub_forward` | 16 | 116 | 698 | 88,200 | **682** |
| `scrub_reverse` | 16 | 24 | 698 | 88,200 | **682** |

The differing service-call totals are permitted because a completion sequence can
take different numbers of calls. The 682 omissions per direction are not: only the
first render in each row is preceded by a service call whose `more_work` is false.
Consequently replay is green while accepting traces that violate the exact PM-issued
call vector. The two scrub observations and the complete ten-family playback bundle
are rejected for acceptance at this commit.

## Exact playback observation

Apart from `P1-R12-V01`, the raw observation audit found no mismatch:

- the case set is exactly the ten assigned families;
- adapter kind/ID agree between manifest and observation; source/build declarations
  are present; outcome is `exited`, exit is zero, and stderr is empty;
- every recorded callback is ordered, in device range, a successful positive-count
  read, and attached only to `tape_mount` or `tape_service`; no render, seek, rate,
  status, info, tell or side-switch callback appears;
- empty/zero-rate, `INT32_MAX`, reverse-zero, corrected `INT32_MIN`, side-switch,
  position, endpoint, warm-state and underrun-result fields match the public contract;
- all 16 signed Q16.16 rates and per-row output counts match WP-08, and each scrub
  direction records 88,200 rendered frames;
- all seven PCM-bearing outputs match independently reconstructed verifier bytes:
  1, 1, 2, 88,200, 88,200, 2 and 1 frames respectively; and
- saved `result.json` exactly matches the package's recomputed result.

These facts do not cure the missing service cadence. Candidate PCM remains
verifier-derived, unlistened and unaccepted; it is not a WP-11 golden. A corrected
oracle, exact re-import, fresh trace and new independent disposition are required.

## Exact mount observation

The landed independent mount package authenticates and all ten package checks pass.
The exact raw log contains one provenance record plus 289 unique cases in package
order. Fixture hashes, allowed results, stdout parsing, callback accounting/ranges,
stored errors and stored PASS/FAIL fields all match independent recomputation:
**289 pass, 0 fail**.

The row-3 boundary cases are:

| Exact case | Expected / actual result | Writes | Flushes | Chunk reads | Disposition |
|---|---:|---:|---:|---:|---|
| `M-stage-row3-side0` | `0` / `0` | 0 | 0 | 0 | PASS |
| `M-stage-row3-side1` | `0` / `0` | 0 | 0 | 0 | PASS |
| `M-stage-unmatched-row3-H-boundary` | `8` / `8` (`TAPE_ERR_INCONSISTENT`) | 0 | 0 | 0 | PASS |

This narrowly accepts the exact 289 recorded mount observations, including the
§9.3.3 row-3 shape and strict `H > len` negative. It accepts neither the extracted
helper design nor allocator, complete WP-06/WP-08, implementation or merge status.

The mount log itself authenticates adapter executable bytes as SHA-256
`57b8274e2bff7f3d597211ae1a7072d75b0780a7979f3c1196a8dd6cd0323ed7`.
It does **not** embed a product commit SHA. Association with pre-run commit
`86eb3b777...` is a separate fact supplied by Git parentage and the committed run
packet; executable hash and commit association are not conflated here.

## Commands and results

Executed only against clean archives of public contracts, verifier-owned packages,
raw evidence and Git metadata:

```text
git rev-list --parents -n 1 f100937...  -> sole parent 86eb3b7...
git rev-list --parents -n 1 86eb3b7...  -> sole parent 6a8b2fb...
git ls-tree <exact refs and paths>       -> all five assigned tree identities match
sha256sum <spec/WP-08/evidence/log>      -> every supplied digest matches
mode/blob comparison                    -> 18 checked, 0 mismatches
PYTHONDONTWRITEBYTECODE=1 python3 tests/playback_complete_draft8/selftest.py
                                           -> SELFTEST PASS; 10 families, 20 + 18 controls
PYTHONDONTWRITEBYTECODE=1 python3 input/package/replay.py product-evidence
                                           -> REPLAY PASS
independent raw JSON audit              -> P1-R12-V01; all other playback checks pass
make -C tests/mount_draft8 check        -> 10 tests, OK
independent cases.py/run.check replay   -> 289 pass, 0 fail
PYTHONDONTWRITEBYTECODE=1 make -C tests check
                                           -> full verifier suite PASS
```

## Boundary, holds and next owner

No implementation/firmware, Software adapter/probe source, private test, PR diff or
mixed discussion was inspected or executed. PR #77, #64 and #20 remain draft and
held. Allocator, recording, crash/recovery, warm-start negatives, state/operations,
performance, hardware/card behavior, WP-11 listening/goldens and all
purchase/qualification/fabrication/charging/safety and Michael-reserved approvals
remain excluded and held.

**Next owner: PM.** Route a fresh verifier issue to correct the scrub oracle and add
a negative control that removes a per-render service sequence. After exact mechanical
product import, Software must generate a fresh exact product trace; a new independent
disposition is required before playback acceptance or merge consideration. The
mount-only disposition above is complete at its stated boundary.
