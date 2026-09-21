# SURGE record — WP-06a v1.1 mutators (21 Sep 2026)

Independent coverage only. Not acceptance. Not a merge.

`tests/writability_draft8/` covers the WP-06a rows mount_draft8 deferred:
writable device + valid v1.1 media, `info.writable == false`, repair skipped
with `needs_repair` true, arm/reset_b/promote/respool `READ_ONLY`, feed/commit
`BUSY`, zero writes.

Self-test synthetic and green. Product observations are not in this cut.
