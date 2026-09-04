# PM Decisions 004 — Verification Lead

**From:** Program Manager · **Date:** 4 Sep 2026 · **Re:** all fourteen DRAFT-4 findings, DRAFT-5, and where to aim
**Supersedes:** Decisions 003.

**All fourteen accepted. None rejected, none deferred. Four changed the design rather than the text. Goldens are unblocked — all three of the things you said had to be resolved first are resolved.**

---

## 1. Your DRAFT-4 pass — outcome

Every finding was correct. The four that required a design decision rather than a correction are the ones I most want you back on:

- **V4-001**, the blocker. You found a compatibility barrier that existed in one document and in no code path. `effective_writable = (dev.write != NULL) && (version_minor == 0)` is now one predicate, computed at mount, exposed as `tape_info.writable`, consulted by every mutator and by repair. `tape_info` also gains `version_minor` so firmware can say why.
- **V4-002.** You were right that my scalar "equivalent" was neither equivalent nor usable in the stated mount order, and right about *why* — the `free_next` dependency was circular. Deleted. The interval model is yours as proposed, with a bounded algorithm and an explicit note that chunk sharing with disjoint frame ranges stays legal.
- **V4-003 and V4-004** turned out to be one defect: DRAFT-4 asked recovery to *infer* promote's progress from index shapes, and every such inference was a reachability argument. See §2 — that is the change I most want attacked.
- **V4-007.** Neither of your two options survived unchanged; I picked the first and recorded why the second was rejected. The three in-progress rows now differ only in which continuation is allowed.
- **V4-008.** Synchronous, and the row and abort rule are **deleted rather than specified**. Commit writes ≤ 97 blocks and 2 flushes, and a new firmware criterion pins the latency to a measured number rather than to my belief that it is bounded.
- **V4-010.** Fetch, emit, then advance. §6.3 is now one normative loop rather than three sections that had to be read together.
- **V4-013.** Portable floor division, verified equal to the arithmetic shift over the full domain, plus a two-toolchain requirement in WP-11 — because a single-toolchain green is not evidence of portability.
- **V4-014.** Answered exactly as you proposed, and the same boundary is now enumerated for `tape_dup`, which had the identical gap and nobody had asked about.

Full dispositions are in **PM Decisions 007**, which Michael has.

**Your product-decision check on duplicate is accepted and recorded in `tapefs` §9.5**, so it does not get relitigated by the next reader.

---

## 2. Before you start: what my own audit found, so you do not spend your pass rediscovering it

I ran three rounds of independent adversarial audit over DRAFT-5 before shipping. **They found 35 defects in my own work, three of them blockers.** All are fixed in what you are receiving. The ones worth your calibration:

- **`promote_stage` was a terminal state.** I introduced the field to fix V4-003/V4-004, and in doing so created a worse bug than either. One power loss during one superblock write left stage 1 on media; no ordinary operation writes the superblock, so a child recording on Side B afterwards moved B's index; every later `tape_promote` matched no resume row and returned `TAPE_ERR_INCONSISTENT` with zero writes. **Promote permanently disabled by one power cut plus normal use, and reported as a media fault.** Re-spool made it permanent rather than fixing it. Fixed by stage clearing in `tape_arm`/`tape_reset_side_b`/`tape_respool` — and then fixed again, because my first wording ("before doing anything else") made four specified zero-write refusals write.
- **`tape_dup` produced unmountable cartridges, three separate ways.** It never wrote the destination's `a_high_water`; it did not say *where* the source's chunks go while the capacity precondition assumed compaction; and it committed "under §8", which selects the *inactive* slot — so a destination whose old A0 held a higher `sequence` would mount **the previous cartridge's index** and play the wrong audio silently.
- **Mount validated only the requested side**, while `free_next` is defined over Side B's index. A Side-A mount would have allocated over Side B's live chunks.
- **Two RESUME rows were the same predicate when `S == 0`** — the ordinary first-use path. After I fixed that, rows 1 and 3 still overlapped, and the justification I gave for the fix was itself a reachability argument.
- The termination rule I added for V4-007 was unscoped, so a `TAPE_ERR_BUSY` returned to any other call cancelled the operation it was meant to protect.

**A self-audit is not an adversarial review.** It catches contradictions, arithmetic, and rules stated in one document and enforced in neither. It cannot catch the things I still believe are true, and the list above is mostly things I believed on the first pass.

---

## 3. Where to aim

In this order — newest normative text with the least scrutiny first.

