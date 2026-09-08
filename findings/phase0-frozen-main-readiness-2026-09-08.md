# Frozen-main independent review and Phase-1 readiness — 8 September 2026

## Disposition

**Phase 0 is authentically and correctly scoped as frozen on canonical `mmsanders/Digital-Tape/main`.**
The signed freeze record at product commit `61e31ba5483d69ec5d85643a1bc496fd4cca9cb9`
identifies the exact DRAFT-8 bytes previously reviewed by Verification at zero blocker / zero major.
It freezes TapeFS §§1–8, Engine API §§2–8 and §12, and the acceptance text; it explicitly does
**not** claim operations/state freeze, full WP-10, WP-11 goldens, hardware qualification or SD-block
atomicity acceptance.

**Verification readiness: GO for the next development phase under the existing test-first boundary.**
This is not blanket approval to merge held/uncovered engine behavior. The next verifier-owned work is
VT8-001 operation/media observation, followed by the remaining WP-10/WP-11/WP-12a obligations.

## Independent main checks

- `spec/VERSION.md` carries the same DRAFT-8 hashes authenticated in the third-cut review.
- `docs/PHASE0-FREEZE.md` records Michael's 8 September signature and preserves V8R3-001 as editorial debt rather than silently mutating the reviewed hash.
- Current-main CI's **spec-bundle**, **mount-package self-check**, **build**, **guardrail**, and **gate-can-go-red** jobs are green.
- The workflow is red only at the deliberately held WP-11 golden gate: `tests/golden/MANIFEST` is absent. That is a declared missing verifier deliverable, not a Phase-0 regression.
- The imported `tests/mount_draft8/run.py` is byte-identical to verification `main` (`891d737c19430f18c7d7695c97a2141a140305da`), preserving the authored assertion boundary.
- No engine implementation source, PR #20 diff/discussion, private implementation test, or unlanded implementation artifact was inspected in this return.

## Mount-run observation disposition

The run packet states that the unchanged 289-case verifier suite observed 15 failures before DRAFT-8
reconciliation and 0 failures after, with the failures confined to the pre-read addressability and stale-
partner repair behaviors covered by the authored mount tranche. The runner/test source and coverage
contract independently support those assertions and do not silently expand into allocator, operation,
warm-start or state-transition acceptance.

**Evidence-access hold:** the two raw observations are committed only as gzip JSONL. Through the current
verification connector they are available as the exact compressed blobs, but not as decompressed record
streams. I therefore have **not independently recomputed the per-record 15/289 and 0/289 counts from the
raw payload** in this return. This is not an engine finding, but it means I am not stamping the after-run as
independently accepted solely from Software's summary. For a final run disposition, publish a lossless
plain `.jsonl` companion (or another connector-readable record stream) without changing the existing raw
blobs. Until then, source/coverage integrity is independently confirmed and record-level engine-run
acceptance remains pending.

## FINDING: VR-P1-001

**SEVERITY:** process major — non-specification; does not reopen the signed Phase-0 contract  
**AREA:** frozen-main repository governance

**CLAIM:** canonical `main` is not protected against direct updates. GitHub reports `protected: false`, and
the repository's only ruleset, `Branch protection on main`, has `enforcement: disabled`.

**REPRO:** inspect the branch metadata and repository rulesets on current main. The spec-bundle gate runs
and can detect a bad push, but no enforced rule prevents that push from becoming canonical first.

**IMPACT:** the signed byte-level freeze is currently protected by project discipline and after-the-fact CI,
not by a repository write barrier. A future agent or human can accidentally alter a frozen spec or bypass
the intended PR/test-first sequence and leave canonical main red until repaired. This is a convergence and
auditability risk, not evidence that the frozen bytes are wrong.

**FIX:** enable the main ruleset (or equivalent branch protection) so frozen-main changes require a PR and
the spec-bundle/required guardrail checks before merge. Keep PM disposition as the authority for any
intentional frozen-contract change. This can be done without changing a frozen spec byte.

## Next verifier tranche: VT8-001

Published under `tests/ops_draft8/` with two deliberately narrow IDs:

- `VT8-001-RB-ALLSLOT` — degraded-B `tape_reset_side_b` must consume sequence
  `max(all structurally-valid A0/A1/B0/B1) + 1`, including a semantically-invalid high-sequence slot;
  it must move/write no chunk data and must recover to a selectable B.
- `VT8-001-REC-ALLOCSEQ` — a one-chunk Side-B splice begins at independently derived `free_next`, never
  below `a_high_water`; its committed index consumes that same all-slot sequence base + 1; an ordinary
  stage-0 recording does not increment `sb_generation`.

The package observes only public operations, callback LBAs and final raw metadata. It explicitly refuses an
allocate-only or sequence-query product API. Warm start, transport transitions, promote/respool, long-op
state, crash injection, PCM and the 10,000-sequence WP-07 fuzz remain excluded.

Verifier package self-test result: **2 conforming observations accepted; 6 targeted mutations caught**.
Runner plumbing result against a clearly labeled synthetic adapter: **2/2 PASS**. Neither is product-engine
acceptance; they establish that the verifier oracle and mechanical contract are ready to be imported before
corresponding implementation work.

## Readiness summary

**Ready now:** continue Phase-1 development with verifier tests landing before the corresponding behavior;
mechanically integrate/run the two VT8-001 cases; continue independent WP-11 oracle/golden work and prepare
full WP-10/WP-12a tranches.

**Not yet accepted/frozen:** operations/state, full WP-07, complete WP-10, WP-11 goldens, hardware safety,
media atomicity, or any held implementation behavior outside landed independent tests.

**Immediate project hygiene:** enforce protection on `main`, and expose the existing raw mount JSONL in a
connector-readable lossless form so Verification can finish the record-level disposition without relying on
a summary.
