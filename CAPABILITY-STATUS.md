# Verification capability status

**Snapshot: 14 October 2026 UTC.** Verification input `df637f7fb962a98b8698d16a531ceb0e8365c2a6`;
Product input `b0d0847b85cee6eac4b2624f9835052a950b902e`.
Live bounded assignments remain in issues; PM owns Product STATUS/dashboard synchronization.
Michael has replaced the mistaken Windows 10 requirement with Windows 11 and requested no Mac pull repeat.

| Area | State | Independent basis |
|---|---|---|
| WP-06 mount, device and index commits | COMPLETE | Verification #138: 40 accepted rows, 2 unreachable by spec, none open |
| WP-07 allocator/COW | COMPLETE | Verification PR #67; Product #215 unchanged integration |
| WP-08 playback/seek/scrub | COMPLETE | Verification #143; WP08-L04 exact-candidate confirmation; L01/L14 closed by Michael #367 |
| WP-09 recording/editing | COMPLETE | Verification #143; L01 closed by Michael #367 |
| WP-10 crash harness | COMPLETE | Verification #141: DRAFT-10 ledger, 63 rows, zero open |
| WP-11 CLI/goldens | COMPLETE | Verification #143: 10/10 goldens, 11,572,876 comparisons per configuration, 7/7 mutations; Michael #367 |
| WP-12/12a re-spool/long operations | COMPLETE | Verification #143 ledger: 31 covered + 2 unreachable + 3 vacuous, zero open |
| WP-13 embedded readiness | COMPLETE | Verification #83; accepted DRAFT-9 carried to DRAFT-10 by Product #361 |
| WP-36 slot capability | COMPLETE | Verification PR #57; Product #200 unchanged integration |
| Product golden gate | GREEN | #369 disposed at `b61a9e9`, merged at `d93ca4e` with the same tree |
| Product main protection | ACTIVE / STRICT | Product STATUS records ruleset 22084355; old VR-P1-001 unprotected snapshot is historical |
| Operations freeze | DECLARED | ADR-162 / Phase 2 kickoff |
| Phase 2 | OPEN | Existing kickoff; bounded assignments only |
| Q-P2-1 any-subset mode (#183) | Model controls PASS; engine execution BLOCKED | [New package](tests/wp10_subset_r1/README.md); Product adapter import and original operation-outcome evaluation required; no engine/batching acceptance |
| WP15 APP-1 preflight (#183) | RETURN FOR CORRECTION | [R3 findings](findings/P2-R3-WP15-PREFLIGHT-2026-10-15.md): four contract findings plus §3 bindings; full app tests follow Software build issue; G2/physical holds unchanged |
| WP14 software/native CI | PASS | Exact Product #390 candidate and unchanged merged root; Verification PR #158 |
| WP14 release identity | Authenticated | Verification PR #159; original exact platform binaries |
| WP14 physical pulls | PASS 10/10 | [Ten-cut independent disposition](findings/P2-R1-WP14-PULLS-2026-10-14.md); Windows 11; no Mac repeat |
| WP16 INGEST-1 | Stage1 authored; Stage2 HELD at3c7a187 | [Disposition](findings/P2-R2-WP16-STAGE2-2026-10-15/README.md): import authenticated;1641 actual output pairs identical across submitted runners; required native/Windows11 evidence incomplete. [Package](tests/wp16_ingest_stage1/README.md) has Verification-owned Windows pin-path correction;1927 cases/1763 sources unchanged. Direct Software435 corrections; no Product/native/fullWP16 acceptance; physical A6 hold survives |
| WP14 final Windows success/A9 | PASS bounded observations | [Final witness](findings/P2-R1-WP14-FINAL-WIN-2026-10-14.md); load1677.7328603s, reinsert/OK/canonical A+B hashes and lengths; [final README bytes PASS](findings/P2-R1-WP14-FINAL-WIN-README-2026-10-14.md) |
| WP14 full package | HELD | Native shipped-binary >4GiB captures remain; #426 method correction needed |
| Windows 11 off-card A6 | HELD: native export unsupported | [Actual rehearsal](findings/P2-R1-WP14-WIN-REHEARSAL-2026-10-15.md): exact binary/exit0/OK; whole XML audited; class GUID placement and undecoded Read/Thread payloads block native result proof. PM routes correction; no unchanged retry/physical handoff |
| Hardware/media/target/release | Excluded | Hardware parked through Phase 2; qualification and physical gates remain held |

The [Stage 2 disposition](findings/P1-R63-WP11-STAGE2-DISPOSITION-2026-10-03.md) preserves the completed #143 return and its
subsequent listening closure. The [package index](tests/README.md) distinguishes
original publication claims from final Phase 1 state. Phase 1 closure is unchanged. Physical dispositions retain their exact witness boundaries; no Product rerun was performed.

The superseded [12 September capability report](archive/CAPABILITY-STATUS-2026-09-12.md)
is preserved byte-for-byte, with its SHA-256 in [the archive index](archive/README.md).
Round findings retain their original hashes and exact coverage limits.

The [3 October capability snapshot](archive/CAPABILITY-STATUS-2026-10-03.md) is preserved byte-for-byte in the archive.
