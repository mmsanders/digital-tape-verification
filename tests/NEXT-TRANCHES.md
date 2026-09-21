# Phase 1 Verification — dependency-ordered next tranches

**Planning status:** proposal after P1-R1-V only. These are not current assignments
and do not authorize implementation inspection or product acceptance.

The DRAFT-6 `WP10-PLAN.md`, `WP11-PLAN.md`, and `WP12A-PLAN.md` are historical design
records. Their old DRAFT-6 blocker/status claims are superseded by issued DRAFT-8 and
must not be used as current acceptance authority. Useful harness ideas remain
provenance only; new assertions cite current DRAFT-8 bytes.

1. **Playback + independent goldens (WP-08/WP-11).** First establish byte-exact
   independent PCM fixtures and transport boundary cases against DRAFT-8 Engine API
   §§6/8. Include seek→render phase, reverse endpoints/rates, side switching, warm
   descriptor negatives, and cross-target byte identity. Human listening remains a
   separate Michael step before golden acceptance.
2. **Recording breadth + random edit sequences.** `tests/record_draft8/` on
   `surge/wp09-record-tranche` publishes eight public-API families plus six
   refusal/abort rows (Side-A READ_ONLY, SEQUENCE_EXHAUSTED, INDEX_FULL,
   CARTRIDGE_FULL short-accept, abort-disarm, stage-1 refusal leaves stage).
   Still outstanding: successful stage-1 clearing write, multi-chunk edits,
   random 10 000-edit histories, and product observations.
3. **Format / dup / empty-promote refusals.** `tests/format_dup_draft8/` on
   `surge/format-dup-refusal-tranche` covers §9.5 items 1–4, §9.6 preconditions,
   and empty-promote `INVALID_ARG`. Does **not** encode WP-10 crash tables.
4. **Complete crash closure (WP-10).** With each operation oracle independently
   authored, enumerate write/flush boundaries in both durability modes, remount from
   durable bytes only, and classify exact permitted states. Explicitly include the
   DRAFT-8 V7-001 **two-interruption** partner-first closure, stage clearing/resume,
   format/duplicate identity boundary, generation/sequence exhaustion, and FAULTED
   barriers. Operations/state do not freeze before the actual complete green run.
5. **Long operations + state matrix (WP-12a).** After operation semantics/crash states
   above are executable, cover budget/continuation identity, zero budget, stable
   argument mismatch, allowed concurrent render/service, progress-callback reentry,
   BUSY cells, I/O failure to FAULTED and both normative exclusions. Tie every state
   cell to current DRAFT-8 API text rather than DRAFT-6 labels.

This order minimizes circular oracles: playback expectations precede goldens,
recording semantics precede crash classification, and operation outcomes precede the
full continuation/state matrix. WP-10 and WP-12a build on the operation oracles
above and are not started from this surge cut.
