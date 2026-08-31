FINDING  V-001
SEVERITY major
AREA     spec/tapefs-v1.md §4, §7
CLAIM    The index byte layout places entries in block 0, while the commit protocol writes entries only to blocks 1–127 and then zero-pads block 0; both rules cannot be true.
REPRO    §4 says entry i begins at byte `64 + 12*i`, so the first 448 bytes after the header are in slot block 0. §7 step 3 writes the entry array into blocks 1–127 only, and step 5 writes block 0 as a 64-byte header zero-padded to 512 bytes. Following §7 therefore omits/zeros the first part of the entry array that §4 says is normative, while following §4 requires modifying block 0 before the commit write.
IMPACT   Non-empty committed indexes either fail CRC/validation or require violating the stated atomic commit protocol. Editing cannot be implemented interoperably from this draft.
FIX      Move the normative entry-array start to byte 512 (block 1), or redesign the commit protocol. Byte 512 preserves the dedicated commit-header block and still leaves ample room for 4096 entries.

FINDING  V-002
SEVERITY blocker
AREA     spec/tapefs-v1.md §6, §9.4 | spec/engine-api.md §7
CLAIM    Re-spool as specified can overwrite chunks still referenced by the live Side B index before commit, so power loss can corrupt the cartridge.
REPRO    Let `a_high_water = 100`, `free_next > 102`, and live B timeline order reference chunk 101 before chunk 100. §9.4 says re-spool rewrites the timeline starting at chunk 100 and performs no commit until the rewrite is complete. Writing the first output to chunk 100 destroys data that the still-live pre-re-spool index needs later. Yank power before the final index commit: mount correctly selects the old index, but that index now references overwritten chunk 100. §9.4 also says interrupted partial work is above `free_next`, contradicting its stated destination starting at `a_high_water`.
IMPACT   A child can lose/corrupt an otherwise valid cartridge by removing it during re-spool, violating the project's highest-priority guarantee.
FIX      Re-spool needs a copy-on-write compaction algorithm that never overwrites any chunk referenced by the currently live index before a durable replacement index exists. This likely requires a different multi-generation/scratch protocol; the present one-step description is not safe enough to implement.

FINDING  V-003
SEVERITY blocker
AREA     spec/tapefs-v1.md §9.5 | spec/engine-api.md §7
CLAIM    Duplicate has no destination precondition or crash-recovery protocol, so an interrupted copy can destroy an existing destination cartridge.
REPRO    `tape_dup(src, dst)` is defined as a whole-cartridge copy to a writable destination, with no requirement that `dst` be blank/disposable. Start with a valid destination containing different family audio, begin the raw copy, then remove power after metadata/chunks have been partially overwritten. The draft defines neither an old-state-preserving write order nor a finalization marker that makes the destination recover as either pre-copy or post-copy.
IMPACT   A child can lose the destination cartridge by yanking it during copy. The source remains safe, but the project's guarantee applies to the cartridge being written too.
FIX      Either make “destination must be blank/disposable” a hard, mechanically checkable precondition and define what blank means, or specify a transactional duplication/finalization protocol that guarantees the destination mounts as old or new after every write boundary.

FINDING  V-004
SEVERITY major
AREA     spec/tapefs-v1.md §7 | spec/engine-api.md §2, §6
CLAIM    The commit protocol has no final flush after the header commit block, so `tape_commit` can return success before the commit is durable.
REPRO    The block-device contract says only `flush` guarantees data has reached media. §7 flushes chunks, writes entries, flushes, then writes the commit header, with no following flush. If `write` returns after controller acceptance and `tape_commit` returns TAPE_OK, immediate power loss can discard the header and remount the pre-operation index.
IMPACT   A recording reported as successfully committed can disappear after power loss. This does not corrupt the cartridge, but it violates normal commit durability and makes crash tests timing-dependent on the device implementation.
FIX      Flush after the commit-header write before returning success. Specify the outcome if that final flush fails: state may be indeterminate until remount, so the API must not claim a definite pre/post state without checking.

