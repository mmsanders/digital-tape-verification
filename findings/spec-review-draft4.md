# DRAFT-4 adversarial specification review

Review target: `spec/tapefs-v1.md`, `spec/engine-api.md`, and `spec/acceptance.md`, all DRAFT-4, plus PM Decisions 003, received 3 Sep 2026.

Method: clean whole-document review in the priority order from PM Decisions 003. The pass began with entry non-overlap, promote, re-spool, duplicate, the state matrix, and position arithmetic. No engine implementation, engine implementation branch, diff, issue, or review was inspected.

Summary: **1 blocker, 12 major findings, and 1 question. DRAFT-4 is not ready to freeze.** The earlier cartridge-corruption findings are substantially addressed, but the forward-minor read-only rule is not enforced by the API state model, promote has reachable crash generations omitted from both its recovery table and WP-10, and several API contracts still admit two incompatible implementations.

---

FINDING: V4-001
SEVERITY: blocker
AREA: `tapefs-v1.md` §4.1; `engine-api.md` §3, §5, §10
CLAIM: A cartridge with `version_minor > 0` is declared read-only at mount, but every write authorization in the API is defined only by `dev.write != NULL`, so the state matrix permits a v1 engine to mutate newer-minor media.
REPRO: Mount a structurally valid v1.1 cartridge on a device whose `write` callback is non-NULL. TapeFS phase 2 says the mount continues read-only. Engine §3 says the absence of `write` is the one permission mechanism, while §10 defines `W` as `write != NULL`. The mounted-idle row therefore authorizes `reset_b`, `promote`, and `respool`; `arm` is also authorized on Side B. Nothing in the matrix or error definition makes the compatibility read-only state override `W`.
IMPACT: A v1 engine can commit v1 indices or superblocks onto media whose newer minor semantics it does not understand. This defeats the explicit compatibility barrier and can corrupt a cartridge.
FIX: Define one effective-writable predicate, for example `dev.write != NULL && mounted_version_minor == 0`, expose it through `tape_info.writable`, and require every `W`/`W+SideB` cell and repair path to use it. Retain the raw callback check inside `dev_write` as a last-line assertion, not as the complete permission model. Add a v1.1 writable-device test proving every mutator and repair performs zero writes and returns `TAPE_ERR_READ_ONLY` where applicable.

---

FINDING: V4-002
SEVERITY: major
AREA: `tapefs-v1.md` §5.1; `engine-api.md` invariant 20
CLAIM: The proposed scalar “equivalent” test for entry non-overlap is neither equivalent to pairwise physical-frame disjointness nor usable in the stated mount order.
REPRO: Put two one-frame entries at the same physical frame of one chunk. `total_frames = 2`, while the stated capacity expression permits up to `CHUNK_FRAMES`; the scalar inequality passes although the entries overlap. For Side B, the expression also depends on `free_next`, which §7 derives only from the live B index after slot validation, while non-overlap is itself part of deciding whether that slot is valid.
IMPACT: An implementation using the advertised equivalent check can accept overlapping entries. That invalidates the premise behind promote/re-spool reasoning and makes independent mount oracles disagree.
FIX: Delete the scalar equivalence. Define each entry as one checked half-open physical-frame interval, `[(uint64_t)first_chunk_id * CHUNK_FRAMES + start_frame, start + frame_count)`, and require every pair to be disjoint. This is checkable from index metadata without reading chunks. Specify an O(n log n) sort-and-scan or equivalent bounded algorithm if mount-time cost matters. The rule does not forbid legitimate splice trims because disjoint subranges of the same chunk remain allowed.

---

