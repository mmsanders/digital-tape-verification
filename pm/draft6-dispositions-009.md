# PM Decisions 009 — DRAFT-6 dispositions, PR decisions, and the substitute verifier

**From:** Program Manager · **Date:** 5 Sep 2026
**Re:** all nine findings V6-001…V6-009; issue #23; the open PRs; the library's real print budget
**Distribution:** Michael, Software Lead, Hardware Lead, Verification Lead
**Companion:** `spec/tapefs-v1.md`, `spec/engine-api.md`, `spec/acceptance.md`, `spec/VERSION.md` — all DRAFT-7

**All nine accepted. None rejected. Issue #23 accepted — it was a real gap and it was mine.**

---

## 0. Merge decisions, stated first from now on

Michael has asked that every communiqué open with a merge verdict. Here are all three.

| PR | Verdict |
|---|---|
| **`Digital-Tape` #20** — WP-06 read path, WP-07 allocator | **Do not merge. Keep as draft.** Two independent holds: structural Rule 1 (the Verification Lead's WP-10 tests are not on `main`), and it is now **three revisions behind** — 148 checks green against DRAFT-4 while `main` carries DRAFT-6 and this bundle makes it DRAFT-7. It is not stale in the sense of abandoned; it is correctly parked. Rebase and reconcile, do not merge |
| **`Digital-Tape` #23** — acceptance.md carries no audit language | **Valid. Fixed in DRAFT-7.** Close it when the bundle lands |
| **`Digital-Tape-Verification` #1** — "DRAFT-5 adversarial review" | **Merge, then change the rule.** See §4 |

---

## 1. The nine findings

Six touch the freeze candidate, so **the Phase 0 signature is held for a second round.** That is the standard Michael raised and the verifier applied it correctly without being asked twice.

| # | Finding | Disposition |
|---|---|---|
| **V6-001** | Degraded-B has *two* causes — neither B slot valid, **and both valid at equal `sequence`** — but `tape_reset_side_b` assumed only the first, so its "highest live sequence + 1" wrote 11 against a surviving B1 at 500 and **the recovery returned success while changing nothing** | Both causes named in §4.4. The recovery writes **B0 at `cartridge_sequence + 1`**, which is a maximum over every structurally valid slot — so it wins selection in both cases |
| **V6-002** | §4.5 reserved the worst case unconditionally, so an **empty re-spool** near the counter boundary returned `TAPE_ERR_SEQUENCE_EXHAUSTED` instead of the zero-write `TAPE_OK` its own §9.4 requires | §4.5 is now **branch-exact**, and every branch is decidable before the first write. Phase 2's cost reduces to `S ≥ len`, both known at classification |
| **V6-003** | **`live_sequence` was never defined.** Every "commit at `sequence + 1`" had no base | New **§5.5**: `cartridge_sequence` is the maximum over every *structurally valid* slot of all four, with structural validity defined for index slots for the first time |
| **V6-004** | Invariant 7 required **both** counters to advance on every logical update, so a verifier asserting it literally **fails every ordinary recording** — no recording writes a superblock | The two counters now have **separate domains**: `sequence` on index commits, `sb_generation` on superblock updates, repair on neither |
| **V6-005** | WP-08's side-switch regression started from a state the matrix forbids — `at_end` on a non-empty timeline can only be set while *Playing*, where `set_side` was `BUSY`, and `tape_set_rate(0)` clears the flags | **`tape_set_side` is now permitted while Playing**, rate retained. That matches the object — you can turn a tape over while the motor runs — and it makes the transition testable instead of dead text |
| **V6-006** | A `tape_dup` destination failure was specified to return the source to *Mounted, idle*, but dup can start from *Playing* and nothing changes the rate | Termination returns to **the underlying transport state**. A destination-only failure alters the source's position, rate and ring **not at all** |
| **V6-007** | The final superblock write was one crash row where it is two boundaries; format had **no row at all** for "inside step 5" | Both tables split into mirror and primary boundaries, with the torn-primary outcome named |
| **V6-008** | The high-generation fallback always zeroed the mirror first — and these raw operations accept a destination whose **mirror is the only valid copy**, so that order could leave both invalid | The fallback zeroes the **non-selectable copy first**. So does the ordinary step 1, for the same reason |
| **V6-009** | WP-12a demanded `TAPE_ERR_BUSY` from *every* callback re-entry, contradicting the four exemptions I had written two sections earlier; and the termination rule read literally ended the operation on that BUSY | The four exempt calls **succeed**; a re-entry BUSY **never** terminates |

**Issue #23** — PM Decisions 008 §4 told three people an independent audit had been added to `acceptance.md`. The word "audit" appeared in it **zero times**. The Hardware Lead found it. The hardware safety section now requires procedure, instrument and calibration, conditions, raw readings, derivation, and **stated measurement uncertainty** — the last because the thermal margins are narrow enough for the uncertainty to decide pass or fail. Second time this round that something I announced as done existed only in a communiqué.

---

## 2. What my own audit found

Two audit passes over DRAFT-7. **27 defects, two of them blockers**, both introduced by *my fixes for this round's findings*:

