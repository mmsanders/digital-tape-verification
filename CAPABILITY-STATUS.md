# Capability status — DRAFT-8 independent mount tranche

Date: 7 Sep 2026

This is the current Verification Lead status snapshot. Canonical product specs remain `mmsanders/Digital-Tape` `main`; the DRAFT-8 material below is an authenticated **surge candidate**, not a claim of PM issuance. Historical pass details remain under `findings/` and `PM-NOTES.md`.

| Area | Status | Evidence / boundary |
|---|---|---|
| Verification publication point | **Current** | Completed verifier findings/status land on `digital-tape-verification/main`; review branches are not authoritative publication points. |
| Surge third-cut authentication | **Complete** | Supplied TapeFS, engine API, and acceptance hashes exactly match the supplied DRAFT-8 manifest and current PR #25 packet: `3bffa0ec…cbb`, `537eadc4…e3a1`, `7f78fba7…6b7`. |
| Third-cut adversarial review | **Complete; no blocker/major** | `findings/surge-draft8-third-cut-review.md` records **0 blockers, 0 majors, 1 documentation question**. |
| Phase-0 paper gate | **Met on these exact candidate bytes** | Standing threshold is zero blocker and zero major in TapeFS §§1–8 and engine §§2–8, §12. No such finding remains. This is contingent on byte-identical PM issuance/signoff; it is not an official freeze. |
| V7-001 cartridge-survival blocker | **Closed** | Partner-first/candidate-last ordinary superblock updates, stale-partner repair, and the two-interruption closure criterion remain coherent. No repeated-interruption rollback reproduced. |
| V8C-001 pre-read geometry | **Fixed** | `DEVICE_ADDRESSABLE` runs before mount callbacks; raw format/duplicate geometry precedes destination superblock classification; WP-06d now requires zero callbacks at the named phase-0 boundaries. |
| V8C-002 generation identity boundary | **Fixed** | Step-1 WIP increases within the old cartridge; final format/duplicate identity assignment establishes a new cartridge at generation 1 and lies outside the monotonicity span. |
| V8C-003 / V8R2-001 raw divergent media | **Fixed for mechanical oracle** | With headroom, equal-generation-divergent uses the higher-generation v1 WIP template; without headroom, mirror-first zeroing explicitly yields the surviving primary's own mount result after the first zero. TapeFS crash tables and WP-10 agree. |
| V8R3-001 | **Documentation question only** | §4.6's generic post-classification “Then” paragraph should be scoped to branches that actually write a new higher-generation superblock; detailed §9.5/§9.6 behavior is already singular. Not a blocker/major. |
| WP-10 | **Mechanically testable as written; not yet run green** | Required two-interruption closure, two durability modes, counter boundaries, raw divergent/exhausted destinations, format/duplicate final-write states, and per-operation outcome sets are singular on paper. Operations/state freeze still waits for the actual run. |
| WP-11 | **Testable as written** | Golden arithmetic/portability requirements remain coherent. |
| WP-12a | **Testable as written** | Callback exemptions, 45-cell/33-B accounting, BUSY persistence, destination-failure return-to-Playing, and FAULTED override remain coherent. |
| Hardware safety audit | **Contract auditable; no result yet** | Procedure, instrument/calibration, ambient conditions, raw readings, derivation, and measurement uncertainty remain required. No raw measurement package was reviewed in this round. |
| Crash-injection infrastructure | **Complete below implementation adapter seam** | Verifier-owned torn-write/flush-failure/power-cut infrastructure remains independent of engine implementation. |
| Implementation blindness | **Preserved** | This pass did not inspect `engine/`, implementation branches/diffs/issues, PR #20 implementation details, or unlanded implementation artifacts. |

## Independent mount tranche — 7 September 2026

**Ready for mechanical test integration; no engine execution or package acceptance.**
`findings/phase0-mount-tranche-2026-09-07.md` is the PM return. Source, adapter contract,
289 deterministic fixtures, full coverage matrix and raw evidence are in
`tests/mount_draft8/`. Ten package self-tests and the legacy C99 harness pass;
the negative engine control is red and missing-engine execution fails explicitly.

Coverage is mount admission/selection, interval validity, both-side/degraded-B/stage
classification, repair and mount-derived ownership/free space. Allocator decisions,
running sequence consumption, actual writes/edits/reset/recovery, PCM and full WP-07
10,000 random edit sequences remain unaccepted. **VT8-001** documents the public-API
observability dependency. Product main remains DRAFT-7 at the checked head
`ed5efd834aa8f7a96bc8ef811569b2687d919526`; candidate issuance/authentication and
test-first integration remain the acting authority's next steps.

## Current verifier work that may proceed

- Prepare for PM issuance review of these exact candidate hashes; re-authenticate if the PM changes any hashed file.
- Implement/run WP-10 against the issued bundle, including V7-001 two-interruption closure and generation-exhausted equal-generation-divergent raw-destination cases.
- Continue WP-11 independent golden/oracle work.
- Exercise WP-12a state-matrix/re-entry/FAULTED cases independently.
- Prepare hardware-audit procedure/checklists while waiting for measurement packages.

## Current stop conditions

- **Do not call Phase 0 officially frozen until the PM issues/signs a canonical bundle.** The verifier paper threshold is met only for the exact authenticated third-cut bytes above.
- **Do not treat this clean paper pass as a green WP-10.** Operations and the state matrix still freeze only after the actual WP-10 run is green against the issued bytes.
- **Do not unblock or merge implementation PR #20 from verification** until verifier-authored tests and the PM process authorize that review boundary.
- Do not inspect engine implementation to resolve normative ambiguities.