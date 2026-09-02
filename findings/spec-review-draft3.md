# DRAFT-3 adversarial specification review

Review target: `spec/tapefs-v1.md` DRAFT-3, `spec/engine-api.md` DRAFT-3, and `spec/acceptance.md` DRAFT-1, all issued 2 Sep 2026.

Method: clean whole-document review in the priority order from PM Decisions 002. This was not a delta review against DRAFT-1. No engine implementation, engine implementation diff, or engine implementation issue was inspected.

Summary: 4 blocker findings, 11 major findings, and 1 question. DRAFT-3 is not ready to freeze. The three new storage protocols still have reachable interruption states outside their stated guarantees, and one geometry check permits audio to overlap the mirror superblock.

---

FINDING: V3-001
SEVERITY: blocker
AREA: `tapefs-v1.md` §5.1–5.2; `engine-api.md` invariant 2
CLAIM: The normative `last_chunk_id` expression can wrap before either bounds check, allowing an out-of-range run—and for Side A, a run crossing `a_high_water`—to validate.
REPRO: The operands `first_chunk_id`, `start_frame`, and `frame_count` are all u32. With `start_frame = 131071` and `frame_count = 0xffffffff`, the subexpression `start_frame + frame_count - 1` exceeds `UINT32_MAX`. Even if that subexpression is widened, adding its quotient to a large `first_chunk_id` can overflow u32. The spec requires 64-bit arithmetic for superblock geometry but gives no widening rule here. A direct C transcription therefore wraps before testing `last_chunk_id < total_chunks` or `last_chunk_id < a_high_water`.
IMPACT: A CRC-correct malicious or damaged index can make validation accept a run whose physical extent reaches the Side B sandbox or beyond the device. Rendering may read the wrong audio or issue out-of-range I/O; a later operation can treat the invalid extent as legitimate. On Side A this defeats the central immutability boundary.
FIX: Define the calculation with checked 64-bit intermediates and reject on either addition overflow. For example compute `span = (uint64_t)start_frame + frame_count - 1`, `last = (uint64_t)first_chunk_id + span / CHUNK_FRAMES`, then compare `last` to `total_chunks` and `a_high_water` before narrowing. Add the arithmetic maxima to the normative invalid-media cases.

---

FINDING: V3-002
SEVERITY: blocker
AREA: `tapefs-v1.md` §9.3 phase 2; `engine-api.md` invariant 4; `acceptance.md` WP-10
CLAIM: Phase 2 of promote can overwrite chunks still referenced by the live Side B index before the replacement B index commits.
REPRO: Start with `a_high_water = 1`, a two-chunk B timeline, and a live B run referencing sandbox chunk 1. Phase 1 writes a compacted copy above `free_next`, commits A there, and raises `a_high_water = E`, but it does not change B. Phase 2 then writes the promoted timeline to `[0, 2)`, overwriting chunk 1 while the old B index remains live. Yank before the final B-index commit. Mount can select the old B index, which now references overwritten data; it is neither the pre-promote nor post-promote Side B state.
IMPACT: A power loss during the advertised individually crash-safe second phase can corrupt Side B audio. This violates the cartridge-survival invariant and WP-10's pre/post requirement.
FIX: Make B non-live or redirect it to the phase-1 compacted copy before any phase-2 write can overlap its old references, using an ordered commit that itself has an explicit crash state. Enumerate every A-index, B-index, and superblock boundary. The final protocol must preserve a complete permitted A and B generation at every boundary.

---

