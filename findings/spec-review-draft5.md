# DRAFT-5 adversarial specification review

Review target: the three files identified by `spec/VERSION.md` as DRAFT-5 (`tapefs-v1.md`, `engine-api.md`, and `acceptance.md`), plus PM Decisions 004 and 007, received 4 Sep 2026. The supplied SHA-256 values match all three reviewed files exactly. The independent convergence assessment was read as PM-only context and was not treated as normative authority or republished here.

Method: targeted closure review followed by a clean whole-document pass. The pass began with `promote_stage`, both-side mount, duplicate, the three in-progress state rows, render/interpolation, and interval disjointness, then covered the remaining API, operation, acceptance, and publication contracts. No engine implementation, implementation branch, implementation diff, implementation issue, or unlanded implementation artifact was inspected.

Summary: **2 blockers and 13 major findings. DRAFT-5 is not ready for the second behaviour freeze.** Neither blocker is in the Phase 0 candidate sections, so the PM's narrow “no blocker in the candidate” signature condition is met; however, candidate sections still contain eight major defects, and byte-exact goldens remain blocked. The later behaviour scope contains both blockers.

---

FINDING: V5-001
SEVERITY: blocker
AREA: `engine-api.md` §9.1, §10; `tapefs-v1.md` §8–§9.4; `acceptance.md` WP-12a
CLAIM: A long-operation continuation that returns `TAPE_ERR_IO` is required to put the instance back in ordinary Mounted-idle even though the specification simultaneously says the selected on-media generation is indeterminate until remount.
REPRO: Start re-spool with old B at `[10,12)` and pass-1 destination `[12,14)`. Let the new B header write complete, then make its flush return failure. The header may or may not be durable. Section 9.1 ends the operation and enables every Mounted-idle mutator; WP-12a tests only that unmount succeeds. If the instance retains the old B/free pointer while the new header is durable, an immediate recording may allocate chunk 12 and overwrite the now-live re-spooled generation. The inverse durability outcome requires the old generation. The instance cannot select between them without rereading media.
IMPACT: A recoverable I/O error followed by an API call expressly permitted by the state matrix can overwrite live audio and corrupt the cartridge. “The next mount resolves it” is not a safety rule while the API permits mutation before that mount.
FIX: On an indeterminate write/flush failure, enter a poisoned/recovery-required state that permits only status and unmount, or synchronously reread and select the durable generation before returning to Mounted-idle. Add WP-12a cases that attempt every idle mutator after ambiguous failures in both durability modes and prove zero unsafe writes.

---

FINDING: V5-002
SEVERITY: blocker
AREA: `tapefs-v1.md` §9.5; `engine-api.md` invariants 6, 17; `acceptance.md` WP-10 duplicate oracle
CLAIM: Duplicating a valid empty Side A passes every precondition but writes a forbidden zero-length entry, then commits a valid destination superblock.
REPRO: Use a freshly formatted source, whose Side A has `total_frames == 0` and zero entries. Capacity passes and `len_A == 0`. Duplicate step 3 nevertheless defines A0 as one entry `{0, 0, src_A.total_frames}` and B0 as the same shape, so both contain `frame_count == 0`, forbidden by §5.2 and invariant 6. Step 4 then commits `VALID` and the operation can return `TAPE_OK`; the destination has no selectable Side A index.
IMPACT: A successful copy can erase a reusable destination and replace it with an unmountable cartridge. This is direct cartridge loss through a normal, valid source state.
FIX: Define an empty-source branch that writes valid zero-entry A0/B0 slots and `a_high_water = 0`, or refuse before any destination write. Add clean, reusable-destination, and every-crash-boundary empty-copy cases to WP-10.

---

FINDING: V5-003
SEVERITY: major
AREA: `tapefs-v1.md` §4.1–§4.2, §9.3.3; `engine-api.md` invariant 25; `acceptance.md` WP-10
CLAIM: WP-10 and invariant 25 require mount to reject stage-1 media matching no RESUME row, but the normative mount algorithm never performs that validation.
REPRO: Construct two individually valid indices and a CRC-valid superblock with `promote_stage = 1` whose A/B shapes match none of the three rows. Section 4 admits the field value, selects both indices, and completes mount. Only a later `tape_promote` reaches §9.3.3's `TAPE_ERR_INCONSISTENT`, while WP-10 explicitly requires the mount itself to return that error.
IMPACT: Two conforming mount implementations can disagree, the crafted-media oracle has no implementable source in the mount algorithm, and another ordinary operation can clear the stage before the required fault is reported.
FIX: Add RESUME-shape validation to the mount/admission algorithm, with exact error ordering and zero-write behavior, or change invariant 25 and WP-10 to assign the check to `tape_promote`. Add one valid case per row and unmatched crafted cases.