- **Promote's four index commits collided on `sequence`.** My §5.5 said "the second index writes `+ 2`" and stopped — enough for a two-commit operation. A FRESH promote commits **four**, so steps 7 and 8 reused steps 2 and 3's values. Between steps 7 and 9 **both Side A slots are valid at the same `sequence`**, which §5.3 calls `TAPE_ERR_INCONSISTENT` and *"the cartridge is unusable"* — and every recovery needs a mount. **The cartridge and all of Side A's music, lost.** Two rows of §9.3.4 promised a resumable state there and were false. Fixed with a running counter.
- **My fix for the generation-0 destination removed the `WRITE_IN_PROGRESS` barrier.** I chose "treat generation 0 as blank and skip step 1". Step 1 is the barrier that makes a destination unmountable for the length of the copy, and **every reusable-media crash row derives from it.** Skipping it leaves a stale `VALID` superblock over indices that no longer exist, for ~29 seconds. A power cut at the wrong moment then produces a cartridge that **mounts and plays the source's music while reporting the destination's previous UUID** — so the device's position table, keyed by that UUID, indexes a different timeline. Silent, and permitted by no oracle. The other fix — `max(existing, 1) + 1` — closes the original hole and keeps the barrier.

Also: promote's three superblock writes never said `sb_generation + 1` (this document is byte-exact by charter, so the general rule in §4.1 is not enough); the adopt-in-place branch over-reserved a sequence it never uses; and M-3's fix landed in one document of three.

**Both blockers were in text written to close a finding.** That is now three rounds running. The pattern is not that fixes are rushed — it is that a fix is the only text in the document that has never been reviewed by anyone but its author.

---

## 3. The substitute Verification Lead — my assessment

Michael swapped to a different ChatGPT agent for this round and asked for an extra hard look.

**It is good. Keep it through Monday.** Specifically:

- **It verified the three SHA-256 hashes against `spec/VERSION.md` before reviewing**, and said so. No previous pass did that unprompted. It is the first reviewer to treat the manifest as the thing it is.
- **It kept the implementation-independence boundary and stated it twice**, including a closing statement naming exactly what it did and did not open.
- **It ran independent numerical traces on the transport arithmetic and then declined to file against §6.2, §6.3 and §8**, saying so explicitly. That is the harder judgement and the more useful one — a weak reviewer pads the list. It is also correct: I re-traced those sections myself.
- **It applied the raised freeze standard** — no blocker *and* no major in the candidate — without being told twice, and recommended against signature on that basis.
- **It updated `PM-NOTES.md`**, which I asked the regular lead for three rounds running and did not get.
- **All nine findings are real.** I verified V6-002, V6-003, V6-004, V6-005, V6-007, V6-008 and V6-009 against the documents myself.

**I looked hard for under-calling and did not find it.** Nine findings and zero blockers, against fourteen and fifteen with two blockers in the previous rounds, is the shape you would expect if a reviewer were being soft. So I took the two most blocker-shaped findings and checked whether they had been mis-graded. **V6-001**: the recovery fails, but the starting state is already a media fault, and no *new* data is lost. **V6-008**: the fallback can brick a cartridge — that is being erased on purpose. Both are correctly **major**. The grading is right.

**The one thing I cannot tell from a single sample is depth versus quality.** Nine findings on a draft that had just absorbed fifteen findings and thirty-seven self-audit fixes is a plausible number. It is also what a shallower pass would produce. So, a cheap calibration when the regular lead returns: **have them review DRAFT-7 without first reading the substitute's DRAFT-6 findings**, and compare what each finds in the overlapping text. That costs one pass and tells us something we currently have no way to know.

---

## 4. The verification repository has the publication gap I already fixed once

`Digital-Tape-Verification` `main` carries findings up to **DRAFT-3**. The DRAFT-4, DRAFT-5 and DRAFT-6 passes all live on branches. PR #1 has been open since 3 September and its title still says DRAFT-5.

This is the same failure as `Digital-Tape` `main` publishing DRAFT-3/DRAFT-3/DRAFT-1, in the other repository, and I did not look for it there. **Findings land on that repository's `main`**, from now on, for the same reason specs do: a document three streams read as truth cannot live only on someone's branch. PR #1 should be merged (or re-scoped and merged) so `main` carries every pass.

---

## 5. The library, and the printer decision reversed

Michael can print **twice a month per library card** and can borrow credits from at least two other people — **six plates a month guaranteed, possibly more.** He is not buying a printer, and M-04 closes.

Two consequences that matter more than the count:

**Six plates is not six designs.** The WP-04 plate already carries seventeen objects. Six plates a month at ten-plus variants each is a real iteration loop — call it 2–4 months for a latch instead of 5–10. That is the difference between a schedule and a wall.

**We cannot choose the material, and that changes the clasp design.** Single spool, no colour choice, and probably PLA. Decisions 006 §2 assumed PETG. The relevant property is **not** cycle fatigue — a cartridge is opened once or twice in its life — it is **creep under sustained load**, because a clasp is engaged 99.99 % of the time. PLA creeps at room temperature under sustained strain, so a lip held deflected for a year loses its grip.

**The design rule that follows, and it is the important instruction in this round's hardware communiqué: the clasp must not be held deflected when closed.** The lip snaps past and returns to near-zero strain; retention comes from the undercut geometry, not from stored spring force. A clasp designed that way is indifferent to the material the library happens to have loaded — which is the only kind of clasp we can actually specify.

Michael is asking the library on Monday whether he can supply his own filament. His question list is in his queue.

---

## 6. Next

- **Software Lead** — land the DRAFT-7 bundle; #20 stays a draft; then reconcile the read path against a fourth revision of the mount and a new `cartridge_sequence` rule.
- **Verification Lead** — a DRAFT-7 pass aimed at §5.5's running counter, §4.5's branch table, and the reordered step 1. Merge the review branches to that repo's `main`.
- **Hardware Lead** — the plate is verified sound and printable; **two items on the card must be settled before the trip** (three buttons are the same part; four clasp variants share two mating halves). Then the creep-resistant clasp geometry.