FINDING: V3-003
SEVERITY: blocker
AREA: `tapefs-v1.md` §9.4; `engine-api.md` invariants 7, 10
CLAIM: The stated two-pass re-spool does not guarantee that the second, downward destination is disjoint from the first-pass live copy.
REPRO: Let `a_high_water = H`. Start B as a two-chunk alias of A, then edit a small region so most of the timeline still references immutable A chunks below H while one live B entry references newly allocated chunk H. Its compacted length is two chunks and `free_next = H + 1`. The low destination `[H, H + 2)` overlaps live chunk H, so pass 1 correctly writes up to `[H + 1, H + 3)` and commits it. The advertised pass 2 then writes down to `[H, H + 2)`, which overlaps live chunk `H + 1` from pass 1. A yank after overwriting that chunk but before the second commit leaves the first-pass index live and corrupted. More generally, pass 2 is disjoint only if `free_next >= a_high_water + compacted_chunks`; the precondition `free space >= timeline length` does not imply that.
IMPACT: A fragmented but valid cartridge can be corrupted by re-spool despite the destination-disjointness invariant that was meant to close V-002.
FIX: Define destination selection over explicit half-open ranges and check disjointness before every pass. If the safe temporary range does not lie entirely above the intended low range, either retain the first-pass layout, use a protocol with another safe staging generation, or refuse without change. State which cases must succeed and make the capacity precondition match that rule.

---

FINDING: V3-004
SEVERITY: blocker
AREA: `tapefs-v1.md` §3, §4.1 geometry
CLAIM: The geometry inequality permits the last audio chunk to overlap the mirror superblock.
REPRO: The chunk store occupies `[lba_chunk_base, lba_chunk_base + total_chunks * 1024)`, while the mirror occupies block `block_count - 1`. The validator accepts `lba_chunk_base + total_chunks * 1024 <= block_count`. At equality, the last chunk's final block is exactly `block_count - 1`, the mirror block.
IMPACT: The mirror and referenced audio cannot coexist: filling the last accepted chunk overwrites the mirror, while mount repair or any superblock update overwrites the final referenced audio block. Either path corrupts part of the cartridge, and leaving the collision unrepaired removes the intended two-copy protection.
FIX: Reserve the mirror explicitly: require `lba_chunk_base + (uint64_t)total_chunks * CHUNK_BLOCKS <= (uint64_t)block_count - 1`, with a prior `block_count > lba_chunk_base` check. Add exact-equality and one-block-short refusal tests.

---

FINDING: V3-005
SEVERITY: major
AREA: `tapefs-v1.md` §5.2, §8; `engine-api.md` errors and mount lifecycle
CLAIM: There is no normative algorithm for choosing between the two index slots for a side.
REPRO: The document defines per-slot validity and a shared monotonic `sequence`, but never says: choose the only valid slot; choose the higher sequence; or require byte identity when two valid slots have equal sequence. `TAPE_ERR_NO_VALID_INDEX` and the `TAPE_ERR_INCONSISTENT` comment imply such rules, but no rule connects them to A0/A1 or B0/B1. Promote recovery explicitly depends on falling back from a newer invalid A slot to the previous one, which cannot be implemented byte-exactly from §5.2 alone.
IMPACT: Two conforming implementations can mount different generations after the same crash. The crash oracle cannot decide which state is correct, and stale or partially updated audio may be selected.
FIX: Add an index-slot resolution subsection parallel to §4.1, including zero/one/two valid cases, higher-sequence selection, equal-sequence handling, exhaustion comparison, side-specific validation against the selected superblock, and whether any repair is performed.

---

FINDING: V3-006
SEVERITY: major
AREA: `tapefs-v1.md` §4.1; `engine-api.md` `TAPE_ERR_VERSION`
CLAIM: The exactly-one-valid-copy rule orders repair before the version check, while the next paragraph requires an unsupported version to touch nothing and never trigger repair.
REPRO: Mount writable media with one structurally valid v2 superblock and one torn copy. The bullet for exactly one valid says to use it and rewrite the other. The following paragraph says "Only then" check `version_major`, and if it is not 1 return `TAPE_ERR_VERSION`, touch nothing, and never trigger repair. Both orders cannot be followed.
IMPACT: A v1 engine may modify newer-format media even though the compatibility rule expressly forbids that downgrade path. Tests cannot distinguish the required I/O trace.
FIX: Separate resolution from mutation. Select a candidate without writing; validate version, state, and geometry; only a supported, mountable v1 candidate may enter an explicitly ordered repair path. Specify repair flush and error semantics. Clarify that generation increments once per logical update, not once per physical copy write.

