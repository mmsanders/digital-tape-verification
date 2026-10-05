# WP14 R1 coverage — partial publication, no candidate acceptance

All expectations derive from Product `437283291c944d24a3d574dee0e3f44ba97e1896`.
The normative input bytes and manifest are in `spec/`. E1 constants are proposed;
PM/Michael must settle them. No existing package bytes were modified.

| Criterion | Published check / control | Actual status and remaining work |
|---|---|---|
| A1 | Exact MBR oracle, independent FAT16 chain/README reader; alternate conforming FAT sizes; corrupt cluster/label/signature controls; image provision runner | Oracle self-tested. Proposed E1; native OS readability/timestamps not witnessed |
| A2 | Black-box bare-image load/verify/dump on all 10 WP11 references and optional generated full C60, both sides; exact byte/length comparison | Candidate not run; remove/reinsert witness held; named tail rule needs citation |
| A3 | Normalized native flush observation checker; no-op, hidden OS failure and coalescing controls; physical pull checklist | Synthetic checker controls only; native candidate flush capture and actual no-op-flush candidate controls unbound on every OS |
| A4 | Independent six-rule policy in specified order; equality at 128 GiB and SD-bus exception; trace zero-write/zero-write-open checks; write-open controls for all six refusals | Pure oracle checked; candidate facts seam schema/symbol and capture unbound; loop naming blocked by P2V-002 |
| A5 MBR_LAYOUT | Seven exact-recognition contradiction witnesses, validation oracle | P2V-001 blocked; not silently converted to bare-image MOUNT errors |
| A5 PARTITION_TYPE | Each entry type corrupted independently | P2V-001 blocked |
| A5 PARTITION_TRUNCATED | Actual capacity one sector short with original MBR | P2V-001 blocked |
| A5 MOUNT | Independent both-bad-superblock and selected-A-index-byte corruption fixtures; CLI asserts finding and unchanged file | Fixture checks green; candidate not run |
| A5 NEEDS_REPAIR | One torn primary superblock; NULL binding must preserve it | Fixture/checker self-tested; CLI not run |
| A5 SIDE_B_DEGRADED | Both B slots invalid, A valid; standby-invalid clean control | Fixture self-tested; candidate not run |
| A5 READ_ERROR | Require bound port read failure on a referenced chunk during actual service/dump, not mount metadata, with SIDE/FRAME | No candidate adapter yet; not covered by a synthetic filesystem truncation |
| A5 literal NULL | Trace requires all engine bindings write_is_null; non-NULL and write-open controls | Checker controls green; needs authenticated candidate instrumentation and actual non-NULL binary control, even if no writes occur |
| A6 | Sparse 64,000,000,000-byte image; partition mirror at >4 GiB reached by provision/load/verify/dump/record/reset/promote/respool/play/scrub; extent trace checker | Published runner, not executed against candidate. Platform runs still required |
| A7 | One-second label with 44,101-frame source, exit 2/plain overage and whole bare-file hash unchanged | Published runner, not executed; target write trace still required |
| A8 | Exact Product base engine tree required; unchanged original 10 goldens/replays, publication/import ancestry and CI configurations | Stage2 requirement, no candidate supplied/disposed |
| A9 | Wall-time capture in real-card checklist | Recorded only; no gate/timing claim |

`selftest.py` prints the exact census and killed controls. Those are **verifier
tests**, not Product A1–A8 cases. `runner.py` is an unaffected subset and always
labels its result `whole_package_accepted: false`. It cannot satisfy Stage1's
full census/controls requirement as currently blocked. No skip yields acceptance.

Settled regression library: truthful geometry and mirror reservation;
standby-invalid is legitimately clean; old byte-flip cases must corrupt the
selected slot; native service must actually read the injected chunk; reverse
frame zero is preserved by WP11's existing reference. No exact call-count oracle
is imposed on a different legal trace. Engine budget-1 regressions remain A8
in their original suites, not a fabricated CLI option.
