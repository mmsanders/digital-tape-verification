# WP-09 — independent DRAFT-8 record tranche

Verifier-owned package authored from the frozen DRAFT-8 contract without
inspection of product implementation. It covers eight public record families
plus six refusal/abort rows and is **not** full WP-09 / WP-11 acceptance.

Normative DRAFT-8 SHA-256 values:

- TapeFS `3bffa0ec46d7ba3779b02cbee6fac1edaf5094553f78270ee379759655147cbb`
- Engine API `537eadc423e1a7bde726d689206b8fe93bef164d57e48e8ff71e07eaf8a7e3a1`
- Acceptance `7f78fba7b66b4fc6e96d15399c62468249bb30fbccbb59bf9f57b4532f56b6b7`

Frozen geometry is the same 60-second / 21-chunk / 23,553-block medium used by
`tests/ops_draft8/`.

## Cases

| ID | Script |
|---|---|
| `WP09-OW-MID` | seek 128, overwrite 64 frames |
| `WP09-OW-END` | seek 256, overwrite 64 frames (append) |
| `WP09-OD-MID` | seek 128, overdub 64 frames |
| `WP09-SP-T0` | seek 0, splice 64 frames |
| `WP09-SP-MID` | seek 128, splice 64 frames |
| `WP09-SP-END` | seek 256, splice 64 frames (append) |
| `WP09-EMPTY-COMMIT` | arm overwrite, commit with zero accepted frames |
| `WP09-ARMED-BUSY` | seek and set_rate while armed must be BUSY |
| `WP09-RO-SIDE-A` | mount A, arm → `TAPE_ERR_READ_ONLY` |
| `WP09-SEQ-EXHAUSTED` | `cartridge_sequence = 0xFFFFFFFD`, arm → `TAPE_ERR_SEQUENCE_EXHAUSTED` |
| `WP09-INDEX-FULL` | 4096 live-B entries, splice-arm → `TAPE_ERR_INDEX_FULL` |
| `WP09-CART-FULL` | `free_next == total_chunks`; arm OK; feed short-accept 0 |
| `WP09-ABORT-DISARM` | arm, abort, zero writes |
| `WP09-STAGE-REFUSE` | `promote_stage = 1` + exhaustion; refusal leaves stage |

## Self-test

```sh
python3 tests/record_draft8/selftest.py
```

A synthetic green run is package evidence only. It is not product acceptance
and not a listened golden.

See `COVERAGE.md` for the assertion/exclusion matrix and `ADAPTER.md` for the
product-adapter contract. Next owner after publication: Software, for a
mechanical public-API adapter on a two-commit tranche branch, then independent
disposition of raw product observations. Do not merge this branch onto
verification `main` without Michael/PM/Verification review.
