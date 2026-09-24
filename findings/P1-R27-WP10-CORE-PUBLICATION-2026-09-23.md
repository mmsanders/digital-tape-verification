# P1-R27 Verification return — WP-10 core commit/reset-B/stage-clear crash publication

Date: 23 September 2026  
Authority: independent Verification, issue #60

## Publication disposition

**PASS — bounded independent WP-10 core crash package published and self-tested.**

This is verifier authorship/publication only. It is **not product acceptance** and
expressly **not complete WP-10**.

The package was authored from authenticated DRAFT-8 public specifications before
inspecting current product engine implementation. Digital-Tape was not modified.

## Frozen inputs

Authoring integration point:
`e4a356586fd67d118868ba457e26d2c9805e7c7a`

DRAFT-8 hashes:

- `spec/tapefs-v1.md`:
  `3bffa0ec46d7ba3779b02cbee6fac1edaf5094553f78270ee379759655147cbb`
- `spec/engine-api.md`:
  `537eadc423e1a7bde726d689206b8fe93bef164d57e48e8ff71e07eaf8a7e3a1`
- `spec/acceptance.md`:
  `7f78fba7b66b4fc6e96d15399c62468249bb30fbccbb59bf9f57b4532f56b6b7`

## Immutable package

Path:
`tests/crash_core_draft8/`

Package publication commit:
`18ff453e80fa245ad2d10066a1df262b443905b7`

Immutable package tree:
`d99aa7d095ea9ee7228d6bddddd682848dfb8a55`

The publication diff from Verification base
`3cdffae0671fa29f6d361a72c449f50331b26f4d` contains exactly ten package files:

- `ADAPTER.md`
- `COVERAGE.md`
- `README.md`
- `fixture.py`
- `media.py`
- `oracle.py`
- `planner.py`
- `runner.py`
- `selftest.py`
- `synthetic_adapter.py`

## Bounded frozen coverage

This publication covers exactly:

1. **Record commit**
   - overwrite;
   - overdub;
   - splice.

2. **Reset Side B**
   - healthy/selectable Side B;
   - degraded-B caused by equal-sequence divergent valid B slots.

3. **§8 stage clearing**
   - through `tape_arm`;
   - through `tape_reset_side_b`;
   - through `tape_respool`.

4. **V7-001 two-interruption closure**
   - all three stage-clear entry paths;
   - both candidate orientations;
   - one-copy and newer-candidate/stale-partner recovery shapes.

## Exact exhaustive injection set

Canonical case-set SHA-256:

`6c924fd7bdd54b180084fe58cc50ef49d96fc068b968b8022383685ecf235c96`

### First-interruption tranche

Every scenario runs in:
- `flush_required`;
- `write_through`.

Each has exactly two targeted block writes and two target flushes.

For each 512-byte block write the verifier enumerates:
- before write: 0 bytes landed;
- every torn prefix: 1 through 511 bytes landed;
- after complete write: 512 bytes landed.

Both target flushes are separately interrupted.

Therefore each first-interruption scenario has:

`2 * (2 * 513 + 2) = 2,056` cases.

Eight scenarios:

| Scenario | Cases |
|---|---:|
| record / overwrite | 2,056 |
| record / overdub | 2,056 |
| record / splice | 2,056 |
| reset-B / healthy | 2,056 |
| reset-B / degraded equal-sequence | 2,056 |
| stage clear / arm | 2,056 |
| stage clear / reset-B | 2,056 |
| stage clear / re-spool | 2,056 |

**First-interruption total: 16,448.**

### V7-001 closure

Stage clearing uses four raw recovery seeds:

1. current primary only, mirror invalid;
2. current mirror only, primary invalid;
3. current primary beside stale lower-generation mirror;
4. current mirror beside stale lower-generation primary.

For each:
- 3 stage-clear callers;
- 2 durability modes;
- second interruption on the next partner write at every landed-byte count 0…512.

`3 * 4 * 2 * 513 = 12,312`.

**Two-interruption closure total: 12,312.**

### Grand total

**28,760 independent injection cases.**

Breakdown:
- flush-required: 14,380;
- write-through: 14,380;
- torn-write cases: 28,616;
- before-write/partner: 56;
- after-write/partner: 56;
- first-interruption flush faults: 32.

Clean baselines and repair-preservation setup faults are not counted as injection cases.

## Durability model

The package does not treat "old or new" as an unrestricted permitted set.

It independently maintains working and durable media.

A completed unflushed write:
- remains non-durable in `flush_required`;
- becomes immediately durable in `write_through`.

A torn block explicitly lands the selected prefix into durable media.

For every case the oracle independently simulates the **exact durable 512-byte
metadata bytes**, then compares the product's pre-remount durable snapshot to those
bytes.

This directly detects an implementation/harness that interprets the two durability
modes incorrectly.

## Durable-only remount oracle

The product adapter may not authoritatively classify a result as "old", "new", or
"safe".

Verifier-owned `media.py` independently parses raw durable bytes:
- superblock magic/CRC;
- candidate/partner generation selection;
- admission;
- A0/A1/B0/B1 index magic/CRC;
- entry extents and total frames;
- half-open physical-frame interval disjointness;
- Side-A `last < a_high_water`;
- B-slot selection;
- stage-1 RESUME-row classification.