FINDING  V-005
SEVERITY major
AREA     spec/tapefs-v1.md §3, §8 | spec/engine-api.md §2, §4
CLAIM    Mirror fallback requires a write during mount, but mounting the source slot with `write == NULL` is explicitly normal.
REPRO    Put a cartridge with a bad primary-superblock CRC and a valid mirror in the source slot. §8 says mount from the mirror and rewrite the primary. The API says source devices have `write == NULL`, and mounting Side A on such a device is normal. One reading attempts a null write/crashes; another must silently skip the normative repair.
IMPACT   A cartridge that is explicitly recoverable by its mirror may fail to play in the normal read-only source slot.
FIX      Define mirror fallback and repair separately: read-only mount must succeed from a valid mirror without mutation; repair may be deferred until the cartridge is in a writable slot.

FINDING  V-006
SEVERITY major
AREA     spec/tapefs-v1.md §3, §8
CLAIM    Unsupported `version_major` is treated both as superblock corruption eligible for mirror fallback/repair and as a distinct TAPE_ERR_VERSION condition.
REPRO    §3 says the mirror is read when the primary fails “magic, version or CRC” and the primary is rewritten from a successful mirror. §8 step 1 again treats `version_major` validation as part of fallback, while step 2 says `version_major != 1` must refuse with TAPE_ERR_VERSION. On future v2 media with a valid v2 primary and stale valid v1 mirror, a v1 implementation following step 1 could accept the stale v1 mirror and rewrite the v2 primary instead of refusing the cartridge.
IMPACT   Old firmware can mutate or effectively downgrade newer-format media, and the specified error result is ambiguous.
FIX      Unsupported major version is not corruption. If a superblock has valid magic/CRC but unsupported major, refuse without fallback repair. Only structurally corrupt copies should trigger mirror recovery; define how disagreement between two structurally valid versions is handled.

FINDING  V-007
SEVERITY major
AREA     spec/tapefs-v1.md §3, §9.3
CLAIM    Promote changes superblock state but does not define how both superblock copies are updated, so mirror fallback can resurrect stale `a_high_water`.
REPRO    Complete promote through new A index and primary superblock `a_high_water = E`, leaving the mirror at the old high-water mark under the literal “write a new superblock” step. Later corrupt only the primary CRC. Mount falls back to the stale mirror, rewrites the primary from it, and rejects the promoted A slot because its chunks are now above the restored old high-water mark.
IMPACT   A successfully promoted Side A can disappear after a later primary-superblock fault; stale metadata becomes authoritative again.
FIX      Specify a crash-safe two-copy superblock update protocol with a generation/sequence or equivalent rule. Both copies need explicit update order and recovery semantics; “primary authoritative unless invalid” is insufficient once mutable fields exist.

FINDING  V-008
SEVERITY major
AREA     spec/tapefs-v1.md §6, §9.3, §9.4
CLAIM    Promote permanently strands all pre-promote Side B allocations below the new `a_high_water`, contradicting the claim that re-spool later recovers that space.
REPRO    Let old `a_high_water = 100` and `free_next = 200`. Promote copies compacted B to fresh `[S,E) = [200,250)` and sets `a_high_water = 250`. Chunks 100–199 are now below the high-water mark, unreferenced, and by §6 immutable forever. Re-spool starts at the new `a_high_water = 250`; it cannot reclaim 100–199. This leak exists after a successful promote as well as after the accepted crash state between steps 3 and 4.
IMPACT   Promote consumes historical B allocation permanently. Repeated promote operations can exhaust cartridge capacity much faster than the live audio requires.
FIX      Redesign promotion/high-water ownership so obsolete B chunks are reclaimable, or explicitly accept the permanent capacity cost and provision/test a bound. Remove the incorrect statement that the next re-spool recovers these chunks.

FINDING  V-009
SEVERITY major
AREA     spec/tapefs-v1.md §9.3, §11
CLAIM    The single preroll cache is updated after the new Side A becomes live, so a crash can leave a valid new A paired with stale old-A preroll that cannot be detected.
REPRO    Promote from A_old to B_new. Complete step 3 so the new A index is valid under the new `a_high_water`, then lose power before step 5 regenerates preroll. On the next mount, A_new is the live index, but the only preroll region still contains A_old. The cache carries no generation binding or CRC described by the format.
IMPACT   Cold playback can emit the wrong first ~3 seconds and violates the bit-identical playback contract after an allowed power-loss point.
FIX      Make preroll explicitly non-authoritative and verifiable against the live A generation with fallback to chunk playback/rebuild, or double-buffer/version the preroll so an A commit and its cache can be selected consistently.

