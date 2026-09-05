# DRAFT-6 adversarial specification review

Review target: the canonical DRAFT-6 bundle published on `mmsanders/Digital-Tape` `main` (`spec/tapefs-v1.md`, `spec/engine-api.md`, `spec/acceptance.md`) under `spec/VERSION.md`, plus PM Decisions 005 and 008 received 5 Sep 2026. The three supplied courtesy copies hash byte-for-byte to the canonical manifest: TapeFS `696ec41c62ec02250455a1ec8ba1afad01e4aaeb84cd5fe2914c9bf5d3c98056`, engine API `4faabc9135d30355ca029afacf2ea8069da4811a1df61e167a6e1fae9337f6fd`, acceptance `f470442d712f1f5ebe96dd7d31705a449338e143b427248e9909e617173bf086`.

Method: directed review in PM-005 order — `FAULTED`, four-phase mount/degraded-B, every §4.5 headroom row, §8.1 and duplicate/format recovery, §6.2/§6.3 flag arithmetic — followed by a clean whole-document pass and independent numerical transport traces. No engine implementation, implementation branch/diff, implementation issue, or unlanded implementation artifact was inspected.

Summary: **0 blockers, 9 majors. DRAFT-6 does not meet the Phase-0 freeze standard.** Six findings touch the freeze candidate (`V6-001` through `V6-006`), so the required “no blocker and no major in candidate sections” signature condition is not met. The highest-priority defects are the degraded-B recovery hole, path-insensitive/undefined counter semantics, an invariant that makes ordinary index-only updates nonconforming, and two new state-transition contradictions around side switching and duplicate failure.

`engine-api` §6.2, §6.3 and §8 survived the directed pass and independent traces at −0.5×, −1.0×, −2.0×, both extreme rates, empty/one-frame timelines, and the stated interpolation floor identity. **No finding is filed against those three sections.** On the PM's stated condition, the arithmetic/phase prerequisite for freezing golden PCM is therefore clear; fixture promotion still remains subject to the WP-11 listening/approval policy.

Testability verdicts: **WP-10 — not testable as written** (`V6-002`, `V6-003`, `V6-007`, `V6-008`); **WP-11 — testable as written**; **WP-12a — not testable as written** (`V6-009`).

---

FINDING: V6-001
SEVERITY: major
AREA: `tapefs-v1.md` §§4.2, 4.4, 5.3, 9.2; `acceptance.md` WP-06f
CLAIM: Degraded-B includes the equal-sequence `TAPE_ERR_INCONSISTENT` case, but `tape_reset_side_b` assumes degraded-B means neither B slot is valid and its prescribed B0 write does not necessarily recover the side.
REPRO: Let Side A's live index have `sequence = 10`. Make B0 and B1 both individually valid at `sequence = 500`, with different valid entry arrays. §5.3 makes Side B unselectable with `TAPE_ERR_INCONSISTENT`; §4.2 therefore mounts Side A in degraded-B and §5.3 says this state is recoverable by `tape_reset_side_b`. §9.2 instead states that “neither B slot is valid,” chooses B0, and writes it at “the cartridge's highest live sequence + 1.” With no live B, that is 11 under the text's own terminology. B1 at 500 remains valid and wins §5.3 on the next selection, so the reset did not recover B. The same defect applies to a stage-1 + degraded-B mount after its clearing write.
IMPACT: A recovery call expressly promised to repair either Side-B selection error can return success while leaving the damaged generation selected on remount. The current-session view and remounted view can disagree about which B generation is live. This is a freeze-candidate recovery/state defect, even though the equal-sequence starting state itself denotes media fault or an implementation bug.
FIX: Split degraded-B's two causes in the recovery algorithm. For the equal-sequence case, choose a deterministic destination and issue a sequence strictly above every valid B candidate and the live A sequence, with §4.5 exhaustion handled before any write; or explicitly make equal-sequence B non-recoverable and change §5.3/§4.2/WP-06f accordingly. Do not retain the false “neither slot is valid” premise.

