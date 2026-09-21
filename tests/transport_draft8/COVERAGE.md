# Transport extra assertion matrix

| ID | Assertion | Basis | Control |
|---|---|---|---|
| SS-A01 | set_side A→B resets position 0, clears flags, invalidates ring | Engine API §5 transition table; inv. 31 | kept old position |
| SS-A02 | set_side to the already-mounted side is OK | Engine API §10 ᵂ | conforming |
| SS-A03 | set_side B on degraded-B is NO_VALID_INDEX, zero writes | Engine API §5 / §10 N | degraded allowed |
| SS-A04 | set_side while armed is BUSY, zero writes | Engine API §10 armed row | armed set_side allowed |
| WARM-A01 | NULL / data-NULL / zero-frames / short buffer / past-end / resume-out / uuid / side mismatch all cold-mount | Engine API §5 ordered warm algorithm V5-007 | null-data used |

Excluded: warm-start *use* path (needs listened PCM / WP-11), rate-retain Playing switch audio identity, crash, continuation.
