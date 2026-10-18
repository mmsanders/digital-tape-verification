# Verification capability status

**Snapshot: 17 October 2026 UTC.** Verification original input `fc80e0ece3f84f8c7ad468c695cb22b3d6abd21d`;
Product input `05315e2d464376400e122cd982dbb93dc084c1fb`.
18 October update: [Verification206 readiness](findings/P2-206-READY-2026-10-18/RETURN.md)
clears one exact corrected-kit Windows11 INGEST collection under existing policy.
Script74e1af2c corrects204's policy/summary-exit transport findings; unchanged
kitffb0f78a/exes d923613b,d544b6f5 authenticate. This supersedes the older INGEST
collection wording below; actual Windows11/full-package evidence is pending.
Physical read-only A6 readiness is unchanged.

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
| Q-P2-1 any-subset mode (#197) | Available retained operation rows PASS; overall443 HELD | [17 October operation rows](findings/P2-SUBSET-ROWS-2026-10-17/README.md): core/promote/format-dup/respool/load scopes independently evaluated, copy/live-set/durability controls PASS. Full duplicate source/PCM, broader DRAFT10 residue/repeated-LBA/sampled coverage and404 host faults/seam detail remain. No overall integration or batching permission; PM owns next coverage |
| WP15 APP-1A (#196) | Issued contract preflight / report-parser-S4 package AUTHORED | [17 October preflight](findings/P2-APP1A-PREFLIGHT-2026-10-17/README.md): Q1-Q7 paper preflight has no new contradiction;627 parser fixtures and real-process adapter published. Software452 imports/builds S1/S4 and returns exact host head directly to196; native/physical/G2 and held436 dependency remain. No app acceptance |
| WP14 software/native CI | PASS | Exact Product #390 candidate and unchanged merged root; Verification PR #158 |
| WP14 release identity | Authenticated | Verification PR #159; original exact platform binaries |
| WP14 physical pulls | PASS 10/10 | [Ten-cut independent disposition](findings/P2-R1-WP14-PULLS-2026-10-14.md); Windows 11; no Mac repeat |
| WP16 INGEST-1 (#192) | Available host receipts PASS; overall exact6126d04 HELD | [Host disposition](findings/P2-192-HOST-2026-10-17/README.md): AP4 numerical/source/relations/profile/positive native transaction receipts completed; existing byte/logical-path source binding PASS. Actual Windows11, exact-shipping exhaustion and known Windows visibility limit remain. Reviewed Windows collection instructions ready on Michael447. No Product/native/fullWP16 integration authorization |
| WP14 final Windows success/A9 | PASS bounded observations | [Final witness](findings/P2-R1-WP14-FINAL-WIN-2026-10-14.md); load1677.7328603s, reinsert/OK/canonical A+B hashes and lengths; [final README bytes PASS](findings/P2-R1-WP14-FINAL-WIN-README-2026-10-14.md) |
| WP14 full package | HELD | Actual physical native shipped-binary >4GiB captures remain; Windows193 method PASS; Mac method held |
| Windows 11 off-card A6 | Exact method/rehearsal PASS; physical held | [Verification193](findings/P2-R1-WP14-A6-R4-2026-10-17/README.md): exact441 a50a211,16 controls and full original1,232,801-event replay PASS. Software integration preauthorized; reviewed one-verify physical instructions ready for Michael447. Mac and physical/full-package holds survive |
| Hardware/media/target/release | Excluded | Hardware parked through Phase 2; qualification and physical gates remain held |

The [Stage 2 disposition](findings/P1-R63-WP11-STAGE2-DISPOSITION-2026-10-03.md) preserves the completed #143 return and its
subsequent listening closure. The [package index](tests/README.md) distinguishes
original publication claims from final Phase 1 state. Phase 1 closure is unchanged. Physical dispositions retain their exact witness boundaries; no Product rerun was performed.

The superseded [12 September capability report](archive/CAPABILITY-STATUS-2026-09-12.md)
is preserved byte-for-byte, with its SHA-256 in [the archive index](archive/README.md).
Round findings retain their original hashes and exact coverage limits.

The [3 October capability snapshot](archive/CAPABILITY-STATUS-2026-10-03.md) is preserved byte-for-byte in the archive.