The adapter then performs a fresh real-product remount from **durable bytes only**.
Its actual remount result must agree with the independent raw-media oracle.

## Record commit

The record crash scope begins after one generated frame has been accepted and
`tape_service` has made the new COW chunk durable.

The verifier requires pre-commit metadata to remain the exact fixture state. The
pending chunk may differ, and its pre-commit hash becomes the persistence reference.

Frozen commit targets inactive B1, sequence 21:

- overwrite:
  `{2,0,1}`;
- overdub:
  `{2,0,1}, {0,1,131071}`;
- splice:
  `{2,0,1}, {0,0,131072}`.

Each transaction is exactly:
1. one entry-array block;
2. flush;
3. one block-0 header;
4. flush.

Every post-crash chunk hash must equal the pre-commit durable hash set. The crash may
choose the old or committed metadata generation according to the exact injected bytes,
but it may not damage already-durable user data.

This is persistence evidence only; it does not claim WP-09 audio/golden correctness.

## Reset-B

### Healthy

The fixture has selectable B at sequence 20. Reset copies live A into inactive B1 at
sequence 21 using one entry block + flush + header block + flush.

No chunk write is permitted.

### Degraded equal-sequence

B0 and B1 are both individually valid at sequence 500 with different entries. Side-A
mount therefore enters degraded-B.

Recovery writes B0 directly at sequence 501.

The fixture deliberately makes old B0's entry differ from Side A, so after B0's new
entry array is durable but before its new header is committed, old B0's CRC no longer
matches. B1 can consequently be the sole valid B slot.

That third intermediate state is explicitly accepted by the independent raw-media
oracle rather than incorrectly forcing reset into a two-state old/new model.

## §8 stage clearing

The verifier fixture is exactly §9.3.3 RESUME row 1:

- current superblocks generation 10;
- `promote_stage = 1`;
- `promote_staging_chunk = 2`;
- `a_high_water = 3`;
- live A and B each `{2,0,131072}`.

The clear writes:
- generation 11;
- stage 0;
- staging chunk 0;
- H unchanged at 3.

On a healthy pair §4.6 requires:
1. mirror partner write;
2. flush;
3. primary candidate write;
4. flush.

The baseline additionally proves the public caller reaches its first post-clear write:
- arm → feed/service reaches a chunk write;
- reset-B → reaches its index write;
- re-spool → reaches a chunk write.

That post-clear probe write is stopped before any byte lands and is not part of this
tranche's injection count.

## V7-001 closure

Current stage-1 generation 10 uses H=3 and live Side A at chunk 2.

The stale recovery copy deliberately uses generation 9 / H=1. If it ever becomes the
only selected copy, Side A violates `last < a_high_water` and the cartridge becomes
unusable.

To preserve a permitted one-copy/stale-partner state through mount, the later product
adapter must fail phase-4 repair **before the repair write lands**, require mount
success with `needs_repair=true`, then clear that setup fault and inject the tested
second interruption on the next logical partner write.

The byte oracle accepts only:
- the still-current generation-10 stage-1 state; or
- the durable generation-11 cleared state.

A rollback to generation 9/H=1 is a hard failure.

## Software binding contract

Software should import exact tree

`d99aa7d095ea9ee7228d6bddddd682848dfb8a55`

byte-for-byte under Structural Rule 1.

Software may add only mechanical:
- public-API operation scripting;
- dual working/durable fault device;
- power-cut/torn-write injection;
- raw compact snapshot production;
- build/CI/evidence retention glue.

It must not alter:
- fixtures;
- case planner/count/digest;
- durability semantics;
- expected transaction block bytes;
- permitted states;
- raw-media parser;
- oracle.

Production has no sampling/count override.

## Self-test disposition

GitHub Actions:
- workflow run: `35951947803`
- job: `107482166264`
- conclusion: **success**

WP-10 package output:

- PASS exhaustive planner
  `16448 12312 28760 6c924fd7bdd54b180084fe58cc50ef49d96fc068b968b8022383685ecf235c96`
- PASS frozen fixture/media-oracle controls
- PASS representative exact-byte crash oracles
- PASS skipped-injection negative control
- PASS wrong-durability-mode negative control
- PASS illegal-torn-outcome negative control
- PASS stale-partner-selection negative control
- PASS missing-second-interruption-state negative control
- PASS malformed-provenance negative control
- PASS streaming protocol smoke
- PASS all WP-10 core crash package self-tests

## Acceptance boundary

A later exact product run that passes this package and is independently dispositioned
can accept **only this bounded core WP-10 tranche**.

It does not complete WP-10.

## Explicit exclusions

Still outstanding in later WP-10/WP-12a work:

- full promote crash enumeration / all §9.3.4 recovery rows;
- format/duplicate crash identity-assignment;
- equal-generation-divergent raw-destination crash cases;
- full re-spool pass-1/pass-2 crash enumeration;
- shared-sequence/headroom/counter-boundary families;
- final format/duplicate superblock boundaries;
- general WP-12a continuation/re-entry/FAULTED acceptance;
- hardware media-atomicity validation;
- unrelated WP-07/WP-09/WP-11/WP-13 acceptance.

Issue #60 may close as completed when this publication PR is ready for PM review.