FINDING: V4-003
SEVERITY: major
AREA: `tapefs-v1.md` §9.3 recovery table; `acceptance.md` WP-10 promote oracle
CLAIM: Promote's recovery table omits the reachable phase-2 index generations after steps 7 and 8.
REPRO: Complete phase 1 and pass step 5. After step 7 commits A to `[0,len)`, crash before step 8: A selects the new low generation while B still selects `[S,S+len)`. Crash after step 8 but before step 9: both indices select `[0,len)`, while the superblock still carries `a_high_water = S+len`. Both states pass §5.2. The table instead groups every crash “between 4 and 9” as both sides at `[S,S+len)`.
IMPACT: WP-10 will reject conforming, intact crash states or an implementation will be pressured to hide them. Re-run behavior from those states is also undefined.
FIX: Enumerate boundaries after steps 7 and 8 separately, include the low-A/high-B mixed pair and the both-low/old-high-water state in WP-10, and define how a repeated `tape_promote` resumes each state without another copy.

---

FINDING: V4-004
SEVERITY: major
AREA: `tapefs-v1.md` §9.3 preconditions and resume detection
CLAIM: A crash between phase-1 steps 3 and 4 can make the documented “re-run promote” recovery fail `TAPE_ERR_CARTRIDGE_FULL` even though the only required staging run was successfully written.
REPRO: Choose a valid cartridge with exactly `len` free chunks above the original `free_next = S`. Crash after B commits `[S,S+len)` but before the superblock raises `a_high_water`. Mount falls A back to its old generation but selects B's new generation, so derived `free_next = S+len`. Resume detection rejects the state because A and B differ. The precondition now sees zero tail chunks and refuses before it can reuse or finalize the already durable phase-1 copy.
IMPACT: An interrupted promote can become impossible to complete by the specified re-run path without first performing a different destructive operation. Repeated crashes at this boundary can also consume successive staging runs when extra capacity exists.
FIX: Add a resume detector for the A-old/B-phase1 state that validates the durable B staging run and completes or safely reconstructs phase 1 without allocating another `len` chunks. Include an exact-tail-capacity crash test.

---

FINDING: V4-005
SEVERITY: major
AREA: `tapefs-v1.md` §9.4; `acceptance.md` WP-12
CLAIM: Re-spool has no empty-Side-B behavior, although its postcondition requires one non-empty entry and the format forbids zero-length entries.
REPRO: Call `tape_respool` on a freshly formatted or reset-to-empty Side B. `len = ceil(0 / CHUNK_FRAMES) = 0`. The destination rule admits a zero-length run vacuously, while WP-12 says a completed pass leaves exactly one entry and §5.2 requires every entry's `frame_count >= 1`.
IMPACT: Implementations may no-op, return `TAPE_ERR_INVALID_ARG`, emit an invalid zero-length entry, or claim a completed pass with contradictory state. The crash and golden suites have no unique oracle.
FIX: Define empty re-spool explicitly. Prefer a write-free `TAPE_OK` no-op leaving the valid empty index at zero entries, or mirror promote's `TAPE_ERR_INVALID_ARG`; update WP-12 to exempt or assert that outcome.

---

FINDING: V4-006
SEVERITY: major
AREA: `tapefs-v1.md` §9.5–9.6; `engine-api.md` §9
CLAIM: Raw-device duplicate and format do not state the complete block-count/geometry preflight that must occur before their first destructive write.
REPRO: Call `tape_format` or `tape_dup` with a raw destination whose `block_count` is too small for the fixed index LBAs, the mirror, or `2048 + total_chunks * 1024` blocks. The operations derive chunks from `nominal_length_s`, but neither precondition states the exact 64-bit inequality or error returned before step 1. Duplicate's capacity predicate compares only source frames with derived chunk count, not whether that count physically fits the destination.
IMPACT: A formatter can begin destroying reusable media before discovering impossible geometry, and independent implementations can issue out-of-range I/O or return different errors. WP-10 cannot assert the promised rejection-with-zero-writes behavior.
FIX: Apply the §4.1 geometry arithmetic to the proposed new image against the raw device before any write, including fixed metadata LBAs and the reserved mirror block. Define the error (`TAPE_ERR_GEOMETRY` or `TAPE_ERR_DEST_TOO_SMALL`) and require zero writes on failure for both operations.

---

