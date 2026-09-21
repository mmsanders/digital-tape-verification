# WP-12 — independent DRAFT-8 re-spool tranche

Verifier-owned package from TapeFS §9.4 and Engine API §9 / acceptance WP-12.
No product implementation was inspected. Not package acceptance.

Four public-API cases:

| ID | Script |
|---|---|
| `WP12-EMPTY` | empty Side B → `TAPE_OK`, `more_work=false`, zero writes; same fixture `tape_promote` → `TAPE_ERR_INVALID_ARG` |
| `WP12-TWOPASS` | V3-003 worked example: H=10, B spans chunks 10–11; pass 1 `[12,14)`, pass 2 `[10,12)` |
| `WP12-FULL` | no pass-1 destination → `TAPE_ERR_CARTRIDGE_FULL`, zero writes |
| `WP12-DEGRADED` | equal-sequence B → `TAPE_ERR_NO_VALID_INDEX`, zero writes |

```sh
python3 tests/respool_draft8/selftest.py
```

Exclusions: bit-exact PCM identity after respool, crash injection, WP-12a
continuation matrix, stage-1 clearing, sequence-exhaustion branches other
than the empty zero-needed row implicit in EMPTY. Synthetic green is not
product acceptance.