FINDING  V-010
SEVERITY major
AREA     spec/tapefs-v1.md §4, §8 | spec/engine-api.md §7
CLAIM    `tape_format` does not define initial slot validity/sequence values, and writing four valid empty slots with equal sequences makes the new cartridge fail mount immediately.
REPRO    API §7 says format writes “four empty index slots.” If A0 and A1 are both valid empty indexes with the same initial sequence, mount §8.5 returns TAPE_ERR_INCONSISTENT for Side A; the same applies to B. The format provides no normative alternative initialization.
IMPACT   Two reasonable formatter implementations produce different media, and the simplest interpretation produces a freshly formatted but unusable cartridge.
FIX      Define byte-exact initial slot state and globally shared initial sequences, e.g. one valid generation per side with the inactive partner intentionally invalid, plus the exact sequence numbers used.

FINDING  V-011
SEVERITY major
AREA     spec/tapefs-v1.md §3, §9.5, §10 | spec/engine-api.md §2, §7, §9
CLAIM    The engine is required to generate fresh RFC 4122 v4 UUIDs (and a format Unix timestamp) but the API exposes no entropy or clock source and forbids other hardware/OS coupling.
REPRO    Call `tape_format` or `tape_dup` twice from identical initial engine state. The only external capability available to the engine is block read/write/flush; there is no RNG, random-byte callback, UUID input, clock, or format-epoch parameter. A deterministic implementation cannot guarantee fresh v4 identities across devices/reboots, while adding a hidden RNG/clock violates the architecture.
IMPACT   Duplicate UUIDs merge device-side resume state, defeating the resolution to the seeded identity defect; implementations must violate either the UUID rule or the engine boundary.
FIX      Make identity/time caller-supplied (preferred: pass a 16-byte UUID and format epoch), or add explicit entropy/time callbacks to the platform boundary. State the required collision handling policy.

FINDING  V-012
SEVERITY major
AREA     spec/engine-api.md §6 | spec/tapefs-v1.md §9.1
CLAIM    The API does not define what `tape_commit` does when accepted recording frames are still buffered in `rec_ring` and have not been drained by `tape_service`.
REPRO    Arm recording, call `tape_feed` until it accepts frames, then stop transport and call `tape_commit` before enough service iterations have drained the ring. The draft allows at least three readings: commit drains synchronously, commit returns TAPE_ERR_BUSY until drained, or commit commits only already-written chunks and drops accepted buffered frames.
IMPACT   Under the third reading, a normal stop/commit loses up to the recording ring's buffered tail even without a crash. Tests cannot define what “accepted” means at commit time.
FIX      Define an explicit recording barrier: accepted frames remain owed by the engine; commit must either drain them to media before committing or refuse with a defined status until service has done so. Specify when feeding becomes forbidden during commit.

FINDING  V-013
SEVERITY major
AREA     spec/tapefs-v1.md §9.1 | spec/engine-api.md §5, §6
CLAIM    `tape_feed` is specified as ring-only/interrupt-safe but is also specified to report media allocation exhaustion that is discovered by `tape_service`, leaving asynchronous full-card error delivery undefined.
REPRO    `tape_feed` only writes `rec_ring`; `tape_service` performs all card I/O and drains/allocates chunks. If the last free chunk fills while service drains previously accepted frames, the next factually correct TAPE_ERR_CARTRIDGE_FULL is known in service context, not necessarily in the feed call that accepted those frames. The draft nevertheless defines cartridge-full as a short `tape_feed` return.
IMPACT   Firmware can miss the full condition or disagree on which frames were accepted/owed, risking silent recording-tail loss and nondeterministic tests.
FIX      Define reservation semantics that let feed know exact remaining capacity without I/O, or make `tape_service` the authoritative asynchronous error source and specify how feed behaves after that latched error.

