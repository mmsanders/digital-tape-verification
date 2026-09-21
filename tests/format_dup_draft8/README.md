# Format / duplicate / empty-promote refusal tranche

Verifier-owned package. Independent of WP-10 crash tables and of the
identity-assignment *success* path. Authored from issued DRAFT-8 TapeFS
§9.5 items 1–4, §9.6 preconditions, and Engine API invariants 18, 22, 30.

Not product acceptance. Not a merge onto verification `main`.

## Cases

| ID | Assertion |
|---|---|
| `FMT-RO` | `write == NULL` → `TAPE_ERR_READ_ONLY`, zero callbacks |
| `FMT-GEOM-0` | `block_count == 0` → `TAPE_ERR_GEOMETRY`, zero callbacks |
| `FMT-GEOM-1` | `block_count == 1` → `TAPE_ERR_GEOMETRY`, zero callbacks |
| `DUP-ALIAS` | dest aliases src → `TAPE_ERR_INVALID_ARG`, `more_work=false`, zero writes |
| `DUP-RO` | dest `write == NULL` → `TAPE_ERR_READ_ONLY` |
| `DUP-GEOM-0` | dest `block_count == 0` → `TAPE_ERR_GEOMETRY`, zero callbacks |
| `DUP-TOO-SMALL` | dest geometry OK, Side A does not fit → `TAPE_ERR_DEST_TOO_SMALL` |
| `PROMOTE-EMPTY` | empty Side B → `TAPE_ERR_INVALID_ARG`, `more_work=false`, zero writes |

```sh
python3 tests/format_dup_draft8/selftest.py
```
