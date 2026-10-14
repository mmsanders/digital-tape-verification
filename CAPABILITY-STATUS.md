# Verification capability status

**Snapshot: 14 October 2026 UTC.** Verification input `a3de077a7fb8b7b66cd2e66bcb2b43484948c2b4`;
Product input `46b48edd6210e541adf3d3e64ec5fd691c2a75f9`.
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
| WP14 software/native CI | PASS | Exact Product #390 candidate and unchanged merged root; Verification PR #158 |
| WP14 release identity | Authenticated | Verification PR #159; original exact platform binaries |
| WP14 physical pulls | PASS 10/10 | [Ten-cut independent disposition](findings/P2-R1-WP14-PULLS-2026-10-14.md); Windows 11; no Mac repeat |
| WP14 full package | HELD | Final post-pull C60/A9 and native shipped-binary >4GiB capture remain |
| Hardware/media/target/release | Excluded | Hardware parked through Phase 2; qualification and physical gates remain held |

The [Stage 2 disposition](findings/P1-R63-WP11-STAGE2-DISPOSITION-2026-10-03.md) preserves the completed #143 return and its
subsequent listening closure. The [package index](tests/README.md) distinguishes
original publication claims from final Phase 1 state. Phase 1 closure is unchanged. The new physical acceptance is bounded to the ten pulls; no Product rerun was performed.

The superseded [12 September capability report](archive/CAPABILITY-STATUS-2026-09-12.md)
is preserved byte-for-byte, with its SHA-256 in [the archive index](archive/README.md).
Round findings retain their original hashes and exact coverage limits.

The [3 October capability snapshot](archive/CAPABILITY-STATUS-2026-10-03.md) is preserved byte-for-byte in the archive.