FINDING  V-014
SEVERITY major
AREA     spec/tapefs-v1.md §9 | spec/engine-api.md §4, §6, §7
CLAIM    Cartridge-operation preconditions are not specified, so the seeded state-transition questions remain unresolved for reset, promote, re-spool, duplicate, unmount, and playback.
REPRO    The draft specifies TAPE_ERR_BUSY for `tape_set_side` during armed/uncommitted recording but gives no equivalent state matrix for `tape_reset_side_b`, `tape_promote`, `tape_respool`, `tape_dup`, or `tape_unmount`. Examples with divergent plausible behavior: reset B while B is playing; promote while rec_ring contains accepted/uncommitted frames; re-spool while playback/service is active; duplicate into a mounted destination with pending state; unmount while recording is armed.
IMPACT   Independent implementations can make incompatible choices, including choices that discard work or expose the crash-unsafe interleavings the design is intended to exclude.
FIX      Add a normative operation/state matrix listing allowed calls and exact errors for mounted side, playback active, recording armed, pending frames/chunks, commit in progress, re-spool/promote/duplicate in progress, and read-only devices.

FINDING  V-015
SEVERITY major
AREA     spec/tapefs-v1.md §2 | spec/engine-api.md §2, §7, §9
CLAIM    The address space passed as `tape_dev` is undefined: TAPEFS LBAs are partition-2-relative, while `tape_format` is named as a cartridge formatter but has no mechanism to create the required MBR/FAT32 partition.
REPRO    If `tape_dev` represents the whole SD card, `tape_format` writing the primary superblock at LBA 0 overwrites the MBR. If it represents partition 2, the engine can format TAPEFS correctly but cannot create partition 1, `README.TXT`, or the MBR required by the media spec. The API does not say which device view is required.
IMPACT   A caller can create non-conforming media or overwrite the partition table while following a reasonable reading of the API.
FIX      State explicitly that every engine `tape_dev` is a partition-2 block view and move card provisioning/MBR/FAT creation to a separate tool/spec, or add a distinct raw-card provisioning interface. Do not overload `tape_format` across both address spaces.

FINDING  V-016
SEVERITY major
AREA     spec/tapefs-v1.md §3, §8 | spec/engine-api.md §2
CLAIM    Mount does not require structural validation of superblock geometry against constants and `tape_dev.block_count` before using it for I/O.
REPRO    Construct a superblock with correct magic/version/CRC but `a_high_water > total_chunks`, `preroll_frames > CHUNK_FRAMES`, a nonstandard index/chunk LBA, or `total_chunks` whose chunk-store end exceeds `block_count`. §8 only names magic/version/CRC at superblock validation; later calculations can use internally inconsistent values and address outside the intended TAPEFS region.
IMPACT   Malformed-but-CRC-valid media can cause out-of-range reads/writes, persistent mount failures, or corruption outside the intended region if the platform block layer does not hard-bound the partition view.
FIX      Make all immutable constants and geometry relations normative mount checks before any repair/write: fixed sample/chunk/index values, exact LBAs, `a_high_water <= total_chunks`, preroll bound, mirror location, and overflow-safe chunk-store end within `block_count`.

FINDING  V-017
SEVERITY major
AREA     spec/tapefs-v1.md §9.1 | spec/engine-api.md §5, §6
CLAIM    The audio arithmetic is not specified byte-exactly enough to support the required cross-target golden fixtures.
REPRO    For overdub, “soft-clipped to 16-bit” does not define a transfer function; saturation, piecewise soft limiting, and other nonlinear mappings all satisfy ordinary-language “soft clip” while producing different samples. For fractional-rate playback, “linear interpolation” does not define phase initialization, integer precision, rounding of negative values, endpoint handling, or overflow behavior. Two C99 implementations can both follow the prose and produce different bytes.
IMPACT   Independent goldens cannot distinguish a bug from a permitted implementation choice, weakening the safety test that must catch wraparound and the bit-identical desktop/firmware contract.
FIX      Specify exact integer formulas, intermediate widths, rounding rules, phase convention, endpoint behavior, and the exact clip transfer function. Avoid implementation-defined signed-shift/overflow behavior.