---

FINDING: V5-004
SEVERITY: major
AREA: `tapefs-v1.md` §4.2, §9.3–§9.4; `engine-api.md` §5, §10; `acceptance.md` WP-06f
CLAIM: A Side-A mount with no selectable Side B is deliberately supported, but the state matrix still allows `tape_promote` and `tape_respool`, whose inputs are undefined without a live B index.
REPRO: Mount Side A on media with a valid A and two invalid B slots. Section 4.2 succeeds with `free_next = a_high_water`; `tape_set_side(B)` refuses and `reset_b` can recover. The Mounted-idle row nevertheless marks both promote and re-spool `W`, while their algorithms immediately use `B.total_frames` and B's live entries. No result or zero-write rule covers this state.
IMPACT: Implementations may dereference absent state, silently treat B as empty, perform writes, or invent `TAPE_ERR_NO_VALID_INDEX`; WP-06f cannot distinguish them.
FIX: Add the degraded-B condition to the state model and require `TAPE_ERR_NO_VALID_INDEX` with zero writes from B-dependent operations until `reset_b` succeeds. Exercise promote/re-spool as well as set-side in WP-06f.

---

FINDING: V5-005
SEVERITY: major
AREA: `engine-api.md` §6.3, §8, §11; `acceptance.md` WP-08
CLAIM: Snapping reverse playback from `max_pos` to `max_pos - 1` fixes the first sample but shifts every following sample by one 32.32 least-significant unit, so −1.0× does not emit frames in reverse order.
REPRO: Use mono values conceptually `[0, 1000, 2000]` in each channel, seek/clamp to end, and set rate to `-0x00010000`. The normative loop emits 2000 at `3<<32 - 1`; after subtracting one frame it is at `2<<32 - 1`, which interpolates frames 1 and 2 at `f = 0xFFFFFFFF` and emits 1999, then emits 999. Expected grid-aligned reverse is 2000, 1000, 0.
IMPACT: Reverse playback has a byte-exact phase defect and audible duplicated/shifted samples. Golden fixtures would freeze the defect rather than merely document an endpoint choice.
FIX: Snap to the fixed-point position of the last frame, `(total_frames - 1) << 32`, then apply the existing fetch-before-advance loop. Add a non-linear multi-frame −1.0× golden from end, not only an assertion about the first emitted frame.

---

FINDING: V5-006
SEVERITY: major
AREA: `engine-api.md` §8; `acceptance.md` WP-11 portability gate
CLAIM: The new interpolation formula still performs `b - a` before the cast, so it is not portable to a conforming target with 16-bit `int`.
REPRO: On a C99 implementation where `int16_t` promotes to a 16-bit `int`, choose `b = 32767`, `a = -32768`. In `(int64_t)(b - a)`, the subtraction overflows before conversion; signed overflow is undefined. The document claims portability across every freestanding C99 target and casts only after the unsafe operation.
IMPACT: The same valid samples can produce arbitrary or differing PCM across supported C99 implementations, defeating the byte-exact cross-target contract.
FIX: Cast both operands before subtraction, for example `((int64_t)b - (int64_t)a) * (int64_t)f`. Compile and run the oracle on a toolchain configuration that makes integer-promotion assumptions visible.

---

FINDING: V5-007
SEVERITY: major
AREA: `engine-api.md` §5; `acceptance.md` WP-11 mutation 7
CLAIM: The normative warm-start validation dereferences the optional descriptor before testing it for NULL and never checks whether its payload pointer is NULL.
REPRO: The API explicitly permits `warm == NULL`, but the algorithm first evaluates `warm->start_frame` and `warm->valid_frames` to compute `end`. Separately, pass a non-NULL descriptor with matching metadata, positive `valid_frames`, sufficient `data_bytes`, and `data == NULL`; every listed predicate passes.
IMPACT: A normal cold mount or a malformed retained descriptor can cause undefined behavior or a read from address zero instead of falling back to cold service as promised.
FIX: Branch on `warm == NULL` before reading any field, require `warm->data != NULL`, then perform checked arithmetic. Add both cases to mutation 7 and the mount matrix.

---

FINDING: V5-008
SEVERITY: major
AREA: `engine-api.md` §7, §10; `tapefs-v1.md` §9.1; `acceptance.md` WP-09
CLAIM: The matrix allows commit immediately after arm with no accepted frames, but zero-frame overwrite/overdub/splice semantics are not defined.
REPRO: Mount a non-empty Side B, seek to the middle, `tape_arm(TAPE_REC_OVERWRITE)`, feed nothing, then call `tape_commit`. This is the “Armed, no frames owed” row, where commit is allowed. “Overwrite replaces the timeline from the current position” permits truncating the tail, while an empty commit can equally be a no-op; neither result is selected.
IMPACT: Pressing and immediately releasing record can either preserve or delete the remainder of a recording depending on implementation, and the golden suite has no oracle.
FIX: Define zero-accepted-frame commit per record mode, preferably as a zero-write no-op, or forbid it with a specific result. Add all three modes at start/middle/end to WP-09.

