# Verification #374 — Stage A disposition

Inputs and exact document hashes: [INPUTS.json](INPUTS.json).
Independent package: [p3_r1_r374](../../tests/p3_r1_r374/README.md).
No firmware implementation was inspected, no engine/port Product bytes were
changed, and no frozen oracle or golden was regenerated.

## Results

| Lane | Result | Boundary |
|---|---|---|
| 365 deferred load faults | PASS, 365/365 actual requested failures; no state/provenance violation | Adds to the 39 prior executed coordinates: all 404 originally missing write/barrier coordinates now have actual execution. Each new row has its sole requested native fault, raw working image and fresh cold verify/dump observations |
| Fault controls | PASS | Missing actual-fault marker and impossible new-A/empty-B state rejected on actual returned observations |
| Six remaining long-copy requests | PROVED UNAVAILABLE on the exact fixture | Requested operation units 63,64,65,127,128,129; each `no_lower_run/pass1` operation completed successfully with exactly three write units and no cut. Full histories retained. Zero new executed long cuts; none silently substituted |
| F1 host half | PASS 10/10 published vectors, byte-exact canonical WAV and PCM | Seven normal-rate cases and three scrub vectors; sample mutation rejected. This proves the off-target comparison/reference half, not firmware output |
| F2 gate method | PASS positive boundary and negative controls | Real compiled 204801-byte .bss rejected; exact limits and invalid/negative inputs tested. Candidate firmware map/target stack are not supplied by this result |
| F6 engine identity method | PASS | Exact Product engine/port-inclusive tree d96b4245 checked; added engine/port file rejected; clean tree accepted again |
| Partition method | AUTHORED / QUALIFIED on controlled adapter | Twelve independently built WP-14 cases and blanket-accept/wrong-offset controls. Actual firmware binding is untested until Software's exact-head adapter exists |
| F3/F5 | Checklist authored | Target timing, Play/Stop/removal and painted-stack checks require witnessed bench evidence |
| DRAFT-11 | REVISE BEFORE ISSUANCE | [Five numbered findings and row-by-row preflight](PREFLIGHT.md). Engine descriptive text, Record-light key behavior and actual scrub vectors need reconciliation. Hardware supplies S2 and Michael authorizes issuance |
| Repository baseline | REFRESHED | README, capability status, historical PM-log banner and navigation indexes reflect Phase 2 closure / Phase 3 opening; prior status/index bytes archived with hashes |

The completed fault lane ran in [CI 41394541716](https://github.com/mmsanders/digital-tape-verification/actions/runs/41394541716)
at verifier `78d50383`. Its later long-runner import failed before that lane ran;
that failure is preserved, not called green. The corrected
[CI 41395321522](https://github.com/mmsanders/digital-tape-verification/actions/runs/41395321522)
at verifier `072f9ec3` independently replayed the retained fault lane, then passed
the six long requests, all host goldens and qualified controls. No 365-fault repeat
was performed for the import correction. Both runs compiled the previously
disposed Product transport `55552ad4fe57e99827ab8eb016044d0486017877`, not firmware.

## Evidence and reproduction

[EVIDENCE.json](EVIDENCE.json) pins source CI artifacts and permanent release ZIP
hashes. [PAYLOAD-AUDIT.json](PAYLOAD-AUDIT.json) records their generated fixture
origins. The fault ZIP adds the prior public baseline bytes by exact SHA plus
`INITIAL-PROVENANCE.json`; the first run recorded this hash on every input but
did not retain another copy of baseline bytes. No actual observation was rewritten.

Use `python3 tests/p3_r1_r374/fetch_review.py DESTINATION` to download and authenticate both release ZIPs
and reproduce the independent [SUMMARY.json](SUMMARY.json) with no Product code
or campaign execution. On Windows use a canonical LF export for the historical
packages' own source-hash guards; checkout CRLF conversion is not package drift.

Commands actually run include:

```
python3 tests/p3_r1_r374/wp17.py selftest
python3 tests/p3_r1_r374/partition_selftest.py
python3 tests/p3_r1_r374/static_control.py
python3 tests/p3_r1_r374/crash.py PRODUCT OUTPUT
python3 tests/p3_r1_r374/replay.py RETAINED_FAULTS
python3 tests/p3_r1_r374/crash.py PRODUCT OUTPUT long
python3 tests/p3_r1_r374/wp17.py host --product PRODUCT --out OUTPUT
python3 tests/p3_r1_r374/review_retained.py FIRST SECOND --out SUMMARY.json
```

Campaign `/usr/bin/time` CPU (user+system, including children): fault lane
296.82 s; failed long-runner import 0.27 s; corrected long requests 1.30 s.
The earlier #210 reported upper bound 608.49 s carries as reported provenance,
not an independently measured aggregate. Build/review overhead is not relabeled
campaign CPU. Admission checks ran before each case, with a 30-second next-case
allowance and the original 7200-second / 2-GiB bounds. New compressed publication
ZIPs total 60,319,009 bytes; original artifacts and all time receipts are pinned.

## Remaining holds and next owner

No comprehensive arbitrary-subset claim for large epochs or repeated-LBA coverage
is added. The six long cut coordinates do not exist on their issued fixture;
this closes their reachability investigation, not six cut executions. **No
automatic write-batching or overall historical #443 clearance follows.** PM
disposes the recorded remaining-model/coverage boundaries before enabling batching.

Stage B awaits the exact Software #642 head and Hardware #641 rig method return.
If those inputs are absent at handoff, return Stage A and stop under #374 rather
than poll. Actual firmware clearance, target PCM/stack/timing, physical operation,
card atomicity/qualification, speaker/headphone safety and release are excluded.
Fabrication/charging remain CLOSED; G2 and macOS remain deferred, not waived.
