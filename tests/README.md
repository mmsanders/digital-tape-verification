# Verification harness

This directory contains only implementation-independent verifier infrastructure. It does not include or inspect engine implementation.

## Components

- `fault_block_device.[ch]`: caller-owned, allocation-free 512-byte block device model. In the default flush-required mode, writes first enter volatile working media, `flush` makes them durable, and `power_cut` discards unflushed state. Selectable write-through mode makes every completed block durable immediately so both allowed device behaviours can be tested. A fault can fire before any block in a multi-block request, after any prefix of a block has durably landed, or at a selected flush.
- `crash_harness.[ch]`: records a clean operation's write/flush trace and reruns the scenario for every block outcome from 0 through 512 landed bytes and for every flush failure. Each run resets the fixture, simulates power loss, remounts, applies the operation-specific remount predicate, invokes invariant validation, and reports a deterministic case record. The predicate permits `INCOMPLETE` or blank-format `BAD_MAGIC` only where the DRAFT-5 operation oracle allows them.
- `test_fault_block_device.c` and `test_crash_harness.c`: self-tests for the infrastructure itself.
- `audio_oracle.[ch]` and `test_audio_oracle.c`: verifier-owned C99 reference arithmetic for overdub saturation and variable-rate interpolation. Negative interpolation uses explicit floor division rather than implementation-defined signed right shift.
- `SUITE-3-INVARIANTS.md`: DRAFT-5 review-state property list and independent-oracle obligations.
- `WP10-PLAN.md`: exhaustive crash-session matrix and current spec blockers.
- `WP11-PLAN.md`: golden-fixture, diagnostics, runner, and mutation-test plan.

## Build and self-test

```sh
make -C tests check
```

All self-test executables return zero on success and print nothing.

## DRAFT-5 integration boundary

The scenario callbacks deliberately keep format knowledge outside the harness. DRAFT-5 operation adapters must supply:

1. `prepare`: restore a byte-exact valid starting cartridge and initialize the engine under test.
2. `operate`: perform one specified edit/format/duplicate/promote/re-spool session.
3. `remount`: discard engine state and mount only from the post-crash durable bytes.
4. `validate`: assert the cartridge mounts, Side A identity, permitted pre/post Side B generation, CRC/generation coherence, run bounds, write-before-reference, and allocation reachability.

The generic loop and scenario-specific non-mounting support are complete. Operation adapters cannot be frozen while `findings/spec-review-draft5.md` leaves duplicate, long-operation error recovery, promote-stage admission, and eager-durability states unresolved. The infrastructure itself depends only on the block-device contract and remains implementation-independent.

Every crash scenario must be run once in flush-required mode and once in write-through mode. This brackets the block-device contract without assuming that a successful unflushed write is either certainly durable or certainly lost.
