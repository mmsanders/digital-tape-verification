# WP-06a remaining mutator assertion matrix

Mount admission of v1.1 (`writable == false`) already lives in
`tests/mount_draft8/`. This package covers the mutator and repair-skip rows
that package explicitly deferred.

| ID | Assertion | Basis | Control |
|---|---|---|---|
| W06A-A01 | Writable device + valid v1.1 mounts `TAPE_OK` | TapeFS §4.3; Engine API §3.1 | mount result |
| W06A-A02 | `tape_info.writable == false`, `version_minor == 1` | Engine API §3.1, §5 | writable-true mutation |
| W06A-A03 | Torn partner: `needs_repair == true`, zero writes (repair skipped) | TapeFS §4.1 phase 4; WP-06a | needs_repair hidden |
| W06A-A04 | `arm` / `reset_b` / `promote` / `respool` are `TAPE_ERR_READ_ONLY` | Engine API §3.1, §10 W; acceptance WP-06a | arm-allowed |
| W06A-A05 | `feed` / `commit` are `TAPE_ERR_BUSY` (never armed) | Engine API §10 idle row; WP-06a | feed returned READ_ONLY |
| W06A-A06 | Zero writes and flushes on every row | invariant 23 | write mutation |

Excluded: source-slot `write == NULL` (WP-36), format/dup raw-device gating,
crash, continuation, listened PCM.
