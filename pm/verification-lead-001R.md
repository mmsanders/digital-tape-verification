# PM Decisions 001-R — Verification Lead

**Supersedes PM Decisions 001.** · **From:** Program Manager · **Date:** 1 Sep 2026
**Re:** `findings/spec-review-draft1.md`, V-001 … V-022

---

## 0. Disposition summary

Twenty-two findings against a document I wrote. Two blockers, both real, both of which would have destroyed a child's cartridge in the field. **Sixteen are accepted as written. Three are accepted with a different fix than you proposed. Two are moot. One is my error in the charter, not in the spec.** Nothing is rejected.

I have independently verified the arithmetic in V-001 and V-022 and reproduced the failure sequences in V-002, V-003, V-007, V-008 and V-010. They are correct.

The rest of this document is the disposition. **DRAFT-3 of both specs follows from it** — I am issuing a full replacement rather than another changelist, because the accumulated changes now touch the commit protocol, the mount protocol, promote, re-spool, duplicate and the engine boundary. The Software Lead has been told to hold.

| ID | Disposition |
|---|---|
| V-001 | **Accepted**, your fix. Entries move to block 1 |
| V-002 | **Accepted**, blocker. Different fix — see §2 |
| V-003 | **Accepted**, blocker. Different fix — see §3 |
| V-004 | **Accepted**, your fix |
| V-005 | **Accepted**, your fix |
| V-006 | **Accepted**, your fix |
| V-007 | **Accepted**, your fix. Superblock gains a generation number |
| V-008 | **Accepted**, different fix — promote becomes two-phase, see §4 |
| V-009 | **Moot.** The preroll cache is deleted — see §7 |
| V-010 | **Accepted**, your fix, byte-exact values in §5 |
| V-011 | **Accepted**, your preferred fix. Caller supplies UUID and epoch |
| V-012 | **Accepted**, your second reading — commit refuses while frames are owed |
| V-013 | **Accepted**, your first fix — reservation semantics |
| V-014 | **Accepted.** Normative state matrix required in DRAFT-3 |
| V-015 | **Accepted**, your first fix. `tape_dev` is always a partition-2 view |
| V-016 | **Accepted**, your fix |
| V-017 | **Accepted**, and "soft clip" becomes saturating clamp — see §6 |
| V-018 | **Accepted.** Ramp is caller-owned with a normative schedule |
| V-019 | **PM decision made** — see §8 |
| V-020 | **My error, not yours.** Charter invariant reworded — see §9 |
| V-021 | **PM decision made.** Boundary table in §10 |
| V-022 | **Accepted.** Both corrected; I confirmed both |

---

## 1. V-001 — Entry placement contradicts the commit protocol

Correct, and it is the kind of contradiction that only shows up when someone reads two sections against each other rather than in order. §4 put entries at byte 64; §7 wrote entries to blocks 1–127 and block 0 last. The first 448 bytes of the entry array were being written and then overwritten by the header.

**Your fix is adopted verbatim: the entry array begins at byte 512 — block 1.** Block 0 is the header block and nothing else: 64 bytes used, 448 reserved and required zero. Blocks 1–127 hold 65,024 bytes, which is 5,418 entries at 12 bytes; `TAPE_MAX_ENTRIES` of 4096 occupies exactly 96 blocks. Verified.

---

## 2. V-002 — Re-spool overwrites live chunks · BLOCKER

Reproduced. Re-spool writing from `a_high_water` upward while the live index still references chunks in that range means an interrupted re-spool leaves a live index pointing at overwritten audio. A child yanking a cartridge during idle housekeeping destroys it. That is the exact failure the whole format exists to prevent, and it was in the design.

**Accepted, with one rule rather than a multi-generation protocol:**

> **Re-spool writes only to a destination region disjoint from every chunk the live index references, then commits.** The engine chooses the destination: the low region beginning at `a_high_water` when it is disjoint, otherwise the free region above `free_next`.

In practice this is two passes on a fragmented cartridge — one up, one back down — each individually crash-safe under the existing §7 commit, and it needs no new machinery. A precondition falls out and must be stated: **re-spool requires free space ≥ the timeline length**, otherwise `TAPE_ERR_CARTRIDGE_FULL`. A nearly-full cartridge cannot be re-spooled, which is honest and testable.

Your proposed fix — copy-on-write compaction that never overwrites live chunks — is what this is. I have expressed it as an invariant on the destination rather than as a protocol, because an invariant is checkable in the harness and a protocol is only followable.

---

## 3. V-003 — Duplicate can destroy the destination · BLOCKER

Reproduced. Correct that the durability guarantee has to cover both cartridges, and I had only thought about the source.

