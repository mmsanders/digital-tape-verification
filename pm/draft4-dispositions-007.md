# PM Decisions 007 — DRAFT-4 dispositions, the freeze split, and the canonical bundle

**From:** Program Manager · **Date:** 4 Sep 2026
**Re:** all fourteen findings V4-001…V4-014; the independent Convergence Brief; and one desync I found on `main` while checking freshness
**Distribution:** Michael, Software Lead, Hardware Lead, Verification Lead
**Companion:** `spec/tapefs-v1.md`, `spec/engine-api.md`, `spec/acceptance.md`, `spec/VERSION.md` — all DRAFT-5

**All fourteen findings accepted. None rejected, none deferred. Four of them changed the design rather than correcting the text.**

---

## 0. Before the dispositions: `main` is publishing three different revisions

Checked this morning, cache-busted, from `main`:

| File on `main` | Revision |
|---|---|
| `spec/tapefs-v1.md` | DRAFT-3 |
| `spec/engine-api.md` | DRAFT-3 |
| `spec/acceptance.md` | **DRAFT-1** |

Each of those files claims in its own header to be versioned in step with the other two. Two of them are two revisions apart. DRAFT-4 never landed on `main` at all — it exists only in my hands and in the Verification Lead's review branch, which is exactly what the Convergence Brief said and I had not confirmed until now.

This is the **third** silent desync on this project: the unversioned charter, then a stale spec on `main` that three streams would have read as truth, now three spec files at three revisions. All three were caught by a person happening to look. None was caught by a mechanism.

**So DRAFT-5 ships with one:** `spec/VERSION.md`, a manifest carrying each file's revision and SHA-256, plus `tools/ci/verify-spec-bundle.sh`, which fails a PR if any spec file's content or revision drifts from it. I wrote the gate, ran it green against the DRAFT-5 files, flipped one byte and confirmed it goes red. It is in `VERSION.md` ready to land.

I am not treating this as anyone's failure to update a file. Three streams reading `main` for truth, and nothing checking that `main` is internally consistent, is a system defect and it was mine to notice two rounds ago.

---

## 1. The freeze splits

The Convergence Brief's first recommendation was "do not freeze DRAFT-4", and it was right — but "not yet" is not a plan, and the Phase 0 gate is now the longest-standing open item in the project.

**Decision: the freeze splits by kind, not by document.**

| Frozen at the Phase 0 gate — the **candidate** | Frozen one round later, at the **first green WP-10 run** |
|---|---|
| `tapefs` §§1–8: constants, lengths, the geometry predicate, layout, superblock, mount, index, chunks, ownership, commit | `tapefs` §9: operations |
| `engine-api` §§2–8 and §12: error codes, device, memory, lifecycle, transport arithmetic, recording, exact audio arithmetic, invariants | `engine-api` §10: the state matrix |

**Why.** The byte-level surface is what the read path and the golden fixtures are built against, and it is the part four adversarial rounds have not broken. Operations and the matrix are *behaviour*, and behaviour should freeze when tests prove it, not when prose settles — every one of this round's blockers was in behaviour. Freezing the format now unblocks Streams 1, 3, 4 and 5; freezing behaviour now would freeze something the verifier is still finding blockers in.

Michael signs the Phase 0 gate on §§1–8 and §§2–8/§12 when the Verification Lead's DRAFT-5 pass returns without a blocker against them.

---

## 2. The anti-loop rule, adopted

The Brief proposed: *do not accept a DRAFT-5 prose patch unless the corresponding state table, interval model, or reference algorithm is updated first.* Adopted, stated in both specs as **"no prose-only patch"**:

> A change is accepted only when it lands as a change to a reference algorithm, a table, an interval model, an enumerated state, a signature, a matrix cell, or an invariant — with the prose following. A finding that can only be answered by rewording is a documentation defect and is batched, not drafted.

Every DRAFT-5 change complies. Where DRAFT-4 argued in prose, DRAFT-5 either computes or stores.

---

## 3. The fourteen dispositions

### V4-001 (blocker) — a v1 engine could write to v1.1 media · **accepted**

`tapefs` §4.1 declared a `version_minor > 0` cartridge read-only. Every write authorisation in the API was `dev.write != NULL`. **Nothing joined them**, so on a writable device the state matrix authorised `reset_b`, `promote`, `respool` and arming Side B against v1.1 media — committing v1 structures onto media whose newer semantics this engine does not understand.

