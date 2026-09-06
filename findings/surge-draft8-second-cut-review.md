# Surge DRAFT-8 second-cut — independent adversarial review

Review target: the user-supplied second-cut surge candidate associated with `mmsanders/Digital-Tape` PR #25. The three supplied spec files hash exactly to the supplied manifest and to the hashes advertised by the current PR packet:

- TapeFS `22dca61503dbfda40abee53a5ab5eeb968cb887da67b4611ae0adcd67e7835a7`
- engine API `537eadc423e1a7bde726d689206b8fe93bef164d57e48e8ff71e07eaf8a7e3a1`
- acceptance `3c7647247b6780be6fa68c6f7649d5bedda10219b2231bd470318e11d0890d53`

**Status boundary:** these are surge-candidate bytes, not a claim that the PM has canonically issued DRAFT-8 on `Digital-Tape/main`. This file therefore remains surge-labelled rather than `spec-review-draft8.md`.

Method: authenticate exact bytes, review the actual spec changes and their cross-document effects, re-trace the previous V8C findings, then run a clean consistency/crash-oracle pass over the candidate and the unchanged high-risk areas. The optional `FOR-VERIFICATION-LEAD.md` was treated only as non-normative context and not as evidence. Current PR #25 description/comments were read only to confirm candidate identity and process boundary. No `engine/` source, implementation diff/branch/issue, PR #20 implementation detail, or unlanded implementation artifact was inspected.

Summary: **0 blockers, 1 major, 1 documentation/coverage question.** The second cut fixes V8C-001 and V8C-002, and it fixes the ordinary-headroom form of V8C-003. One generation-exhausted equal-generation-divergent path remains inconsistent across the Phase-0 §4.6 text, the raw-operation crash tables, and WP-10. Because that contradiction touches `tapefs` §4.6, the standing zero-blocker/zero-major Phase-0 gate is **not yet met**. This is nevertheless the closest candidate so far: the DRAFT-7 cartridge-survival blocker remains closed and no new corruption/loss blocker was found.

Acceptance verdicts: **WP-11 testable as written. WP-12a testable as written. WP-10 is not final-testable as written until V8R2-001 is dispositioned**, because the mandated generation-exhausted equal-generation-divergent raw-destination case still has incompatible permitted outcomes. Generic WP-10 infrastructure and all undisputed cases may proceed.

---

FINDING: V8R2-001
SEVERITY: major
AREA: `tapefs-v1.md` §4.5–§4.6, §9.5 step 1/crash table, §9.6 step 1/crash table; `acceptance.md` WP-10 counter-boundary/equal-generation-divergent oracle and format/duplicate allowed-state sets
CLAIM: The second cut correctly routes ordinary equal-generation-divergent raw destinations through a higher-generation v1 `WRITE_IN_PROGRESS` template, but when the equal generation is already at the §4.5 exhaustion boundary the operation must fall back to zeroing both copies; after the first durable zero, the surviving arbitrary primary is not `TAPE_ERR_INCOMPLETE` and is not necessarily an “unchanged old cartridge,” contradicting the new §4.6 statement and the fallback crash rows.
REPRO: Create a raw format/duplicate destination whose primary and mirror are both structurally valid, byte-divergent, and have the same `sb_generation = 0xFFFFFFFD`. Let all refusal preconditions pass. §9.5/§9.6 classify the shape for the v1 template path, but §4.5 headroom cannot increment the generation, so step 1 takes the generation-exhausted fallback and zeroes both superblock copies, mirror first under the equal-generation tie-break. Cut power after the mirror zero is durable and before the primary zero. The mirror is now invalid and the untouched primary is the sole structurally valid candidate. Because raw classification admitted it on magic+CRC alone, remount can return whatever that primary's own admission/index state implies (`TAPE_ERR_VERSION`, `TAPE_ERR_INCOMPLETE`, `TAPE_ERR_UNSUPPORTED_STATE`, `TAPE_ERR_GEOMETRY`, an index error, or a successful mount). It is not forced to `TAPE_ERR_INCOMPLETE`. Yet candidate §4.6 says that on equal-generation-divergent raw media “a durable first write is `TAPE_ERR_INCOMPLETE`, not an arbitrary surviving copy.” Both raw-operation boundary-fallback tables also call the one-zero state “the old cartridge, unchanged,” which assumes a selected old candidate that this input did not have. WP-10's equal-generation-divergent oracle only names the surviving-copy result for a *torn* first template write; it does not cleanly name the fully durable first-zero fallback state for duplicate, while the format row is broader than the TapeFS table.
IMPACT: The exact counter-boundary shape WP-10 mandates has two incompatible normative stories. An implementation following the required exhaustion fallback cannot satisfy the unconditional §4.6/template claim and the raw crash tables simultaneously. This is not a cartridge-loss blocker: format/duplicate are destructive raw-device operations and the surviving copy is still structurally intact. It is a major because §4.6 is inside the Phase-0 candidate and the first-green-WP-10 behavior gate is not singular at a required injection point.
FIX: Qualify §4.6's equal-generation-divergent template statement with generation headroom. When headroom is unavailable, explicitly route to the §4.5 zeroing fallback and define the first-durable-zero result as **the mount result of the surviving primary**, not “old cartridge unchanged.” Add that exact fallback row to both §9.5 and §9.6 tables and to WP-10's equal-generation-divergent/per-operation allowed-state sets. Preserve non-selectable/partner-first zero order. The ordinary-headroom path should remain the new v1 WIP template path.

