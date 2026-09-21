# WP-12 mechanical adapter contract

`wp12_respool_probe CASE_ID INPUT.vo08 OUTPUT.vo08`

Stdout one JSON object:

```json
{"format":"WP12-RESPOOL-OBSERVATION-1","adapter_kind":"product","calls":[],"events":[]}
```

Shared geometry: 60 s, 21 chunks, 23 553 blocks. Mount Side B, `warm == NULL`.

Scripts:

1. `WP12-EMPTY` — `tape_promote` (expect `TAPE_ERR_INVALID_ARG`, `more_work=false`), then `tape_respool` with positive budget until `more_work=false` (expect `TAPE_OK` on the first call, zero events).
2. `WP12-TWOPASS` — repeat `tape_respool` with a small positive budget until `more_work=false`. Must terminate.
3. `WP12-FULL` / `WP12-DEGRADED` — one `tape_respool`; expect the named refusal; zero writes.

`block_budget == 0` is not used here (WP-12a). Do not change fixtures or expected destinations.