The compatibility barrier existed in one document and in no code path. That is the shape of defect this project keeps producing: a rule written where it reads well rather than where it is enforced.

**Fix.** One predicate, `tapefs` §4.3 and `engine-api` §3.1:

```
effective_writable = (dev.write != NULL) && (mounted version_minor == 0)
```

Computed at mount, stored, exposed as `tape_info.writable`, consulted by every mutator and by superblock repair. `dev_write`'s null check survives as a debug assertion, not as the permission model. `tape_info` gains `version_minor` so firmware can say *why*. New criterion WP-06a.

**One scope decision inside this.** `tape_format` and `tape_dup` take a raw device and are gated only on `write != NULL`. The version barrier protects media you intend to keep from *silent partial* writes; erasing a cartridge is neither silent nor partial. A v2 cartridge put in the work slot and copied over is destroyed on purpose, and a v1 player must be able to reclaim any card in the house.

### V4-002 (major) — the scalar non-overlap test · **accepted, deleted**

I wrote that rule under time pressure in DRAFT-4 to close a hole in the promote proof, flagged it to the verifier as the least-settled text in the format, and it was worse than unsettled. The scalar "equivalently" was **not equivalent** — two one-frame entries at the same physical frame pass it — and it was **circular**, depending on `free_next`, which is derived from an index whose validity the test is part of deciding.

**Fix.** Deleted. Each entry is one half-open physical-frame interval `[first_chunk_id × CHUNK_FRAMES + start_frame, + frame_count)` in 64-bit; every pair within one index must be disjoint. Checkable from index metadata with no chunk reads, before `free_next` exists. Sharing a chunk with disjoint frame ranges — the splice-trim shape — stays legal; **across sides, overlap is required**, because that is copy-on-write. Bounded method given (heapsort over ≤ 4 096 u16 indices, 8 KiB in `mem`). New criterion WP-06c.

### V4-003 (major) — promote's recovery table omitted the post-step-7 and post-step-8 states · **accepted**
### V4-004 (major) — an interrupted promote could become impossible to finish · **accepted**

These are one defect with two symptoms, and the fix is structural.

DRAFT-4 asked recovery to *infer* "is a promote in flight, and how far did it get?" from the shapes of two indices. Every such inference was a reachability argument, and reachability arguments are what have failed most often on this project — the invalid promote proof, the unsatisfiable pass 2, the impossible worked example.

**Fix, three parts:**

1. **`promote_stage` and `promote_staging_chunk`**, two u32 in the superblock's reserved space (offsets 124 and 128; reserved 384 → 376; the block still totals 512 with the CRC at 508). Written by superblock writes that already happen — **zero extra writes, zero extra flushes**. The intermediate state now says what it is instead of being guessed at.
2. **Adopt-in-place.** If Side B is already a single compacted run at or above the water line, phase 1 copies nothing: it adopts the run, commits A to it, and raises the mark. This kills V4-004 outright — the crash state the verifier described *is* "B is one compacted run above the water line", and adopting it needs no allocation, so the `TAPE_ERR_CARTRIDGE_FULL` cannot occur and repeated crashes cannot consume successive staging runs. It also needs no knowledge that a promote happened, which is why it is a short-circuit rather than a detector.
3. **A three-row RESUME table and an eleven-row recovery table**, both decidable from the entry arrays and the superblock, neither resting on reachability.

### V4-005 (major) — empty re-spool had no behaviour · **accepted**

`TAPE_OK`, `*more_work = false`, **zero writes**, valid zero-entry index left as it stands.

The same input to `tape_promote` returns `TAPE_ERR_INVALID_ARG`. **Same input, opposite answers, deliberately:** re-spool's job is to compact and reclaim, and an empty timeline is already maximally compact with nothing to reclaim; promoting an empty side would **erase Side A**. `acceptance.md` WP-12 asserts both in one test so the asymmetry is visible rather than looking like an inconsistency.

### V4-006 (major) — format and dup could destroy media before discovering impossible geometry · **accepted**

`GEOMETRY_OK(nominal_length_s, block_count)` is now stated **once**, in `tapefs` §2.1, and used in all three places — mount, duplicate, format. `tape_format` and `tape_dup` both apply it before any write. `tape_dup`'s preconditions are now a **normative ordered list** — aliasing, writability, geometry, capacity — so two implementations return the same error on a destination that fails more than one.