FINDING  V-018
SEVERITY major
AREA     spec/engine-api.md §5, §9 | verification charter Suite 2
CLAIM    The required 4×→12× scrub spool-up ramp has no owner or normative time/rate curve in an engine that is forbidden to know about buttons.
REPRO    `tape_set_rate` accepts an instantaneous explicit rate. The prose says “the transport” ramps while a scrub button is held, but §9 forbids the engine from referencing buttons and no API takes hold duration or requests a scrub ramp. One firmware can ramp linearly over 0.5 s and another exponentially over 1 s; both use only valid `tape_set_rate` calls, but the charter asks for a golden fixture including the spool-up ramp.
IMPACT   The scrub sound cannot be independently golden-tested and cross-target behavior can diverge without violating this API.
FIX      Assign ramp ownership explicitly. If caller-owned, specify an exact rate-versus-time/frame schedule as a firmware-level contract used by goldens; if engine-owned, expose a button-agnostic transport/ramp API with exact timing semantics.

FINDING  V-019
SEVERITY question
AREA     spec/tapefs-v1.md §10 | spec/engine-api.md §4, §5 | cross-cutting firmware
CLAIM    The proposed resume-position mechanism does not state how the latest position is persisted when a child physically yanks a cartridge without a successful `tape_unmount`.
REPRO    Play to frame N, then remove the source cartridge abruptly. §10 says device flash holds the position and describes mount/unmount as the position handoff; an abrupt removal can prevent unmount after the media disappears. `tape_tell` exists, so firmware could checkpoint periodically or on a card-detect edge, but no cadence, accuracy, flash-wear policy, or removal timing assumption is stated.
IMPACT   The seeded requirement “pull it out mid-song, put it back later, resume where it was” is not yet mechanically testable and may resume at an older checkpoint or zero.
FIX      needs PM decision — define required resume accuracy after yank/power loss and assign a firmware persistence policy (periodic checkpoints and/or pre-disconnect card-detect handling). The engine API already has enough information via `tape_tell` if the caller owns persistence.

FINDING  V-020
SEVERITY question
AREA     verification charter Suite 1 | spec/tapefs-v1.md §6
CLAIM    The charter's literal crash assertion that no chunk is “written, unreferenced, and unallocated” conflicts with the format's deliberate reuse model for aborted writes.
REPRO    Write a fresh pending chunk above committed `free_next`, then lose power before index commit. §6 intentionally remounts with the old B index and therefore derives the old lower `free_next`; the just-written chunk contains stale bytes but is now free/unallocated and will be reused. That is the intended no-leak behavior, yet it matches the charter's prohibited literal state.
IMPACT   A mechanically correct crash harness can report false failures against the intended format.
FIX      Reword the invariant to prohibit unreachable *allocated* space below derived `free_next` (or equivalent capacity loss), while explicitly permitting stale bytes in free chunks above `free_next`.

FINDING  V-021
SEVERITY question
AREA     spec/tapefs-v1.md §9.1 | spec/engine-api.md §4, §5, §6
CLAIM    Several boundary operations required by the planned golden tests have no exact API result/state semantics.
REPRO    The draft does not define `tape_seek` beyond end (only mount resume clamps), forward render at exact end, reverse render at frame 0, splice into an empty index, splice at exact end where there is no “entry containing the insertion point,” or overwrite/overdub beginning at end. Multiple reasonable implementations differ in return code, rendered count, position, and resulting index.
IMPACT   The verifier cannot write independent mechanical assertions for charter-required t=0/end/empty and end-of-tape fixtures without choosing behavior the spec has not chosen.
FIX      needs PM decision — add a compact boundary-semantics table for seek/render and all three edit modes at empty/t=0/exact-end/beyond-end positions.

FINDING  V-022
SEVERITY minor
AREA     spec/tapefs-v1.md §1, §3
CLAIM    Two byte/numeric constants in the normative format are internally wrong or incomplete.
REPRO    `CHUNK_SECONDS` is listed as 2.97233… but `131072 / 44100 = 2.972154195…`. In the superblock, reserved offset 124 size 380 ends at byte 503, while CRC begins at byte 508, leaving bytes 504–507 unspecified even though the CRC covers bytes 0–507.
IMPACT   The time error can leak into documentation/tests, and the four unspecified CRC-covered bytes violate the document's “normative and byte-exact” requirement.
FIX      Correct `CHUNK_SECONDS` and define bytes 504–507, likely by making the reserved field size 384 and requiring zero.
