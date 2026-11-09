# Verification capability status

**Phase 3 open. Phases 1 and 2 complete.** Baseline authenticated against Product
`3826018653e504217f37a16d8864fb0d597e22e6` (ADR-198–201).
Current assignments come only from live `verification-lead` issues started by Michael.

| Area | Current state | Independent boundary / next owner |
|---|---|---|
| Phase 1 engine | COMPLETE, 36/36 | Existing independent package dispositions carry; engine tree d96b4245 pinned |
| Phase 2 desktop tools | COMPLETE, 12/12 with G2 deferred | Windows 11 x64; WP-14/WP-16 and WP-15 acceptance as recorded by Product; host scope frozen |
| G2 unaided app test | DEFERRED, not waived | Michael runs the issued protocol before anyone else uses the app for real work |
| Phase 3 bench firmware | OPEN | FW-1 independent package published; target halves remain pending |
| Software642 / ee478a91 | CLEARED for authorized off-target integration | [V378 correction/disposition](findings/P3-R1-V378/DISPOSITION.md), ADR-202: 28 admission cases and 4 controls pass; unchanged host/static/tree results carry. Exact head only, required current-base CI; no target/package acceptance |
| Q-P2-1 remaining coverage | 365 faults PASS; 6 long cuts proved unavailable | [#374 disposition](findings/P3-R1-374/DISPOSITION.md): all 404 previously missing load faults executed with prior receipts; exact long fixture ends after 3 units. No batching permission inferred |
| Hardware651 / c55e5ad | Bounded artifact correction CLEARED | [V392](findings/V392/DISPOSITION.md):339 published +3 CLI cases pass; required current-base Product CI remains an integration condition, physical method NOT CLEARED. |
| Hardware651 / baf176c | HOLD: outer loader exceptions | [V390](findings/V390/DISPOSITION.md): original27/71/229/7 pass; NUL manifest filename/deep JSON still raise; physical method NOT CLEARED. |
| Software658 / e0b6bb02 | HOLD: supported-platform census removed | [V390](findings/V390/DISPOSITION.md): manual macOS/selection controls pass; Windows/Linux retained-evidence audit must remain required or receive explicit PM scope disposition. |
| Hardware651 / 18852b5 | HOLD | [Review](findings/HW651-18852B5/DISPOSITION.md): unauthenticated setup awards proof/credit; invalid manifests raise; Product CI not green. Existing27/71/229 pass |
| Hardware651 correction1 | Remaining record bindings published | [Records return](findings/HW651-RECORDS/DISPOSITION.md): plan4/loader/rollback ready for import; exact implemented-head and physical method review pending |
| Software652 /0db6ce5c | Bounded behavioral corrections CLEARED | [V394 laneA](findings/V394-KIT/DISPOSITION.md); original/import/fix lineage retained, red ordering CI still blocks integration. |
| Census / review-order policy | Independent NEW packages ready | [V394 B/C](findings/V394-POLICY/DISPOSITION.md); immutable companion oracle/fixtures before Software658 changes; returned adapter/gate disposition pending. |
| Software652 / d62e0de0 | HOLD: deadline, resolved confinement, malformed types | [V388 review](findings/V388/DISPOSITION.md); existing109/4/53/47 pass; six new failures ready for unchanged import. |
| Software652 IF/3 | Remaining Software bindings published | [IF/3 return](findings/SW652-IF3/DISPOSITION.md): 53 checker/47 capture cases; import then exact implemented-head review pending |
| Round 2 / V382 | Ready executable subsets published; corrected declarations/heads pending | [Return](findings/P3-R2-V382/DISPOSITION.md): BE1 109 bundles/4 fake-port cases, 71 rig rows; exact2faa1180 R374-1 passes27; no whole-method clearance |
| DRAFT-11 | PROPOSED, not in force | [Independent preflight](findings/P3-R1-374/PREFLIGHT.md); PM resolves findings, Hardware supplies speaker limit, Michael authorizes |
| WP-17 target F1/F2/F3/F5 | PENDING bench evidence | Host goldens and static sizes do not establish target PCM, stack, timing or physical behavior |
| Atomicity self-run method | REVIEWED, implementation/policy held | [V398 method review](findings/V398-HARDWARE-METHOD/DISPOSITION.md): planted-tear control detected; optional-CID/new route, P4 and SPI scope need disposition. ADR208 supersedes old instrument gates. Zero cards qualified |
| Hardware/media/release | Excluded from current software acceptance | Fabrication/charging CLOSED; no physical or acoustic acceptance inferred |
| macOS and ADR-196 limitations | DEFERRED / retained | Existing PM boundaries stand |

Latest return: [Verification #397](https://github.com/mmsanders/digital-tape-verification/issues/397); prior publications preserved.
Product [STATUS](https://github.com/mmsanders/Digital-Tape/blob/main/docs/STATUS.md)
and [Phase 3 ledger](https://github.com/mmsanders/Digital-Tape/blob/main/docs/PHASE3-LEDGER.md)
record phase gates. The [tests index](tests/README.md) and [findings index](findings/README.md)
retain original publications and their exact identities.

The [pre-Phase3 status snapshot](archive/CAPABILITY-STATUS-PRE-P3-374.md) preserves
the superseded round narrative byte-for-byte; its SHA-256 is in [the archive index](archive/README.md).
Older HOLD/pending wording describes its dated input, not a current assignment.
No old test, oracle, golden, evidence byte or disposition changes with this refresh.

V397: [census/transport](findings/V397-CENSUS/DISPOSITION.md), [ordering](findings/V397-ORDER/DISPOSITION.md) and [runner restoration](findings/V397-RUNNER/DISPOSITION.md) independently cleared within their bounded scopes. Required current-base Product CI remains an integration condition.

V398: [ADR208 existing preflight delta](findings/V398-PREFLIGHT/PREFLIGHT.md), [41 timing semantic fixtures/10 controls](findings/V398-METHOD-TESTS/DISPOSITION.md) and [self-run method review](findings/V398-HARDWARE-METHOD/DISPOSITION.md) published. Software serial binding and Hardware/PM declared self-run policy remain named dependencies. F3/F4 target results remain pending; retired instruments/CID are not gates.
