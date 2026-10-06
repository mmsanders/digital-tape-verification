# WP14 P2-R1 amended independent package — progress publication

Assignment: Verification #146; normative input Product ADR-164 merge
`25b6439019396a54ce12e8298dd58f8a5d8a17e9`. Authored without reading the WP14
implementation. Original paper report and historical evidence remain preserved.
See [coverage](COVERAGE.md) and [delta preflight](../../findings/P2-R1-WP14-DELTA-2026-10-06.md).
**Stage 1 is not complete, Stage 2 has not begun, no candidate accepted.**

```sh
python3 tests/wp14_r1/check_pins.py
python3 tests/wp14_r1/selftest.py
python3 tests/wp14_r1/amendment_selftest.py
```

These are verifier selftests, with zero Product runs. E-1 is now approved; the
exact overlay and supplemental manifest are confirmed by `check_pins.py`.
`spec/adr164/` contains exact amended document bytes. Frozen copies in `spec/`
and the original `INPUTS.json` remain unchanged.

After publication and Software's import/binding, run the candidate image suite:

```sh
python3 tests/wp14_r1/runner.py /absolute/path/to/tapectl > candidate-image-evidence.json
python3 tests/wp14_r1/native.py --platform linux /absolute/path/to/capture-transport > native-linux.json
```

Repeat native runs on macOS and Windows; see [transport requirements](NATIVE-TRANSPORT.md).
The image runner writes temporary regular files only. It round-trips all ten
unchanged reference WAV inputs on bare and provisioned images, plus a mandatory
full C60. Exact WAV bytes and final frame are required; no regenerated goldens.
Full C60 needs roughly 2 GiB scratch. The 64 GB target is sparse; a filesystem
without hole preservation can consume its full apparent size.

Missing transport is a binding dependency, not a skip that yields acceptance.
Native results require authentic candidate capture, exact-head and binary hashes,
actual no-op/non-NULL/policy mutants, and referenced service-read failure. The
adapter captures facts and events; it does not supply expectations or PASS.
Malformed provenance cannot count as killing a candidate control. Review raw
capture against CI artifacts before any disposition; JSON labels are not proof.

[Michael's real-card checklist](REAL-CARD.md) includes macOS provision/load,
remove/reinsert, ten pulls, Windows 10 cross-platform readback **and fresh Windows
provision/load**, README evidence and >4GiB access capture. Tested binary release
hashes are still required before script-ready delivery. Physical and named-OS
holds remain distinct from software CI. Server 2025 is supplemental.
