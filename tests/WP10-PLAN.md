# WP-10 exhaustive crash-injection plan

Status: infrastructure executable; engine-operation adapters blocked where DRAFT-3 has no single allowed-state oracle. See `findings/spec-review-draft3.md`.

## Harness contract

For each operation and starting fixture:

1. Run once without faults and record the exact per-block write count and flush count.
2. Restore the byte-identical fixture before every case.
3. For each observed block write, cut power with 0, every prefix 1–511, and all 512 bytes durably landed.
4. Fail each observed flush in turn.
5. Repeat in flush-required and write-through durability modes.
6. Destroy all volatile engine/device state and remount from durable bytes only.
7. Decode media with a verifier-owned parser; never call engine parsing, CRC, run, rendering, or allocation helpers from the oracle.
8. Report baseline writes, flushes, total injection cases, passed cases, and failed cases.

## Required scripted operations

| Operation | Required starting cases | Oracle status |
|---|---|---|
| format | blank media; reusable C-60/C-90/C-120 media | Blocked by V3-008/V3-013 |
| mount/repair | primary bad; mirror bad; both bad; unequal/equal generations; v2 candidate; read-only | Blocked in part by V3-005/V3-006 |
| play/seek | empty, one frame, run boundary ±1, exact end, reverse start, max representable timeline | Blocked at long-timeline/rate extremes by V3-010 |
| overwrite/overdub/splice | t=0, mid-run, exact boundary, end; full/index-full; owed frames | State cursor blocked by V3-011 |
| commit | every chunk/entry/header/final-flush boundary | Ready after operation adapter exists |
| reset B | non-empty A with shared immutable references | Oracle rule identified by V3-009 |
| re-spool | low disjoint, fragmented requiring up, overlapping second-pass candidate, insufficient tail | Blocked by V3-003 |
| promote | crash at every write/flush in both phases; old B overlaps low target | Blocked by V3-002/V3-013 |
| duplicate | same/different geometry; insufficient destination; aliased handles; every WIP boundary | Blocked by V3-007/V3-013 |

## Universal checks

- Every referenced frame of every state declared recoverable is byte-identical to its declared generation.
- No I/O range crosses `block_count`; the chunk store never touches the mirror.
- Header/entry CRC, generation, sequence, side, run extent, and totals are independently recomputed.
- Side A write destinations are never below the live immutability boundary except within a fully specified promote phase.
- Side B may reference A chunks but never allocates or writes below `a_high_water`.
- `free_next` is independently derived from live B run ends with checked arithmetic.
- The selected index/superblock pair is one exact allowed generation, never a mixture.
- Source media in duplicate receives zero writes.

## Integration seam

PM Decisions 002 says the Software Lead's `dev_sim` is readable from `tests/` on `main`. As of this review, `Digital-Tape/main/tests/` contains only README and empty crash/fuzz/golden directories; no `dev_sim` is present there. Integration waits for it to land on `main`, preserving the structural spec → verifier tests → implementation order.
