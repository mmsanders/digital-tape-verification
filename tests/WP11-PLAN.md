# WP-11 golden-suite and mutation plan

Status: test architecture defined; fixtures cannot be frozen until the DRAFT-3 arithmetic, state, and format findings are dispositioned.

## One-command runner

`make -C tests check` currently builds and runs the strict-C99 verifier infrastructure. The same target will grow adapters, golden comparisons, properties, crash sessions, and mutation checks so local and CI behavior remain identical.

## Fixture policy

- Every fixture has a manifest containing a stable ID, purpose, nominal length, source seed or provenance, frame count, SHA-256, listening record, listener, date, and PM approval reference.
- Fixtures are committed once. The normal runner can consume but cannot regenerate them.
- Regeneration requires an explicit maintenance command plus a logged PM approval; CI rejects a fixture hash change without the matching approval record.
- C-60, C-90, and C-120 parameters are exercised; no global test constant assumes 90 minutes or 1,817 chunks.

## Byte-exact diagnostics

On the first PCM mismatch the comparator emits:

- first differing frame and channel;
- expected value, actual value, and signed delta;
- total differing samples and peak absolute delta;
- an audible-difference WAV with matching sample rate/channel metadata;
- fixture ID, engine target, seed, and exact command for replay.

There is no numeric tolerance.

## Golden families

- 1.0× playback, final-frame `b = a`, run boundaries ±1, exact start/end, and reverse.
- Every scrub-rate table value, driven as instantaneous `tape_set_rate` calls; firmware owns time/ramp generation.
- Overwrite, overdub, and splice at t=0, mid-run, run boundary, and end.
- Overdub extrema including `32767 + 32767`, `-32768 + -32768`, opposite signs, and one-LSB boundaries.
- File-backed and serviced/ring-buffer rendering must emit identical bytes.

## Mutation gate

The live mutations are:

1. run-end off by one;
2. index header committed before the chunk flush;
3. sequence not incremented;
4. CRC over the wrong byte range;
5. a Side B allocation/write one chunk below `a_high_water`;
6. overdub saturating clamp replaced by a narrowing cast;
7. replacement pending PM disposition of V3-015, because the charter's preroll-cache mutation has no DRAFT-3 target.

Each mutation must be applied independently and must make the suite fail for the intended reason before a phase gate passes.
