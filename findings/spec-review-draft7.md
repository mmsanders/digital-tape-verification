# DRAFT-7 adversarial specification review

Review target: the canonical DRAFT-7 bundle published on `mmsanders/Digital-Tape` `main` (`spec/tapefs-v1.md`, `spec/engine-api.md`, `spec/acceptance.md`) under `spec/VERSION.md`, plus PM Decisions 006 and 009 received 6 Sep 2026. The supplied courtesy copies hash exactly to the canonical manifest: TapeFS `94f385272641654819c5a2d7dd4dd6217629cab32a019182522ae423c715a95f`, engine API `cbf34cccfc08fa891f9e8be667381d4c4e6d8d7831b5aaf7e988ffe7d02e4724`, acceptance `0213726b98875ee6b48bd4d2a50eb67353245f19b07a41fbfe0d0a95995200a8`.

Method: directed pass in PM-006 order — §5.5 running `next_sequence`, every §4.5 branch, §9.5/§9.6 raw-destination barrier ordering, the degraded-B/FAULTED matrix overrides, and §9.3.4 under §8.1's two durability models — followed by a clean whole-document pass. The sequence table was independently recomputed for FRESH allocating/adopt-in-place, all RESUME entries, and both re-spool passes. No engine implementation, implementation branch/diff, implementation issue, or unlanded implementation artifact was inspected.

Summary: **1 blocker, 3 majors, and 1 documentation question. DRAFT-7 does not meet the Phase-0 freeze standard.** The blocker (`V7-001`) and one major (`V7-002`) touch the freeze candidate. The new §5.5 running counter itself survived the directed traces: FRESH allocating uses four distinct values, adopt-in-place uses three or one as appropriate, RESUME resumes from the re-evaluated maximum without reuse, and two-pass re-spool consumes two successive values. The listed §4.5 counts match the operation bodies, apart from the zero-consumption predicate defect in `V7-002`.

Acceptance verdicts: **WP-10 is mechanically executable as written, but is not sufficient as the final safety/freeze gate until `V7-001` is added as a two-interruption closure case and `V7-002`/`V7-003`/`V7-004` are dispositioned. WP-11 is testable as written. WP-12a is testable as written.** The DRAFT-7 callback exemptions, BUSY persistence, FAULTED override, 45-cell/33-B accounting, and destination-failure return-to-Playing rule now form one executable oracle. The hardware-safety audit contract is also mechanically auditable once measurement packages exist; no hardware raw-data package was supplied in this round, so no hardware pass/fail audit is claimed here.

---

FINDING: V7-001
SEVERITY: blocker
AREA: `tapefs-v1.md` §4.1, §8, §9.3.2–§9.3.4; `engine-api.md` §5 (`needs_repair`), invariant 27; `acceptance.md` WP-10
CLAIM: Ordinary superblock logical updates always write the mirror first, but mount neither repairs nor quarantines a stale-but-structurally-valid lower-generation partner, so a second interruption can destroy the only current superblock and roll selection back to metadata that rejects both current Side-A indices.
REPRO: Start with identical valid superblocks at generation `G`, `a_high_water = 1`, stage 0; live Side A in chunk 0; and live Side B as one compact two-chunk run `[2,4)` (`len = 2`). A FRESH promote adopts B in place (`S = 2`), commits its phase-1 A index, then step 4 writes the mirror at generation `G+1`, `a_high_water = 4`, `promote_stage = 1`. Cut power after that mirror is durable but before the primary write. On remount §4.1 selects the newer mirror; the old primary is still structurally valid, so phase 4 does not repair it because repair is restricted to “exactly one” valid copy. Resume promote: step 5 passes because `[0,2)` is disjoint from `[2,4)`, step 6 writes low, step 7 commits A at `[0,2)`, and step 8 commits B there. Now begin step 9. It again writes the mirror first. Tear that mirror block so its CRC fails, then cut power. The only structurally valid superblock left is the stale primary from generation `G`, with `a_high_water = 1`. The two A slots are now the phase-1 staging index ending at chunk 3 and the phase-2 low index ending at chunk 1. §5.2 requires `last < a_high_water`; `3 < 1` and `1 < 1` are both false. Mount therefore returns `TAPE_ERR_NO_VALID_INDEX`, and every defined promote/recovery path requires a successful mount.
IMPACT: Two ordinary cartridge removals/power losses at explicitly permitted write boundaries can turn a previously recoverable promote into an unusable cartridge and make the current Side-A audio unreachable. This violates the highest-priority cartridge-survival invariant. The same root exists after a phase-4 repair failure: mount may succeed with only one current copy, yet mutators remain allowed and the next mirror-first update can tear that copy.
FIX: Make every ordinary logical superblock update preserve the selected/current candidate until the replacement copy is durable — e.g. write the non-selected/stale/invalid partner first and the selected candidate last, with a deterministic tie-break for equal byte-identical copies, as DRAFT-7 already does for raw format/duplicate step 1. Alternatively, require successful restoration of current-generation redundancy before any mutator. Extend mount/`needs_repair` semantics to stale lower-generation partners as needed. Add a WP-10 closure test that seeds each superblock-writing operation from every permitted one-copy/newer-mirror recovery state and injects a second torn write/power loss; the current one-fault-from-clean-fixture enumeration cannot detect this path.

---

