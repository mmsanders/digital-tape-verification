# Phase 1 Verification — dependency-ordered next tranches

**Planning status:** proposal after P1-R1-V only. These are not current assignments
and do not authorize implementation inspection or product acceptance.

The DRAFT-6 `WP10-PLAN.md`, `WP11-PLAN.md`, and `WP12A-PLAN.md` are historical design
records. Their old DRAFT-6 blocker/status claims are superseded by issued DRAFT-8 and
must not be used as current acceptance authority. Useful harness ideas remain
provenance only; new assertions cite current DRAFT-8 bytes.

Independent surge packages now published (draft PRs, not accepted):

- `tests/record_draft8/` — eight families, six refusals, multi-chunk, empty-B
  splice, empty commit in all three modes, successful stage-1 clear on arm
- `tests/respool_draft8/` — empty / two-pass / full / degraded / stage-1 clear
- `tests/slot_draft8/` — source-slot A/B playback, mutators, format RO
- `tests/format_dup_draft8/` — format/dup preconditions including order and
  `block_count ∈ {0,1,LBA_CHUNK_BASE}`, empty-promote
- `tests/transport_draft8/` — set_side transition + eight warm-start negatives

Still outstanding and **not stacked** only in the sense of product observations
and 10 000-edit histories. Everything below **does stack** and was not started:

1. **WP-11 goldens / listening.** Human listening remains a separate Michael step.
   Warm-start *use* (accepted descriptor) needs those goldens.
2. **Complete crash closure (WP-10).** Write/flush boundaries in both durability
   modes, remount from durable bytes only, V7-001 two-interruption partner-first,
   format/dup identity-assignment commits, generation/sequence exhaustion crash
   rows, FAULTED barriers. Operations/state do not freeze before that green run.
3. **Long operations + state matrix (WP-12a).** Budget/continuation identity,
   zero budget, stable argument mismatch, re-entry, BUSY cells, I/O → FAULTED
   and both normative exclusions.

This order minimizes circular oracles. WP-10 and WP-12a build on the operation
oracles above and are not started from this surge cut.