1. **`tapefs` §4 and §9.3 — `promote_stage`.** A **new superblock field** is the largest structural change since DRAFT-3. Attack the whole machine: the two u32 and the reserved-byte arithmetic; §9.3.0's entry classification; adopt-in-place; the decline path's clearing write; §9.3.3's three RESUME rows and §9.3.4's eleven recovery rows. Specifically: **do the three RESUME rows partition every state, including crafted media?** Both `S > 0` guards are there because they did not, twice. **Is stage clearing complete** — is there any path that commits an index onto stage-1 media other than promote's own steps 7–8? **Does re-running terminate from every row?**
2. **`tapefs` §4.2 — both-side mount.** New, and it changes what a successful mount means. A Side-A mount now depends on Side B's index having been selected. Is the Side-B-unselectable path fully specified, including `tape_set_side`?
3. **`tapefs` §9.5 — duplicate.** Rewritten end to end after my audit found three holes in it. Explicit write order, four ordered preconditions, a new crash table. Enumerate the boundaries yourself; my table is one round old.
4. **`engine-api` §10 — the three in-progress rows.** Forty-five cells that DRAFT-4 tested nowhere, and where V4-007's fix and its own error-exit rule interact. WP-12a is new and I would like your judgement on whether it is testable as written.
5. **`engine-api` §6.3 and §8 — the render loop and the interpolation.** These are freeze candidates and goldens depend on them byte for byte. §6.3 also settles things DRAFT-4 never stated: rate 0, empty timelines, reverse from `max_pos`, and the `at_start`/`at_end` lifecycle.
6. **`tapefs` §5.1 — the interval model**, in your own formulation. I took your fix; check I took it correctly, and that nothing elsewhere still leans on the deleted scalar.

Then everything else.

---

## 4. Goldens are unblocked

You wrote that golden PCM must not be frozen until the render phase convention, the portable negative interpolation rule, and the checked warm-range arithmetic were resolved. **All three are resolved in DRAFT-5**, and `engine-api` §§2–8 and §12 are the freeze candidate precisely so you can author fixtures against a stable surface while §9 and §10 stay open.

WP-11 gains two things from your pass:

- A **portability gate**: exhaustive `(b − a, f)` equivalence against the arithmetic-shift result, and green on **at least two toolchains, one of them the embedded target**.
- Mutation 7 gains arithmetic-maxima fixtures — `start_frame` near `UINT32_MAX`, `valid_frames == 0`, and `data_bytes` one byte short. Without those the mutation was not catchable, which you identified.

WP-10 gains six new oracle rows and the promote allowed-state set now enumerates all eleven boundaries, including the two you found. **WP-06 gains six sub-criteria** (06a–06f); those are the Software Lead's to satisfy and yours to confirm.

**Confirm WP-10, WP-11 and WP-12a are testable as written, or say what is not.** That is a deliverable in its own right and I would rather hear it now than after you have built against them.

---

## 5. The freeze splits

| Frozen at the Phase 0 gate | Frozen at the first green WP-10 run |
|---|---|
| `tapefs` §§1–8 · `engine-api` §§2–8, §12 | `tapefs` §9 · `engine-api` §10 |

Behaviour freezes when tests prove it, not when prose settles — and every blocker in the last two rounds has been in behaviour. **Your DRAFT-5 pass returning without a blocker against the candidate sections is what Michael signs the Phase 0 gate on.** A blocker in §9 or §10 does not block that signature; it blocks the second freeze, which is yours to gate with WP-10.

---

## 6. Three process notes

**The canonical bundle.** `spec/VERSION.md` now carries each spec file's revision and SHA-256, and a CI gate fails any PR where they drift. `Digital-Tape` `main` is stated as the single canonical publication point; **the copy on your review branch is a courtesy copy, and a disagreement with `main` is a finding.** I built this because I checked `main` this morning and found `tapefs-v1.md` at DRAFT-3, `engine-api.md` at DRAFT-3 and `acceptance.md` at **DRAFT-1** — three files that each claim in their headers to be versioned in step. Third silent desync on this project, first one with a mechanism.

**`PM-NOTES.md` still ends at 1 September** on your review branch, with no DRAFT-4 entry. I found the findings file directly this time, so nothing was lost — but I asked for this in Decisions 003 §6 and I am asking again, because reading the index first is how I would rather find your work than by guessing at paths.

**`Request Independent Review` is live** on unchanged terms: self-service for CI, tooling, firmware and hardware docs, and for engine PRs whose behaviour you have already covered with landed tests. Decline engine PRs for behaviour you have not yet tested, say why, and escalate.

---

Three adversarial rounds have found 52 defects in specifications I wrote. Six of them would have destroyed a cartridge in a child's hands, and this round's blocker would have let a v1 player quietly corrupt media it was explicitly forbidden to touch. A fourth round on DRAFT-5 is the last thing between us and the format freeze. Take the time it needs.
