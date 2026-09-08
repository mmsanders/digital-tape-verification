# Capability status — Phase 0 frozen / Phase-1 entry

Date: 8 Sep 2026

Canonical `mmsanders/Digital-Tape/main` has now **frozen the signed Phase-0 DRAFT-8 scope**. This status distinguishes that signed paper/ABI/media contract from still-open operations, implementation acceptance, WP-10/WP-11 completion and hardware qualification.

| Area | Status | Evidence / boundary |
|---|---|---|
| Phase-0 contract | **FROZEN on canonical main** | `docs/PHASE0-FREEZE.md`, product commit `61e31ba5483d69ec5d85643a1bc496fd4cca9cb9`. Signed scope: TapeFS §§1–8; Engine API §§2–8 and §12; acceptance text. Exact DRAFT-8 hashes are the previously authenticated third-cut bytes. |
| Independent paper review | **Complete** | Third-cut review remains 0 blockers, 0 majors, 1 documentation question. V8R3-001 is retained as editorial debt rather than changing frozen bytes. |
| Frozen bundle CI | **Green** | Current-main spec bundle, build, verifier mount-package self-check, guardrails, and gate-negative-control jobs are green. |
| Current overall workflow | **Expected red: WP-11 hold** | Golden job fails because `tests/golden/MANIFEST` is absent. This is the declared verifier-owned WP-11 fixture hold, not a frozen-spec regression. |
| Main protection | **Process risk open (VR-P1-001)** | Product `main` reports unprotected and repository ruleset enforcement disabled. Freeze is currently procedural + after-the-fact CI. Recommend enabling PR/required-check protection without changing spec bytes. |
| Mount tranche source integrity | **Confirmed** | Product `tests/mount_draft8/run.py` is byte-identical to verifier publication (`891d737c…`). Coverage still excludes allocation/sequence consumption/warm-start/state transitions/operations. |
| 289-case product observation | **Record-level disposition pending evidence access** | Run packet reports 15/289 before and 0/289 after. Compressed raw blobs are present, but current verifier connector does not expose decompressed JSONL records; do not convert Software's summary into independent acceptance. Request a lossless plain-JSONL companion. |
| VT8-001 next tranche | **Authored and self-tested** | `tests/ops_draft8/`: `VT8-001-RB-ALLSLOT` and `VT8-001-REC-ALLOCSEQ`; public operation/media observations only. Oracle accepts 2 conforming synthetic observations and catches 6 targeted mutations; runner plumbing 2/2 against labeled synthetic adapter. Await mechanical product adapter/import, then real run. |
| WP-10 | **Mechanically specified; not complete green** | Operations/state remain unfrozen until actual full WP-10. V7-001 two-interruption closure remains mandatory. |
| WP-11 | **Oracle work may proceed; goldens absent** | Arithmetic/portability contract is frozen/testable; human-listened committed fixtures still outstanding. |
| WP-12a | **Testable; not yet complete** | State-matrix/re-entry/FAULTED contract remains a follow-on tranche. |
| Hardware / media atomicity | **Not qualified** | No raw measurement package or card-atomicity acceptance audited here. |
| Implementation boundary | **Preserved** | This return did not inspect engine implementation, PR #20 diff/discussion, private implementation tests or unlanded code. New implementation review is behavior-scoped only after independent tests land. |

## Development recommendation

**GO for Phase-1 development under test-first holds.** Do not reopen Phase-0 paper work merely because implementation proceeds. Land/import VT8-001 tests before allocator/running-sequence implementation acceptance; continue WP-11/WP-10/WP-12a independently; do not treat clean mount coverage or Software regression results as approval of excluded behavior.
