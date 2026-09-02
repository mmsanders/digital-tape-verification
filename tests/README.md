# Verification harness

This directory contains only implementation-independent verifier infrastructure. It does not include or inspect engine implementation.

## Components

- `fault_block_device.[ch]`: caller-owned, allocation-free 512-byte block device model. In the default flush-required mode, writes first enter volatile working media, `flush` makes them durable, and `power_cut` discards unflushed state. Selectable write-through mode makes every completed block durable immediately so both allowed device behaviours can be tested. A fault can fire before any block in a multi-block request, after any prefix of a block has durably landed, or at a selected flush.
- `crash_harness.[ch]`: records a clean operation's write/flush trace and reruns the scenario for every block outcome from 0 through 512 landed bytes and for every flush failure. Each run resets the fixture, simulates power loss, remounts, invokes invariant validation, and reports a deterministic case record.
- `test_fault_block_device.c` and `test_crash_harness.c`: self-tests for the infrastructure itself.
- `SUITE-3-INVARIANTS.md`: DRAFT-3-reconciled property list and independent-oracle obligations.
- `WP10-PLAN.md`: exhaustive crash-session matrix and current spec blockers.
- `WP11-PLAN.md`: golden-fixture, diagnostics, runner, and mutation-test plan.

## Build and self-test

```sh
make -C tests check
```

Both executables return zero on success and print nothing.

## DRAFT-3 integration boundary

The scenario callbacks deliberately keep format knowledge outside the harness. DRAFT-3-specific adapters still must supply:

1. `prepare`: restore a byte-exact valid starting cartridge and initialize the engine under test.
2. `operate`: perform one specified edit/format/duplicate/promote/re-spool session.
3. `remount`: discard engine state and mount only from the post-crash durable bytes.
4. `validate`: assert the cartridge mounts, Side A identity, permitted pre/post Side B generation, CRC/generation coherence, run bounds, write-before-reference, and allocation reachability.

Those adapters and assertions cannot be finalized until PM dispositions resolve V3-002, V3-005, V3-008, V3-013, and V3-014. The infrastructure itself depends only on `engine-api` §3 and is complete.

Every crash scenario must be run once in flush-required mode and once in write-through mode. This brackets the block-device contract without assuming that a successful unflushed write is either certainly durable or certainly lost.
