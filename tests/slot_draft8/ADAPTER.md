# WP-36 mechanical adapter contract

`wp36_slot_probe CASE_ID INPUT.vo08 OUTPUT.vo08`

The adapter device **must** have `write == NULL`. A wrapper that swallows
writes is a defect. Stdout:

```json
{"format":"WP36-SLOT-OBSERVATION-1","adapter_kind":"product","calls":[],"events":[]}
```

Mount the requested side with `warm == NULL`. Record every block callback.
Playback cases may render a small fixed count. Mutator case must invoke
`tape_arm`, `tape_reset_side_b`, `tape_promote` and `tape_respool`.
