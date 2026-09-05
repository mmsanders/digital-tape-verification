# PM Notes

## 2026-08-31 — DRAFT-1 specifications received; adversarial review started

Received and preserved verifier-side copies of:

- `spec/tapefs-v1.md`
- `spec/engine-api.md`

Both documents identify themselves as **DRAFT-1, issued for adversarial review, not frozen**. I am therefore treating them as review inputs, not as final acceptance-test authority.

First-pass mechanical findings are in `findings/spec-review-draft1.md`. The current pass contains two blocker findings and multiple major/question findings. Highest-priority items for PM attention are:

1. Re-spool as currently described can overwrite chunks referenced by the still-live B index before commit, so interruption can corrupt a cartridge (`V-002`, blocker).
2. Duplicate has no destination precondition or crash protocol, so interruption can destroy a pre-existing destination cartridge (`V-003`, blocker).
3. Index entries are normatively placed starting at byte 64, but the commit protocol writes entries only to blocks 1–127 then zero-pads block 0 (`V-001`).
4. Promote's mutable superblock/high-water and single preroll cache do not have a complete two-copy/generation crash protocol (`V-007`, `V-009`).
5. Fresh UUID/format time generation is impossible through the current engine boundary because there is no entropy or clock input (`V-011`).
6. Recording commit/full-card semantics are underspecified across the interrupt-safe ring and service loop (`V-012`, `V-013`).

I have not inspected engine implementation, implementation PRs/diffs, or implementation issues while producing these findings.

### Still needed before WP test implementation

Please provide when available/frozen:

- WP-10 acceptance criteria
- WP-11 acceptance criteria
- revised/frozen TAPEFS and engine API specs after PM disposition of adversarial findings

No clarification from the user is required for the current spec-review pass.

## 2026-08-31 — Startup note (superseded)

At verification startup the required spec documents were not yet available. They have now been received as DRAFT-1 review copies; see above.

## 2026-09-01 — PM Decisions 001-R received and controlling

Received PM Decisions 001 and the superseding PM Decisions 001-R. I am treating 001-R as controlling. PM accepted all 22 DRAFT-1 findings in some form: sixteen as written, three with a different fix, two moot, and one as a charter defect rather than a spec defect. No finding was rejected.

Per 001-R, I have stopped reviewing DRAFT-1 and will wait for full replacement DRAFT-3 specs. When they arrive, review priority is: re-spool destination disjointness, two-phase promote, duplicate's WRITE_IN_PROGRESS protocol, and superblock generation/recovery. WP-10/WP-11 acceptance criteria remain outstanding and are expected in spec/acceptance.md with DRAFT-3.

Authorized pre-DRAFT-3 work has begun:

- tests/fault_block_device.[ch]: caller-owned C99 block simulator with per-block fault ordinals, unflushed-vs-durable media, power-cut rollback, before-block failure, torn-block persistence, and flush failure.
- tests/test_fault_block_device.c: strict-C99 self-test; compiled with -std=c99 -Wall -Wextra -Werror -pedantic and passed locally.
- tests/SUITE-3-INVARIANTS.md: parameterised run-based invariant scaffold, including corrected free-space semantics and the new re-spool/promote invariants.

Independent-review boundary remains in force: CI/tooling/host tooling/firmware/docs requests may be reviewed; engine behavior may be reviewed only after verifier-authored tests for that behavior have landed. A marked engine PR outside that boundary must be declined without reading its diff and escalated to PM.

## 2026-09-01 — Pre-DRAFT-3 capability completion audit

Completed every deliverable that PM Decisions 001-R authorizes before DRAFT-3. The initial block-device scaffold is now paired with a generic exhaustive crash runner. A clean trace is replayed for every individual block in batched writes with 0 through 512 landed bytes, and at every flush failure. Each case resets the fixture, simulates the operation and power cut, remounts, invokes independent invariant hooks, and emits a deterministic case record. The self-test's two writes/two flushes produce 1,029 passing cases.

The Suite 3 document now specifies parameterized geometry, consecutive-run bounds, generator/replay/shrinking obligations, independent-oracle rules, corrected free-space reachability, and re-spool/promote crash properties. Exact media decoding and operation adapters remain intentionally unimplemented until DRAFT-3 supplies their normative definitions.