FINDING: V7-002
SEVERITY: major
AREA: `tapefs-v1.md` §4.5, §10; `engine-api.md` invariants 29–30; `acceptance.md` WP-10
CLAIM: The branch-exact headroom table correctly gives zero consumption to no-op branches, but the normative availability formula still rejects those branches whenever the current counter itself is `0xFFFFFFFE` or `0xFFFFFFFF`.
REPRO: Craft a mountable cartridge with an empty valid Side B and one structurally valid index at `sequence = 0xFFFFFFFF`; §5.2/§5.3 impose no upper validity bound on the stored sequence. `tape_respool` is the explicit zero-write branch: §9.4 requires `TAPE_OK`, §4.5 says `sequence_needed = 0`, `generation_needed = 0`, and invariant 29 says a branch that writes nothing is not refused for counters it will never consume. The formula nevertheless evaluates `0xFFFFFFFF + 0 <= 0xFFFFFFFD` as false and requires `TAPE_ERR_SEQUENCE_EXHAUSTED`. The same contradiction exists for a NOTHING-TO-DO promote and independently for a selected `sb_generation` of `0xFFFFFFFE`/`0xFFFFFFFF` when generation_needed is zero.
IMPACT: Two conforming implementations can disagree on valid crafted media, and the newly branch-exact zero-write guarantee fails exactly at the reserved boundary values §10 says crafted media can reach. No media is damaged, but the acceptance oracle is incomplete at the exhaustion boundary.
FIX: Define zero-needed headroom as available regardless of the current value, e.g. test each counter only when its `needed != 0`, or explicitly make the reserved stored values invalid at mount (which would change the stated crafted-media model). Add zero-consumption WP-10 cases at `0xFFFFFFFE` and `0xFFFFFFFF` for both counter domains.

---

FINDING: V7-003
SEVERITY: major
AREA: `tapefs-v1.md` §4.1, §9.5 step 1, §9.6 step 1 and both crash tables; `acceptance.md` WP-10
CLAIM: Raw format/duplicate accept any structurally valid superblock, but step 1's “non-selectable copy first, selected candidate last” barrier is defined only for a mount-selectable candidate and does not define bytes/outcomes for structurally valid media that §4.1 would refuse before `WRITE_IN_PROGRESS`.
REPRO: Two accepted shapes expose the gap. (1) Put structurally valid primary and mirror copies at the same `sb_generation` with different CRC-correct contents. Raw `tape_format`/`tape_dup` do not mount or reject this; yet §4.1 names no selected candidate — it returns `TAPE_ERR_INCONSISTENT` — so step 1 has no normative “selected candidate last” order or canonical template. (2) Give the destination exactly one structurally valid superblock with `version_major = 2`. Step 1 says to write “it” with `state = WRITE_IN_PROGRESS`, a new generation and cleared stage, but does not say to rewrite the version. If that WIP copy becomes durable and power is lost, mount checks `version_major` before `state` and returns `TAPE_ERR_VERSION`, while both raw-operation crash tables classify the post-barrier reusable state as `TAPE_ERR_INCOMPLETE`. An implementation that canonicalises the version to 1 instead would produce the table's result, but those bytes are not specified.
IMPACT: The raw operations have accepted inputs for which their byte-exact first step or permitted remount result is undefined. A WP-10 implementation can either reject a safe implementation or silently narrow the input domain without a spec basis. This is not a cartridge-loss blocker because format/duplicate are already destructive/re-runnable raw-device operations, but their recovery contract is not singular.
FIX: Add an explicit raw-superblock classification for step 1 that covers every structurally valid pair, defines a deterministic template/order when §4.1 would have no candidate, and specifies which admission-prefix fields the WIP barrier writes so the intended remount error is guaranteed. Alternatively add preconditions/refusals for unsupported/inconsistent existing superblocks, with zero writes and corresponding acceptance cases. Add at least foreign-major and equal-generation-divergent destinations to WP-10.

---

FINDING: V7-004
SEVERITY: major
AREA: `tapefs-v1.md` §4 superblock `label`, §9.5; `engine-api.md` §5 `tape_info.label`, §9 `tape_dup`; `acceptance.md` WP-10 duplicate destination shape
CLAIM: A successful duplicate never defines the destination superblock's 32-byte `label`, and the API supplies no destination label argument.
REPRO: Duplicate a source labelled `ALBUM A` onto a reusable destination labelled `OLD TAPE`. §9.5 step 4 normatively assigns state, generation, water line, stage fields, new UUID, epoch and destination geometry, but says nothing about `label`. `tape_dup` has no label parameter. Copying the source label, retaining `OLD TAPE`, or zeroing the field all satisfy the written step while producing different CRC-covered superblocks and different `tape_info.label` after the same successful operation.
IMPACT: A byte-exact operation has multiple observable successful results, including a plausible stale visible label from the cartridge that was just erased. The duplicate acceptance oracle checks UUID/audio/layout but cannot distinguish these implementations.
FIX: Make the label assignment part of the step-4 normative state — for example explicitly copy the source label, explicitly blank it, or add a caller-supplied destination label — and add the chosen bytes to the duplicate destination-shape acceptance case.

---

FINDING: V7-005
SEVERITY: question
AREA: `engine-api.md` §10
CLAIM: The paragraph after the state matrix says `tape_service` is “always allowed,” while the FAULTED override row and its preceding normative text require `TAPE_ERR_FAULTED` from `tape_service` specifically.
REPRO: Enter FAULTED after an indeterminate mounted-device write. The row at §10 marks service `F`, §7.2 explains that service is forbidden because it can touch indeterminate media, and WP-12a tests that exact result. The later sentence says `tape_service` is always allowed because it clears owed frames.
IMPACT: The executable oracle is otherwise singular — table, §7.2 and acceptance agree — so this does not block WP-12a. But the stale sentence points directly at the unsafe behavior V5-001's quarantine was introduced to prevent.
FIX: Documentation-only: qualify the sentence as applying to every non-FAULTED mounted row, or state the FAULTED exception explicitly. No state-table change is needed.