---

FINDING: V6-002
SEVERITY: major
AREA: `tapefs-v1.md` §§4.5, 9.3, 9.4, 10; `engine-api.md` invariants 29–30; `acceptance.md` WP-10
CLAIM: The §4.5 sequence-headroom table reserves worst-case commits even on branches whose normative result consumes fewer or zero sequences, contradicting the promised per-operation preflight and the explicit empty/no-op outcomes.
REPRO: Three independent branches show the table is not the operation actually specified. (1) Empty Side B re-spool is unconditionally `TAPE_OK`, zero writes (§9.4; invariant 30), but the table requires two sequences; at live sequence `0xFFFFFFFD` it therefore returns `TAPE_ERR_SEQUENCE_EXHAUSTED` instead of the required no-op. (2) RESUME at promote step 5 whose `[0,len)` overlaps the live staging run declines by writing only the clearing superblock; it consumes **zero** sequences, but the table reserves two. At `0xFFFFFFFC` the table refuses a completion that needs no index commit. (3) A FRESH promote whose phase 2 is predictably going to decline consumes two phase-1 sequences, not four; from `0xFFFFFFFB` it can safely commit `0xFFFFFFFC` and `0xFFFFFFFD`, yet the four-sequence row refuses before the first write.
IMPACT: Valid cartridges near the defined counter boundary are refused even when the specified operation can complete without writing a forbidden sequence. The empty re-spool case directly contradicts invariant 30 and its acceptance criterion; the RESUME case can strand a stage-1 cartridge solely because the preflight counted commits that the chosen branch will never execute. WP-10 cannot have a single counter-boundary oracle from the current table.
FIX: Make headroom a branch-exact classification performed before the first write: explicit empty re-spool 0/0; promote FRESH-success versus FRESH-decline; RESUME-step-5-success versus step-5-decline; and the existing step-8/step-9 cases. Reserve only commits the already-decidable branch will actually perform. Keep all arithmetic in 64-bit.

---

FINDING: V6-003
SEVERITY: major
AREA: `tapefs-v1.md` §§4, 5.3, 8; `engine-api.md` invariant 7 and invariant 29; `acceptance.md` WP-10
CLAIM: The global sequence counter used by §4.5 and by every `sequence + N` commit has no normative definition of its current value; `live_sequence` appears only in the headroom formula.
REPRO: Mount Side A with live A `sequence = 10` and live B `sequence = 500`, a perfectly valid state because the counter is shared across sides and later B edits may have advanced it. §4.5 evaluates `(uint64_t)live_sequence + needed`, but no section defines `live_sequence`. Promote from the Side-A mount then says to commit A at `sequence + 1` and B at `sequence + 2` without naming the base. A side-local reading writes 11/12; B's old valid slot at 500 still wins §5.3, and after the phase-1 superblock lands the stage oracle can see A at the staging generation but B at the old generation and reject the cartridge. A global reading based on 500 writes 501/502 and works. Both source values are present in the mounted state; the reference algorithm never selects one.
IMPACT: The counter-exhaustion gate and the on-media generation selected after a cross-side operation depend on an undefined scalar. The prose “monotonic per cartridge, shared across all four slots” strongly suggests a global maximum, but the document's stated rule is that ambiguity is a defect and the tests need an executable oracle, not an inference.
FIX: Define the current cartridge sequence after §5.3 selection, for example `live_sequence = max(live_A.sequence, live_B.sequence)` when both are selectable and the appropriate deterministic value in degraded-B, and state every commit as an increment from that scalar. Feed the same scalar to §4.5. Cover unequal A/B live sequences in WP-06/WP-10.

---

