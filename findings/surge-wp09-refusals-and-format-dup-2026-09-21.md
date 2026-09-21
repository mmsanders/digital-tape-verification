# SURGE record — WP-09 refusal slice + format/dup refusals (21 Sep 2026)

Independent coverage only. Not acceptance. Not a merge.

## What landed

- `tests/record_draft8/` on `surge/wp09-record-tranche` (draft PR #21) gains six
  rows that do not depend on the first eight families being accepted:
  Side-A `READ_ONLY`, `SEQUENCE_EXHAUSTED` at `0xFFFFFFFD`, splice `INDEX_FULL`
  at 4096 entries, `CARTRIDGE_FULL` short-accept 0, abort-disarm, and stage-1
  + exhaustion leaving `promote_stage` untouched.
- New `tests/format_dup_draft8/` on `surge/format-dup-refusal-tranche`: format
  RO / geom 0 / geom 1, dup alias / RO / geom 0 / dest-too-small, empty-promote
  `INVALID_ARG`. Preconditions only. No WP-10 crash table and no identity
  commit success path.

Self-tests are synthetic and green. Product observations are not in this cut.

## Stopped here

WP-10 complete crash and WP-12a continuation/state build on settled operation
oracles plus the two-interruption / identity-boundary tables. Not started.
WP-11 goldens still need Michael listening. Successful stage-1 clearing write
and multi-chunk record remain open on WP-09.
