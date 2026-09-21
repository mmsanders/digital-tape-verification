# SURGE record — WP-06h not-mounted contract (21 Sep 2026)

Independent coverage only. Not acceptance. Not a merge.

`tests/notmounted_draft8/` covers Engine API §10 Not mounted / V5-009:
every ordinary call before mount and after unmount is `NOT_MOUNTED`;
`tape_tell` leaves `*out_frame` untouched; zero writes.

Self-test synthetic and green. Product observations are not in this cut.