FINDING: V6-004
SEVERITY: major
AREA: `tapefs-v1.md` §4.1/superblock semantics; `engine-api.md` invariant 7; `tapefs-v1.md` §4.5
CLAIM: The freeze-candidate invariant says `sb_generation` strictly increases across successive logical updates, while the normative headroom table and commit protocol specify ordinary logical updates that consume zero superblock generations.
REPRO: Format a cartridge (`sb_generation = 1`), mount Side B, record frames, service them durable, and commit the B index under §8 with `promote_stage == 0`. The operation is a logical update and increments `sequence`, but §8 writes no superblock and §4.5 explicitly gives `tape_arm`/commit zero `sb_generation` unless stage clearing applies. The quiescent cartridge therefore still has `sb_generation = 1`, violating engine invariant 7's requirement that both `sequence` and `sb_generation` “strictly increase across successive logical updates.” `tape_reset_side_b` and ordinary re-spool have the same contradiction.
IMPACT: Invariant 7 is declared assertable at any quiescent point, so a verifier implementing it literally fails every ordinary recording/reset/re-spool that does not clear a promote stage. Conversely, incrementing the superblock to satisfy the invariant adds writes and counter consumption not present in the operation algorithms or §4.5. The candidate cannot be frozen with both contracts normative.
FIX: Separate the counters' domains in the reference invariant and field definition: `sequence` advances on every index commit; `sb_generation` advances only on logical **superblock** updates (stage set/clear, promote water-line updates, WIP invalidation, etc.), with repair excluded. Or change the operation algorithms/headroom table to actually update the superblock on every logical update; the former is substantially smaller and matches the current protocols.

---

FINDING: V6-005
SEVERITY: major
AREA: `engine-api.md` §§5, 6, 10; `acceptance.md` WP-08
CLAIM: WP-08's required side-switch flag/ring regression starts from a state in which `tape_set_side` is forbidden by the normative state matrix.
REPRO: WP-08 requires a non-empty Side A “at frame 1000 with `at_end` set,” then calls `tape_set_side(B)` and inspects the transition. On a non-empty timeline, §6.3 sets `at_end` by forward rendering at the end while `rate_q16_16 != 0`; that is the §10 **Playing** row, where `set_side` is `TAPE_ERR_BUSY`. `tape_set_rate(0)` cannot make the setup idle while preserving the flag because `tape_set_rate` clears both endpoint flags. Mount and seek also clear them. There is no public path to the stated non-empty idle precondition. The criterion additionally wants a non-zero rate for the first post-switch render; that part is reachable only by setting the rate *after* a successful idle side switch.
IMPACT: The new V5-013 regression cannot be executed as written, so the freeze-candidate transition's endpoint-flag clauses have no black-box acceptance path. A test can either obey the matrix and lose the required precondition, or obey WP-08 and receive `TAPE_ERR_BUSY` before the transition under test.
FIX: Either permit `tape_set_side` from Playing and define the transport consequence, or split WP-08 into reachable tests: exercise ring invalidation from an idle side switch then set a non-zero rate before rendering; separately remove or replace the impossible “flag set before side switch” assertion unless the state matrix provides a way to reach it.

---

FINDING: V6-006
SEVERITY: major
AREA: `engine-api.md` §§7.2, 9.1, 10
CLAIM: The duplicate-destination failure exclusion requires a return to `Mounted, idle`, but `tape_dup` is allowed to start while Playing and no failure transition changes its non-zero playback rate.
REPRO: Start in the Playing row with `rate_q16_16 != 0`, then call the permitted `tape_dup`. While Dup is in progress, `tape_set_rate` is BUSY, so the rate remains non-zero. Make a destination `dev_write` fail. §7.2 correctly excludes the source from FAULTED, but then says the operation “returns to Mounted, idle.” If the engine leaves the rate untouched, the instance is Playing by §10, not idle. If it silently sets the rate to zero to satisfy the named state, it stops the source audio — the exact user-visible effect the exclusion's rationale says it is avoiding — and no algorithm authorises that rate change. §9.1's generic non-fault error transition has the same “Mounted, idle” wording.
IMPACT: There is no single conforming post-error state for a duplicate started during playback. Implementations can stop audio, resume Playing, or invent another transition, and WP-12a currently does not distinguish them.
FIX: Define long-operation termination as returning to the underlying transport state that existed while the operation ran: Playing if the retained rate is non-zero, otherwise Mounted-idle. State explicitly that a destination-only duplicate failure does not alter source position/rate/ring. Add a Playing-source destination-failure case.

