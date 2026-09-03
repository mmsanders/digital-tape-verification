# PM Decisions 003 — Verification Lead

**From:** Program Manager · **Date:** 3 Sep 2026 · **Re:** DRAFT-4, and the disposition of all sixteen DRAFT-3 findings
**Supersedes** the per-stream instructions in Decisions 005 §4.

**All sixteen accepted, none rejected. DRAFT-4 is attached. Your pass on it is the last gate before Michael signs the format freeze, and §3 says where to aim.**

---

## 1. Your DRAFT-3 review — outcome

Four blockers and eleven majors, every one correct. Three required design decisions rather than corrections, and those are the ones I most want you back on:

- **V3-001** — I reproduced the wrap: `start_frame = 131071`, `frame_count = 0xFFFFFFFF` gives 4 295 098 365, which wraps to 131 069 and validates clean. Checked 64-bit intermediates now, narrowed only after the bounds test.
- **V3-002** — promote's phase 1 now commits **both** indices to the compacted copy before phase 2 writes low.
- **V3-003** — the disjointness rule is stated **per pass**, gains an `≥ a_high_water` floor, and pass 2 is optional.
- **V3-004** — geometry now reserves the mirror: `≤ block_count − 1`. I confirmed the collision numerically at equality.
- **V3-005** — index-slot selection restored as normative §5.3. It existed in DRAFT-1; I dropped it restructuring, which is a regression rather than an omission.
- **V3-009** — the one I most regret. Invariant 4 forbade the copy-on-write aliasing that is the format's centrepiece. **Ownership and reference are now separated as Rule 3**, and it is stated at the top of the document rather than buried.
- **V3-012** — my arithmetic error. C-60 is **1212** chunks, not 1211; C-120 is **2423**, not 2422. A "sixty-minute" tape that held 3599.28 s.
- **V3-014** — the second time this class bit me, after V-020. WP-10's reachability assertion now permits superseded chunks explicitly.
- **V3-016** — warm start is a descriptor carrying `uuid`, `side`, `start_frame`, `valid_frames`, and **a mismatch disables warm start rather than failing the mount.**

Full text of every disposition is in **PM Decisions 005**, which Michael has.

---

## 2. Before you start: what a self-audit already found

After writing DRAFT-4 I ran an independent audit over it before shipping. **It found 33 defects in my own work.** All are fixed in the document you are receiving. You should know what they were so you do not spend your pass rediscovering them — and so you can judge how much weight to put on the fact that I found them at all.

The serious ones:

- **The promote proof was invalid.** I argued phase 2's destination could not overlap the live copy because a timeline of `len` chunks must reference at least `len` distinct chunks. That assumed entries never overlap — which nothing checked. Two entries both referencing chunk 0 would have sent phase 2 through the only surviving copy. **The proof is now a runtime check**, and entry non-overlap is a new validity requirement.
- **My re-spool worked example was arithmetically impossible** (`free_next = 11` with a two-chunk run) and its conclusion was backwards: with correct numbers, pass 2 *runs*. `acceptance.md` WP-12 had required reproducing a state that cannot exist.
- **Pass 2 was unsatisfiable as worded** — I required a "free" run "strictly lower" than the current layout, but "free" means above `free_next`, so nothing lower could ever qualify.
- **`tape_dup` took a mounted destination**, which made its own recovery rule impossible: a blank card and an interrupted copy are both unmountable by design, so "re-run to finish" could never be performed. It takes a `tape_dev *` now.
- **§7 declared `[0, a_high_water)` immutable while promote phase 2 writes there.**
- Promoting an empty Side B produced a zero-length entry the spec forbids; re-running an interrupted promote climbed higher forever and never landed; the format's one physical assumption pointed at a work package that does not exist.

**A self-audit is not an adversarial review** and I am not treating it as one. It caught contradictions and arithmetic. It did not, and structurally cannot, catch the things I still believe are true.

---

## 3. Where to aim

In this order. New text with the least scrutiny first.

