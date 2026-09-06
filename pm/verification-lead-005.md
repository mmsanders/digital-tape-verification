# PM Decisions 005 — Verification Lead

**From:** Program Manager · **Date:** 4 Sep 2026 · **Re:** all fifteen DRAFT-5 findings, DRAFT-6, and a freeze standard you effectively set
**Supersedes:** Decisions 004.

**All fifteen accepted. None rejected. Both blockers were credible cartridge-loss paths and both are closed. And your freeze-impact section changed Michael's mind, which is the most consequential thing a review has done on this project.**

---

## 1. The freeze standard moved because of your last paragraph

You reported that neither blocker touched the Phase 0 candidate sections — the exact condition I had told Michael I would bring him a signature on — and then wrote that the candidate "does not meet the convergence assessment's stronger clean-pass standard" because eight majors remained in it.

I put both to Michael. **He held the signature for a round.**

**The standard is now: no blocker *and* no major in the candidate sections.** You were right that the narrow gate was the wrong gate, and you were right in the way that mattered: the eight included a reverse-playback phase defect that would have been frozen into the goldens as the reference, and an ABI contradiction in `tape_tell` that no implementation could satisfy. A gate that passes those is set too low, and I set it.

**Your DRAFT-6 pass is what measures against the new standard.**

---

## 2. The dispositions, briefly

Full text is **PM Decisions 008**, which Michael has. In one line each:

- **V5-001** → **`FAULTED`**, a quarantine state (`engine-api` §7.2). Four calls permitted, `tape_service` explicitly not, and it overrides every other mounted row. Two exclusions where nothing became indeterminate: phase-4 repair, and a `tape_dup` failure against the *destination*.
- **V5-002** → an explicit empty-source branch in `tape_dup`. **Third instance of the same family**, so invariant 30 now enumerates all four empty behaviours and `acceptance.md` asserts them in one test.
- **V5-003** → mount is **four phases**; index selection and the stage oracle at 3, repair at 4. Your point that stage clearing would have erased the evidence is the one that decided the placement.
- **V5-004** → **degraded-B** (`tapefs` §4.4), with all fifteen matrix cells defined.
- **V5-005** → snap to `(total_frames − 1) << 32`. See §3 — I got the fix wrong first.
- **V5-006** → both operands cast before subtracting.
- **V5-007** → ordered algorithm, NULL guard first, `data != NULL` added.
- **V5-008** → zero-frame commit is a zero-write no-op in all three modes, and it disarms.
- **V5-009** → `tape_result tape_tell(const tape *, uint64_t *)`. New **WP-06h** exercises the Not-mounted row, which no work package previously touched despite §10 claiming every cell was covered.
- **V5-010** → new **`tapefs` §8.1 durability convention**. Every boundary between a write and its flush admits both outcomes; WP-10 runs each in both modes and reports which.
- **V5-011** → 45 cells exercised, 33 `B`; `block_budget == 0` → `TAPE_ERR_INVALID_ARG`.
- **V5-012** → full-domain equivalence is now a **proof**, written out in `engine-api` §8; the gate is 131 071 deltas × 12 boundary `f` values plus 10⁷ seeded pairs, on two toolchains, one with integer-promotion width visible.
- **V5-013** → normative side-switch transition. The stale ring was the dangerous part.
- **V5-014** → no re-entry from a callback, **except** `tape_render`, `tape_status`, `tape_get_info`, `tape_tell` — banning render would put a dropout in every copy.
- **V5-015** → **`tapefs` §4.5**, headroom per logical operation, preflighted in 64-bit. Recording reserves at `tape_arm`.

---

## 3. What my own audit found, so you do not spend your pass rediscovering it

Three audit passes over DRAFT-6 before shipping: **37 defects, six blockers.** All fixed. **Two of the six were introduced by my fixes for your findings**, which is the fact I most want you to have:

- **My V5-005 fix stopped frame 0 ever being emitted.** I set `at_start` on the step that *lands* on frame 0, and the loop tests the flag before emitting — so `[0,1000,2000]` at −1.0× gave 2000, 1000, stop. The first frame of every tape, dropped on every rewind, and WP-08's own new golden unachievable against the normative algorithm. Corrected and traced numerically across −1.0×, −0.5×, −2.0×, from position 0, and at `total_frames == 1`.
- **My V5-003 fix made a cartridge permanently unmountable.** I put the stage oracle before the degraded-B branch. Every resume row constrains a live Side B, so a cartridge that was both stage-1 and degraded-B matched nothing and returned `TAPE_ERR_INCONSISTENT` — and the only recovery needs a successful mount. All of Side A's music, unreachable, on a cartridge whose Side A was intact. Degraded-B is now decided first.
- **My V5-015 headroom predicate wrapped in u32.** `0xFFFFFFFC + 4 == 0` passes. `acceptance.md` crafts exactly that `sequence`, so a conforming-but-32-bit engine would have passed the test written to catch it.
- `engine-api` §5 still described DRAFT-5's mount order, reinstating V5-003 inside the document that fixed it. The warm-start algorithm fell through from `use:` into `cold:`, so warm start could never engage. RESUME-at-step-5 over-stated its generation headroom and stranded stage-1 media at the boundary.

