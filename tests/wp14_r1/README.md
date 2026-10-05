# WP14 P2-R1 independent preflight / partial package

Assignment: Verification #146. Read [COVERAGE](COVERAGE.md) before importing or
claiming acceptance. Full Stage1 is blocked by the [preflight report](../../findings/P2-R1-WP14-PREFLIGHT-2026-10-05.md).
Stage2 has not begun. Authored without reading WP14 implementation.

```sh
python3 tests/wp14_r1/selftest.py
python3 tests/wp14_r1/check_pins.py
```

The self-test proves oracle behavior and reproduces contract contradictions. It
imports no Product code. Candidate checks use only public commands:

```sh
python3 tests/wp14_r1/runner.py /absolute/path/to/tapectl --proposed-e1 --full-c60 > candidate-image-evidence.json
```

Do not interpret a green subset as WP14 PASS. E1 is opt-in as an unapproved
proposal, not an issuance. The runner writes temporary **regular image files
only**. Source/reference WAVs are the existing published golden package, unchanged;
it uses all ten reference WAVs as round-trip inputs, not a golden regeneration.
Full C60 needs roughly 2 GiB scratch space; the 64 GB image is sparse but can use
up to its full apparent size on filesystems that do not preserve holes.

Mechanical adapter work still required from Software: facts-file format and seam
symbol; loop identity allowance from PM; authentic write-open/write/OS-flush and
NULL-binding observations; shipped-binary symbol absence with the test binary as
negative control; real flush mutants and read-error injection; exact platform
builds; engine/import identity and unchanged goldens/replays. `trace_audit` is
independent expectations over observed events, not self-attestation by the target.
Each observation must bind exact binary/head, platform and capture source.

[REAL-CARD](REAL-CARD.md) is the requested checklist for Michael, held before
destructive execution pending contract/owner approval and a tested binary. It
contains the permitted-outcome recording procedure; it does not call all nonzero
verify exits failures or qualify PNY atomicity.