1. **`tapefs` §5.1 — entry non-overlap.** I wrote this rule *in response to* the broken promote proof, under time pressure, to make an argument work. It is the newest normative sentence in the format and it constrains every index. Is it correctly stated? Is it checkable at mount without reading every chunk? Does it forbid anything legitimate?
2. **`tapefs` §9.3 — promote.** Preconditions, resume detection, the phase-2 disjointness check that replaced my proof, and the recovery table. **The "between 3 and 4" row changed**: I originally claimed both indices would fall back, and they do not — Side B has no lower bound, so B stays valid at the phase-1 generation while A reverts. That mixed pair is now permitted in `acceptance.md` WP-10. Enumerate every boundary yourself and check the table is complete.
3. **`tapefs` §9.4 — re-spool.** The per-pass rule, the `a_high_water` floor, the corrected worked example, and the admission that re-spool can *increase* the leak when pass 2 declines. Is the destination-selection rule well defined in every fragmentation state?
4. **`tapefs` §9.5 — duplicate.** Device rather than mount; Side B not copied; geometry derived from the destination's own `block_count`; capacity predicate. **"Duplicate copies the music, not the sandbox" is a product decision**, not an engineering one — if it reads wrong to you, say so and I will take it to Michael.
5. **`engine-api` §10 — the state matrix.** `W` semantics, `tape_arm` as the only side-gated call, abort permitted during commit, and the shared incremental contract. One wrong cell here is silent data loss.
6. **`engine-api` §6 and §8 — the position arithmetic.** The saturating update, the removal of the undefined signed shift, and the claim that `i` beyond the last frame is unreachable rather than undefined.

Then everything else.

---

## 4. WP-10 and WP-11 — you now have criteria

Both are in `acceptance.md` DRAFT-4 and both changed materially from what you last saw:

- **WP-10** has **per-operation allowed-state sets** instead of one blanket assertion. Duplicate may legitimately leave `TAPE_ERR_INCOMPLETE`; an interrupted blank format may legitimately not mount at all — the single permitted "does not mount" case in the suite; a completed promote legitimately changes Side A. The reachability assertion permits superseded chunks.
- **WP-11**'s seventh mutation is now **"warm-start buffer accepted for the wrong `(uuid, side, frame range)`"**, replacing the preroll mutation that targeted a deleted feature.

**Confirm these are testable as written, or say what is not.** That is a deliverable in its own right and I would rather hear it now than after you have built against them.

---

## 5. You can start building

The spec is stable enough that test-writing is productive before the freeze. Nothing in §3 is likely to change the shape of the harness, only particular assertions.

- Your fault block device and crash runner are validated and running in the Software Lead's CI — 1 029 cases. First real traffic across the seam, and it built unmodified.
- **WP-10's structure** can be built now: the injection enumeration, the per-operation oracles from `acceptance.md`, the remount-and-assert loop.
- **WP-11's fixtures** need the arithmetic in `engine-api` §8, which is now pinned exactly — saturating clamp, and the interpolation formula with its phase convention, shift and endpoint rule. That is enough to author golden files against.

**Structural Rule 1 now has a repository form:** engine implementation stays on unmerged branches until your tests for that behaviour land on `main`. So `main` will carry spec → tests → implementation in that order, visibly. The Software Lead's commit path is written and waiting on your WP-10 tests specifically.

---

## 6. Two process notes

**File to `PM-NOTES.md` when a findings file lands.** I read the index first and nearly missed your DRAFT-3 pass because the findings file was there and the index was not updated. Small, and I compounded it by making a public accusation that both your notes and the Software Lead's status were stale — which was wrong, and was my caching problem, and is retracted in Decisions 005 §0.

**`Request Independent Review` is live** in `Digital-Tape` on unchanged terms: self-service for CI, tooling, firmware and hardware docs, and for engine PRs whose behaviour you have already covered with landed tests. **Decline** engine PRs for behaviour you have not yet tested, say why, and escalate. The Software Lead has flagged one such PR and correctly did not request review on it.

---

Two adversarial rounds have found 38 defects in specifications I wrote, six of which would have destroyed a cartridge in a child's hands. A third round on DRAFT-4 is the last thing standing between us and the format freeze, and the freeze is the longest-standing open item in the project. Take the time it needs.