---

FINDING: V5-009
SEVERITY: major
AREA: `engine-api.md` §6, §10
CLAIM: The Not-mounted row requires `TAPE_ERR_NOT_MOUNTED` from every ordinary call, but `tape_tell` returns only `uint64_t` and has no error channel.
REPRO: Call `tape_tell` after init and before mount, or after unmount. The matrix assigns an enum result the function signature cannot return without confusing it with a valid frame position.
IMPACT: Implementations must invent a sentinel, return stale/zero position, or change the ABI; callers and conformance tests cannot agree.
FIX: Change `tape_tell` to return `tape_result` with an output pointer, or state a separate total function contract and exempt it from the Not-mounted row.

---

FINDING: V5-010
SEVERITY: major
AREA: `tapefs-v1.md` §9.5–§9.6 crash tables; `acceptance.md` WP-10
CLAIM: Duplicate and format classify states by whether a flush has completed, assuming a completed-but-unflushed block write cannot already be durable; the block-device contract permits eager persistence.
REPRO: On a write-through-conforming device, let duplicate step 1's mirror WIP write complete and cut power before its flush. The new mirror is durable and mount returns `TAPE_ERR_INCOMPLETE`, not “old cartridge unchanged.” On blank media, let the final mirror `VALID` write complete before its flush; mount can select the completed new cartridge, not only `TAPE_ERR_BAD_MAGIC`. Format has the same two boundaries.
IMPACT: The normative recovery tables and an exhaustive WP-10 runner reject safe outcomes allowed by the device contract, or the runner silently assumes one durability model and misses the other.
FIX: Express rows in terms of which atomic block value is durable, not whether flush was called, and permit the union before successful flush. Run every boundary in both flush-required and write-through modes.

---

FINDING: V5-011
SEVERITY: major
AREA: `engine-api.md` §9.1, §10; `acceptance.md` WP-12a
CLAIM: WP-12a is internally unexecutable: it later calls all 45 cells in the three long-operation rows “B cells,” although only 33 are B, and it requires every smaller-than-work budget to terminate without defining budget zero.
REPRO: Each row has 15 columns: four allowed cells (`render`, `service`, status/info/tell, and the matching continuation) and eleven B cells, for 33 B cells total. The final sentence demands a continuation check “after each of the forty-five B cells.” Separately, `block_budget = 0` is smaller than any non-empty job, and “at most 0 blocks” permits no progress forever while the criterion requires the loop to terminate.
IMPACT: No test suite can satisfy the literal count, and two engines can legitimately disagree on zero-budget termination/error behavior.
FIX: Require all 45 cells exercised but continuation persistence after the 33 B cells. Define zero budget as `TAPE_ERR_INVALID_ARG` with no state change, or explicitly exclude it and add a positive minimum.

---

FINDING: V5-012
SEVERITY: major
AREA: `acceptance.md` WP-11 portability gate
CLAIM: The demanded “full `(b-a,f)` domain” exhaustive comparison is computationally infeasible and the phrase “exhaustive-by-construction sweep” does not define a finite reduction.
REPRO: There are 131,071 deltas and 2^32 phase values, approximately 5.63×10^14 pairs, before running the suite on the embedded target. The criterion names five phase values but simultaneously says full-domain equivalence; sampling those values is not exhaustive, while iterating the literal domain is not a practical gate.
IMPACT: WP-11 cannot have one auditable green result; implementations may claim either a sample sweep or an impossible literal exhaust as compliance.
FIX: Make algebraic/formal equivalence the full-domain proof and define a finite executable boundary/property set, or provide the exact reduction that makes the sweep exhaustive by construction. Keep the two-toolchain golden run as a separate requirement.

---

FINDING: V5-013
SEVERITY: major
AREA: `engine-api.md` §5–§6, §11
CLAIM: `tape_set_side` does not define the new position, endpoint flags, or warm/ring state when the two side timelines differ.
REPRO: Mount Side A at frame 1000 with `at_end` set, where Side B is only 100 frames long, then call `tape_set_side(B)`. The function can retain and clamp the numeric position, reset to zero, or attempt a device-stored resume; it can clear or preserve `at_end`, and it can keep or invalidate buffered frames. The text only says it commits and discards nothing.
IMPACT: The first rendered frame after a side switch and `tape_tell`/status are not byte-exact across implementations; a stale play ring can also expose audio from the old side.
FIX: Add a side-switch state transition defining position/clamp, flags, play-ring invalidation/refill, and `tape_info` changes. Add unequal-length and boundary cases to WP-08.

