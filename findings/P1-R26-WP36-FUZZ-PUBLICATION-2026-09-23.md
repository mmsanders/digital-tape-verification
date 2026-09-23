# P1-R26 Verification return — WP-36 100,000-sequence fuzz publication

Date: 23 September 2026  
Authority: independent Verification, issue #54  
Product implementation source/diff inspected: **no**  
Product modified: **no**

## Disposition

**PUBLISHED — independent verifier package ready for Software import/binding.**

Verification has authored and published the dedicated WP-36 random transport
source-slot fuzz package at:

`tests/wp36_fuzz_draft8/`

The package publication commit is:

`c65df73abaf2624e99ac3c06b8c864a445d81ec2`

and the immutable package subtree is:

`9ac9c43962b49c98f7007983921be9500a51cb5a`

This round does **not** constitute WP-36 product acceptance. No Digital-Tape
product code was modified or executed by Verification for this publication.
The next step is a separate Software import/binding under Structural Rule 1,
followed by independent Verification disposition of the resulting exact
real-product evidence.

## Normative inputs / blindness

The package was derived from the frozen public specifications at integrated
Digital-Tape main:

`e6606d0e9c5f5fcc77a8bab9fefba8e3be483d15`

using:

- TapeFS §4.3 effective writability;
- Engine API §3.1 NULL-write capability / debug `dev_write` instrument;
- Engine API §§5–6 and §10 public transport/state semantics;
- Acceptance WP-36;
- the already-published `slot_draft8` five-case package only as a deterministic
  precursor and boundary reference.

Frozen spec SHA-256 identities:

- `tapefs-v1.md`:
  `3bffa0ec46d7ba3779b02cbee6fac1edaf5094553f78270ee379759655147cbb`
- `engine-api.md`:
  `537eadc423e1a7bde726d689206b8fe93bef164d57e48e8ff71e07eaf8a7e3a1`
- `acceptance.md`:
  `7f78fba7b66b4fc6e96d15399c62468249bb30fbccbb59bf9f57b4532f56b6b7`

Verification did not inspect product `engine/` implementation while deriving
or tuning the package.

## Frozen acceptance target

The exact target remains:

> Fuzzing over 100,000 random transport input sequences against a source-slot
> device with `write == NULL` produces zero calls to `dev_write` on that
> device. The debug assertion never fires.

The package operationalizes this as a fail-closed process boundary: the future
product adapter has literal `dev.write = NULL`, the product engine must be
built with the frozen debug write assertion active, and any attempted internal
`dev_write` therefore kills the product process. Process death, assertion,
signal, nonzero exit, timeout, premature EOF or malformed output is a verifier
failure.

A non-NULL write wrapper that merely counts, rejects or swallows writes is
explicitly nonconforming.

## Generator / reproducibility

The verifier owns the generator. The production runner exposes no sequence-count
or seed override.

Fixed generator identity:

- algorithm: `splitmix64-v1`;
- master seed: `0x5730365a5eed2026`;
- sequence count: **exactly 100,000**;
- sequence length: 8–32 random public operations;
- exact total operation census: **1,997,914**;
- canonical full-plan SHA-256:
  `6a6637336eff798e6c7824af76e3d4f227eefcd9ff35e7850a14fd14a1d22bae`.

Each sequence has its own deterministically derived 64-bit seed and is
independently reproducible by sequence index. A product failure retains the
exact failing index, seed and operation list as a compact reproducer instead of
committing a massive raw 100,000-sequence transcript.

## Random transport alphabet

Every sequence starts from a fresh successful mount of a valid non-empty
read-only source fixture on Side A or Side B and finishes by unmounting.

The public input alphabet is:

- `tape_seek`;
- `tape_tell`;
- `tape_set_rate`;
- `tape_render`;
- `tape_service`;
- `tape_status`;
- `tape_get_info`;
- `tape_set_side`.

This is deliberately transport/state input rather than randomized recording or
long-operation mutation. The deterministic precursor already exercises mounted
read-only mutator refusals; WP-36 specifically calls for random transport input
sequences.

## Exact generated coverage census

The fixed 100,000-sequence plan contains:

### Mount side

- A: 49,965
- B: 50,035

### Operation counts

- info: 250,140
- render: 249,525
- seek: 249,810
- service: 248,859
- set_rate: 249,690
- set_side: 249,768
- status: 249,711
- tell: 250,411

### Transport-state exposure at generated calls

- stopped: 875,044
- playing forward: 562,886
- playing reverse: 559,984

### Rate classes

- zero: 31,288
- positive: 78,001
- negative: 77,827
- `INT32_MAX`: 31,257
- `INT32_MIN`: 31,317

### Seek classes

- in range: 132,562
- exact end: 31,629
- beyond end: 85,619

### Side switching

- target A: 125,346
- target B: 124,422
- cross-side flips: 125,172
- same-side successful set requests: 124,596

The generator also varies render frame counts and service block budgets and
asserts that every required operation/state/rate/seek/side class is actually
present in the committed plan. Minimum and maximum sequence lengths (8 and 32)
are both exercised.