FINDING: V4-007
SEVERITY: major
AREA: `engine-api.md` §9–10 state matrix
CLAIM: The shared incremental contract requires repeated calls to `tape_respool`, `tape_promote`, and `tape_dup`, while the in-progress state row forbids all three calls.
REPRO: Start any long operation with a budget smaller than its work. Section 9 says subsequent calls drive it to completion and `more_work` remains true. The “Respool / promote / dup in progress” row returns `TAPE_ERR_BUSY` for the continuation call, so no public call can advance the operation.
IMPACT: The three operations cannot complete under the normative state matrix, and adapters cannot encode a conforming call loop.
FIX: Mark the matching operation's continuation call allowed and reject only different long-operation calls, with argument-stability rules; or state that only the first operation call starts work and all continuation occurs through `tape_service`. Make one model normative.

---

FINDING: V4-008
SEVERITY: major
AREA: `engine-api.md` §7 and §10 commit/abort contract
CLAIM: “Commit in progress” and abort-during-commit are unobservable through the synchronous API as specified.
REPRO: `tape_commit(tape *)` has no budget or `more_work`. Section 7 says it executes §8 and returns success only after the final flush. A caller cannot invoke `tape_abort` during that call without concurrency, which the API neither permits nor defines. If `tape_commit` returns before completion, its return value and the mechanism that advances it are unspecified.
IMPACT: One implementation must make commit synchronous, rendering the commit-in-progress row and abort rule unreachable; another can make it asynchronous with invented return/state semantics. State-machine and crash tests cannot choose one.
FIX: Either make commit explicitly incremental (define the initiating return, continuation via `tape_service`, and abort boundary) or remove the in-progress/abort-during-commit state and specify a synchronous commit. Do not rely on concurrent re-entry.

---

FINDING: V4-009
SEVERITY: major
AREA: `engine-api.md` §6 position update; `acceptance.md` WP-08
CLAIM: The positive-rate clamp underflows when one step is larger than the entire timeline, so the advertised saturating update can move position out of range.
REPRO: Use a one-frame timeline (`max_pos = 1 << 32`), position 0, and `rate_q16_16 = INT32_MAX`. Then `s` is about `2^47`, so `max_pos - s` wraps as unsigned. `position > max_pos - s` is false and the code executes `position += s`, leaving `position > max_pos`; the next index is out of range.
IMPACT: A valid API input can bypass the endpoint clamp, leading to out-of-range audio access and cross-target disagreement.
FIX: Compare without subtracting the step from the endpoint: `if (position >= max_pos || s >= max_pos - position) clamp; else position += s`. Add tiny timelines at maximum positive rate to WP-08.

---

FINDING: V4-010
SEVERITY: major
AREA: `engine-api.md` §6, §8, §11; `acceptance.md` WP-08
CLAIM: The stated update/fetch phase skips the frame selected by `tape_seek`, contradicting “seek … lands on the specified frame.”
REPRO: Seek to frame N at 1.0x. Section 6 says the clamp/update is evaluated before each sample is fetched, then §8 fetches `i = position >> 32`; the supplied update advances position by one frame first, so the first rendered frame is N+1. If the intended order is fetch then update, the sentence and pseudocode placement do not state it.
IMPACT: Two conforming renderers differ by one frame at every seek and at stream start, so golden fixtures cannot be frozen byte-exactly.
FIX: State one sample-phase algorithm explicitly: fetch/interpolate at current position, emit, then compute and clamp the next position; or declare the opposite and change the seek criterion. Include the first frame after seek in normative examples.

---

FINDING: V4-011
SEVERITY: major
AREA: `engine-api.md` §5 warm-start validation; `acceptance.md` WP-11 mutation 7
CLAIM: The warm-start containment expression has no checked-width rule and can wrap its 32-bit end point.
REPRO: Supply `start_frame` near `UINT32_MAX` with non-zero `valid_frames`. A direct C evaluation of `start_frame + valid_frames` wraps before testing whether the half-open range contains the 64-bit `resume_frame`. The spec gives checked 64-bit rules for media extents but not this mutation-sensitive descriptor.
IMPACT: A stale or unrelated retained buffer can be accepted for the wrong frame range, exactly the defect mutation 7 is meant to catch; the engine can then read outside the valid retained samples.
FIX: Compute `end = (uint64_t)start_frame + valid_frames`, reject/ignore if `end > total_frames` or overflows the descriptor's permitted range, and test zero length plus arithmetic maxima. If the caller must provide backing byte length independently, add it to the descriptor.

