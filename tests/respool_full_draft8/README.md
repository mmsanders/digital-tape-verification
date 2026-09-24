# Full re-spool DRAFT-8 verifier

Independent verifier-first publication for Digital-Tape-Verification issue #72:
full WP-12 re-spool shapes, exhaustive WP-10 pass crash durability, counter
boundaries, and the re-spool row of WP-12a.

## Frozen inputs

- Digital-Tape: `45c08bd7e25aeb6ca858faf4d30d139999f8dbd7`
- Digital-Tape-Verification: `fe432ffac622b9d9e9c68e566d2cb9881f2aee62`
- TapeFS: `3bffa0ec46d7ba3779b02cbee6fac1edaf5094553f78270ee379759655147cbb`
- engine-api: `537eadc423e1a7bde726d689206b8fe93bef164d57e48e8ff71e07eaf8a7e3a1`
- acceptance: `7f78fba7b66b4fc6e96d15399c62468249bb30fbccbb59bf9f57b4532f56b6b7`

The package pins the previously published independent
`tests/respool_draft8/oracle.py` by Git blob SHA
`3c63f190e87915f410a199128e1a08590b8ee6bd`; it does not import product code.

## Contents

- `planner.py` — canonical 22,562-case crash manifest and SHA-256.
- `fixture.py` — verifier-owned clean/crash fixtures, raw data digests and the
  pinned narrow-oracle loader.
- `oracle.py` — independent metadata selection, disjoint-destination,
  bit-identity, pass-2 live-copy, state-matrix and FAULTED contract checks.
- `selftest.py` — positive synthetic controls plus required red controls.
- `reproducer.py` — exact JSON failure-retention format.
- `ADAPTER.md` — later product-binding boundary; raw observations only.
- `COVERAGE.md` — exact frozen criteria, counts, exclusions and two API
  non-applicabilities.

## Run

```sh
python3 tests/respool_full_draft8/selftest.py
```

The repository workflow `.github/workflows/verifier-package-selftests.yml`
(**Verification package selftests**, job **verifier package selftests**) discovers
`tests/*_draft8/selftest.py` automatically, so this publication needs no workflow
modification.

Expected planner output:

- cases: **22,562**
- flush_required: **11,281**
- write_through: **11,281**
- canonical case-set SHA-256:
  `bc3e4cff6f61888faf9c5b97ccd136e9fec4417ef9cab4a46d084b4aae7ec444`

This package is not product acceptance. Software must first import the immutable
publication under Structural Rule 1 and provide raw observations through
`ADAPTER.md`; independent Verification then disposes that evidence.
