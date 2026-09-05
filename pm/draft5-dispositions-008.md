# PM Decisions 008 — DRAFT-5 dispositions, and the freeze held for one round

**From:** Program Manager · **Date:** 4 Sep 2026
**Re:** all fifteen findings V5-001…V5-015; Michael's four answers; the library printing constraint
**Distribution:** Michael, Software Lead, Hardware Lead, Verification Lead
**Companion:** `spec/tapefs-v1.md`, `spec/engine-api.md`, `spec/acceptance.md`, `spec/VERSION.md` — all DRAFT-6

**All fifteen accepted. None rejected, none deferred. Michael has held the Phase 0 signature for one round to clear the eight majors sitting in the candidate sections — the right call, and it is the reason this document exists rather than a freeze certificate.**

---

## 0. The narrow gate was met and we did not walk through it

The Verification Lead's DRAFT-5 pass found **2 blockers and 13 majors**, and reported that **neither blocker touches the Phase 0 candidate sections**. That is, precisely, the condition I told Michael I would bring him a signature on.

I brought him the condition instead of the signature, and he declined it. Correctly. The candidate sections still held eight majors, `tape_tell`'s signature was contradicting its own document, and byte-exact goldens were blocked on three separate defects. "No blocker in the candidate" was a gate I wrote before I knew what the majors would be, and a gate that would have frozen a document with a known one-frame phase defect in reverse playback is a gate that was set too low.

**The Phase 0 signature now requires: no blocker *and* no major in the candidate sections.** That is the standard the independent convergence assessment proposed and I did not adopt at the time.

---

## 1. The two blockers

### V5-001 — a recoverable I/O error could destroy audio · **accepted**

DRAFT-5 said an errored long-operation continuation "ends the operation" and returned the instance to *Mounted, idle* — where the matrix permits every mutator — while separately saying the selected on-media generation is indeterminate until remount. **Those two sentences are not compatible**, and the gap is exploitable by an ordinary call.

The concrete loss: re-spool with old B at `[10,12)` and a pass-1 destination of `[12,14)`. The new B header write completes; its flush fails. The header may or may not be durable. The instance still holds the *old* index and the old `free_next`, so an immediately permitted `tape_arm` + `tape_feed` allocates chunk 12 and **overwrites the live re-spooled generation** if that header did land.

**Fix: `FAULTED`, a quarantine state** (`engine-api` §7.2). Any `dev_write`/`dev_flush` failure against the instance's own device puts it there; exactly four calls remain — status/info/tell, `tape_render`, `tape_abort`, `tape_unmount` — and everything else returns `TAPE_ERR_FAULTED` with zero block operations, `tape_service` emphatically included. The only exit is unmount and remount, which is the operation that resolves the media honestly.

Two exclusions, both because nothing became indeterminate: **`tape_mount`'s phase-4 repair** (it changes no logical state) and a **`tape_dup` failure against the destination** (the source was never written — faulting it would kill the audio a child is listening to because the card in the *other* slot was pulled).

### V5-002 — duplicating a blank tape destroyed the destination · **accepted**

DRAFT-5's `tape_dup` step 3 wrote `{0, 0, src_A.total_frames}` unconditionally. On a **freshly formatted source** — an ordinary, valid cartridge — that is `frame_count == 0`, which §5.2 forbids. Every precondition passed, and step 4 then committed `state = VALID`. So `tape_dup` **returned `TAPE_OK` having erased a reusable destination and replaced it with a cartridge whose Side A has no selectable index.** A child copying a blank tape loses the tape they copied onto.

**Fix: an explicit empty-source branch** writing valid zero-entry A0/B0 and `a_high_water = 0`.

**This is the third time the empty case has fallen outside a destructive general case** — after V4-005's empty re-spool and the empty promote. So `engine-api` invariant 30 now enumerates all four empty behaviours together, and `acceptance.md` asserts them in one test. A family of defects deserves a family of assertions.

---

## 2. The thirteen majors, in one line each

