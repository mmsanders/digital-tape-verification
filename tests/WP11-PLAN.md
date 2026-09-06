# WP-11 golden-suite and mutation plan — DRAFT-6

Status: **WP-11 is testable as written.** The DRAFT-6 directed adversarial pass found no defect in `engine-api` §§6.2, 6.3, or 8. The reverse transport phase, endpoint lifecycle, widening order, and floor-interpolation identity survived independent numerical traces. Golden PCM is therefore eligible to be frozen **only through the existing fixture policy**: generated once from independent expectations, listened to by a human, committed, and changed only with logged PM approval. Implementation output is never the oracle.

## One-command runner

`make -C tests check` is the verifier entry point. The same target must run media-oracle, arithmetic differential, golden, property, crash-session, and mutation checks so local and CI behavior are identical.

## Fixture policy

- Every committed fixture records stable ID, purpose, nominal length, source seed/provenance, frame count, SHA-256, listening status, listener/date, and PM approval reference.
- Candidate generation is separate from acceptance fixtures. The engine-under-test may be compared with a fixture but must never generate its own expected bytes.
- Only a human-listened candidate may be promoted to committed acceptance status.
- Normal CI consumes fixtures and cannot regenerate them.
- Regeneration requires an explicit maintenance command plus logged PM approval; CI rejects an unexplained fixture-hash change.
- C-60, C-90, and C-120 parameters remain exercised; no global constant assumes one tape length.

## Independent PCM arithmetic oracle

`audio_oracle.c` implements the verifier formulation, not the engine formulation:

- overdub widens both signed 16-bit operands before addition and clamps to `[-32768, 32767]`;
- interpolation computes the signed 64-bit product independently and explicitly converts C99 truncation toward zero into mathematical floor for a negative non-integral quotient;
- expected transport positions and endpoint events are generated from the normative fixed-point state transition, not by calling engine helpers.

The DRAFT-6 review independently traced at least:

- `[0, 1000, 2000]` from end at −1.0× → `2000, 1000, 0`;
- the same timeline at −0.5× and −2.0×;
- zero- and one-frame timelines;
- `INT32_MAX` and `INT32_MIN` rate boundaries;
- reverse from zero and endpoint stop behavior;
- positive and negative interpolation deltas around every integer/fraction boundary used by the portability gate.

No finding is filed against §§6.2, 6.3, or 8 in DRAFT-6.

## Portability gate

Full-domain equivalence is supplied by the proof in `engine-api` §8. The executable gate is finite and exact:

1. Cross **all 131,071** values of `b - a` in `[-65535, 65535]` with
   `f ∈ {0, 1, 2, 0x40000000, 0x7FFFFFFE, 0x7FFFFFFF, 0x80000000, 0x80000001, 0xC0000000, 0xFFFFFFFD, 0xFFFFFFFE, 0xFFFFFFFF}` — **1,572,852 pairs**.
2. Add **10,000,000** pairs from a committed seeded PRNG stream.
3. Add explicit int16-extreme pairs, including `b = 32767, a = -32768` and the negation.
4. Compare every result byte-exactly with independently computed `floor(d / 2^32)` behavior.
5. Require green on at least two toolchains, one the embedded target and at least one configuration that makes integer-promotion assumptions visible.

A finite executable sweep is evidence supporting the proof; it is not described as literal enumeration of the approximately `5.6 × 10^14` full `(delta,f)` domain.

## Golden families

- 1.0× from stream start and immediately after seek; run boundaries ±1; exact start/end; final-frame `b = a`.
- Reverse from end on a **non-linear multi-frame** signal so a one-subframe phase shift cannot hide behind a constant sample; include −0.5×, −1.0× and −2.0×.
- Every scrub-rate table value as an instantaneous `tape_set_rate` input; firmware owns the time ramp.
- Maximum positive/negative rate on one-frame and short timelines.
- Overwrite, overdub, and splice at t=0, mid-run, exact run boundary, and end.
- Zero-accepted-frame commit in all three record modes, with byte-identical pre/post index and preserved tail.
- Overdub extrema: `32767+32767`, `-32768+-32768`, opposite signs, and one-LSB boundaries.
- Warm-start valid match plus descriptor-NULL, data-NULL, UUID, side, start, end, zero-length, byte-short, and checked-overflow mismatches.
- File-backed/service-ring rendering byte identity.

`acceptance.md` WP-08's side-switch regression is currently defective under `V6-005`; that is a WP-08/state-transition issue, not a defect in WP-11's arithmetic portability or fixture mechanism. Do not silently rewrite that unreachable setup into a golden expectation.

## Byte-exact diagnostics

On mismatch emit first differing frame/channel, expected and actual samples, signed delta, differing-sample count, peak absolute delta, fixture ID, target/toolchain, seed/replay command, and an audible-difference WAV. There is no tolerance.

## Mutation gate

Each mutation is applied independently and must fail for the intended reason:

1. Run end off by one.
2. Index header committed before chunk flush.
3. Sequence not incremented.
4. CRC over the wrong byte range.
5. Side B allocation/write one chunk below `a_high_water`.
6. Overdub saturation replaced by a narrowing cast.
7. Warm-start accepted for the wrong `(uuid, side, frame range)`, including wrapped range arithmetic, **plus `warm == NULL` and valid metadata with `data == NULL`** as separate pointer cases.

Any mutation the suite does not catch is a verifier coverage finding, not permission to weaken the mutation.

## Freeze boundary

For DRAFT-6, the specific PM condition on `engine-api` §§6.2, 6.3 and 8 is satisfied by this adversarial pass. The verifier can now construct/listen/promote the byte-exact PCM fixtures without consulting engine implementation. This does **not** imply Phase-0 spec signature: `findings/spec-review-draft6.md` contains six majors in the broader freeze candidate, and that candidate remains held.
