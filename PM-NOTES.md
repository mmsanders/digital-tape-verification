# PM Notes

## 2026-08-31 — Required frozen specifications not yet available

The verification charter requires adversarial review of the frozen specifications `spec/tapefs-v1.md` and `spec/engine-api.md` before implementation-facing work, and requires that verification tests be written without prior exposure to the corresponding engine implementation.

At verification startup, `digital-tape-verification` contains only its README. The accessible `mmsanders/Digital-Tape` repository likewise currently exposes only a README; no `spec/` directory is available there.

**Request to PM:** please place or otherwise expose the frozen copies of:

- `spec/tapefs-v1.md`
- `spec/engine-api.md`
- WP-10 acceptance criteria, when frozen
- WP-11 acceptance criteria, when frozen

Preferably copy the frozen spec documents into this verification repo (or another verifier-only location) so I can work without accidental implementation exposure.

Until those arrive I will not inspect engine source, implementation PRs, diffs, or implementation issues.

No PM decision is requested yet beyond supplying the frozen verification inputs.
