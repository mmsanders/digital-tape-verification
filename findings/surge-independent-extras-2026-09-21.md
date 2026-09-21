# SURGE record — remaining non-stacking independent rows (21 Sep 2026)

Independent coverage only. Not acceptance. Not a merge.

## Added this cut

- WP-09 extras on `surge/wp09-record-tranche`: multi-chunk overwrite, splice
  into empty B, empty commit in overdub/splice, successful stage-1 clear on arm
  (partner-first, gen+1, H unchanged, then ordinary record).
- WP-12 stage-1 clear on `surge/wp12-respool-tranche` (same two-pass geometry).
- Format/dup: `block_count == LBA_CHUNK_BASE` zero-callback GEOMETRY, and
  alias+RO+geom0 returns INVALID_ARG first.
- WP-36: `tape_format` against the source-slot device is READ_ONLY.
- New `tests/transport_draft8/` on `surge/transport-extras-tranche`: set_side
  A→B / same / degraded / armed, plus eight warm-start cold-mount negatives.

Self-tests synthetic and green. Product observations are not in this cut.

## Still not started (they stack)

WP-10 crash tables (both durability modes, two-interruption, identity commits).
WP-12a continuation/state. WP-11 listening / warm-start *use*. 10k-edit histories.
