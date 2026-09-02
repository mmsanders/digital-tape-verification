# PM Decisions 002 — Verification Lead

**From:** Program Manager · **Date:** 2 Sep 2026
**DRAFT-3 of both specs and DRAFT-1 of `spec/acceptance.md` accompany this. Everything you listed as "still needed" in PM-NOTES is now delivered. The adversarial review of DRAFT-3 is the critical path for the whole project.**

---

## 1. What you are receiving

Three files, pasted by Michael:

- `spec/tapefs-v1.md` **DRAFT-3** — full replacement. Incorporates V-001…V-022 per the disposition in Decisions 001-R, plus decisions since.
- `spec/engine-api.md` **DRAFT-3** — full replacement.
- `spec/acceptance.md` **DRAFT-1** — the WP-10 and WP-11 criteria you asked for, plus every other work package's, plus the firmware criteria the specs reference.

**Do not diff against DRAFT-1.** Review DRAFT-3 as a whole; the surface moved too far for a delta pass to be economical.

---

## 2. Transport, settled

Your repository is public. **I read `PM-NOTES.md` and `findings/` directly on every pass, and the Software Lead may read it directly to pull test source into `tests/`.** File there; do not relay through Michael. Michael pastes spec drops into you once per draft, because your instance has no browsing — that is the only human step remaining, and it is low-frequency.

The Software Lead proposed, and I approved, a structural form of seam rule 1: engine implementation stays on unmerged branches until your tests for that behaviour are on `main`. `main` will carry spec → tests → implementation in that order, visibly. Your standing instruction not to open `engine/` stands regardless.

Also decided on the Software Lead's proposal: a test of yours that calls an API the spec does not define is treated as a **spec finding** and routed to me — it is never "fixed" by adding the call. You already produced this case with `tape_status` and seek; both are now in the spec.

---

## 3. What changed since Decisions 001-R — attack these first

The disposition in 001-R told you the shape of the fixes. DRAFT-3 has the text. New material has had the least scrutiny, so in priority order:

1. **`tapefs` §5.1–5.2 — run-length entries.** Every bounds check is now against `last_chunk_id`, computed from `start_frame + frame_count − 1`. The Side A immutability invariant lives in that one line of integer arithmetic. I would expect a real defect to be findable here and I would rather you found it.
2. **`tapefs` §9.4 — the re-spool disjointness rule.** Stated as an invariant on the destination rather than as a protocol. Check whether "lowest disjoint region" is well-defined in every fragmentation state, and whether the two-pass case can leave the second pass without enough contiguous space.
3. **`tapefs` §9.3 — two-phase promote.** Both phases are meant to be individually crash-safe. Enumerate the boundaries.
4. **`tapefs` §4.1 — the two-copy superblock with generation.** New. Order is mirror → flush → primary → flush. Check the equal-generation case and the read-only path.
5. **`tapefs` §9.5 — duplicate.** `WRITE_IN_PROGRESS`, identity written last. Your V-003 reproduced against DRAFT-1; reproduce it against this.
6. **`engine-api` §10 — the state matrix.** New, normative, and exactly the kind of table where one wrong cell is a silent data loss. Read it cell by cell against §7's owed-frames rules.
7. **`engine-api` §8 — the exact arithmetic.** Both formulas are now pinned; check them for overflow at the extremes and for the `b = a` endpoint.

Then everything else.

**Two things that are no longer targets:** the preroll cache (deleted; V-009 moot) and `nominal_length_s` as a limit (it is a label; `tapefs` §2).

---

## 4. Decisions since 001-R you should know

- **C-60 is the standard cartridge** — 635 MB, 1 211 chunks. C-90 and C-120 are permitted by the format. **Parameterise every test on `nominal_length_s`**; do not bake in 90 minutes or 1 817 chunks.
- **Record light shows Side B headroom** via `tape_status().entries_free` — thresholds in `acceptance.md`. The wall behaviour is: record button does not hold.
- **Resume policy** as in 001-R §8, now normative in `acceptance.md`: checkpoint every 10 s and on transport change, resume 2 s early, accuracy window `[checkpoint − 12 s, checkpoint − 2 s]`.
- **Two budgets:** RAM 200 KiB, `.rodata` 32 KiB. Stack ≤ 8 KiB.
- **Correction to 001-R:** the splice headroom after re-spool is roughly **2 000 splices**, not 4 000. Each splice costs two entries — one split, one insert. I counted entries. `tapefs` §5.1 has the corrected figure.
- **The charter now carries a revision marker** (Rev C). Your copy of the Verification Charter is unchanged in substance; the crash-assertion rewording from 001-R §9 is the only edit.

---

## 5. On `Request Independent Review`

Live in `mmsanders/Digital-Tape`. Terms unchanged from Decisions 001: self-service for CI, tooling, firmware, hardware docs, and engine PRs whose behaviour you have already covered with landed tests; **decline** engine PRs for behaviour you have not yet tested, say why, and escalate. Your `findings/` format applies.

---

## 6. Next steps

1. Adversarial review of DRAFT-3, in the order in §3. File to `findings/spec-review-draft3.md` in your repository. Use the same severity discipline; `blocker` is reserved for cartridge loss or hearing harm.
2. Confirm `spec/acceptance.md` WP-10 and WP-11 criteria are testable as written, or say what is not.
3. Begin the fault-injecting block device and crash-harness structure against `engine-api` §3 — nothing in them depends on open findings, and the Software Lead's `dev_sim` (power-loss-after-N, torn writes) exists and can be read from `tests/` on `main`.
4. When your DRAFT-3 findings are dispositioned, Michael gets the format-freeze sign-off (Q-001). Your pass is the last gate before it.

The DRAFT-1 review found two blockers I was three days from freezing. That is the standard. Hold it against DRAFT-3.
