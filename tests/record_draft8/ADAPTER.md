# WP-09 mechanical adapter contract

The adapter calls only the frozen **public API** and exposes public-call plus
block-device observations. It is not a product API and must not expose engine
internals or private allocator state.

## Invocation

`wp09_rec_probe CASE_ID INPUT.vo08 OUTPUT.vo08`

Exit 0 only when the scripted calls completed and final VO08 media was written.
Stdout is one JSON object:

```json
{
  "format": "WP09-REC-OBSERVATION-1",
  "adapter_kind": "product",
  "calls": [],
  "events": []
}
```

`adapter_kind` is `product` or `synthetic`. Every public call appends one ordered
`calls` object with `phase`, `fn`, symbolic `result`, and the fields the script
depends on (`side`, `frame`, `mode`, `accepted`, `more_work`, `rate_q16_16`).
`tape_feed` also reports `events_from_call` — the number of block callbacks
raised during that one public call, which must be 0.

Every block callback appends, in order:

`{"phase":"...","op":"read|write|flush","lba":N,"count":N,"rc":0}`

Flush omits `lba/count`. The wrapper records every callback; it must never
filter observations to make a verdict pass.

## Shared fixture

60-second nominal tape. Derived `total_chunks = 21`. Medium is 23,553 blocks.
Live A0 sequence 10, structurally valid A1 at 700 with `side=1` (invalid for A),
live B0 `[(0,0,256)]` at sequence 20, B1 empty. `a_high_water == free_next == 3`.
`cartridge_sequence == 700`. Mount Side B, `warm == NULL`.

## Scripts

All cases start:

1. fresh instance; `tape_mount(B)`;
2. `tape_seek(CASE.seek)`;
3. `tape_arm(CASE.mode)`.

Then:

- `WP09-*-MID/END/T0` with `feed > 0`: `tape_feed` exactly `feed` frames;
  `tape_service` until `more_work == false`; `tape_commit`; unmount; remount B.
- `WP09-EMPTY-COMMIT`: `tape_commit` immediately after arm; require `TAPE_OK`;
  unmount; remount B. Zero block events.
- `WP09-ARMED-BUSY`: after arm, `tape_seek(0)` and `tape_set_rate(1.0×)` must
  both return `TAPE_ERR_BUSY`; `tape_abort`; unmount. Zero block events.

Modes: overwrite cases use `TAPE_REC_OVERWRITE`, overdub `TAPE_REC_OVERDUB`,
splice `TAPE_REC_SPLICE`.

## Permitted integration edits

Only mechanical include/header/library paths and a sparse `tape_dev` wrapper.
Do not change fixtures, expected entries, arguments, accepted results, callback
classification or oracle assertions to fit a product build.
