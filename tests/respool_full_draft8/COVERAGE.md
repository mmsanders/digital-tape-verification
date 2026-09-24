# Issue #72 coverage — full re-spool crash + WP-12a

Authority is frozen DRAFT-8 at:

- TapeFS SHA-256 `3bffa0ec46d7ba3779b02cbee6fac1edaf5094553f78270ee379759655147cbb`
- engine-api SHA-256 `537eadc423e1a7bde726d689206b8fe93bef164d57e48e8ff71e07eaf8a7e3a1`
- acceptance SHA-256 `7f78fba7b66b4fc6e96d15399c62468249bb30fbccbb59bf9f57b4532f56b6b7`

No product implementation was consulted in authoring this package.

## WP-12 functional shapes

Covered by verifier-owned fixtures and the pinned independent raw metadata oracle:

- successful completed pass is exactly one B entry and preserves logical audio bytes;
- invariant 10 at each planned chunk write: destination is at/above H and disjoint
  from the then-live A and B sets;
- corrected V3-003: H=10, live B=[10,12), free_next=12, pass 1 [12,14), then
  pass 2 [10,12);
- pass-2 eligibility is evaluated after pass-1 commit, permitting reclamation of the
  old [10,12) chunks only when they have ceased to be live;
- no-lower-run fixture commits pass 1 and declines pass 2;
- empty B returns TAPE_OK / more_work=false / zero writes with its valid zero-entry
  index unchanged;
- no qualifying pass-1 destination returns TAPE_ERR_CARTRIDGE_FULL with media
  unchanged;
- Side A metadata and a verifier-designated Side-A raw data region are immutable.

## WP-10 re-spool crash enumeration

Planner total: **22,562** deterministic cases.

| Dimension | Count |
|---|---:|
| flush_required | 11,281 |
| write_through | 11,281 |
| V3-003 pass 1 | 10,250 |
| V3-003 pass 2 | 10,250 |
| no-lower-run pass 1 | 2,062 |
| chunk-copy interruption points | 16,388 |
| data-flush faults | 6 |
| entry-block before/torn/after | 3,078 |
| entry-block flush faults | 6 |
| header before/torn/after | 3,078 |
| header flush faults | 6 |

Canonical case-set SHA-256:
`bc3e4cff6f61888faf9c5b97ccd136e9fec4417ef9cab4a46d084b4aae7ec444`.

Every copied block has before/after interruption coverage. Every targeted one-block
metadata write has before, all torn prefixes 1…511, after, and its following flush
fault. Every case is run in both durability modes and requires a fresh remount from
durable bytes only.

The raw oracle permits only the valid pre-pass or valid post-pass selected layout.
Torn/new inactive metadata may exist but may not be selected. A selected post-pass
index must be byte-exact to the verifier-generated commit. Side A remains unchanged.

For pass 2, **every injection**, including destination writes into reclaimed [10,12),
must retain the raw SHA-256 of the sole live pass-1 audio at [12,14). A committed
pass 2 additionally requires [10,12) to hash identically. This is the explicit proof
that a pass-2 crash cannot destroy the only live copy created in pass 1.

## Counter/headroom boundaries

Covered:

- empty re-spool at cartridge_sequence=0xFFFFFFFD: zero-consumption TAPE_OK;
- crafted empty re-spool at sequence=0xFFFFFFFF and sb_generation=0xFFFFFFFF:
  zero-consumption TAPE_OK without consulting either counter;
- one-commit branch with no sequence headroom: TAPE_ERR_SEQUENCE_EXHAUSTED and zero
  writes;
- corrected two-pass geometry with exactly one sequence remaining: pass 1 commits and
  optional pass 2 is skipped;
- ordinary stage-0 re-spool commits advance cartridge sequence while leaving
  superblock bytes/sb_generation unchanged.

The last item is important to issue wording: frozen TapeFS §4.5 explicitly classifies
a two-pass-capable geometry with only one sequence remaining as the **one-commit
branch**. It does **not** permit refusing that case one-short of two commits. The
package follows the frozen rule and treats a refusal there as a defect. Only a branch
that needs its first/only commit and is one short refuses with zero writes.

§8 stage-clear crash closure is excluded because Verification #69 already accepted it.
This tranche uses stage-0 media for its crash campaign.

## WP-12a re-spool row

The package requires all 15 columns of the Respool-in-progress row, exactly once per
fresh equivalent fixture:

- 11 B cells => TAPE_ERR_BUSY, zero block operations, operation identity unchanged;
- render, service, status/info/tell and matching respool continuation are allowed;
- matching continuation advances the same operation;
- repeated small budgets reach completion without restart;
- block_budget=0 is INVALID_ARG with no work/state loss on initiation and continuation;
- an unrelated BUSY call cannot terminate the operation; the next continuation
  advances the same operation;
- own-media write **and** flush failure on continuation terminate more_work and enter
  FAULTED.

The package also requires the full 15-column Faulted row:

- all 11 F cells => TAPE_ERR_FAULTED and zero block operations;
- render, status/info/tell, abort and unmount are the four allowed calls;
- Faulted overrides an armed/frames-owed condition;
- render drains the retained ring to zero/underrun and abort remains allowed.

### Frozen API N/A cells in issue prose

Two requested generic long-operation checks have no re-spool call surface:

1. `tape_respool(t, block_budget, more_work)` has no stable continuation argument
   besides the two fields DRAFT-8 explicitly allows to change. There is no
   "changed continuation argument" to mutate.
2. Re-spool has no progress callback parameter. DRAFT-8 says callback re-entry is
   triggered by the current `tape_progress_fn` surface, exposed by promote/duplicate,
   not respool. A respool-originated callback re-entry test would require inventing
   non-frozen API.

The verifier asserts those surfaces are absent so a product adapter cannot silently
invent them.

## Negative controls

Synthetic self-tests prove the package goes red for:

- Side-A/live-set corruption (overlap control);
- an illegal/stale layout selection at a flush-required header boundary;
- a wrong pass-2 destination;
- BUSY terminating/restarting the in-progress operation;
- a FAULTED-row call leaking through and performing media I/O.

## Exclusions / no duplicate acceptance

Not claimed here:

- §8 stage-clear crash closure accepted in Verification #69;
- the previous narrow clean 8/8 re-spool product evidence except as fixture/oracle
  dependency;
- promote crash/resume or promote WP-12a (R29-VER-A);
- format/duplicate raw identity or duplicate WP-12a (R29-VER-B);
- WP-11 audio listening/goldens;
- any product implementation result. This publication is verifier-first only.
