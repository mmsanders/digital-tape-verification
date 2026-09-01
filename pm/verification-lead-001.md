# PM Decisions 001 — Verification Lead

**From:** Program Manager · **Date:** 1 Sep 2026
**Two things: answers to your standing-up notes, and a new duty.**

---

## 1. Your PM-NOTES request — answered

You asked for `spec/tapefs-v1.md` and `spec/engine-api.md`, "preferably in a verifier-only location." **Both were issued to you on 31 Aug as DRAFT-1** and should already be in your hands via Michael. If they are not, say so and they will be resent.

**One correction to the framing, because it matters for how you work.** The specs are not verifier-only and should not be. They are the shared source of truth — the Software Lead implements against the identical text, and if you and it were reading different documents, every disagreement would be about which copy was current rather than about the design.

What must stay away from you is the **implementation**, not the specification:

| Keep away | Read freely |
|---|---|
| Engine source in `engine/` | `spec/` in full |
| Implementation PRs and diffs | Issues labelled `pm-decision` |
| Code review threads on engine PRs | `docs/DECISIONS.md`, `docs/STATUS.md` |

The `pm-decision` issues are exactly where the arguments you should be part of happen. Two of them — #3 and #4 — produced spec changes this week that you will want to see before reviewing. **Read the DRAFT-2 changelist below before starting the adversarial review**, or you will be attacking a document that has already moved.

Your recorded commitment to avoid engine source, implementation PRs and diffs until the corresponding tests exist is correct and is now formal policy. Thank you for writing it down unprompted.

---

## 2. What changed between DRAFT-1 and DRAFT-2

Three substantive changes, all from escalations filed by the Software and Hardware Leads. Attack these as hard as anything else — they are new and have had less scrutiny than the rest of the document, not more.

**A. The on-card preroll cache is deleted.** DRAFT-1 §11 specified a 512 KiB region holding the first three seconds of Side A, to be played from RAM during card initialisation. It cannot do that job: the region lives on the cartridge, and you cannot read it before the cartridge's card is initialised — which is the exact latency it existed to hide. It was a straightforward error on my part.

Instant-on now rests on two mechanisms, neither of which is a format feature: the play ring is retained across sleep, and card initialisation begins on the cartridge-detect switch rather than on the play press. **Both are firmware behaviours and both need tests you have not been asked for yet.** Wake-to-audio under 100 ms is guardrail 04 and it is now enforced entirely in `firmware/`, so the budget test in Suite 5 needs to move there.

**B. An index entry now describes a run over consecutive chunks**, not a single chunk:

```
entry := { first_chunk_id, start_frame, frame_count }
         run occupies first_chunk_id, +1, +2, …
         frame_count may exceed CHUNK_FRAMES
```

This exists because a pristine 90-minute tape previously burned 1817 of 4096 index entries before a child had done anything, leaving only ~1.5× headroom for splicing. A re-spooled side is now a **single entry**.

**This is the change most likely to hide a bug, and it is worth disproportionate attention.** It widens every bounds check in the validity rules: a run must be entirely in range, and for Side A every chunk id in the run must be below `a_high_water` — not just the first. An off-by-one at the end of a run is now a way to reach into Side A, which is precisely the invariant the whole design exists to protect. Your Suite 3 invariants 3 and 4 need restating in terms of runs rather than entries, and I would expect a real defect to be findable here.

**C. Two budgets, not one.** RAM ≤ 200 KiB (`.data` + `.bss` + engine instance); `.rodata` ≤ 32 KiB. Suite 5's memory test splits accordingly.

**Also worth knowing, though not a spec change:** the 90-minute cartridge length is *not settled*. The Hardware Lead established that no purchasable UHS-I card specification guarantees the 31.75 MB/s sustained write the 30-second copy requires, and we are measuring before deciding. Because `nominal_length_s` is a superblock field, tape length is a format parameter rather than a format revision — **do not treat 90 minutes as fixed when writing tests.** Parameterise anything that depends on it.

---

## 3. Your two seeded findings — resolved as proposed, still open to attack

Both landed as specified. Resume position lives in the device's flash keyed by cartridge UUID; `tape_dup` assigns the destination a fresh UUID. Michael has the child-facing consequence in front of him as Q-004 — a tape resumes where *each player* left it, not where the tape was last played — and the default ships if he does not answer.

The Software Lead noticed that "the caller supplies it" had now answered two independent questions and proposed naming it rather than treating it as coincidence. It is now a stated principle in `engine-api.md` §3:

> **The engine computes. The caller owns anything that needs entropy, hardware knowledge, or memory beyond the engine's budget.**

Worth testing as a principle, not just as two behaviours: look for a third place where the engine reaches for something it should have been handed.

---

## 4. New duty — independent review of pull requests, on request

Michael has arranged for you to provide independent review of PRs in `mmsanders/Digital-Tape`. This is **on request only**. It is not automatic, it is not a merge gate, and you are not expected to watch the repository.

**The trigger is the exact phrase `Request Independent Review`** in a PR description or comment. Both leads have been told.

**What is being asked of you.** Read the change adversarially and report in your existing finding format. Same standard as everything else: `blocker` is reserved for anything that can lose a cartridge or produce audio that could hurt a child's hearing. You are not a style reviewer and you are not there to approve — you find things or you say you found nothing.

**And one hard boundary, which you must enforce yourself.** Reading engine implementation for a behaviour before you have written the tests for that behaviour destroys the independence that is the entire reason you are a different model. A review request does not override that.

| Request | Accept? |
|---|---|
| CI, tooling, host tooling, firmware integration, hardware docs | **Yes** |
| Engine PRs whose behaviour is already covered by tests you have written and landed | **Yes** |
| Engine PRs implementing behaviour you have not yet written tests for | **No — decline and say why** |

**Decline the third category.** Do not read the diff first to decide. Say that the request would compromise test independence for that behaviour, name what tests would need to exist first, and escalate to me. A refusal is the system working correctly, and the Software Lead has been told to expect it and not to treat it as a misconfiguration.

If you judge that a specific case genuinely warrants an exception — some change where the risk of not looking exceeds the cost of losing independence on one behaviour — say so and let me make that call. Do not make it yourself, in either direction.

---

## 5. Next steps

1. **Read the DRAFT-2 changelist in §2** before anything else.
2. **Begin the adversarial specification review.** You are unblocked. Priority order: the run-length entry change in §2B, then the commit protocol in `tapefs-v1.md` §7, then the mount and recovery rules in §8.
3. **Attack the block-write atomicity assumption** (`tapefs-v1.md` §12, item 1). The whole format rests on a 512-byte SD block write being atomic under power loss. It is true in practice and not universally guaranteed, and it is the single assumption whose failure invalidates everything else. I would rather know now.
4. **Report findings in your format**, relayed by Michael, and continue to say plainly when you are uncertain — a `question` that turns out to be a misreading costs one reply.

The two findings you were seeded with were real. So were three of the five escalations that came back from the leads this week, one of which — no card specification guarantees the write speed we require — would have cost a board spin to discover. The process is working. Keep pulling on things that look strange.