---

FINDING: V3-007
SEVERITY: major
AREA: `tapefs-v1.md` §2, §9.5; `engine-api.md` `tape_dup`
CLAIM: Duplicate has no defined geometry/capacity rule when source and destination differ, and the API does not forbid aliasing the source and destination.
REPRO: Mount a C-90 source and a smaller C-60 destination, then call `tape_dup`. Step 3 says to write the source's geometry, including a mirror LBA and `total_chunks` derived for a different `block_count`; the resulting destination fails §4.1 or does out-of-range I/O. Conversely, preserving destination geometry may not fit the source. The API also permits `src == dst` or two handles over the same block view; step 1 then marks the source `WRITE_IN_PROGRESS` and the operation destroys the only copy it is reading.
IMPACT: A successful-looking duplicate can yield an unmountable destination, and an aliased call can erase the source cartridge.
FIX: Require distinct, non-overlapping devices; reject aliasing before any write. Define the exact capacity predicate and whether destination geometry is preserved or freshly derived from its `block_count`. Refuse an insufficient/mismatched destination atomically, before writing `WRITE_IN_PROGRESS`.

---

FINDING: V3-008
SEVERITY: major
AREA: `tapefs-v1.md` Rule 2, §9.6; `acceptance.md` WP-10 format cases
CLAIM: Format has a byte-exact final image but no write order or interrupted-format state, so Rule 2 and exhaustive format crash behavior are not implementable.
REPRO: Format an existing valid cartridge. §9.6 does not say when old/new indices, primary superblock, mirror superblock, or identity are written. Writing either final VALID superblock before all new indices are durable can expose a mixed cartridge after a yank; writing identity last is stated only as a rule, not a protocol. On blank media, power loss before any valid superblock also cannot satisfy WP-10's unconditional "remount succeeds" criterion.
IMPACT: Implementations may choose different and unsafe format orders, and the exhaustive crash suite has no allowed-state oracle.
FIX: Specify format as an ordered destructive transaction, including the first recognisable invalid/in-progress write, all flushes, the final identity assignment, behavior on blank versus reusable media, and every permitted remount result. Align WP-10 with those states.

---

FINDING: V3-009
SEVERITY: major
AREA: `tapefs-v1.md` §7, §9.2–9.3; `engine-api.md` invariant 4; `acceptance.md` WP-07
CLAIM: The required Side B lower bound contradicts reset B and completed promote, both of which make B reference Side A chunks below `a_high_water`.
REPRO: With non-empty A and `a_high_water > 0`, `tape_reset_side_b` copies A's index to B without moving chunks. Every B run therefore has `first_chunk_id < a_high_water`. Completed promote likewise commits B identical to A. This violates engine invariant 4 and WP-07's requirement that fuzzing never produce such a B run, even though §5.2 intentionally has no Side B lower-bound validity check.
IMPACT: No implementation can simultaneously pass reset/promote semantics and WP-07. A test following the matrix will report correct copy-on-write aliasing as corruption, or an implementation may needlessly copy audio and violate the sub-second/no-movement criterion.
FIX: Distinguish Side B references from Side B-owned writable allocations. Permit B to reference immutable A chunks below the mark; forbid allocation/writes there. Rewrite invariant 4 and WP-07 in terms of newly allocated/write destinations, and define how the independent oracle identifies ownership.

---

