# Verification harness scaffold

This directory contains only implementation-independent verifier infrastructure. It does not include or inspect engine implementation.

## Components

- `fault_block_device.[ch]`: caller-owned, allocation-free 512-byte block device model. Writes first enter volatile working media; `flush` makes them durable; `power_cut` discards unflushed state. A fault can fire before any block in a multi-block request, after any prefix of a block has durably landed, or at a selected flush.
- `crash_harness.[ch]`: records a clean operation's write/flush trace and reruns the scenario for every block outcome from 0 through 512 landed bytes and for every flush failure. Each run resets the fixture, simulates power loss, remounts, invokes invariant validation, and reports a deterministic case record.
- `test_fault_block_device.c` and `test_crash_harness.c`: self-tests for the infrastructure itself.
- `SUITE-3-INVARIANTS.md`: run-based property list to bind to DRAFT-3's exact media definitions when issued.

## Build

```sh
cc -std=c99 -Wall -Wextra -Werror -pedantic \
  tests/fault_block_device.c tests/test_fault_block_device.c \
  -o test_fault_block_device

cc -std=c99 -Wall -Wextra -Werror -pedantic \
  tests/fault_block_device.c tests/crash_harness.c \
  tests/test_crash_harness.c -o test_crash_harness
```

Both executables return zero on success and print nothing.

## DRAFT-3 integration boundary

The scenario callbacks deliberately keep format knowledge outside the harness. DRAFT-3-specific adapters still must supply:

1. `prepare`: restore a byte-exact valid starting cartridge and initialize the engine under test.
2. `operate`: perform one specified edit/format/duplicate/promote/re-spool session.
3. `remount`: discard engine state and mount only from the post-crash durable bytes.
4. `validate`: assert the cartridge mounts, Side A identity, permitted pre/post Side B generation, CRC/generation coherence, run bounds, write-before-reference, and allocation reachability.

Those adapters and assertions cannot be finalized until DRAFT-3 and `spec/acceptance.md` arrive.
