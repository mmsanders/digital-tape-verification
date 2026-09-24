# Full re-spool product-binding contract

This package is verifier-owned and implementation-independent. Software may import
this directory byte-for-byte and bind the frozen public API to it, but may not change
the planner, fixture bytes/digests, durability model, state oracle, permitted layouts,
negative controls, or coverage declarations.

The verifier was authored against Digital-Tape
`45c08bd7e25aeb6ca858faf4d30d139999f8dbd7` and Verification
`fe432ffac622b9d9e9c68e566d2cb9881f2aee62`, before product implementation
inspection.

## Product adapter boundary

The later Software binding exposes **raw observations only**. It must not emit
"old/new", "valid", "safe", "passes", overlap verdicts, or any other result that
duplicates verifier logic.

For each planner case it returns one `WP10-RESPOOL-OBSERVATION-1` object containing:

- the exact planner case identity and confirmation that the planned injection fired;
- `fresh_remount_from_durable_only=true`;
- the raw remount return code;
- a pre- and post-crash compact snapshot: exact primary/mirror 512-byte
  superblocks plus the first two blocks of all four index slots;
- the exact targeted device event (write LBA/count or flush);
- SHA-256 observations of verifier-designated raw audio regions and the Side-A
  control region.

A failing observation is retained with `reproducer.retain_failure` as
`WP10-RESPOOL-FAILURE-1`, including the exact planner case, injection coordinate,
pre/post metadata snapshots, target event and raw-region hashes. That record is enough
to diagnose the chunk/index/superblock state without reading implementation source.

## Dual-image crash device

The product binding uses separate working and durable images.

- Reads come from working bytes.
- In `write_through`, a successful write changes working and durable bytes.
- In `flush_required`, a successful write changes working only.
- A successful flush makes all preceding working writes durable.
- A torn one-block metadata write copies exactly the requested prefix (1…511 bytes)
  into working **and durable** bytes, then faults.
- `before_write` lands no target byte.
- `after_write` permits the full write to return, then cuts power before the
  following flush. Therefore the write is durable only in `write_through`.
- `at_flush` fails/cuts before that flush changes durability. Preceding writes may
  already be durable in `write_through`.
- After every injected interruption, destroy the running instance and working image.
  Remount a fresh instance initialized only from durable bytes.

## Crash targets

The canonical planner contains 22,562 cases and no runtime sampling switches.

For each pass, every copied chunk block has a before-write and after-write interruption
point, and the data flush is faulted. Each targeted one-block metadata write—the
entry-array block and index-header commit—has before-write, **all 511 nontrivial torn
prefixes**, after-write and following-flush fault coverage. Both durability modes run
every case.

The corrected V3-003 fixture is fixed at H=10, live B=[10,12), len=2,
free_next=12:

1. pass 1 copies to [12,14) and commits B1 sequence 701;
2. pass 2 copies back to [10,12) and commits B0 sequence 702.

The pass-2 campaign begins from the committed pass-1 durable image. Every pass-2
observation must expose the raw SHA-256 of [12,14), allowing the verifier to prove
that the operation never destroys the only live pass-1 copy while writing reclaimed
[10,12).

The no-lower-run fixture keeps the existing verifier-owned ten-fragment source and
compacts to chunk 10 once; pass 2 must decline.

## Clean functional and headroom observations

Software must also expose the ordinary call/event traces already understood by the
pinned `respool_draft8/oracle.py` for these verifier fixtures:

- empty Side B;
- corrected two-pass V3-003;
- no-lower-run decline;
- no valid pass-1 destination / CARTRIDGE_FULL;
- sequence-exhausted one-commit branch;
- one-sequence-remaining branch, where pass 1 succeeds and optional pass 2 is skipped.

The stage-clear transaction is not rebound here; Verification #69 already closed it.

Two extra empty fixtures carry (a) cartridge_sequence 0xFFFFFFFD and (b) deliberately
crafted sequence=sb_generation=0xFFFFFFFF. Re-spool must return TAPE_OK,
more_work=false and perform zero write/flush operations. A zero-needed counter is not
consulted.

## WP-12a raw state observations

For each of the 15 matrix columns, use a fresh equivalent fixture so calls such as
unmount do not affect later cells. Emit result code, block-operation count, and an
opaque operation token before/after. The token is observation only: it identifies
whether the same in-progress operation survived a BUSY call; it is not a product
concept or pass/fail verdict.

The binding additionally emits:

- repeated small-budget respool calls through terminal more_work=false;
- budget-zero initiation and continuation observations, including before/after state;
- an interfering BUSY call followed by an ordinary continuation;
- separate continuation write-failure and flush-failure observations;
- a Faulted-over-armed fixture with frames owed;
- render counts while the Faulted ring drains, underrun indication, and abort result.

### Frozen API non-applicabilities

Do not invent adapter hooks to satisfy prose that the public API cannot express.

`tape_respool(t, block_budget, more_work)` has no operation-specific continuation
argument other than `block_budget` and `more_work`, both explicitly allowed to
change. Therefore the changed-stable-argument continuation test has no respool input
to mutate.

Re-spool also has no `tape_progress_fn` parameter. The no-re-entry rule is triggered
while an engine callback is executing, and DRAFT-8 states that the current callback
surface is `tape_progress_fn`; only promote and duplicate expose it. Therefore there
is no respool-originated progress callback in which to re-enter respool. The adapter
must report these surfaces as absent, not create a private callback or private
argument.

## Forbidden binding behavior

Software must not:

- inspect or modify verifier expectations based on product behavior;
- collapse durable bytes into an adapter verdict;
- skip planner cases or torn lengths;
- reuse the live engine instance after simulated power loss;
- substitute the previously accepted narrow 8/8 clean re-spool evidence for this
  crash/state campaign;
- include promote, format/duplicate, or §8 stage-clear acceptance in this tranche.
