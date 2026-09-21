# Mechanical adapter contract

`wp_transport_probe CASE_ID INPUT.vo08 OUTPUT.vo08`

Stdout one JSON object `WP-TRANSPORT-OBSERVATION-1`.

- Warm cases: mount with the named descriptor defect; report `warm_start_used` on mount and `tape_get_info`. Must be false.
- `SS-A-TO-B`: mount A, seek 10, set_side B, tell, status, info, one render before service.
- `SS-DEGRADED-B`: mount A on equal-sequence B, set_side B.
- `SS-ARMED-BUSY`: mount B, arm, set_side A, abort.

Do not change fixtures or expected results to fit a product build.