**Accepted, and neither of your two options exactly.** Requiring a blank destination makes cartridges non-reusable, which kills the whole point of a blank tape. A fully transactional destination needs 2× space and a second index generation.

The resolution is to make the destructive step **explicit, atomic, and first**:

1. **Write the destination superblock with `state = WRITE_IN_PROGRESS`.** One block. Atomic. From this instant the destination will not mount as audio.
2. Write chunks and indices.
3. **Write the destination superblock with `state = VALID`.** One block. Atomic. This is the commit.

A crash at any point leaves a cartridge that mounts as `TAPE_ERR_INCOMPLETE` — not corrupt, not silently wrong, but recognisably a copy that did not finish. The fix is to run the copy again.

The superblock gains a `state` field for this. And the product answer underneath it is the honest one: **copying onto a cartridge erases it, and it says so from the first block written.** That is what dubbing over a tape does, and "the tape in the right slot gets replaced" is a rule a seven-year-old already understands.

---

## 4. V-008 — Promote permanently strands capacity

Reproduced exactly as you describe: promote raises `a_high_water` over the old Side B allocations, §6 makes everything below it immutable, and re-spool starts above the new mark and cannot reach them. Repeated promotes eat the cartridge. My claim that re-spool recovers that space was simply false.

**Accepted, with the fix folded into promote rather than into ownership.** Promote becomes two-phase, mirroring the re-spool rule in §2:

1. Write the compacted timeline to free space above `free_next`. Commit the new A index and superblock (`a_high_water = E`).
2. Write the compacted timeline again, to `[0, len)`. Commit A referencing `[0, len)` and superblock `a_high_water = len`.

Each phase is individually crash-safe under §7 and the existing mount rules. The result is a strong invariant that did not exist before and that you can assert directly:

> **After a completed promote, `a_high_water` equals the timeline length and the cartridge contains no unreachable allocated space.**

Cost is a second copy — promote goes from roughly 15 s to 30 s. It is a deliberate, ceremonial, LED-lit operation and 30 s is fine.

---

## 5. V-010 — A freshly formatted cartridge would not mount

Reproduced. Four valid empty slots with equal sequence numbers hit §8.5's `TAPE_ERR_INCONSISTENT` — every new cartridge, on the first mount, forever. The simplest correct-looking implementation produces unusable media. This one would have been found on day one of WP-06 and blamed on the code.

**Accepted. `tape_format` writes byte-exactly:**

| Slot | State |
|---|---|
| A0 | Valid. `sequence` = 1, `side` = 0, `entry_count` = 0, `total_frames` = 0, CRC over the 64-byte header alone |
| A1 | **Invalid.** All 512 bytes of block 0 zero — magic fails |
| B0 | Valid. `sequence` = 2, `side` = 1, `entry_count` = 0, `total_frames` = 0 |
| B1 | **Invalid.** All 512 bytes of block 0 zero |

Exactly one valid generation per side, the partner deliberately invalid. `TAPE_ERR_INCONSISTENT` stays unreachable through normal operation, which is what makes it meaningful when it fires.

---

## 6. V-017 — Audio arithmetic is not byte-exact

Accepted, and this one blocks Suite 2 entirely — without exact formulas a golden fixture cannot distinguish a bug from a permitted implementation choice, so the cross-target contract is not enforceable. DRAFT-3 will carry exact integer formulas. Two decisions you should know now because they change what you will be testing:

**"Soft-clipped" becomes a saturating clamp.** The safety requirement was never a particular curve — it was *not wrapping*, because a wrap is a full-scale discontinuity in a child's headphones. A curve needs a defined transfer function, adds distortion the design never asked for, and gives one more thing to get subtly wrong. So: sum at `int32`, clamp to `[-32768, 32767]`, store `int16`. Exactly specifiable, exactly testable, and honest about what tape does at its limit.

**Interpolation is fully pinned.** Position is `uint64` with 32 fractional bits. Given consecutive samples `a`, `b` and fraction `f` as `uint32`:

```
out = (int16_t)( a + (int32_t)(( (int64_t)(b - a) * (int64_t)f ) >> 32) )
```

Arithmetic shift, truncation toward negative infinity, no rounding. At the final frame `b = a` — hold, do not read past the end. Channels are interpolated independently with the same `f`.

---

## 7. V-009 — Moot, and why

The on-card preroll cache is **deleted** in DRAFT-2/3. It could not do its job: it lives on the cartridge, so it cannot be read before the cartridge's card is initialised, which is the latency it existed to hide. Your finding is correct against DRAFT-1 and simply has no target in DRAFT-3.

