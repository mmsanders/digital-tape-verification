# Mechanical adapter contract

`wp06h_probe CASE_ID INPUT.vo08 OUTPUT.vo08`

Stdout one JSON object `WP06H-OBSERVATION-1`.

- `NM-BEFORE`: do not mount; issue every ordinary call; then mount/unmount to
  prove the instance still can.
- `NM-AFTER`: mount, unmount, then issue every ordinary call.
- Tell cases pre-load `*out_frame` with `0x1111111111111111` and require that
  exact value after the refusal.

Do not change fixtures or expected results to fit a product build.