---

FINDING: V5-014
SEVERITY: major
AREA: `engine-api.md` §9–§10; `acceptance.md` WP-12a
CLAIM: Progress callbacks can re-enter the same long operation, and the state matrix expressly allows that call while no reentrancy contract protects the active invocation.
REPRO: Start `tape_promote` or `tape_dup` with a callback that calls the same function on the same instance with matching stable arguments. The nested call is classified as an allowed continuation, not BUSY. Both invocations can advance and mutate the same continuation state and invoke callbacks recursively.
IMPACT: Conforming implementations may corrupt operation state/media, recurse until stack exhaustion, or reject the nested call; WP-12a cannot choose one and the 8 KiB stack claim is not protected.
FIX: Forbid all re-entry on the same instance while any engine callback is active (return `TAPE_ERR_BUSY` with no state change), or specify a reentrant algorithm. Add a callback that attempts every engine call, especially the matching continuation.

---

FINDING: V5-015
SEVERITY: major
AREA: `tapefs-v1.md` §8–§10; `engine-api.md` invariant 7; `acceptance.md` WP-10
CLAIM: Sequence exhaustion is defined per commit, but multi-commit logical operations do not preflight enough remaining sequence/generation values before their first write.
REPRO: Begin promote with the shared live index sequence at `0xFFFFFFFC`. Phase-1 A can commit at `0xFFFFFFFD`; the required B commit would reach the forbidden `0xFFFFFFFE` and must refuse, after media has already changed. Stage clearing and the multiple superblock/index updates in promote have analogous headroom questions. Format/duplicate also say to increment an existing structurally valid destination generation before resetting the new cartridge to 1, but do not define behavior at the exhaustion boundary.
IMPACT: Near-boundary media can be partially advanced into a state whose required operation can never finish, with unspecified error ordering and WP-10 outcomes. Crafted high counters reach this immediately; 136-year timing is not a validation rule.
FIX: Give every logical operation an exact counter-headroom precondition and zero-write refusal before step 1, or define safe partial exhaustion states and recovery. Add boundary vectors for each operation, including raw reusable destinations.

---

## WP-10 / WP-11 / WP-12a testability verdict

**WP-10 is not testable as written for final acceptance.** Its structure and verifier-owned exhaustive harness remain sound, but the empty-duplicate success state is invalid (V5-002), mount does not implement the unmatched-stage oracle (V5-003), degraded-B operations lack results (V5-004), the format/duplicate tables omit eager-durability outcomes (V5-010), and counter exhaustion lacks allowed states (V5-015). V5-001 additionally requires a post-I/O-error state oracle before crash testing can permit subsequent calls safely.

**WP-11 is not testable as written and golden PCM must not be frozen.** The finite runner, fixture policy, diagnostics, overdub arithmetic, and warm metadata ranges are usable. Reverse-from-end has a phase defect (V5-005), the purported portable interpolation still has a pre-cast overflow on 16-bit-int C99 targets (V5-006), warm validation has two pointer-safety holes (V5-007), and the full-domain “exhaustive” gate has no executable definition (V5-012).

**WP-12a is not testable as written.** Its same-function continuation model is mechanically testable for positive budgets, but the I/O-error transition is unsafe (V5-001), the cell count and zero-budget rule are contradictory/incomplete (V5-011), and callback re-entry is ungoverned (V5-014).

## Freeze impact

- **Phase 0 candidate (`tapefs` §§1–8; `engine-api` §§2–8 and §12): no blocker found.** Under PM Decisions 004/007's explicit blocker-only signature condition, the narrow Phase 0 blocker gate is clear. The candidate nevertheless has major findings V5-003 through V5-009 and V5-013, so it does not meet the convergence assessment's stronger clean-pass standard, and WP-11 bytes should not be frozen.
- **Second behaviour freeze (`tapefs` §9; `engine-api` §10): blocked.** V5-001 and V5-002 are credible cartridge-corruption/loss paths. The first green WP-10 run cannot be meaningful until their state models and oracles are corrected.

## Publication status

The supplied DRAFT-5 blobs authenticate against the supplied manifest. At review time, `mmsanders/Digital-Tape` `main` still published TapeFS DRAFT-3, engine API DRAFT-3, acceptance DRAFT-1, and no `spec/VERSION.md`. Per the manifest, these verifier copies remain non-authoritative courtesy copies until the Software Lead's mechanical bundle PR lands. This is the already-identified publication gap, not a new content finding, but no freeze signature should identify `main` as DRAFT-5 before that landing.