FINDING: V3-010
SEVERITY: major
AREA: `engine-api.md` §8, §11; `tapefs-v1.md` §5.1, §9.1
CLAIM: The variable-rate position representation and update expression are not defined safely over the format's permitted range.
REPRO: A uint64 value with 32 fractional bits represents fewer than `2^32` whole frames, about 27.1 hours at 44.1 kHz. The format permits Side B timelines beyond nominal length and valid media can exceed that. Separately, `(int64_t)rate_q16_16 << 16` left-shifts negative signed values for reverse playback, which is undefined behavior in C99. Adding a negative signed increment to a uint64 position uses unsigned arithmetic and can wrap near frame 0; positive rates can wrap near the upper representable endpoint. The boundary table requires clamping but gives no pre-update rule.
IMPACT: Long valid timelines become unseekable/unplayable, and ordinary reverse playback has compiler-dependent behavior or can jump to a huge position.
FIX: Either cap valid `total_frames` to the representation and state the cap in media validation, or use a wider/split position. Replace the signed shift with defined multiplication and specify checked saturating endpoint updates before every sample. Define `tape_tell`'s fractional treatment.

---

FINDING: V3-011
SEVERITY: major
AREA: `engine-api.md` §5, §7, §10 state matrix
CLAIM: The state matrix permits transport-position changes while recording is armed/owed without defining which position controls the edit.
REPRO: Both armed rows mark the grouped `seek/rate/render` column allowed. Arm overwrite at frame P, feed frames so they are owed, then seek to Q before service/commit. The API never says whether the recording cursor is anchored at P, follows Q, or advances independently, nor what rendering/rate changes do to it. The matrix also omits `tape_service`, the call required to clear owed frames and progress playback/re-spool.
IMPACT: Conforming implementations can overwrite/splice at different locations for the same call sequence, including silently replacing unintended audio. State-transition tests cannot encode a single expected result.
FIX: Split the grouped column into seek, rate, and render; define a separate recording cursor or forbid position-changing calls while armed. Add `tape_service` and all observable query calls to the normative state rules, including reentrant callback/interrupt behavior.

---

FINDING: V3-012
SEVERITY: major
AREA: `tapefs-v1.md` §2, §3, §9.6; `engine-api.md` `tape_format`
CLAIM: Format does not define how `nominal_length_s` maps to `total_chunks`, and two of the three table values cannot hold their labelled duration.
REPRO: The natural full-duration calculation is `ceil(nominal_length_s * 44100 / 131072)`. It yields 1,212 chunks for C-60 and 2,423 for C-120, but the table specifies 1,211 and 2,422. Those stores are short by 31,808 frames (0.721 s) and 63,616 frames (1.443 s), respectively. `tape_format` receives only the device geometry and nominal seconds; no normative rounding/lookup/capacity formula says what to put in `total_chunks`, especially for permitted non-table lengths.
IMPACT: Independent formatters produce different media, and a standard C-60/C-120 cannot hold the complete labelled duration if the table is literal. Byte-exact format tests cannot be authored.
FIX: Define an overflow-checked formula or an exhaustive allowed-length table, state whether the store must cover the full label duration, and define the required partition block count including the reserved mirror block.

---

FINDING: V3-013
SEVERITY: major
AREA: `acceptance.md` WP-10; `tapefs-v1.md` §9.3, §9.5–9.6
CLAIM: WP-10 requires every injected case to remount successfully with Side A identical to session start, which contradicts the specified outcomes of duplicate, format, and promote.
REPRO: Duplicate deliberately returns `TAPE_ERR_INCOMPLETE` after any crash between its first and final superblock states, so mount does not succeed. A blank format interrupted before identity cannot mount. A completed promote intentionally changes Side A to the former B timeline, so its post-operation state is not byte-identical to session-start A. Yet WP-10 applies all three assertions to a script explicitly covering these operations.
IMPACT: The acceptance suite must either fail conforming behavior or silently weaken its assertions per operation. WP-10 cannot be independently confirmed as written.
FIX: Give each operation an explicit allowed-state set. For promote require A and B to be exact enumerated pre/intermediate/post generations while preserving all referenced audio; for duplicate accept `TAPE_ERR_INCOMPLETE` on the destination after the destructive marker; for format distinguish blank and reusable starts. Keep source-cartridge invariants separate from destination outcomes.