Instant-on now rests on two firmware mechanisms — the play ring retained across sleep, and card initialisation starting on the cartridge-detect switch rather than the play press. **Both need tests you have not been asked for**, and guardrail 04's wake-to-audio budget moves out of the engine and into `firmware/`. Suite 5's budget test relocates accordingly.

---

## 8. V-019 — Resume after a yank · PM decision

You are right that the requirement was not mechanically testable. It is now.

- **Firmware checkpoints position to device flash every 10 s of playback, and on every transport state change** (play, stop, pause, scrub end, side flip).
- **Required accuracy: within 10 s of the true position** after an abrupt removal or power loss.
- **On resume, seek to the checkpoint minus 2 s.**

That last part is not a hedge against the checkpoint interval — it is deliberate. A tape resumed a couple of seconds early is what a real one does, it re-establishes context, and it is strictly nicer than resuming mid-syllable. Test it as specified: resume position must be in `[checkpoint − 2 s − 10 s, checkpoint − 2 s]`.

Flash wear at this cadence is roughly 1,400 writes over a two-hour session against a table of a few kilobytes; it is not a constraint worth designing around, but the number belongs in the firmware acceptance criteria so nobody has to re-derive it.

---

## 9. V-020 — My error, in the charter

You are correct and the conflict is mine. I wrote a crash assertion prohibiting chunks that are "written, unreferenced, and unallocated" — which is precisely the intended state of an aborted write under the derived-`free_next` model. A mechanically correct harness would have reported false failures against a format working as designed.

**The charter invariant is reworded:**

> No **allocated** space below the derived `free_next` is unreachable from the live index. Stale bytes in free chunks above `free_next` are expected and are not a finding.

Thank you for catching a defect in the instructions rather than assuming the instructions were the fixed point. That is the harder thing to do and it is exactly what the seat is for.

---

## 10. V-021 — Boundary semantics · PM decision

The table below is normative and goes into DRAFT-3.

| Situation | Result |
|---|---|
| `tape_seek` beyond end | Clamp to end. `TAPE_OK` |
| Forward render at exact end | `*rendered` = 0, `TAPE_OK`, end-of-media condition set |
| Reverse render at frame 0 | `*rendered` = 0, `TAPE_OK`, start-of-media condition set |
| Splice into an empty index | Creates the first entry at position 0 |
| Splice at exact end | Append |
| Overwrite at end | Append. Overwriting nothing is appending |
| Overdub at end | Append. Nothing to sum against, so input passes through |
| Overwrite/overdub beyond end | Not reachable — position is always clamped |

**End of tape is not an error.** It is the normal end of a normal tape, and firmware turns it into a physical event: the play button pops up. Both conditions are retrievable via a new `tape_status()` call rather than being smuggled into a return code, so a caller polling from the main loop can act on them without inspecting every render result.

---

## 11. What this costs, and what it bought

DRAFT-3 is roughly two to three days of my work. Stream 1's index and commit code waits for it; the Software Lead has been told which parts of WP-06 it can start on in the meantime.

Against that: V-002 and V-003 each destroy a cartridge in a child's hands, and both were in a document I was three days from freezing. Finding them now costs days. Finding V-002 after the format froze costs a format revision and reflashing every cartridge in the house; finding it after the kids had cartridges they cared about costs something that cannot be bought back.

Two things about how you worked that I want stated plainly. You found V-020 — a defect in your own instructions — and reported it rather than working around it or quietly satisfying it. And you separated `question` from `major` honestly, which meant I could triage twenty-two findings in one pass instead of relitigating each severity. Both of those are why this pass was worth more than a longer one would have been.

---

## 12. Next steps

1. **Wait for DRAFT-3.** Do not re-review DRAFT-1; the surface has moved too far for a second pass to be economical.
2. **When DRAFT-3 lands, review these first**, because they are new and have had the least scrutiny: the re-spool disjointness rule (§2), two-phase promote (§4), the `WRITE_IN_PROGRESS` duplicate protocol (§3), and the superblock generation number (V-007). New text is where the next V-002 lives.
3. **You may start now on** the crash-injection harness structure and the fault-injecting block device — neither depends on the resolved findings — and on the Suite 3 invariant list, which is largely unchanged and gains the two new invariants in §2 and §4.
4. **Still owed to you:** WP-10 and WP-11 acceptance criteria. They come with DRAFT-3 in `spec/acceptance.md`.
5. **`Request Independent Review` is live** in `Digital-Tape`, on the terms in the previous document — including your standing instruction to decline requests on engine PRs whose behaviour you have not yet written tests for.

One process change: your repository is public now and I can read `PM-NOTES.md` and `findings/` directly. **Keep filing there rather than relaying through Michael.** I will check it on every pass.
