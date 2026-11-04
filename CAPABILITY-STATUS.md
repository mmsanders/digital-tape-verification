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
| Hardware651 correction1 | Remaining record bindings published | [Records return](findings/HW651-RECORDS/DISPOSITION.md): plan4/loader/rollback ready for import; exact implemented-head and physical method review pending |
| Software652 IF/3 | Remaining Software bindings published | [IF/3 return](findings/SW652-IF3/DISPOSITION.md): 53 checker/47 capture cases; import then exact implemented-head review pending |
| Round 2 / V382 | Ready executable subsets published; corrected declarations/heads pending | [Return](findings/P3-R2-V382/DISPOSITION.md): BE1 109 bundles/4 fake-port cases, 71 rig rows; exact2faa1180 R374-1 passes27; no whole-method clearance |
| DRAFT-11 | PROPOSED, not in force | [Independent preflight](findings/P3-R1-374/PREFLIGHT.md); PM resolves findings, Hardware supplies speaker limit, Michael authorizes |
| WP-17 target F1/F2/F3/F5 | PENDING bench evidence | Host goldens and static sizes do not establish target PCM, stack, timing or physical behavior |
| Atomicity rig method | NOT CLEARED | [#374 Stage B review](findings/P3-R1-374/RIG-METHOD.md) of Hardware 80d26364: judge/cut-proof/electrical gaps; Hardware and PM own correction. Zero cards qualified |
| Hardware/media/release | Excluded from current software acceptance | Fabrication/charging CLOSED; no physical or acoustic acceptance inferred |
| macOS and ADR-196 limitations | DEFERRED / retained | Existing PM boundaries stand |

Latest return: [Verification #382](https://github.com/mmsanders/digital-tape-verification/issues/382); prior publications preserved.
Product [STATUS](https://github.com/mmsanders/Digital-Tape/blob/main/docs/STATUS.md)
and [Phase 3 ledger](https://github.com/mmsanders/Digital-Tape/blob/main/docs/PHASE3-LEDGER.md)
record phase gates. The [tests index](tests/README.md) and [findings index](findings/README.md)
retain original publications and their exact identities.

The [pre-Phase3 status snapshot](archive/CAPABILITY-STATUS-PRE-P3-374.md) preserves
the superseded round narrative byte-for-byte; its SHA-256 is in [the archive index](archive/README.md).
Older HOLD/pending wording describes its dated input, not a current assignment.
No old test, oracle, golden, evidence byte or disposition changes with this refresh.