---

FINDING: V6-007
SEVERITY: major
AREA: `tapefs-v1.md` §§8.1, 9.5, 9.6; `acceptance.md` WP-10
CLAIM: The rewritten duplicate/format crash tables still omit the completed-cartridge outcome when the final primary `VALID` superblock write lands before its flush (or tears invalid), contrary to §8.1's durability convention.
REPRO: On reusable duplicate media after step 1, both superblocks hold higher-generation `WRITE_IN_PROGRESS`. In step 4 the mirror is replaced and flushed as `VALID`, generation 1, while the primary WIP still wins, so remount is incomplete. Now begin the final primary write. If write-through persistence lands the new primary before its flush, both copies are generation-1 `VALID` and the copy is complete. If WP-10 injects a torn primary write, the primary CRC fails and the already-valid mirror is selected, also yielding the completed copy. The §9.5 row “Inside step 4, reusable destination” permits only `TAPE_ERR_INCOMPLETE`. Format has the same transition at step 5 but has no row for “inside step 5” at all: it jumps from “before step 5 = INCOMPLETE” to “after step 5 = new cartridge.”
IMPACT: §8.1 says every between-write-and-flush boundary admits both durability outcomes, while the operation tables reject/omit one of them. A conforming write-through implementation and the required torn-write harness can produce a safe completed cartridge that the normative table says is not permitted. WP-10 therefore lacks one consistent boundary oracle.
FIX: Split the final superblock step into mirror and primary write/flush boundaries in both tables. At the final primary write, permit `INCOMPLETE` if the old WIP primary remains durable and the completed cartridge if the new primary is durable or the primary is torn/invalid leaving the final mirror selected.

---

FINDING: V6-008
SEVERITY: major
AREA: `tapefs-v1.md` §§9.5–9.6 boundary fallback; `acceptance.md` WP-10
CLAIM: The high-generation boundary fallback always zeroes the mirror first and claims the old cartridge remains mountable, but raw format/duplicate accept reusable media whose mirror is the **only** structurally valid superblock copy.
REPRO: Start with a reusable destination where the primary superblock is CRC-invalid and the mirror is the sole structurally valid copy at `sb_generation = 0xFFFFFFFD`. This is a recoverable cartridge under §4.1; a writable mount would normally repair it, but `tape_format`/`tape_dup` take a raw device and do not mount first. Their boundary fallback writes zeroes to the mirror first. Cut power after that flush and before the primary write. Both copies are now structurally invalid, so remount returns `TAPE_ERR_BAD_MAGIC`. Both §9.5 and §9.6 tables instead say “the old cartridge, unchanged — one copy is still structurally valid.” WP-10 permits `BAD_MAGIC` for duplicate only when the destination was blank, and for format only in the blank-media case; neither reusable-media oracle admits this result.
IMPACT: The specified fallback itself generates a recovery state forbidden by both its table and WP-10, from an input the raw operations expressly accept. This is exactly the counter-boundary case WP-10 is required to exercise, so WP-10 cannot be made green without choosing which normative rule to violate.
FIX: Select the zeroing order from the valid-copy set: if exactly one copy is valid, zero the invalid partner first and the valid candidate second; if both are valid, zero the non-selected/lower copy before the selected candidate. Alternatively explicitly permit reusable `BAD_MAGIC` after fallback begins and change the WP-10 state sets, but that weakens the currently stated recoverability guarantee.

---

