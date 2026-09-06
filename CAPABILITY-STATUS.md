# Capability status — surge DRAFT-8 second cut

Date: 6 Sep 2026

This is the current Verification Lead status snapshot. Canonical product specs remain `mmsanders/Digital-Tape` `main`; the DRAFT-8 material below is an authenticated **surge candidate**, not a claim of PM issuance. Historical pass details remain under `findings/` and `PM-NOTES.md`.

| Area | Status | Evidence / boundary |
|---|---|---|
| Verification publication point | **Current** | Completed verifier findings/status land on `digital-tape-verification/main`; review branches are not authoritative publication points. |
| Surge second-cut authentication | **Complete** | Supplied TapeFS, engine API, and acceptance hashes exactly match the supplied DRAFT-8 manifest and PR #25 packet: `22dca615…35a7`, `537eadc4…e3a1`, `3c764724…0d53`. |
| Second-cut adversarial review | **Complete; one candidate major remains** | `findings/surge-draft8-second-cut-review.md` records **0 blockers, 1 major, 1 documentation/coverage question**. |
| Phase-0 freeze gate | **Not yet met** | `V8R2-001` is a major touching candidate §4.6. The standing gate requires zero blockers and zero majors in the candidate sections. |
| V7-001 cartridge-survival blocker | **Still closed** | Partner-first/candidate-last ordinary superblock updates, stale-partner repair, and the two-interruption closure criterion are unchanged. No repeated-interruption rollback was found. |
| V8C-001 pre-read geometry | **Fixed in normative text** | `DEVICE_ADDRESSABLE` runs before mount callbacks; format/duplicate geometry is checked before destination superblock classification. `V8R2-002` asks only for tighter WP-06 coverage of the zero-callback promise. |
| V8C-002 generation identity boundary | **Fixed** | Step-1 WIP remains in the increasing generation domain; final format/duplicate identity assignment establishes a new cartridge and resets `sb_generation = 1`. TapeFS, invariant 7, and WP-10 agree. |
| V8C-003 equal-generation-divergent raw media | **Ordinary path fixed; exhaustion edge open** | With generation headroom, the v1 WIP template gives a singular `INCOMPLETE` result once the first partner write is durable. `V8R2-001` identifies the remaining `sb_generation >= 0xFFFFFFFD` zero-both fallback, where a first durable zero leaves the arbitrary primary as sole candidate but §4.6/crash tables still claim `INCOMPLETE`/old unchanged. |
| WP-10 | **Not final-testable as written** | The mandated generation-exhausted equal-generation-divergent raw-destination boundary remains non-singular (`V8R2-001`). Generic crash infrastructure and undisputed cases may proceed. |
| WP-11 | **Testable as written** | Golden arithmetic/portability requirements remain coherent and unchanged. |
| WP-12a | **Testable as written** | Callback exemptions, 45-cell/33-B accounting, BUSY persistence, destination-failure return-to-Playing, and FAULTED override remain coherent. |
| Hardware safety audit | **Contract auditable; no result yet** | Procedure, instrument/calibration, ambient conditions, raw readings, derivation, and measurement uncertainty remain required. No raw measurement package was reviewed in this round. |
| Crash-injection infrastructure | **Complete below implementation adapter seam** | Verifier-owned torn-write/flush-failure/power-cut infrastructure remains independent of engine implementation. |
| Implementation blindness | **Preserved** | This pass did not inspect `engine/`, implementation branches/diffs/issues, PR #20 implementation details, or unlanded implementation artifacts. |

## Current verifier work that may proceed

- Keep WP-11 oracle/golden work moving from independent expectations.
- Continue generic WP-10 harness and all undisputed cases, including the V7-001 two-interruption closure.
- Exercise WP-12a state-matrix/re-entry/FAULTED cases independently.
- Prepare hardware-audit procedure/checklists while waiting for measurement packages.

## Current stop conditions

- **Do not recommend Phase-0 signature** until `V8R2-001` is corrected and the exact resulting candidate bytes receive another independent pass.
- **Do not treat a paper-clean DRAFT-8 candidate as a green WP-10.** Operations and the state matrix still freeze only after the actual WP-10 run is green against a singular oracle.
- **Do not unblock or merge implementation PR #20 from verification** until verifier-authored tests and the PM process authorize that review boundary.
- Do not inspect engine implementation to resolve normative ambiguities.