See CAPABILITY-STATUS.md for the complete audit. The only remaining items are input-blocked: DRAFT-3 adversarial review and WP-10/WP-11 acceptance tests from spec/acceptance.md.

## 2026-09-02 — PM Decisions 002 and DRAFT-3 review

Received and preserved verifier-side copies of PM Decisions 002, `tapefs-v1.md` DRAFT-3, `engine-api.md` DRAFT-3, and `acceptance.md` DRAFT-1. Everything previously listed as missing has now been delivered.

The clean whole-document adversarial pass is filed at `findings/spec-review-draft3.md`. It reports 4 blockers, 11 majors, and 1 question. The format is not ready for freeze. Highest-priority findings are:

1. `last_chunk_id` can wrap in u32 before the Side A/store bounds checks (`V3-001`, blocker).
2. Promote phase 2 can overwrite chunks still referenced by the live B index (`V3-002`, blocker).
3. Re-spool's downward second pass is not necessarily disjoint from the first-pass live copy (`V3-003`, blocker).
4. Geometry equality permits the last audio chunk to overlap the mirror superblock (`V3-004`, blocker).
5. Index-slot generation selection is absent, so mount/recovery is not deterministic (`V3-005`).
6. WP-10's universal oracle contradicts format, promote, duplicate, and the intentional overwrite leak model (`V3-013`, `V3-014`).
7. WP-11 still mandates a mutation of the preroll cache that DRAFT-3 deleted (`V3-015`).

WP-10 is therefore not mechanically testable as written. WP-11's runner, fixture, byte-difference, and live-mutation requirements are testable, but the seventh mutation needs a current target.

The verifier-owned fault block device and exhaustive crash runner remain valid against `engine-api` §3 and pass strict C99 self-tests. `tests/WP10-PLAN.md` and `tests/WP11-PLAN.md` now map the delivered criteria to executable infrastructure and identify only the assertions blocked by open spec findings. The Software Lead's stated `dev_sim` is not yet present under `Digital-Tape/main/tests/`, so no implementation adapter was inspected or imported.

I have not opened `engine/`, an engine implementation branch, an engine implementation diff, or engine implementation issues during this pass.

## 2026-09-03 — PM Decisions 003 and DRAFT-4 review

Received and preserved PM Decisions 003 and the DRAFT-4 TapeFS, engine API, and acceptance documents. PM accepted every DRAFT-3 finding. The directed DRAFT-4 adversarial pass is filed at `findings/spec-review-draft4.md` and reports **1 blocker, 12 majors, and 1 question**.

The freeze blocker is `V4-001`: TapeFS mounts `version_minor > 0` read-only, but the engine state matrix defines write permission only as `dev.write != NULL`. On a physically writable device, v1 mutators are therefore authorized against newer-minor media, defeating the compatibility barrier.

Highest-priority remaining findings:

1. The entry non-overlap scalar “equivalence” is false and circular during B-slot validation (`V4-002`).
2. Promote omits reachable crash states after phase-2 A/B commits, and the A-old/B-phase1 state can make the documented re-run path fail for lack of a second staging run (`V4-003`, `V4-004`).
3. Empty Side B has no re-spool result (`V4-005`), and raw-device format/duplicate lack a complete geometry preflight before destructive writes (`V4-006`).
4. Long operations require repeated calls while the state matrix forbids those calls; commit-in-progress/abort is likewise unreachable through the synchronous API (`V4-007`, `V4-008`).
5. Positive position saturation underflows for a step larger than the timeline, and the fetch/update phase contradicts seek-to-frame semantics (`V4-009`, `V4-010`).

WP-10 now has the correct per-operation shape but is not final-testable until the promote, re-spool, raw-geometry, and blank-format allowed states are completed. WP-11's live mutation list is now suitable, but byte-exact fixtures cannot be frozen until the render phase and portable negative interpolation semantics are resolved.

The verifier crash harness now supports a scenario-specific remount predicate, so `TAPE_ERR_INCOMPLETE` and the single permitted blank-format `TAPE_ERR_BAD_MAGIC` state can be accepted without weakening other scenarios. Its strict-C99 exhaustive self-test still passes 1,029 cases.