FINDING: V6-009
SEVERITY: major
AREA: `engine-api.md` §9.1; `acceptance.md` WP-12a; engine invariant 28
CLAIM: WP-12a requires every callback re-entry to return `TAPE_ERR_BUSY`, including four calls the engine explicitly requires to remain allowed, and §9.1 separately says a BUSY return from the matching continuation both preserves and terminates the operation.
REPRO: During a promote progress callback call `tape_render`, `tape_status`, `tape_get_info`, and `tape_tell`. Engine §9.1 and invariant 28 exempt all four from the no-reentry BUSY rule so audio/status remain available; WP-12a says a callback that attempts **every engine call** “must receive `TAPE_ERR_BUSY` from each.” No implementation can satisfy both. Then re-enter `tape_promote` itself: §9.1's no-reentry rule says BUSY with **no state change**, but the later termination rule says *any return from a continuation call to the operation's own function other than `TAPE_OK` and `TAPE_ERR_INVALID_ARG` ends the operation*. Its next paragraph protects BUSY only when returned to an “other” call, not the matching reentrant continuation.
IMPACT: WP-12a remains mechanically untestable and the active operation's fate under the exact V5-014 regression is contradictory. One reading keeps the operation intact, another ends it, while the acceptance text additionally rejects the four intentional exemptions.
FIX: Make callback re-entry a first-class exception to the continuation-termination paragraph: BUSY from any prohibited callback re-entry performs no state change and never ends the operation. Change WP-12a to expect the four read/render exemptions to succeed and every other same-instance call — matching continuation included — to return BUSY. Then assert the next ordinary continuation advances the same operation.

---

## Freeze impact

The Phase-0 candidate is **not ready for signature** under PM Decisions 005's raised gate. Candidate-scope majors are:

- `V6-001` — degraded-B recovery does not cover the equal-sequence state it promises to recover;
- `V6-002` — §4.5 headroom is not branch-exact and contradicts zero-write/no-op behavior;
- `V6-003` — the shared live sequence base is undefined in the reference algorithm;
- `V6-004` — `sb_generation` monotonicity contradicts ordinary index-only updates;
- `V6-005` — the new side-switch acceptance regression is unreachable under the matrix;
- `V6-006` — the new duplicate-destination FAULTED exclusion has no conforming transition when duplication began from Playing.

No blocker was found in the candidate or later behaviour scope. This is progress relative to DRAFT-5, but the raised standard is not “no blocker”; it is a clean blocker/major pass on the candidate, and this bundle does not have one.

`engine-api` §6.2, §6.3 and §8 are clean in this pass. The verifier may proceed with the DRAFT-6 golden arithmetic and the finite WP-11 portability runner without treating implementation output as an oracle. This does **not** freeze the rest of the candidate and does not waive the human-listening/PM-approval fixture policy.

## Acceptance testability

- **WP-10: NOT testable as written.** The headroom oracle is branch-inconsistent (`V6-002`) and lacks a defined shared sequence base (`V6-003`); the required dual-durability/torn-write final-primary outcome conflicts with the §9 tables (`V6-007`); and the reusable high-generation fallback produces `BAD_MAGIC` that the required allowed-state sets forbid (`V6-008`). Existing verifier-owned enumeration/harness infrastructure remains valid; operation predicates must wait for disposition.
- **WP-11: testable as written.** The DRAFT-6 interpolation proof and finite differential gate are mechanically finite; the warm-pointer cases are ordered; the reverse/endpoint phase algorithm is internally consistent in this pass. The independent verifier oracle already computes floor division without using the engine formulation.
- **WP-12a: NOT testable as written.** Its callback re-entry result contradicts §9.1/invariant 28, and §9.1 itself does not consistently say whether the matching reentrant BUSY terminates the operation (`V6-009`). The corrected cell count, zero-budget rule, and FAULTED row are otherwise mechanically testable.

## Implementation-independence statement

This review was completed without opening `engine/`, an engine implementation branch or diff, implementation issues, or any unlanded implementation artifact. The only `Digital-Tape` repository content consulted was the canonical published DRAFT-6 specification manifest needed to establish authority/version identity. All counterexamples were derived from the normative documents and verifier-owned reference reasoning.