---

FINDING: V3-014
SEVERITY: major
AREA: `acceptance.md` WP-10; `tapefs-v1.md` §7
CLAIM: WP-10's reachability assertion contradicts the allocator's intentional accumulation of superseded chunks below `free_next`.
REPRO: Overwrite a non-tail B region with freshly allocated chunks above the current maximum. The old chunks are dropped from the live index but remain below the new derived `free_next`. Section 7 explicitly calls these superseded chunks the only leak source until re-spool. WP-10 says no allocated chunk below `free_next` may be unreachable, which the operation now violates. The media has no allocation bitmap that could make "allocated" mean something else mechanically.
IMPACT: Every ordinary overwrite can fail WP-10 despite conforming to the format, and the oracle cannot classify raw stale chunks as allocated versus merely containing bytes.
FIX: Define reachability in terms of live references and write destinations, not an unrecorded allocation state. If the intended check is that `free_next` equals one past the maximum live-B chunk (floored at high-water), state that directly and separately permit superseded unreachable bytes below it until re-spool.

---

FINDING: V3-015
SEVERITY: major
AREA: `acceptance.md` WP-11; Verification Charter §7; `tapefs-v1.md` §12
CLAIM: WP-11 mandates catching all seven charter mutations, but one required mutation targets the deleted preroll cache.
REPRO: The seventh charter mutation is "Preroll cache served stale after a cartridge swap." DRAFT-3 deletes the on-card preroll cache and states instant-on is not a format feature. There is no engine behavior to mutate, yet WP-11 requires all seven mutations before every phase gate.
IMPACT: WP-11 is impossible to pass literally, or a verifier must invent an engine feature that the spec forbids.
FIX: Revise the charter/criterion to replace that mutation with a live DRAFT-3 bug class, such as stale warm-start data accepted for the wrong `(uuid, side, frame range)`, final commit flush omitted, or superblock/index generation selection reversed. Update "soft-clip" to "saturating clamp" while preserving the wrap mutation's substance.

---

FINDING: V3-016
SEVERITY: question
AREA: `engine-api.md` §4–5, §12; `tapefs-v1.md` §12, §14
CLAIM: The warm-start buffer has no normative identity, side, frame-range, or valid-length contract.
REPRO: `tape_mount` accepts `resume_frame`, `warm_start`, and `warm_start_len`, while `tape_init` separately receives the play ring. The spec does not say which frame the first warm byte represents, whether the bytes must match `resume_frame`, how much of a ring is valid, or how the caller proves it belongs to the mounted UUID and side. Pass the retained ring from cartridge X/Side A while mounting cartridge Y/Side B; the stated API gives the engine no basis to reject it and says rendering may begin immediately.
IMPACT: The first hundreds of milliseconds after wake can contain audio from the wrong cartridge/side, and a golden warm-start test has no byte-exact expected mapping. This is not media corruption, but it is a cross-target contract gap.
FIX: State an explicit caller precondition and byte/frame mapping, or pass a descriptor containing UUID, side, starting frame, and valid frame count. Define whether mismatch is rejected or simply disables warm start.

---

## Acceptance testability conclusion

WP-10 is not testable as written because V3-013 and V3-014 make its universal oracle contradictory. WP-11 is otherwise mechanically testable, but its mandatory seven-mutation list is impossible until V3-015 replaces the deleted preroll mutation. The byte-exact comparison diagnostics, fixture immutability/approval log, one-command runner, and mutation-caught requirement are suitable once those three conflicts are dispositioned.

The existing implementation-independent `fault_block_device` and exhaustive `crash_harness` remain valid infrastructure. DRAFT-3 operation adapters are intentionally not frozen while the allowed crash states and index-selection rules above remain open.