`tape_dup` also gains a refusal that was missing entirely: **`dst_dev->write == NULL` → `TAPE_ERR_READ_ONLY`.** The left slot is read-only by design; a firmware path that wired the slots backwards would have called a null pointer.

### V4-007 (major) — the incremental contract and the matrix contradicted each other · **accepted**

DRAFT-4 required repeated calls to drive `respool`/`promote`/`dup` while the in-progress row returned `TAPE_ERR_BUSY` from all three. **None of the three could complete.**

**Decision: the continuation call is the same call.** The one in-progress row becomes three, each with its own operation's column allowed. Argument stability is specified. Continuation via `tape_service` is **rejected** and the rejection recorded: it gives `tape_service` no way to distinguish owed frames from a running operation, and it makes the card write for an operation the caller has stopped tracking.

Also added, because the row had no error exit at all: **a continuation returning anything but `TAPE_OK`/`TAPE_ERR_INVALID_ARG` ends the operation** and returns the instance to idle — a card pulled mid-respool otherwise left an instance `tape_unmount` would refuse forever. And the converse: **`TAPE_ERR_BUSY` returned to any other call does not touch the operation**, or a stray `tape_seek` from the copy screen would silently cancel a 30-second copy.

New criterion WP-12a, which exercises all forty-five cells of the three rows. V4-007 was the one finding of the fourteen with no test attached; it has one now.

### V4-008 (major) — commit-in-progress was unobservable · **accepted**

**Decision: `tape_commit` is synchronous.** The row and the abort-during-commit rule are **deleted rather than specified**.

By the time commit is callable, `tape_service` has already written and flushed every chunk, so a commit writes **at most 97 blocks and performs exactly two flushes** — 96 entry blocks at `TAPE_MAX_ENTRIES` plus block 0. That is not the thirty-second operation that forced `tape_promote` incremental, and inventing asynchronous semantics for it would have added a state machine to buy nothing.

A new firmware criterion pins the assumption to a number: **worst-case commit < 200 ms**, and in every case under the play ring's ~372 ms. A card that misses it is a card-selection finding, not a licence to make commit incremental.

### V4-009 (major) — the positive-rate clamp underflowed · **accepted**

Exactly as reported. One-frame timeline, `rate_q16_16 = INT32_MAX`: `max_pos - s` wraps unsigned, the comparison is false, and position walks past the end. The clamp that exists to prevent out-of-range access was itself the way out.

Now `if (position >= max_pos || s >= max_pos - position)`. The bound `|step| ≤ 2^47` is stated normatively, which is what makes negating `step` safe. WP-08 gains the extreme cases.

### V4-010 (major) — the sample phase contradicted seek · **accepted**

DRAFT-4 said the clamp is evaluated "before each sample is fetched", which made the first frame after `tape_seek(N)` be *N+1* — contradicting seek's own contract and making goldens unfreezable, since two conforming renderers would differ by one frame at every seek.

**Pinned: fetch, emit, then advance.** `engine-api` §6.3 is now a single normative render loop rather than three sections that had to be read together. It also settles what DRAFT-4 left unsaid: rate 0 renders nothing, an empty timeline sets `at_end`, and a negative rate at `max_pos` snaps onto the last frame — which is what makes "press rewind at the end of the tape" work at all.

### V4-011 (major) — warm-start containment could wrap · **accepted**

Checked 64-bit containment, `valid_frames > 0` required. Plus a field the verifier suggested and I should have had: **`data_bytes`**. Principle 1 says the caller owns the buffer; it does not say the engine must take its dimensions on trust. WP-11's mutation 7 gains arithmetic-maxima fixtures, without which the mutation it exists to catch was not catchable.

### V4-012 (major) — an undefined `state` mounted as `VALID` · **accepted**

Admission now requires `state ∈ {0,1}` and `promote_stage ∈ {0,1}`; anything else returns the new `TAPE_ERR_UNSUPPORTED_STATE` with zero writes and no repair. Damaged or future values now fail **closed**, which is the discipline already applied to `version_major` one line above. New criterion WP-06b.

### V4-013 (major) — the interpolation shifted a negative signed integer · **accepted**

The formula demanded flooring in prose and expressed it with an operator C99 does not require to floor. A desktop build and an embedded build could legitimately emit different PCM for the same cartridge.

