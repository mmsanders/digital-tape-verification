# WP-08 R52 coverage and exclusions

The 40 plan rows are unique public executions, not subdivisions renamed as
cases.  The same rows execute under GCC and Clang.

| Coverage | Vectors/assertion | Causal control |
|---|---|---|
| Empty/zero/one frame | empty forward and stopped; one-frame stopped and both extreme directions | endpoint assertions |
| Rates | zero, ±1.0×, positive/negative 1/4, 1/2, 3/4, tiny fractions, large fractions, INT32_MIN/MAX | min/max controls |
| Endpoints | forward/reverse start and end, beyond-end clamp, moving-away flag clearing | endpoint and tell drift |
| Reverse grid | negative rate from exact end snaps to `max_pos-1` before fetch | grid-snap control |
| Interpolation | increasing/decreasing signed samples at and near int16 extrema | negative floor and overflow/wrap controls |
| Run boundaries | four nonuniform runs; seek at −1/0/+1 around all three boundaries in both directions | stale-run-sample control |
| Portability | complete GCC and Clang streams must be byte-identical before oracle comparison | cross-toolchain divergence control |
| Public trace | seek/rate/service/render/tell/status arguments and results; render callback list is empty | exact structural assertions |

Nine red controls are mandatory and killed: negative fractional rounding,
signed interpolation overflow/wrap, INT32_MIN handling, INT32_MAX clamp,
reverse grid snap, stale run sample, endpoint drift, tell drift, and
cross-toolchain byte divergence.

This tranche excludes Product acceptance until a separately authored Product
adapter is built twice and replayed; human listening and WP-11 goldens; prior
WP-08 package re-acceptance; side-switch/warm behavior; hardware timing; and
full WP-08 closure.
