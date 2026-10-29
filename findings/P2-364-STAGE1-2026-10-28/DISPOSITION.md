# C1 Stage 1 — WP-14 and WP-16 accepted on Windows 11

Verification364, 28 October 2026 PDT. Michael manually activated this independent
context. Product input `262466d354dac779b0fda9d712a2d75b73eeec33` (PM622 merged),
Verification input `5512a2d0d7bd8135f4a10016d9469c612340737a`; issue364 scope update
6478266521 permits same-issue continuation when Software624's return is available.
Current AGENTS/agreement/STATUS/charter, live issue and amended contracts read.
Individual lead, no subworkers. No physical run, app launch, tracing or native
receipt session. ADR-195 controls this disposition; old package bytes are unchanged.

**WP-14: ACCEPTED for current Windows 11 Phase 2 scope. WP-16: ACCEPTED for the
integrated unchanged INGEST-1 source and carried Windows 11 binary evidence.**
The following tables are the final criterion disposition, not merely PM's reading.
They supersede the old A6/own-host method holds for current acceptance. They do
not rewrite what earlier methods did or measured. Mac remains deferred.

## WP-14 ledger

| Row | Verdict | Outcome and detecting control / published evidence |
|---|---|---|
| A1 Provision | PASS | [Final Windows witness](../P2-R1-WP14-FINAL-WIN-2026-10-14.md) and [README byte supplement](../P2-R1-WP14-FINAL-WIN-README-2026-10-14.md): exact release, PNY 64 GB, successful provision, correct bytes. [390 software disposition](../P2-R1-WP14-390-2026-10-09.md), `tests/wp14_r1` exact MBR/FAT/README/timestamp mutations carry. |
| A2 Round trip | PASS | Same final witness: C60, physical remove/reinsert, verify OK, canonical A/B full hashes and lengths. Image comparisons reject changed payload/header/length; no new listening or invented sample comparison of absent physical WAVs. |
| A3 Durability | PASS | [Ten pulls](../P2-R1-WP14-PULLS-2026-10-14.md), 10/10 on Windows 11; published interruption/frontier and flush-negative controls in `wp14_r1` carry. This is bounded observed recovery, not media atomicity qualification. |
| A4 Disk safety | PASS | 390 exact-head disposition and independent `wp14_r1` ordered refusal/foreign-mount/write-open controls. ADR-195 does not weaken WP-14 disk safety. |
| A5 Verify read-only | PASS | 390 and `wp14_r1` NULL-write binding; flipped index, torn superblock, truncated partition, wrong type, unreadable chunk controls. |
| A6 Large media | PASS | 14 Oct final witness on 62,537,072,640-byte PNY: provision/load/verify/dump; mirror at 62,537,072,128. [19 Oct retained evidence](../P2-A6-PHYSICAL-2026-10-19/README.md) corroborates two successful 512-byte reads at that address. Existing sparse 64 GB all-command image/native results carry. New `c1_closeout_r1/a6.py` compiles the same port with only the read offset narrowed to uint32: pristine 64 GB verify changes from OK/0 to nonzero. [CI 40791300942](https://github.com/mmsanders/digital-tape-verification/actions/runs/40791300942) passes this real mutant control; full observations/hashes in AUDIT.json. The four post-exit records on other streams are outside A6 under ADR-195. |
| A7 Capacity | PASS | `wp14_r1` exact-fit/overage/exit2 and unchanged-target controls, carried 390 disposition. |
| A8 Engine pin | PASS at input | Product input engine `d96b4245e04d74078f8938744b1394c3018516f7`, accepted ADR-175 engine; prior golden controls carry. C4 rechecks current main. |
| A9 Load time | RECORDED, criterion satisfied | Final witness stopwatch 1677.7328603 s (27 min 57.733 s), reported approximately 27 min 58 s. This is a recorded measurement, not a new throughput threshold or target-system guardrail-10 proof. |

The older `completion_selftest.py` wrapped-offset control detects bad evidence
metadata. The new compiled narrowed-read control proves the actual sparse-image
outcome test can fail. An initial verifier-only CI attempt damaged the primary
superblock and incorrectly expected verify OK; that would legitimately report
repair. The corrected control keeps the image pristine. No Product fix was needed.

## WP-16 ledger

All numerical/codec/resource claims retain the bounds recorded in the
[333 table](../P2-333-INGEST-LEDGER-2026-10-26/README.md),
[Stage B integration clearance](../P2-332-333-REVIEW-2026-10-26/REVIEW.md),
192/203/230/234 and the exact independent publication trees they cite. Current
Product main and Software624 both have **the identical ingest tree `83507899`**.
Source identity carries tests/results; this is not a fresh audio corpus run.

| Row | Verdict | Carried outcome and control basis |
|---|---|---|
| I1 Formats | PASS | Stage1/192 strict admission census, 203 preserved admission and 230 Win11 observed bytes; positive format/profile cases paired with named refusal/source-policy negatives. |
| I2 Conversion | PASS | 192's 1,640 cases/1,657 source instances, calibration/quality/latency/FIR certificates, mono/resample/dither/canonical WAV and load compatibility; 203 equivalence. Controls and tolerances remain those independently published. |
| I3 Loudness | PASS within INGEST-1 | Calibrated final PCM/manifest and peak-limited/silence/unmeasurable exceptions; 203 operation/order preservation; 230 exact output identities. No invented universal convergence/no-panic theorem. |
| I4 Gapless | PASS | Isolated-source/join relations, exact silence/count/trim controls, 230 byte/count evidence. No arbitrary endpoint-continuity promise. |
| I5 Order | PASS | Frozen natural comparator/NFC/logical-path policy and adversarial order/name fixtures; 230 Windows identities. |
| I6 Determinism | PASS | Same-profile byte equalities, including 230's 1,640 Win11 identities with only the declared tool_version change; pinned dependencies. Different binary hashes are never conflated. |
| I7 Length | PASS | Counts, exact capacity/overage, publication/no-replace controls; 203 fallible-allocation correction; 230 publication/flush-close pairs; 234 shipping Windows resource rows (3/4/6 MiB exit1, 8/12/64/unlimited identical pairs). |
| I8 Fixtures | PASS | Original generated/CC0 census, immutable Stage1 tree `609a4c819076a2b85b26cc4f3cd254b92caef6de`. No new source audio. |
| Own-host | PASS under ADR-195 | New bounded static check on the actual integrated first-party ingest source is clean. Ordinary-file mutant remains clean; raw Windows path, POSIX partition path and device-control API mutants in disposable copies fail. Source list/hashes/control hits are in AUDIT.json. No unreviewed new dependency/source delta. Candidate's original `3895f3f3` ingest has no elevation-request manifest; it is started by ordinary `Command`, not runas, from the app. #361 establishes the Medium-integrity unelevated app parent. This establishes the permitted default-invoker route; failed/zero-access open tracing is withdrawn. |

The PE resource audit records **absence**, not fictional explicit `asInvoker`
nodes: app has a common-controls manifest with no execution level; ingest/tapectl
have no manifest resource. [Microsoft's UAC documentation](https://learn.microsoft.com/en-us/windows/win32/secbp/running-with-administrator-privileges)
describes default invoker behavior and token inheritance. The original ingest hash
is unchanged, and its production ordinary-spawn route cannot silently elevate it.
The candidate app's normal launch and make-only UAC prompt are checked in C2 for G1;
the current candidate is not thereby cleared. #361's Medium parent is historical
native evidence as expressly allowed by this assignment, not an assertion that
this new app was launched. No extra manifest-rebuild gate is invented.

## WP-15 authored tests and human checklist

`tests/c1_closeout_r1` adds 28 independent bridge/error cases, executable production
bridge app-origin tests, source/PE controls, and an S3 supplement for lawful own-p1
unmount and invalid-label pre-open refusal. Existing static negative controls already
exist in `wp15_app1a_r1/static_controls.py`; they were also rerun locally against
Software624's actual gate (baseline/ordinary 0, three device mutants 1).

The production bridge CI test has four test functions covering file/mixed rejection,
ingest spawn failure, make spawn failure/UAC decline, and eight recheck mismatches.
Its typed launcher/recheck inputs are unit boundaries, not real OS prompts or child
outcomes. The child-origin matrix separately requires real tool originals delivered
through production completion; no synthetic report is accepted as a real outcome.
The old make runner remains in force; the supplement changes only routing of two
previously impossible-to-pass lawful cases, with foreign-unmount/write controls.

**[Michael's C2 checklist](../../tests/c1_closeout_r1/C2-CHECKLIST.md)** covers exact
ZIP install/hashes/OS build, all four screen states against APP-1 §2, one real make,
verify/A+B dump, file/overage/nonmusic/decline/recheck errors, one pull and successful
remake, screenshots and text returns. It targets about 45 minutes with short music.
**Do not run it until Stage 2 clears the exact candidate.** G1/G3/G4/G5 close after
C2; G2 remains the later witnessed unaided test. Software624's return is present,
so Stage 2 continues in this issue. No Product implementation edits or integration.
