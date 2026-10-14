# ADR-178 authoring checkpoint — incomplete, not an import publication

Authority: Product #430 merge 8180a2ec0c553d701cf81f841c868c0289ee5462,
contract blob 7c6b4c7651eae68f11d30a0b5e7f01b1223916a7. Historical contract blob
a2bb69147ec60f3e81e5e761ffaaa24a75e84e18 remains part of the prior checkpoint
01ddbbdde4edaac13476a150e97edb3b53afe3e2 and #170 feasibility provenance.

The independent frame calculation remains unchanged. `admitted_output_frames`
adds only issued source-level zero-output refusal and a source-naming reason.
`zero_boundary_selftest.py` checks exact nearest/half-up intervals over all 15
issued rates, the four observed zero-output boundaries, positive neighbours,
zero sources before/after positive neighbours and positive gap-inclusive totals.
It performs no I/O and is not a shipping CLI/no-staging evidence claim. The
sample values do not participate in this admission rule, so silence receives
the same zero-output refusal. The full future observation oracle must require
exit2/source reason and no output/staging for these cases.

Run `python3 -B tests/wp16_ingest_r2/zero_boundary_selftest.py`. This is retained
authoring progress only. Complete matrix fixtures, encoded trim qualification,
meter calibration, manifest/transaction/mutation observers, causal controls,
coverage census and full Stage1 publication remain unfinished. Do not import or
call this checkpoint an acceptance package. No candidate implementation/design/
private tests were inspected. #169 remains open; Stage2 has not begun.