**A self-audit is not an adversarial review.** It finds contradictions, arithmetic, and rules stated in one document and enforced in neither. It does not find the things I still believe are true — and on this evidence it is *least* reliable exactly where a finding has just been closed.

---

## 4. Where to aim

Newest normative text with the least scrutiny first.

1. **`engine-api` §7.2 — `FAULTED`.** Entirely new, and it is a **state that overrides other states**, which is the shape most likely to hide an unreachable or a contradiction. Is the trigger complete — is there a writing path on the mounted device that escapes it? Is the permitted set right? Is `tape_abort` in FAULTED genuinely media-free? Are the two exclusions (phase-4 repair, dup destination) safe, or have I carved a hole in the quarantine to protect a use case?
2. **`tapefs` §4.1–§4.2 — the four-phase mount and the step order inside phase 3.** Degraded-B before the stage oracle is load-bearing and one round old. Does anything else depend on the old order? Is invariant 26 — *no failing mount writes anything* — now actually true?
3. **`tapefs` §4.5 — the headroom table.** **Recompute every row against §9's actual write sequences.** I got RESUME-at-step-5 wrong by one, and one row being wrong by one strands media forever.
4. **`tapefs` §8.1 and the two rewritten crash tables.** The durability convention doubles the state space of every boundary. Are the tables complete under it, including the boundary-fallback rows for `sb_generation ≥ 0xFFFFFFFD`?
5. **`engine-api` §6.2/§6.3 — the flag lifecycle.** I have traced it; trace it independently. `at_start`/`at_end` interact with `tape_seek`, `tape_set_rate`, the snap, `tape_set_side`, and §11's rows.
6. **`tapefs` §4.4 — degraded-B**, and whether the fifteen cells are right.

Then everything else.

---

## 5. WP-10, WP-11, WP-12a

Your three testability verdicts were all "not testable as written", and each named specific causes. Every named cause is dispositioned:

- **WP-10** gains **two durability modes on every boundary**, the empty-duplicate case, the degraded-B and stage-oracle cases, the counter boundaries per operation, and the FAULTED oracle.
- **WP-11**'s portability gate is now a finite, runnable definition plus a proof, and mutation 7 gains the two pointer cases.
- **WP-12a** gains the corrected cell counts, zero budget, re-entrancy, and the FAULTED transition with its eleven `F` cells and four allowed calls.

**Confirm they are testable as written, or say what is not.** That verdict is a deliverable in its own right and it has been right three rounds running.

**Goldens.** All three of the things you said had to be resolved were resolved in DRAFT-5, and then two of them were wrong. They are resolved again now, and the reverse-from-end golden you asked for — a multi-frame non-linear timeline, not a first-sample assertion — is in WP-08 because your finding said a first-sample assertion would have missed it. **Do not freeze bytes until your DRAFT-6 pass is clean on `engine-api` §6.2, §6.3 and §8.**

---

## 6. Process

**`PM-NOTES.md` on your review branch still ends 1 September.** Two findings files have landed since. I found both directly, so nothing was lost — but I have asked twice now, and the reason is not bookkeeping: the index is what I read first, and a round where I miss your pass is a round where the leads build against a document you have already broken.

**The manifest is live.** `spec/VERSION.md` is on `main` with a CI gate that the Software Lead proved red-able in three independent ways — including one that found a real hole in my script, where two empty `sed` extractions compare equal. **Your copies are courtesy copies**; `main` is authoritative, and a disagreement is a finding. The publication gap you flagged in your DRAFT-5 pass is closed: `main` published DRAFT-3/DRAFT-3/DRAFT-1 when you reviewed, and it now publishes the bundle, hash-verified.

---

Four adversarial rounds have found 67 defects in specifications I wrote. Two of this round's blockers were cartridge-loss paths a child could reach by ordinary use — copying a blank tape, and pulling a card at the wrong moment. The freeze standard is higher than it was because of your last paragraph, and the thing that closes Phase 0 is your next pass.
