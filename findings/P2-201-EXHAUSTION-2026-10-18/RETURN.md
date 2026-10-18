# Verification201 — independent exhaustion regression / corrected-head dependency

Input Product main24672d37552206f1c8b1288c67161e59b108cbd5; Verification main
0c1eb39e6bd13c70de702f9e3926a9b7b39c03e6. Issue201 updated2026-10-18T01:45:00Z;
authority ADR186/PM456, paired Software457. Required four onboarding documents and
live assignment read. Individual lead; no subworkers. No corrective implementation
or Software-private tests inspected for the newly authored exhaustion expectations.

Stage1 publishes tests/wp16_shipping_exhaustion_r1. It exercises the full actual
shipping ingest process under enforced memory limits, with native return codes,
same-limit load controls,3/4/6/8/12/64MiB and unlimited controls, exact pair identity
against its own unlimited admitted positive, output-parent census and foreign
sentinel. Candidate mode requires actual exit1 exhaustion plus all cleanup and
success conditions; abort/signal/status wrapping cannot pass. Original Windows
shipping0e1ef2cb has a separate real RED control, not a fabricated allocator cap.
Actual first independent run39088035991, publication head8261a73c3b33889a32f1112a470115c876b9fd24,
Windows job117558628700 reproduced the defect. BASELINE-FIRST.json retains all7
rows: unlimited/8/12/64MiB success;3/4MiB clean exit1;6MiB raw3221226505
(0xC0000409), contract RED. All7 load controls exit0, all sentinels intact, no
stage leftovers. Returned artifact12121069796 SHA256
e3171a41b9b57cd10edd946bac823124ca3b873814098b8e2ee3c9e2d8a0bf0b was
downloaded and independently hash-verified. The final CI also retains raw bytes
in an immutable release asset: EVIDENCE.json pins the run39088169415 raw ZIP
SHA256e4f7d5caeb9c46cf4885e9b9a36a86fdbed97022af216caf783e4f9ac48cc195.
`python3 -B findings/P2-201-EXHAUSTION-2026-10-18/fetch.py --out FRESH.zip`
fetches/authenticates it and replays the original red judgment. Existing normal CI
executes that fetch-and-replay before publication; no raw bytes exceed1MiB in Git.

The normal existing Verification workflow runs contract selfcontrols and a bounded
WindowsServer red-control job on this publication branch. Its green status means
that the known bad executable was actually rejected, never accepted. Final PR
comment records the exact CI head/run/artifact/digest and raw measured rows.

Existing APP corpus/static tests remain treebdd861b693516db2e5244660b3e99ee400d506de.
Verification200's corrected same-DEST S1 smoke12/12PASS, actual S4 parser281-case
6-validity/3-message correction, gate cfg blind spot and prior independent
math/source/relations/native-positive receipts are carried unchanged. The withdrawn
different-DEST harness finding remains withdrawn. No duplicate oracle round or
unchanged full audio campaign is performed.

Stage2 awaits Software457's explicit separately pinned exhaustion/report/app
heads, exact imported package provenance and real executable/CI observations.
At activation no fresh corrected head was returned. Do not substitute original
held453/454/455 candidates, infer a PASS, or inspect uncovered implementation to
fill that dependency. Concrete corrections route directly to Software457 with PM
copy; PM owns disagreement and a fresh exact-head Verification tranche at return.
If Software returns while this publication is active, assess the live return first.

No replacement Windows11 kit is authenticated by this authoring publication;
Michael447's old6126d04 kit stays paused and its old instructions/evidence preserved.
No new physical campaign or security change is requested. Native failed-open absence,
Mac enforceable shipping exhaustion, actual Windows11/ordinary security/elevation,
S2/S3/fullAPP/G2, physicalA6/fullWP14/WP16, held436 and subset443/Q-P2-1(b), frozen
engine/format/write/async/batching/firmware/hardware/media and target<30s all survive.

Stop is published independent regression plus explicit corrected-head dependency,
unless an actual new return arrives during this work. Closure is not acceptance.
