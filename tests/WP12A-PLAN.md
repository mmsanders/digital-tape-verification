# WP-12a long-operation plan — DRAFT-6

Status: **WP-12a is not testable as written for final acceptance.** Most of the DRAFT-6 contract is now mechanically singular — corrected cell counts, zero budget, continuation identity, FAULTED quarantine, render/service availability during ordinary long operations, and the two FAULTED exclusions — but the callback re-entry requirement contradicts `engine-api` §9.1/invariant 28 and §9.1 is internally ambiguous about whether a BUSY return from the matching reentrant continuation terminates the active operation (`V6-009`).

No implementation behavior is used to resolve that contradiction. The blocked callback predicate remains unencoded until PM disposition.

## Executable structure now

For each of `tape_respool`, `tape_promote`, and `tape_dup`:

1. Start a job whose work is larger than a positive `block_budget`.
2. Drive it to completion through repeated calls to the **same** function, preserving every stable argument and changing only the explicitly permitted continuation arguments.
3. Exercise all **45 cells** across the three in-progress rows: 15 per row, with four allowed groups and **11 BUSY cells per row / 33 BUSY cells total**.
4. For every BUSY call made outside a progress callback, prove zero block operations and prove the next matching continuation advances the same operation rather than restarting it.
5. Change each stable continuation argument independently; require `TAPE_ERR_INVALID_ARG`, zero work, and the active operation preserved.
6. Exercise `block_budget == 0` on initiation and continuation; require `TAPE_ERR_INVALID_ARG`, zero work, no state change.
7. While the operation is in progress, prove `tape_render` and `tape_service` remain allowed and transport audio remains available.

## FAULTED transition

For every own-device write/flush boundary in a continuation:

- inject the failure;
- require `*more_work == false` and entry to `FAULTED`;
- exercise all **15** cells of the FAULTED row;
- require the 11 forbidden calls (`seek`, `set_rate`, `service`, `arm`, `feed`, `commit`, `set_side`, `reset_b`, `promote`, `respool`, `dup`) to return `TAPE_ERR_FAULTED` with zero block operations;
- require the four allowed groups (`render`, status/info/tell, `abort`, `unmount`) to remain callable;
- prove `abort` clears volatile owed-frame state without media I/O;
- drain the play ring through `render` and require eventual underrun;
- prove FAULTED overrides any armed/transport row until unmount/remount.

Exercise the two DRAFT-6 exclusions separately rather than weakening the generic predicate:

1. a phase-4 mount repair I/O failure does not poison a logical mounted generation;
2. a duplicate **destination** I/O failure does not FAULT the source instance.

The second exclusion needs a Playing-source regression after `V6-006` is dispositioned, because DRAFT-6 currently says the source returns to Mounted-idle while its non-zero playback rate still classifies it as Playing.

## Callback re-entry — blocked predicate

DRAFT-6 currently says two incompatible things:

- `engine-api` §9.1/invariant 28 permit `tape_render`, `tape_status`, `tape_get_info`, and `tape_tell` from a progress callback and require prohibited same-instance re-entry to return `TAPE_ERR_BUSY` without state change;
- WP-12a requires a callback attempting **every** engine call to receive `TAPE_ERR_BUSY` from each.

It also leaves the matching continuation ambiguous: the no-reentry rule says its BUSY return changes no state, while the generic continuation-termination rule treats a non-OK/non-INVALID_ARG return from the operation's own function as ending the operation.

Until PM disposition, the verifier may build the callback driver and record attempted call/result/state/block-I/O triples, but it must **not** bless either interpretation as the acceptance oracle.

The required post-disposition shape should be singular enough to assert all of the following mechanically: which callback calls are exempt, which return BUSY, whether the matching continuation is non-terminating, and that the next ordinary continuation advances the same job.

## Independence boundary

This plan is authored entirely from the DRAFT-6 normative contracts and verifier-owned state/fault machinery. Do not inspect or link engine implementation for the callback behavior until the normative expectation is dispositioned and the corresponding verifier test exists.