---

FINDING: V8R2-002
SEVERITY: documentation / coverage question
AREA: `acceptance.md` WP-06 / WP-06d; `tapefs-v1.md` §4.1 phase 0
CLAIM: TapeFS phase 0 requires `TAPE_ERR_GEOMETRY` with **zero block-device callbacks** for every `block_count <= LBA_CHUNK_BASE`, but WP-06d only forbids out-of-range callbacks for `block_count = 1` and `LBA_CHUNK_BASE`; it explicitly requires no callback at all only for `block_count = 0`. The WP-06 summary also still says §4.1 has “all four phases” even though the candidate now has phase 0 plus phases 1–4.
REPRO: An implementation could call `dev_read(..., LBA 0, ...)` on `block_count = 1`, then return `TAPE_ERR_GEOMETRY`. That violates §4.1 phase 0's “No callbacks / zero reads” ordering but satisfies WP-06d's literal test because LBA 0 is in range and there are zero writes. The same coverage gap exists for `block_count = LBA_CHUNK_BASE` if all reads stay in range.
IMPACT: The spec itself is singular and V8C-001's dangerous `block_count = 0 -> 0xFFFFFFFF` underflow path is directly covered. This does not justify a candidate major. But the acceptance test does not fully prove the new pre-read contract it claims to exercise, so a harmless-but-nonconforming pre-read can pass.
FIX: In WP-06d assert **zero block-device callbacks of any kind** for all three named phase-0 refusal values, not merely zero out-of-range callbacks. Update the WP-06 parenthetical from “all four phases” to “phase 0 plus phases 1–4” (or equivalent).

---

## Disposition checks from the first-cut review

- **V8C-001 — fixed in the spec.** `DEVICE_ADDRESSABLE(block_count) := block_count > LBA_CHUNK_BASE` is evaluated before mount reads; duplicate now evaluates geometry/capacity before destination superblock classification; format already did. No candidate-level pre-read geometry contradiction remains. `V8R2-002` is only acceptance tightening.
- **V8C-002 — fixed.** TapeFS §4.6/§5, engine invariant 7, identity-assignment step text, and WP-10 now agree: step-1 WIP is an ordinary update of the existing cartridge and must increase; the final format/duplicate identity assignment establishes a new cartridge and resets `sb_generation = 1`; monotonicity does not span that boundary.
- **V8C-003 — ordinary path fixed, exhaustion edge remains as V8R2-001.** With headroom, equal-generation-divergent raw media uses mirror-as-partner / primary-as-candidate and the higher-generation v1 WIP template. A durable first template write therefore wins selection and returns `TAPE_ERR_INCOMPLETE`; a torn/non-durable first write is correctly enumerated as the original `INCONSISTENT` state or the surviving primary's own mount result. The only residual defect is when headroom forces the zero-both fallback.
- **V7-001 remains fixed.** Partner-first/candidate-last ordinary superblock updates and stale-partner repair are unchanged, and the two-interruption closure criterion remains present. No repeated-interruption rollback was found.
- **V7-002, V7-004, V7-005 remain fixed.** Zero-needed counters, duplicate source-label copy, and the Faulted `tape_service` exception remain coherent.

## Clean-pass notes (no finding)

- Running `next_sequence`, promote/re-spool branch counts, stage-clearing order, degraded-B recovery, FAULTED override, callback re-entry/BUSY persistence, transport/interpolation arithmetic, and source/destination duplicate-state separation were unchanged by this cut and did not yield a new finding on re-check.
- The supplied manifest matches all three candidate hashes exactly.
- Current PR #25 remains a surge handoff and explicitly says the hashed candidate bytes are not yet canonical `spec/` on the branch; no PM issuance or freeze is inferred from the PR itself.

**Freeze recommendation:** do not call this second cut Phase-0-clean yet because `V8R2-001` is a major touching §4.6. Fixing that one edge without introducing a new candidate major would make the next exact-byte pass a genuine **zero-blocker/zero-major Phase-0 signature candidate**, subject still to PM issuance/signoff. Operations/state remain separately gated on an actual green WP-10; a clean paper pass is not that run.