# P1-R27 Verification return — independent WP-13 embedded-readiness package publication

Date: 23 September 2026
Authority: independent Verification, issue #58

## Publication disposition

**PASS — independent verifier package published and self-tested.**

This round is verifier authorship only. It is **not WP-13 product acceptance**.

The package was authored from the frozen DRAFT-8 public specifications before
inspecting the current product engine implementation. No Digital-Tape product file was
modified in this round.

## Frozen inputs

Authoring integration point:
`e4a356586fd67d118868ba457e26d2c9805e7c7a`

Authenticated DRAFT-8 hashes:
- `spec/tapefs-v1.md`:
  `3bffa0ec46d7ba3779b02cbee6fac1edaf5094553f78270ee379759655147cbb`
- `spec/engine-api.md`:
  `537eadc423e1a7bde726d689206b8fe93bef164d57e48e8ff71e07eaf8a7e3a1`
- `spec/acceptance.md`:
  `7f78fba7b66b4fc6e96d15399c62468249bb30fbccbb59bf9f57b4532f56b6b7`

## Immutable package

Path:
`tests/embedded_readiness_draft8/`

Final package publication commit:
`82847985cd41e2b4b2fc086079ead7e5f2f7669e`

Immutable package tree:
`46c8aa37f1f882e6a371fae7cdb5b96a28ada109`

Published files:
- `ADAPTER.md`
- `COVERAGE.md`
- `README.md`
- `instance_size_probe.c`
- `oracle.py`
- `runner.py`
- `selftest.py`

The publication diff from verification main
`d8fb31b2a3a5fbf5555b19c2158f5727114186bb` contains only those seven package
files.

## Exact six-gate coverage

The package defines exactly the frozen WP-13 criteria:

1. **WP13-G1 — RAM sum**
   `.data + .bss + tape_instance_size() <= 204800 bytes`.
   The verifier-owned `instance_size_probe.c` calls the public
   `tape_instance_size()` API; the oracle recomputes the sum and emits the measured
   instance size explicitly.

2. **WP13-G2 — read-only data**
   `.rodata <= 32768 bytes`, with compiler-equivalent read-only data families
   retained rather than silently dropped.

3. **WP13-G3 — allocator symbols**
   Complete engine undefined-symbol inventory with allocator/free references forbidden.

4. **WP13-G4 — stack**
   Complete function-level engine call graph plus compiler stack usage, maximum path
   <= 8192 bytes. Unknown/unbounded frames, unresolved internal edges and recursion
   fail closed.

5. **WP13-G5 — indirect-call confinement**
   Complete source/call classification with exactly three permitted indirect callback
   funnels:
   `dev_read/read`, `dev_write/write`, `dev_flush/flush`, all in
   `engine/src/dev.h`. Extra or ambiguous indirect calls fail.

6. **WP13-G6 — caller-owned mutable state**
   Every engine object/archive member is classified by ELF symbol type and section
   writability. Any engine-defined mutable OBJECT/TLS symbol or COMMON symbol fails,
   including local file/function statics. Read-only constants/tables are allowed.

The machine-readable result keeps the six rows independent and reports per-gate
measurements, limits and errors rather than collapsing them into one opaque verdict.

## Fail-closed evidence contract

The later product binding must retain exact product/verifier identities, complete build
logs, raw section/symbol reports, stack-usage and call-graph files, engine source hash
inventory, and exact tool versions.

The binding must not:
- omit engine objects/functions/sources;
- replace the verifier-owned instance-size probe;
- mark incomplete graph/symbol/source scans complete;
- suppress allocator or mutable-symbol findings;
- add indirect-call whitelist exceptions;
- change thresholds or classifications.

For stack analysis, a graph whose bound is unknowable is a failure, not a guessed pass.

For invariant 19, numeric RAM headroom cannot excuse even a tiny mutable engine-owned
global/static.

## Verifier self-test

GitHub Actions:
- workflow run: `35948597098`
- job: `107472008051`
- conclusion: **success**

Exact package self-test output includes:

- PASS conforming six-gate evidence
- PASS RAM-sum negative control
- PASS rodata negative control
- PASS allocator-symbol negative control
- PASS stack-bound negative control
- PASS incomplete-stack negative control
- PASS indirect-call negative control
- PASS engine-owned-state negative control
- PASS malformed-provenance negative control
- PASS callback-funnel completeness negative control
- PASS all WP-13 embedded-readiness package self-tests

This demonstrates every required gate can go red and that key completeness/provenance
boundaries fail closed.

## Later Software binding contract

Software should import exact tree
`46c8aa37f1f882e6a371fae7cdb5b96a28ada109` byte-for-byte under Structural Rule 1.

Software may then add only mechanical build/evidence collection glue that produces
`WP13-EMBEDDED-EVIDENCE-1` as specified by `ADAPTER.md`. The exact product evidence
is evaluated by verifier-owned `runner.py`.

A Software green is evidence, not self-acceptance. Independent Verification must audit
the exact raw evidence and binding before WP-13 acceptance.

## Acceptance boundary

If later exact product evidence passes all six rows and independent Verification
authenticates the binding/raw evidence, this package is intended to be sufficient for
**complete frozen WP-13 package acceptance** unless a spec-grounded missing criterion
is discovered.

No additional frozen WP-13 criterion was identified during this authorship round.

## Explicit exclusions

This package does not test or accept:
- runtime functional behavior;
- PCM/audio/goldens/listening;
- WP-07 allocator ownership/edit fuzz semantics;
- WP-10 crash/durability behavior;
- WP-12 or WP-12a operation semantics;
- firmware/hardware measurements;
- performance beyond the six WP-13 resource/structure gates;
- any unrelated work package.

Issue #58 may close as completed once this publication PR is ready for PM review.
