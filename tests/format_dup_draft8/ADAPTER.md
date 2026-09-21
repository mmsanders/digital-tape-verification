# Mechanical adapter contract

`wp_fmt_dup_probe CASE_ID INPUT.vo08 OUTPUT.vo08`

Stdout one JSON object:

```json
{"format":"WP-FMTDUP-OBSERVATION-1","adapter_kind":"product","calls":[],"events":[]}
```

Scripts:

- format cases call only `tape_format` against the named dest constraints.
- dup cases mount the source on Side A, call `tape_dup` once with a positive
  budget, require `more_work==false` on the refusal, unmount. Destination is
  a raw `tape_dev`, not a second mount.
- `PROMOTE-EMPTY` mounts Side B, one `tape_promote` with positive budget,
  requires `TAPE_ERR_INVALID_ARG` and `more_work==false`.

Do not change fixtures or expected results to fit a product build.