The Side-A-only duplicate product decision is coherent and testable; I do not recommend escalating it to Michael absent a contrary product requirement.

I have not opened `engine/`, an engine implementation branch, an engine implementation diff, an implementation issue, or an unlanded implementation artifact during this pass.

## 2026-09-04 — PM Decisions 004/007 and DRAFT-5 review

Received PM Decisions 004, PM Decisions 007, the DRAFT-5 three-file bundle, and its `spec/VERSION.md` manifest. All three supplied hashes match. The independent convergence assessment was read solely as PM context and was not treated as normative or copied into this repository.

The clean DRAFT-5 pass is filed at `findings/spec-review-draft5.md`: **2 blockers and 13 majors**. Both blockers are in the later behaviour-freeze scope:

1. A long-operation I/O error returns the instance to ordinary Mounted-idle while media generation remains indeterminate, permitting a subsequent mutator to overwrite a generation that may be live (`V5-001`).
2. Duplicate of a valid empty Side A erases the destination, writes zero-length entries forbidden by the format, commits `VALID`, and can return success with an unmountable cartridge (`V5-002`).

No blocker was found in the Phase 0 candidate sections, so PM-004's narrow blocker-only signature condition is clear. Those sections still contain eight major defects, including reverse-from-end phase, C99 integer-promotion, warm-pointer safety, absent-B operation state, and an impossible `tape_tell` error result. Golden PCM remains blocked.

WP-10, WP-11, and WP-12a are each **not testable as written for final acceptance**. Their implementation-independent infrastructure remains valid; the exact blockers are mapped in the findings file and the updated plans.

At review time, canonical `mmsanders/Digital-Tape` `main` still carried TapeFS DRAFT-3, engine API DRAFT-3, acceptance DRAFT-1, and no `spec/VERSION.md`. The exact DRAFT-5 files here are courtesy copies until the mechanical canonical-bundle PR lands.

I have not inspected engine implementation, an implementation branch/diff, implementation issues, or unlanded implementation artifacts.

## 2026-09-05 — PM Decisions 005/008 and DRAFT-6 review

Received PM Decisions 005 and 008 and the DRAFT-6 three-file bundle. The supplied TapeFS, engine API, and acceptance files hash exactly to the manifest now published on canonical `mmsanders/Digital-Tape` `main`; canonical `main` was therefore used as authority and the verifier-side DRAFT-5 courtesy bundle was left intact as historical input rather than silently overwritten.

The directed-then-clean DRAFT-6 pass is filed at `findings/spec-review-draft6.md`: **0 blockers and 9 majors**. Six majors touch the Phase-0 freeze candidate (`V6-001` through `V6-006`), so PM-005's raised gate — no blocker and no major in the candidate — is **not met** and I do not recommend signature.

Highest-priority defects are degraded-B recovery of the equal-sequence state (`V6-001`), branch-insensitive and undefined shared sequence headroom (`V6-002`, `V6-003`), `sb_generation` monotonicity contradicting ordinary index-only updates (`V6-004`), an unreachable side-switch acceptance precondition (`V6-005`), and duplicate-destination failure having no conforming return state when the source was Playing (`V6-006`). The later behaviour scope also has incomplete final-primary durability rows and a one-valid-copy boundary-fallback contradiction (`V6-007`, `V6-008`), plus the callback-reentry contradiction in WP-12a (`V6-009`).

**WP-10 is not testable as written** (`V6-002`, `V6-003`, `V6-007`, `V6-008`). **WP-11 is testable as written.** **WP-12a is not testable as written** (`V6-009`). The existing verifier-owned crash and audio-oracle infrastructure remains implementation-independent.

`engine-api` §§6.2, 6.3 and 8 survived independent numerical traces, including reverse −0.5×/−1.0×/−2.0×, extreme rates, empty/one-frame timelines, and the specified floor interpolation identity. No finding is filed against those sections. The DRAFT-6 arithmetic/phase prerequisite for golden PCM is therefore clear; fixture promotion remains subject to the existing human-listening and PM-approval policy.

I did not open `engine/`, an engine implementation branch or diff, implementation issues, or any unlanded implementation artifact during this pass.
