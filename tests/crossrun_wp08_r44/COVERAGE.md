# WP-08 R44 cross-run coverage

Fixed seed `0xA51CE55D`; 17 unique stereo frames partitioned into runs 5/3/7/2. Thirty-three distinct cases: 18 at ±1 and exact position around three run boundaries in both directions; eight fractional positive/negative Q16.16 cases crossing multiple boundaries; seven start/end/zero/extreme-rate cases. Every case has whole, single and uneven render subdivisions with service budgets 256/1/7, exact PCM and public `tell`/endpoint checks after each render, and zero block callbacks from render. Playback arithmetic is modeled from Engine API §§6.1–6.3, §8 and acceptance WP-08, including fetch-before-advance, floor interpolation, reverse-from-end grid snap, reverse frame-zero once, and endpoint clamps. TapeFS §§5.1–5.3 supply the multi-run entry mapping.

Five killed red controls: off-by-one seek/tell, stale prior-run sample, negative fractional rounding, endpoint wrap and service-time output drift. `selftest.py` exercises all cases synthetically; the `replay.py` census/manifest is for a separate Product adapter. This is authoring, not a Product PASS.

Previously accepted ten fixed cadence cases and 16 side/warm metadata cases are excluded, not re-accepted. This package does not test listening, WP-11 two-toolchain arithmetic portability, hardware timing, side-switch transition or Product implementation internals.
