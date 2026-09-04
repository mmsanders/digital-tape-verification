# WP-11 golden-suite and mutation plan — DRAFT-5

Status: runner, fixture policy, diagnostics, golden families, and all seven mutation targets are defined. Byte-exact playback fixtures must not be frozen until the DRAFT-5 reverse phase, C99 promotion, warm-pointer, and exhaustive-proof findings are dispositioned (V5-005/V5-006/V5-007/V5-012).

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

- 1.0x playback from stream start and immediately after seek, final-frame `b = a`, run boundaries ±1, exact start/end, and reverse. The reverse-from-end fixture uses a non-linear multi-frame signal so a one-subframe phase shift cannot hide behind a constant last sample.
- Every scrub-rate table value as an instantaneous `tape_set_rate` input; firmware owns the time ramp.
- Maximum positive/negative rates on one-frame and short timelines, specifically covering V4-009.
- Overwrite, overdub, and splice at t=0, mid-run, exact run boundary, and end.
- Overdub extrema: `32767+32767`, `-32768+-32768`, opposite signs, and one-LSB boundaries.
- Warm-start matches and independent descriptor-NULL, data-NULL, UUID, side, start, end, zero-length, byte-short, and overflow mismatches.
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

- V5-005: reverse from `max_pos` snaps to a subframe rather than the last frame position, shifting all later −1.0× samples.
- V5-006: `b - a` occurs before the widening cast and is undefined on a 16-bit-`int` C99 target.
- V5-007: optional warm metadata is dereferenced before the NULL guard and a NULL data pointer can pass validation.
- V5-012: the claimed full-domain exhaustive gate is approximately 5.63×10^14 pairs and has no finite construction/proof rule.

Stable overwrite saturation fixtures, the verifier's mathematical floor-division oracle, and a finite all-delta/five-boundary-phase sweep can proceed independently. That sweep is evidence, not a claim to satisfy V5-012's undefined full-domain gate.
