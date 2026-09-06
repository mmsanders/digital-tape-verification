# PM Decisions 006 — Verification Lead

**From:** Program Manager · **Date:** 5 Sep 2026 · **Re:** all nine DRAFT-6 findings, DRAFT-7, and a publication gap in your own repository

---

## 0. Merge verdicts

**`Digital-Tape-Verification` PR #1 — merge it, and then change the rule it exposes.**

That PR has been open since 3 September and its title still says DRAFT-5. Meanwhile your repository's `main` carries findings up to **DRAFT-3**, while the DRAFT-4, DRAFT-5 and DRAFT-6 passes all live on branches — `verification/draft4-review` and `verification/draft6-review`.

**This is the same failure I mechanised against in the other repository two rounds ago**, and I did not think to look for it here. `Digital-Tape` `main` was publishing DRAFT-3/DRAFT-3/DRAFT-1 while I believed it carried DRAFT-4; your `main` publishes DRAFT-3 findings while three later passes exist. In both cases the authoritative location was correct and empty, and the real work was on a branch nobody had a reason to look at.

**From now on: findings land on `Digital-Tape-Verification` `main`.** Merge #1, or re-scope and merge it, so `main` carries every pass. A review three streams read as truth cannot live only on a branch — that is the rule I wrote for `spec/` and it applies here for exactly the same reason.

**`Digital-Tape` PR #20 stays a draft** and is not yours to unblock yet: it is held by structural Rule 1 pending your WP-10 tests, and it is three revisions behind besides.

---

## 1. Your nine findings — all accepted

Six touched the freeze candidate, so **the Phase 0 signature is held a second round.** You applied the raised standard correctly and recommended against signature on that basis, which is what the standard is for.

Full dispositions are in **PM Decisions 009**. Briefly:

- **V6-001** → §4.4 names both causes of degraded-B; `tape_reset_side_b` writes B0 at `cartridge_sequence + 1`, a maximum over every structurally valid slot, which is what makes it win selection in the equal-sequence case. Your repro — B1 surviving at 500 against a recovery writing 11 — was exact.
- **V6-002** → §4.5 is branch-exact, with adopt-in-place and phase-2-will-decline as their own rows. Your point that the branch is decidable before the first write was the one that made the fix possible.
- **V6-003** → new **§5.5**. `cartridge_sequence` is the maximum over every **structurally valid** slot, and DRAFT-7 also defines structural validity for an index slot for the first time — including the `entry_count` bound, without which deciding validity could demand a 51 GB read.
- **V6-004** → the counters now have separate domains. This one had been wrong since DRAFT-3 and four passes had not caught it.
- **V6-005** → `tape_set_side` is permitted while Playing, rate retained. *(One correction to your reasoning: `at_end` is also set on an **empty** timeline at any rate, so that case was reachable from idle. Your conclusion holds — a real position on a non-empty Side A is what WP-08 needs, and that was unreachable.)*
- **V6-006** → termination returns to the underlying transport state.
- **V6-007** → both tables split the final superblock into mirror and primary boundaries, with the torn-primary outcome. Format's missing "inside step 5" row is added.
- **V6-008** → the fallback zeroes the non-selectable copy first — **and so does the ordinary step 1**, because your repro applies there too with a torn write.
- **V6-009** → the four exempt calls succeed; a re-entry BUSY never terminates.

**Issue #23**, raised by the Hardware Lead: `acceptance.md` contained the word "audit" zero times while Decisions 008 §4 told three people it had been added. The hardware safety section now requires procedure, instrument and calibration, conditions, raw readings, derivation and **stated measurement uncertainty** — the last because the thermal margins can be decided by it. **That is your audit to perform**, per Michael's answer on issue #8: he witnesses, you audit method and raw data without being in the room.

---

## 2. What my own audit found, so you do not rediscover it

Two passes over DRAFT-7. **27 defects, two blockers, both in text written to fix your findings.**

- **My `cartridge_sequence` rule said "the second index writes `+ 2`" and stopped.** A FRESH promote commits **four** indices, so steps 7 and 8 reused steps 2 and 3's values — and between steps 7 and 9 both Side A slots are §5.2-valid at the same `sequence`, which §5.3 calls `TAPE_ERR_INCONSISTENT` and *"the cartridge is unusable"*. Every recovery needs a mount. **Cartridge lost, and two rows of §9.3.4 falsely promised a resumable state there.** Fixed with a running counter, which agrees with the RESUME path arithmetically.
- **My fix for the generation-0 destination removed the `WRITE_IN_PROGRESS` barrier.** I chose "treat generation 0 as blank, skip step 1", and step 1 is what makes a destination unmountable for the length of the copy — **every reusable-media crash row derives from it.** A power cut in the resulting window produces a cartridge that mounts and plays the *source's* music under the *destination's previous* UUID, so the device's position table indexes a different timeline. Silent. `max(existing, 1) + 1` closes the original hole and keeps the barrier.

Also: promote's three superblock writes never said `sb_generation + 1`, in a document that is byte-exact by charter.

---

## 3. Where to aim

1. **`tapefs` §5.5 — the running counter.** Newest text, and a blocker already came out of it. Trace it through FRESH allocating, FRESH adopt-in-place, every RESUME entry point, and a two-pass re-spool. **Can any two structurally valid slots ever share a `sequence`?** Is `cartridge_sequence` the right base after each?
2. **`tapefs` §4.5 — the branch table.** Recompute every row against §9's write sequences. One row wrong by one strands media.
3. **`tapefs` §9.5/§9.6 step 1** — the reordering and `max(existing, 1) + 1`. Both crash tables were rewritten around it twice in one day.
4. **`engine-api` §10's two override rules** — degraded-B over *Playing*/*Mounted idle*, and FAULTED over everything. Two overrides in one matrix is where an unreachable or a cycle hides.
5. **§9.3.4 under §8.1** — promote's three superblock writes are four injection points each in two durability modes.

---

## 4. Acceptance

WP-11 you called **testable as written**; nothing in DRAFT-7 changes §6.2, §6.3 or §8, and your independent traces of them match mine. **The golden arithmetic is unblocked.**

WP-10 and WP-12a gain the criteria for all nine findings, plus a `sb_generation = 0` destination, the ordinary step-1 write order, the positive half of the counter-domain rule, and a **"no two structurally valid slots share a `sequence`"** assertion after every injection in a FRESH promote — which is the blocker above, made mechanical.

**Confirm they are testable as written, or say what is not.** That verdict has been right four rounds running.

---

## 5. A note on this round's reviewer

Michael tells me this pass came from a substitute agent while the usual capacity was unavailable, and asked me to look at it hard. **I did, and it holds up.** You verified the three hashes against `spec/VERSION.md` before reviewing and said so — no previous pass did that unprompted. You kept the implementation-independence boundary and stated exactly what you did not open. You ran independent numerical traces on the transport arithmetic and then **declined to file against it**, which is the harder call and the more useful one. And you updated `PM-NOTES.md`, which I had asked for three rounds running without success.

I checked seven of the nine findings against the documents myself and looked specifically for under-called severity — nine findings and no blockers, against fourteen and fifteen with two blockers, is the shape a soft pass would have. It is not one: I re-graded V6-001 and V6-008, the two most blocker-shaped, and **major is correct for both** — neither loses data that was not already being destroyed.

The one thing a single pass cannot tell me is depth. So when the usual arrangement resumes, **review DRAFT-7 without reading the DRAFT-6 findings first**, and we will compare what each pass finds in the overlapping text. One pass, and it answers a question we otherwise have no way to answer.
