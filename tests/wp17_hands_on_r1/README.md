# ADR208 F3/F4 hands-on semantic fixtures, r1

Author: independent Verification398 stage2, Product978efb2122377140eb89f01bf73cb76385e00a65. Authored from ADR208, FW1/BE1 and the held public IF3 declaration; no firmware implementation inspected. **41 semantic fixtures and10 detecting controls.**

Run `python -B tests/wp17_hands_on_r1/run.py --selftest --out RESULT.json`.

These are executable normative scenario/decision expectations with a verifier-owned normalized interchange, **not a declared Product serial schema or a firmware adapter**. CASES.json is the reviewable materialization of cases.py. Every result says accepted:false, physical_run:false, candidate_executed:false and UNBOUND_SERIAL_DECLARATION. Synthetic build/log/check records are labeled; none is Michael's evidence. No target timing or firmware checker has been executed or cleared.

New bench procedure: [BENCH.md](BENCH.md). Exact remaining interface dependency: [BINDING-NEEDED.md](BINDING-NEEDED.md). This package supersedes only the old F3/F4 external-instrument/CID method expectations for ADR208, preserving all old package bytes. F1/F2/F5 and unchanged numeric/strict facts carry. F4 remains deferred to WP18/19.

The timer uses integer microseconds only for these semantic fixtures. Public Software declaration must specify actual wire fields/clock conversion; it must not treat these invented normalized keys as an issued interface. The injected150ms control proves the measurement must detect at least150ms; it cannot accept the real wake target. PM-decision context is verifier-reviewed evidence, never a Product-authored approval boolean. CID/instrument/calibration/timebase absence is not a failure.
