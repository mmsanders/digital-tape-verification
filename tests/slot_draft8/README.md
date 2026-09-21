# WP-36 — independent DRAFT-8 source-slot tranche

`dev.write == NULL` is a source slot. Engine API §3.1: the mount is not
effectively writable; every mutator returns `TAPE_ERR_READ_ONLY` and the
device must see zero writes. Acceptance WP-36 asks for that property under
transport-input fuzz; this tranche publishes the deterministic public-API
core the fuzzer must not violate.

| ID | Script |
|---|---|
| `WP36-SRC-A` | mount A, info.writable==false, seek/set_rate/render/service, zero writes |
| `WP36-SRC-B` | same on Side B |
| `WP36-SRC-MUTATORS` | arm / reset_b / promote / respool all `TAPE_ERR_READ_ONLY`, zero writes |

```sh
python3 tests/slot_draft8/selftest.py
```

Not covered: 100 000-sequence fuzzer execution, debug-assertion wiring on a
real `dev_write`, v1.1 version-minor barrier (WP-06a). Synthetic green is
not package acceptance.
