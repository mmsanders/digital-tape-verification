> **Historical Surge checkpoint.** Superseded for current WP-09 scope by the temp Verification repair on PR #21. Use `tests/record_draft8/README.md` and `COVERAGE.md` as the current package boundary; this file is retained as provenance only.

# Surge WP-09 record tranche — 21 September 2026

From: surge support, Michael-directed via Digital-Tape #138.
Input product main: `bfd5f1e3f3a282bb22634f1844c254f71f0d1ef7`.
Input verification main: `8ca23c6acfa9e3ec5e96d54f2ec93cb8c329f3c9`.
Branch: `surge/wp09-record-tranche`.
No merge. No package acceptance.

## Process check (post-audit / eight-work-order remediation)

The remediation changed how rounds run, not what is true. Development is still
possible:

- Structural Rule 1, DRAFT-8 freeze, held PR #20/#64/#96, fabrication CLOSED,
  and WP-11 listening remain intact.
- New gates (`evidence-integrity.yml`, `stream-age.yml`, `repo-hygiene.yml`,
  tranche minimum of 3 coverage rows or 25 cases) do not block authoring
  independent tests on a surge branch.
- What *is* starved is assignment routing. After the audit, Digital-Tape has
  three open issues (#137 hardware size, #129/#130 intake parked) and
  verification has one open issue (#20 A1MINI-01 method audit). There was no
  open `surge` or engine-coverage `verification-lead` issue until #138. That
  is a queue gap, not a process break. This issue is the assignment record.

## Coverage published

`tests/record_draft8/` — eight public-API cases against TapeFS §9.1 and
Engine API §§7/8/10/11. Self-test green locally:

```
python3 tests/record_draft8/selftest.py
```

Eight conforming synthetics pass; eight targeted mutations are caught; the
§8 saturation clamp is proved on seven vectors.

This is not product acceptance, not listened goldens, and not complete WP-09.
Next owner: Software, for a mechanical public-API adapter and raw product
observations on a two-commit tranche branch. Verification (or PM) disposes
those observations later. Do not inspect held engine branches to write the
adapter.
