# Capability status — Phase 0 frozen / Phase-1 verification return

Date: 11 Sep 2026

Canonical `mmsanders/Digital-Tape/main` has now **frozen the signed Phase-0 DRAFT-8 scope**. This status distinguishes that signed paper/ABI/media contract from still-open operations, implementation acceptance, WP-10/WP-11 completion and hardware qualification.

| Area | Status | Evidence / boundary |
|---|---|---|
| Phase-0 contract | **FROZEN on canonical main** | Input product commit `4c273ce57ce6848762b00b8990b0b29a3dc9f74b`; `docs/PHASE0-FREEZE.md` preserves Michael's signed scope. TapeFS §§1–8, Engine API §§2–8 and §12, and acceptance text are frozen at the authenticated DRAFT-8 hashes. |
| Independent paper review | **Complete** | Third-cut review remains 0 blockers, 0 majors, 1 documentation question. V8R3-001 is retained as editorial debt rather than changing frozen bytes. |
| Frozen bundle CI | **Green** | Current-main spec bundle, build, verifier mount-package self-check, guardrails, and gate-negative-control jobs are green. |
| Current overall workflow | **Expected red: WP-11 hold** | Golden job fails because `tests/golden/MANIFEST` is absent. This is the declared verifier-owned WP-11 fixture hold, not a frozen-spec regression. |
| Main protection | **Process risk open (VR-P1-001)** | Product `main` reports unprotected and repository ruleset enforcement disabled. Freeze is currently procedural + after-the-fact CI. Recommend enabling PR/required-check protection without changing spec bytes. |
| Mount tranche source integrity | **Confirmed** | Product `tests/mount_draft8/run.py` is byte-identical to verifier publication (`891d737c…`). Coverage still excludes allocation/sequence consumption/warm-start/state transitions/operations. |
| 289-case product observation | **Independently dispositioned green within mount scope** | Raw gzip JSONL was decoded and every verdict recomputed from regenerated verifier fixtures and raw adapter stdout: 274/289 before, 289/289 after, with zero integrity/verdict mismatches. See `findings/mount-observation-disposition-2026-09-11.md`. This accepts only `tests/mount_draft8/COVERAGE.md`, not PR #20 or excluded behaviour. |
| VT8-001 next tranche | **Published and self-tested; ready for mechanical import** | Exact source is `tests/ops_draft8/` at verifier commit `a91138667673fcf19dc9e83c9034322b982b1771`: `VT8-001-RB-ALLSLOT` and `VT8-001-REC-ALLOCSEQ`; public operation/media observations only. Oracle accepts 2 conforming synthetic observations and catches 6 targeted mutations; runner plumbing is 2/2 against the labeled synthetic adapter. No product run or acceptance yet. |
| WP-10 | **Mechanically specified; not complete green** | Operations/state remain unfrozen until actual full WP-10. V7-001 two-interruption closure remains mandatory. |
| WP-11 | **Oracle work may proceed; goldens absent** | Arithmetic/portability contract is frozen/testable; human-listened committed fixtures still outstanding. |
| WP-12a | **Testable; not yet complete** | State-matrix/re-entry/FAULTED contract remains a follow-on tranche. |
| Hardware / media atomicity | **Not qualified** | No raw measurement package or card-atomicity acceptance audited here. |
| Implementation boundary | **Preserved** | This return did not inspect engine implementation, PR #20 diff/discussion, private implementation tests or unlanded code. New implementation review is behavior-scoped only after independent tests land. |

## Development recommendation

**READY FOR PM REVIEW.** The 289-case mount observations are independently disposed
green only within their documented boundary. Import exact VT8-001 verifier source
before allocator/running-sequence implementation acceptance, then return product-run
observations to Verification. Continue WP-11/WP-10/WP-12a independently; do not
treat clean mount coverage as approval of excluded behavior.
