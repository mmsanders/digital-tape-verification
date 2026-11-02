# Verification capability status

**Phase 3 open. Phases 1 and 2 complete.** Baseline authenticated against Product
`3826018653e504217f37a16d8864fb0d597e22e6` (ADR-198–201).
Current assignments come only from live `verification-lead` issues started by Michael.

| Area | Current state | Independent boundary / next owner |
|---|---|---|
| Phase 1 engine | COMPLETE, 36/36 | Existing independent package dispositions carry; engine tree d96b4245 pinned |
| Phase 2 desktop tools | COMPLETE, 12/12 with G2 deferred | Windows 11 x64; WP-14/WP-16 and WP-15 acceptance as recorded by Product; host scope frozen |
| G2 unaided app test | DEFERRED, not waived | Michael runs the issued protocol before anyone else uses the app for real work |
| Phase 3 bench firmware | OPEN | #374 authors independent FW-1 tests; exact firmware-head clearance is separate |
| Q-P2-1 remaining coverage | 365 faults PASS; 6 long cuts proved unavailable | [#374 disposition](findings/P3-R1-374/DISPOSITION.md): all 404 previously missing load faults executed with prior receipts; exact long fixture ends after 3 units. No batching permission inferred |
| DRAFT-11 | PROPOSED, not in force | [Independent preflight](findings/P3-R1-374/PREFLIGHT.md); PM resolves findings, Hardware supplies speaker limit, Michael authorizes |
| WP-17 target F1/F2/F3/F5 | PENDING bench evidence | Host goldens and static sizes do not establish target PCM, stack, timing or physical behavior |
| Atomicity rig method | Pending Hardware #641 input | Verification review before physical run; zero cards qualified |
| Hardware/media/release | Excluded from current software acceptance | Fabrication/charging CLOSED; no physical or acoustic acceptance inferred |
| macOS and ADR-196 limitations | DEFERRED / retained | Existing PM boundaries stand |

Current work: [Verification #374](https://github.com/mmsanders/digital-tape-verification/issues/374).
Product [STATUS](https://github.com/mmsanders/Digital-Tape/blob/main/docs/STATUS.md)
and [Phase 3 ledger](https://github.com/mmsanders/Digital-Tape/blob/main/docs/PHASE3-LEDGER.md)
record phase gates. The [tests index](tests/README.md) and [findings index](findings/README.md)
retain original publications and their exact identities.

The [pre-Phase3 status snapshot](archive/CAPABILITY-STATUS-PRE-P3-374.md) preserves
the superseded round narrative byte-for-byte; its SHA-256 is in [the archive index](archive/README.md).
Older HOLD/pending wording describes its dated input, not a current assignment.
No old test, oracle, golden, evidence byte or disposition changes with this refresh.
