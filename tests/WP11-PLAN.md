# WP-11 golden-suite and mutation plan — DRAFT-4

Status: runner, fixture policy, diagnostics, golden families, and all seven mutation targets are defined. Candidate fixture generation may begin, but byte-exact playback fixtures must not be frozen until V4-010/V4-013 settle sample phase and portable negative interpolation.

## One-command runner

`make -C tests check` builds and runs the strict-C99 verifier infrastructure. The same target will run media-oracle, golden, property, crash-session, and mutation checks so local and CI behavior remain identical.

## Fixture policy

- Every fixture manifest records stable ID, purpose, nominal length, source seed/provenance, frame count, SHA-256, listening status, listener/date, and PM approval reference.
- Candidate generation is separate from acceptance fixtures. Only a human-listened candidate may be promoted to committed acceptance status.
- The normal runner consumes fixtures and cannot regenerate them.
- Regeneration requires an explicit maintenance command plus logged PM approval; CI rejects a fixture hash change without that approval.
- C-60, C-90, and C-120 parameters are exercised; no global constant assumes one length.

## Byte-exact diagnostics

On a PCM mismatch, emit first differing frame/channel, expected/actual values, signed delta, differing-sample count, peak absolute delta, and an audible-difference WAV, plus fixture ID, target, seed, and replay command. There is no tolerance.

## Golden families

- 1.0x playback from stream start and immediately after seek, final-frame `b = a`, run boundaries ±1, exact start/end, and reverse.
- Every scrub-rate table value as an instantaneous `tape_set_rate` input; firmware owns the time ramp.
- Maximum positive/negative rates on one-frame and short timelines, specifically covering V4-009.
- Overwrite, overdub, and splice at t=0, mid-run, exact run boundary, and end.
- Overdub extrema: `32767+32767`, `-32768+-32768`, opposite signs, and one-LSB boundaries.
- Warm-start matches and independent UUID, side, start, end, zero-length, and overflow mismatches.
- File-backed/service-ring rendering byte identity.

## Mutation gate

Each mutation is applied independently and must make the suite fail for the intended reason:

1. Run end off by one.
2. Index header committed before the chunk flush.
3. Sequence not incremented.
4. CRC over the wrong byte range.
5. Side B allocation/write one chunk below `a_high_water`.
6. Overdub saturation replaced with a narrowing cast.
7. Warm-start accepted for the wrong `(uuid, side, frame range)`, including a wrapped range endpoint.

## Current freeze boundary

- V4-010 must specify whether the current position is fetched before or after advancement; otherwise seek goldens differ by one frame.
- V4-013 must replace implementation-defined negative signed shift with portable floor arithmetic or constrain every supported compiler.
- V4-011 must define checked warm-range containment before mutation 7 has one normative oracle.

Stable overwrite saturation fixtures and runner/diagnostic code can proceed independently of those three points.