## Product-adapter contract

The later product adapter is a persistent process invoked by the verifier-owned
runner. It must attest and mechanically satisfy:

- `adapter_kind=product`;
- source write binding is literal `NULL`;
- debug assertion mode is active.

The verifier streams the exact generated plan to the adapter. The adapter may
not independently regenerate randomness, skip calls based on expected results,
change operation arguments, or reorder the sequence.

For each sequence it must:

1. start a fresh engine instance over the original verifier fixture;
2. bind the source with literal `dev.write = NULL`;
3. mount the verifier-selected A/B side at resume frame 0 with `warm == NULL`;
4. execute every generated operation in exact order;
5. return compact callback/result counters;
6. unmount;
7. reset for the next sequence.

The response must prove the exact sequence identity and number of operations
executed. Callback-counter overflow is fail-closed.

Generated transport calls may return only `TAPE_OK` or the documented
`TAPE_ERR_UNDERRUN` render result in this tranche. Any other operation result
fails the run.

After sequence 99,999, the adapter must exit normally. Any crash/assertion
during the stream fails the run and the verifier retains the current sequence
as the reproducer.

## Verifier self-tests / negative controls

The package self-test proves:

1. the committed generator produces exactly 100,000 sequences;
2. its exact full-plan digest and 1,997,914-op census reproduce;
3. arbitrary sequence index/seed reproduction is deterministic;
4. the streaming protocol completes for a conforming synthetic adapter;
5. an injected synthetic assertion/crash is rejected and the exact failing
   sequence is retained;
6. a non-NULL source-write binding is rejected;
7. a 99,999-sequence evidence summary is rejected;
8. malformed/missing RNG provenance is rejected;
9. a non-NULL binding in final evidence is rejected.

## Repository CI

Final authoritative package CI:

- workflow run: `35893019118`
- job: `107289899345`
- package publication commit:
  `c65df73abaf2624e99ac3c06b8c864a445d81ec2`
- package tree:
  `9ac9c43962b49c98f7007983921be9500a51cb5a`
- conclusion: **SUCCESS**

The job log independently records:

- `PASS deterministic 100000-sequence generator 6a6637336eff798e6c7824af76e3d4f227eefcd9ff35e7850a14fd14a1d22bae 1997914`
- `PASS sequence reproducer determinism`
- `PASS streaming protocol smoke`
- `PASS assertion/crash negative control`
- `PASS non-NULL source-binding negative control`
- `PASS fewer-than-100000 negative control`
- `PASS malformed provenance negative control`
- `PASS summary source-binding negative control`
- `PASS all WP-36 fuzz package self-tests`

### First CI attempt and repair

The first package CI run, `35892698339` / job `107288830758`, correctly
failed before publication readiness.

Cause: the verifier self-test invoked its synthetic Python adapter as an
executable file. Local development had executable permission set, but GitHub's
contents-backed publication checked the file out as mode `100644`, producing
`PermissionError`.

This was a verifier packaging/portability defect, not an acceptance failure.
Verification corrected only `selftest.py` to create a temporary executable
proxy that invokes the synthetic Python adapter. The generator, production
runner, adapter contract, RNG, seed, sequence count, plan digest and all
acceptance conditions were unchanged. The resulting package tree is the final
tree identified above.

## Package contents

The immutable package contains:

- `README.md` — scope, normative inputs, generator identity, usage;
- `ADAPTER.md` — exact later Software binding protocol and NULL/assertion
  requirements;
- `COVERAGE.md` — assertion matrix and explicit exclusions;
- `generator.py` — verifier-owned SplitMix64 plan generator and census;
- `fixture.py` — deterministic valid A/B source fixture;
- `runner.py` — fixed 100,000-sequence fail-closed production runner;
- `selftest.py` — generator/protocol/negative controls;
- `synthetic_adapter.py` — verifier-harness self-test fixture only.

## Structural Rule 1 handoff

The next Software task must import **this exact package tree** into Digital-Tape
before writing the product binding.

The verifier import and product binding/adapter must remain separate commits as
required by Structural Rule 1. Software may adapt include/link paths and supply
the mechanical protocol implementation; it may not modify the verifier
generator, runner, fixture, expected count, seed, digest or acceptance logic to
fit product behavior.

After exact real-product execution, Verification must independently authenticate
and disposition that evidence. A green Software run by itself is not acceptance.

## Explicit exclusions

This publication does not accept or re-test:

- the already-dispositioned deterministic five-case `slot_draft8` precursor;
- real-product WP-36 behavior;
- random edit sequences / WP-07 allocator fuzz;
- recording semantics beyond the deterministic read-only precursor;
- WP-10 crash/durability testing;
- long-operation continuation, argument stability, re-entry, progress or
  FAULTED-state behavior;
- PCM/golden/listening acceptance;
- complete source/helper/package acceptance beyond this published fuzz harness.

## Stop condition

Issue #54's Verification-authoring task is complete when this package and return
are published. Closure means the independent 100,000-sequence verifier is ready
for Software import/binding. It does **not** mean WP-36 product acceptance.