| # | Finding | Disposition |
|---|---|---|
| **V5-003** | Mount never performed the stage-oracle check that invariant 25 and WP-10 both required | **Mount is now four phases**, with index selection and the oracle at phase 3 and repair at phase 4. **No failing mount writes anything** — which invariant 26 claimed and could not deliver. Crucially, §8's stage clearing would otherwise have *erased the evidence*: an ordinary `tape_arm` clears `promote_stage` before anything reported the fault |
| **V5-004** | Degraded-B mount allowed `promote`/`respool` with no live B index | **`tapefs` §4.4** defines the state; both refuse with `TAPE_ERR_NO_VALID_INDEX` and zero writes; `tape_reset_side_b` is the one permitted recovery. The dangerous reading was "silently treat B as empty" — promote of an empty B erases Side A |
| **V5-005** | Reverse-from-end snapped one fixed-point unit off the frame grid | Snap to **`(total_frames − 1) << 32`**. DRAFT-5 got the first sample right and **every sample after it wrong**: `[0,1000,2000]` at −1.0× emitted 2000, 1999, 999. A golden taken from DRAFT-5 would have frozen the defect as the reference |
| **V5-006** | The "portable" interpolation still subtracted before casting | `((int64_t)b - (int64_t)a) * (int64_t)f`. On a 16-bit-`int` C99 target the subtraction overflows first. **The fix for V4-013 contained a second instance of V4-013** |
| **V5-007** | Warm-start validation dereferenced the optional descriptor before the NULL test, and never checked `data` | Rewritten as an **ordered algorithm**, NULL guard first, `data != NULL` added. As written it faulted on every cold boot |
| **V5-008** | Zero-frame commit undefined | **Zero-write no-op, all three modes.** "Overwrite replaces the timeline from the current position" read as permission to truncate the tail — so press-and-release on the record button could have erased the rest of the tape |
| **V5-009** | `tape_tell` had no error channel while §10 demanded one | Signature changed to `tape_result tape_tell(const tape *, uint64_t *)`. An ABI change inside the freeze candidate, which is exactly why holding the freeze was right |
| **V5-010** | Crash tables classified by "was the flush called", but a write may be durable before its flush | **New §8.1 durability convention.** Every boundary between a write and its flush admits **both** outcomes; WP-10 runs each in both modes. The protocol does not change — writing identity last is what makes both safe — the tables just now say so |
| **V5-011** | WP-12a demanded 45 "B cells" where there are 33, and left budget zero undefined | 45 cells exercised, 33 of them `B`; `block_budget == 0` → `TAPE_ERR_INVALID_ARG` |
| **V5-012** | "Full-domain exhaustive" comparison is 5.6 × 10¹⁴ pairs | **Full-domain equivalence is a proof**, now written out in `engine-api` §8. The gate is a finite differential test: 131 071 deltas × 12 boundary `f` values, plus 10⁷ seeded random pairs, on two toolchains |
| **V5-013** | `tape_set_side` left position, flags and ring undefined | Normative transition table: position 0, both flags cleared, **ring invalidated**. The stale ring was the dangerous one — up to 372 ms of the *other side's* audio |
| **V5-014** | A progress callback could re-enter its own operation | Banned, **except `tape_render`, `tape_status`, `tape_get_info`, `tape_tell`** — banning render would put a dropout in every copy |
| **V5-015** | Exhaustion checked per commit, so promote could half-complete and then be unable to finish | **`tapefs` §4.5**: every logical operation preflights its full `sequence` and `sb_generation` headroom in 64-bit and refuses before its first write. Recording reserves at **`tape_arm`**, not at commit — otherwise the refusal arrives after the child has recorded |

---

## 3. What my own audit found this round

Three audit passes over DRAFT-6 before shipping. **37 defects in my own work, of which 6 were blockers.** All fixed. The ones that matter for calibration:

- **Reverse playback never emitted frame 0.** My fix for V5-005 set `at_start` on the step that *lands* on frame 0, and §6.3 tests the flag before emitting — so `[0,1000,2000]` at −1.0× gave 2000, 1000, stop. **The first frame of every tape, silently dropped on every rewind**, and WP-08's own new golden unachievable against the normative algorithm. I have since traced the corrected loop numerically across nine cases including −0.5× and −2.0×.
- **A cartridge that was both degraded-B and mid-promote became permanently unmountable.** My §4.2 put the stage oracle before the degraded-B branch; every resume row constrains a live Side B, so with none present the oracle matched nothing and returned `TAPE_ERR_INCONSISTENT`. The only recovery needs a successful mount. **All of Side A's music, gone, on a cartridge whose Side A was intact.**
- **The headroom predicate I wrote to fix V5-015 wrapped in u32.** `0xFFFFFFFC + 4 == 0`, which passes — so promote would have written the two values §10 forbids, and `acceptance.md` crafts exactly that `sequence`. A conforming-but-32-bit engine would have passed the test written to catch it.
- **`engine-api` §5 still described DRAFT-5's mount order**, so an implementer following it would repair before validating — reinstating V5-003 in the document that fixed it.
- **RESUME-at-step-5 over-stated its generation headroom**, stranding stage-1 media forever at the boundary — the exact failure class §4.5 exists to eliminate.
- The warm-start algorithm **fell through from `use:` into `cold:`**, so warm start could never engage at all.

**A self-audit is not an adversarial review.** It found contradictions, arithmetic, and rules stated in one document and enforced in neither. Two of the six blockers above were introduced *by fixes for the previous round's findings*, which is the pattern worth naming: on this project, the most dangerous text is the text written last, under the most pressure, to close a hole someone just found.

---

## 4. Michael's four answers

- **Phase 0 gate: held one round.** Standard raised to no blocker *and* no major in the candidate sections.
- **Safety sign-off:** Michael witnesses the SPL and thermal measurements; the **Verification Lead independently audits the method and the raw data** without being present. Two checks, neither of them the person who built it. `acceptance.md`'s "witnessed by Michael" stands and the audit is added.
- **Printer:** leaning A1 combo, with four questions answered in his queue and in Decisions 006 to the Hardware Lead. One material finding: **the A1 line does not run nylon** — Bambu supports PLA, PETG and TPU and explicitly does not recommend enclosing the A1 mini. That changes the material plan, not the buy decision.
- **Cartridge shell:** Option 1, but with a **clasp rather than a screw** and a near-invisible seam, plus an assessment of the fully-sealed USB-C route. Both are in Decisions 006 §2. My read: the clasp is feasible for a reason that has not been said out loud yet — **a cartridge is opened once or twice in its life, not weekly** — and the sealed route is feasible but makes a dead card into landfill.

---

## 5. Next

- **Software Lead** — land the DRAFT-6 bundle; then the read path against a mount that now has four phases and a superblock that grew two fields; then WP-06's eight sub-criteria.
- **Verification Lead** — a DRAFT-6 pass aimed at `FAULTED`, the four-phase mount, degraded-B, and §4.5's headroom table. The freeze standard has been raised and it is your pass that measures against it.
- **Hardware Lead** — nothing in DRAFT-6 touches the board. The WP-04 packet as a merged STL is still the critical path, and §2 of your communiqué has the shell work Michael asked for.