---

FINDING: V4-012
SEVERITY: major
AREA: `tapefs-v1.md` §4–4.1
CLAIM: A CRC-correct superblock with an undefined `state` value mounts as though it were `VALID`.
REPRO: Set `state = 2`, recompute the CRC, and make both copies identical. Structural selection succeeds. Admission rejects only `state == WRITE_IN_PROGRESS`; geometry then passes and mount continues.
IMPACT: Damaged or future state values fail open, allowing reads and writes against media whose transaction state is unknown.
FIX: Require `state` to equal one of the defined values and reject every other value without repair or writes. Add an exact invalid-state case to WP-06.

---

FINDING: V4-013
SEVERITY: major
AREA: `engine-api.md` §8 exact interpolation; C99 portability
CLAIM: The byte-exact formula depends on right-shifting a negative signed integer, which is implementation-defined in C99.
REPRO: Choose `b < a` and non-zero `f`. The product is negative, and `negative_int64 >> 32` may be arithmetic or logical according to the implementation. The prose demands arithmetic shift/flooring, but the normative C expression alone is not portable across the C99 targets the API claims to support.
IMPACT: Desktop and embedded builds may emit different PCM for the same cartridge, violating the cross-target and golden-byte contracts.
FIX: Give a portable floor-division formulation that does not right-shift negative signed values, or explicitly constrain and CI-test every supported compiler's signed-shift behavior. The former better matches the freestanding C99 claim.

---

FINDING: V4-014
SEVERITY: question
AREA: `tapefs-v1.md` §9.6; `acceptance.md` WP-10 format oracle
CLAIM: The blank-format recovery table omits the state after the final mirror is durable but before the identical primary is durable.
REPRO: On blank media, crash after step 4's mirror flush and before step 5 completes. Exactly one structurally valid `VALID` superblock exists, both empty indices are durable, and mount succeeds (repairing primary on a writable device). The table says blank-before-step-4 is `BAD_MAGIC` and after-step-5 is complete, but assigns no outcome to this boundary.
IMPACT: WP-10 needs to know whether this is the completed new cartridge, an allowed repair-needed new cartridge, or a supposedly forbidden intermediate.
FIX: Add the boundary explicitly and permit the new empty cartridge with one valid superblock copy (followed by normal mount repair).

---

## Product-decision check: duplicate

The DRAFT-4 decision to copy Side A only and initialize destination Side B as a mirror of the new A is coherent, testable, and consistent with the stated “music, not sandbox” product model. I do **not** recommend escalating it to Michael absent a contrary product requirement.

## WP-10 / WP-11 testability verdict

WP-10's per-operation structure is the right shape and all stable operations are mechanically testable. It is **not yet testable as written for final acceptance** because the promote allowed-state set omits the reachable post-step-7 and post-step-8 generations (V4-003), the exact-tail rerun path is not defined (V4-004), empty re-spool has no oracle (V4-005), raw-device geometry rejection is missing (V4-006), and blank format omits the one-valid-superblock completion boundary (V4-014).

WP-11's comparison diagnostics, fixture policy, golden families, and seven live mutations are mechanically testable. Golden PCM must not be frozen until the render phase convention (V4-010) and portable negative interpolation rule (V4-013) are resolved. Mutation 7 additionally requires the checked warm-range arithmetic in V4-011.

The verifier-owned fault device and exhaustive enumeration remain valid. The crash harness must allow scenario-specific non-zero remount results (`BAD_MAGIC` and `INCOMPLETE`) rather than treating every non-zero result as an infrastructure failure; that update accompanies this review.