Replaced with a portable floor-division using only unsigned shifts, and verified equal to the arithmetic-shift result over the full `(b − a, f)` domain. WP-11 gains a **portability gate**: exhaustive equivalence, and green on **at least two toolchains, one of them the embedded target** — a single-toolchain green is not evidence of portability, which is the whole point.

### V4-014 (question) — the blank-format boundary after step 4 · **accepted, answered as proposed**

Added to the table: exactly one structurally valid superblock (the mirror), both empty indices durable, mount succeeds. On a writable mount phase 3 repairs the primary and `needs_repair` is **false**; the `needs_repair == true` form is asserted on a read-only device. The same boundary is now enumerated for `tape_dup`, which had the identical gap.

---

## 4. The other three decisions the Brief asked me to make

**Duplicate's aliasing contract.** `dev.ctx` pointer equality, plus device identity where the port supplies it, and an explicit **port obligation**: a port that cannot distinguish two devices must not hand the same one to `tape_dup` twice. The engine cannot verify this. Stating it in `engine-api` §3 is the only thing that makes it a contract rather than a hope.

**Canonical authority.** `Digital-Tape` `main`, stated in `spec/VERSION.md`. A copy anywhere else — verification branch, PM communiqué, chat attachment — is a courtesy copy, and a disagreement with `main` is a finding.

**Product-decision check on duplicate.** The Verification Lead reviewed "copy the music, not the sandbox" as a product decision and did not recommend escalating. It stands, and the review is recorded in §9.5 so it does not get relitigated.

---

## 5. What the self-audit found this time

After writing DRAFT-5 I ran an independent adversarial audit over it, as I did for DRAFT-4. **Three rounds, 35 defects in my own work, of which 3 were blockers.** All are fixed in what ships. The serious ones, because the leads should know what almost went out:

- **`promote_stage` was a terminal state.** A power loss during one superblock write left stage 1 on media. Nothing else on the cartridge ever writes the superblock — so a child recording on Side B afterwards moved B's index, every later `tape_promote` matched no resume row, and promote was **permanently disabled and reported as a media fault**. Re-spool made it worse rather than better. One power loss plus ordinary use, bricking the product's headline operation. Fixed by stage clearing in `tape_arm`/`tape_reset_side_b`/`tape_respool` — and then fixed again, because "before doing anything else" made four specified zero-write refusals write.
- **`tape_dup` produced an unmountable cartridge.** It never wrote the destination's `a_high_water`, so the new Side A index failed §5.2's Side A bound; it said "write the source's Side A chunks" without saying where, while the capacity precondition assumed compaction; and it committed "under §8", which selects the *inactive* slot — so on reusable media the **previous cartridge's** index at a higher sequence could win selection and the copy would mount and play the wrong audio, silently. Three holes, one of them silent data substitution.
- **Mount only validated the requested side**, while `free_next` is defined over Side B's index and adopt-in-place's safety rests on Side A's bound having been evaluated. A Side-A mount would have allocated straight over Side B's live chunks.
- Two RESUME rows were the same predicate whenever `S == 0` — which is the ordinary first-use path — falsifying the invariant and the test built on it. Then, after the first fix, rows 1 and 3 still overlapped, and the justification I gave was itself a reachability argument.
- The termination rule I added for V4-007 was unscoped, so a `TAPE_ERR_BUSY` returned to any other call cancelled the operation it was meant to protect.
- Position clearing, rewritten to fix one gap, was made conditional on "has committed a new Side A index" — which excluded three of the four paths the same sentence claimed to include.

**A self-audit is not an adversarial review** and I am not treating it as one. It found contradictions, arithmetic, and rules stated in one document and not the other. It did not, and structurally cannot, find the things I still believe are true.

---

## 6. What each lead does next

One-line summary; the detail is in each lead's own communiqué.

- **Software Lead** — land the DRAFT-5 bundle plus `VERSION.md` and the gate as one mechanical PR; reconcile the read path against seven changed rules; then WP-06's new sub-criteria and WP-07.
- **Verification Lead** — a DRAFT-5 pass aimed first at `promote_stage`, then the state matrix's three new rows, then §4.2. Goldens are unblocked: the three things that were preventing them from being frozen are all resolved.
- **Hardware Lead** — unaffected by DRAFT-5. But the library print constraint is decisive and changes WP-04's design; see that communiqué and Michael's queue item M-04.
