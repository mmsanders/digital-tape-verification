# C1 final clearance — Software624 exact 5101e3f3

29 October 2026 PDT. Michael manually resumed: “Okay, review the software handoff.”
Product input main `262466d354dac779b0fda9d712a2d75b73eeec33`, Verification input
main `98c94677c84feaceb41b23215b34e25e2490a142`; Software
[return6489231909](https://github.com/mmsanders/Digital-Tape/issues/624#issuecomment-6489231909),
exact **`5101e3f32f259beeca91dd829f83d60edd6c2a22`**, Product PR626.
Current refs fetched; the live same-issue scope, agreement and independence carry.
Individual lead. No Product edit/merge, physical card, native app session or wakeup.

**CLEARED:** Software may integrate **this exact head**, with required Product CI
green and the normal merge commit. Michael may run the C2 checklist with the exact
candidate below. No unresolved F364-1/2/3 finding remains on this head.

This is Make-path/head and C2-test clearance, **not WP-15 acceptance**. G1/G3/G4/G5
still require their C2 observations; G2 remains the later unaided witnessed test.
Hardware/media qualification and the accepted query/open/invisible-swap limits
are unchanged. Older candidate ZIPs remain superseded and are not cleared.

## Remaining safety finding is closed

The production change is the requested narrow correction: ERROR_NOT_READY no
longer unconditionally bypasses the failed volume extent query. Only explicit
NO_MEDIA_IN_DRIVE or a successful positive other-device/non-disk query permits the
limited exclusion already disposed in correction2. Same-target or unknown/failed
device-number answers go to `census_failed`, preserving the OS error and refusing
mount fact. Make returns HOST_QUERY_FAILED/1; standalone safety refuses. The new
typed injection is entirely inside TAPECTL_TEST, and absent from the shipping route.

The revised method note now distinguishes ERROR_NOT_READY from no-medium and
describes the exact target/other-device controls correctly. Source review confirms
failed auxiliary queries cannot act as exclusions. No new monitoring cadence,
identity guarantee, kernel observer or physical-reader proof is inferred.

### Independent unchanged old/new regression

[Verification CI40892342523](https://github.com/mmsanders/digital-tape-verification/actions/runs/40892342523)
compiled the same published `c1_volume_query_r2` controller over the known-failing
39636892 probe and the exact corrected5101e3f3 probe. Each run used its own fresh
private hosted VHD with a real mounted NTFS volume. Only the target-volume extent
answer is the typed error21 control; this is not an OS-generated21 or a card run.

| Independent observation | Old39636892 | Corrected5101e3f3 |
|---|---:|---:|
| Baseline mounted volumes | 1 | 1 |
| Controlled target extent failure21 | 1 | 1 |
| Resulting mount count | 0 | 17 (refusing overflow) |
| Query error recorded | false | **true** |
| Pure removable-policy model | REFUSE_NONE | **REFUSE_FOREIGN_MOUNT** |
| Required-query fail-stop | FAIL | **PASS** |

The known-failing source proves the regression detects this defect; the corrected
source now passes without altering the controller or its expected criterion.
The probe driver calls no Make/provision/unmount. Setup formats only its own new
VHD; no physical target is selected. Both original RESULT files are retained.

Software's actual Windows bundle additionally demonstrates the requested positive
neighbor: when error21 is supplied for volumes on **other** devices, positive
device-number checks exclude them, while the target's one mounted volume remains
in the census and causes REFUSE_FOREIGN_MOUNT. Thus the fix neither loses the
target mount nor requires a blanket failure for an unrelated unready device.
No actual empty-slot reader was measured or qualified.

## Complete evidence disposition

The committed `audit.py` uses independent published predicates and hashes original
raw files before judgment. Producer-owned transport wrappers were reviewed as
transport, not used as replacement expectations. All results are in AUDIT.json.

| Item | Independent result |
|---|---|
| F364-1 query outcomes | CLOSED: 3 Linux and **9 Windows** rows, including actual disk-length/geometry/mount-path/extent/enumeration errors, known refusal neighbors, typed same-target21 failure and other-device positive. Error/exit/report binding passes; changing actual query-failure observations to exit3 is rejected. |
| Shared standalone census safety / A4 qualification | CLOSED for this head: all **6 standalone provision** rows refuse with exit3 and zero write-mode opens/writes/unmounts. Incomplete mount facts remain refusing. The independent old/new test closes the identified shared-probe gap. |
| S3 make suite | **31 Linux +10 Windows PASS** through the unchanged independent runner: one retained session, NULL-write verify, standalone equivalence, capacity, refusals, parent/report controls and removal/I/O cases within the published scope. |
| F364-3 lawful own-p1 / label routing | CLOSED: actual mounted own-p1 unmount + success/equivalence passes the supplement; failed-unmount observation is rejected. Invalid-label pre-open refusal passes separate routing. |
| F364-2 G3 | CLOSED for CI/component coverage: **28/28**, 16 real child-origin +12 app-origin cases, exact original report/process/exit/raw hashes and message selection, stderr independence. C2 person-triggerable/native observations remain separate. |
| Candidate packaging / G1 preconditions | ZIP/member hashes, source head, compiled app child pins and tapectl version match. Shipping binary lacks test facts/pause strings. PE resources request no elevation; original ingest/default-invoker/Medium-parent evidence carries. Real prompt/decline remain C2. |
| Engine/format/spec | Unchanged accepted engine `d96b4245e04d74078f8938744b1394c3018516f7`; no spec/format delta. |
| Tests-first/import | r2 tree `7c5dad088d3d92c82ebf1197bd9d56be5ef465da` matches published98c94677; import24866dc7 predates code8e5e757a. Earlier C1/r1 imports unchanged. No imported assertion edited. |

The current Product main262466d3 still contains the older shared probe until
Software integrates this cleared head. **Restore the unqualified A4/fullWP14
status on integration of the corrected probe**, carrying the existing Stage1
physical/other-row evidence; no physical rerun. WP16 acceptance remains unchanged.
This publication does not pretend the Product merge has already happened or edit
PM's Product ledger/dashboard. Software owns integration; PM owns synchronization.

Source scope is small: the unsafe21 exemption is removed; the additional typed
responses and regression plumbing are test-only. App production source is unchanged
from the prior reviewed head (new binary pins are compiled for the rebuilt tapectl).
The method's other previously reviewed bounds carry. No residual finding is
identified in this bounded exact-head review; no universal correctness claim is made.

## Exact cleared candidate and Michael's C2 handoff

**Download:** [Digital-Tape-Windows11-x64-make-candidate.zip](https://github.com/mmsanders/digital-tape-verification/releases/download/evidence-364-final-2026-10-29/Digital-Tape-Windows11-x64-make-candidate.zip).
This is a byte-identical copy of Software's exact candidate40823497892, not a new
build or general Product release. Read and follow the
**[C2 checklist](../../tests/c1_closeout_r1/C2-CHECKLIST.md)**. That checklist is now
authorized for this candidate; record hashes/OS build and return the listed screens
and text files on Verification364. Use short music to stay near45 minutes.

| Item | SHA-256 |
|---|---|
| Candidate ZIP | `b8a689cfbe926202b6d982dcdc5e5eaaa810d13a180556381d04811f9177ceab` |
| digital-tape.exe | `aafb1f3444a9ddcaee599d3c1efb4dcc7e4d78dae82a0d61913abc25b80ad667` |
| tapectl.exe | `0d92bee784c25a41b96c7a864a50d8199c1a2ae6361f225e8b54b303b7f53477` |
| ingest.exe | `3895f3f356c91b8a9fe870c33694da64bf2765df308bef118d657c1be4bb9a20` |

Candidate40823497892, make40823501184 and G3 40823504252 all completed SUCCESS
on the exact5101e3f3 head. Captured Product PR checks:130 SUCCESS. Exact archive,
source and compiled pin checks are explicit in AUDIT.json. No local execution of
any candidate executable was needed for this review.

C2 must still observe normal Windows11 install/launch, make-only UAC and decline,
all four screens/no lists, error sentences, one real make/verify/dump, one physical
pull and successful remake. No actual reader/Win11/native acceptance is inferred
from Server/VHD CI. G2 is later and remains unaided; do not show the app beforehand.

## Durable replay, final stop and owners

[Retained final inputs](https://github.com/mmsanders/digital-tape-verification/releases/tag/evidence-364-final-2026-10-29):
`verification364-final-inputs.zip`, 51,392,352 bytes, SHA-256
`b809b605e102b873ab28ebe25789f6e1318d0f6625e80c0af870ab19fdb09a88`.
Only project CI evidence, candidate and review metadata are retained; no user music
or private workspace material. `fetch.py DEST` authenticates before extraction;
`audit.py DEST --out RESULT` replays all raw-byte judgments without Product execution.

Stage1 and the final Stage2 disposition are published by merge commits to
Verification main; post the final return and close364 at its assigned stop.
**Software624:** integrate this exact cleared head with required CI green, report
merge SHA and close its issue. **Michael:** manually run the C2 checklist when
ready. **PM:** synchronize the ledger/status on the actual integration/C2 evidence.
No polling, automatic lead activation or new native/trace/admission round.
