# P1-R27 Verification return — independent WP-07 allocator/COW 10k package

Date: 23 September 2026  
Authority: independent Verification, issue #59

## Publication disposition

**PASS — independent WP-07 verifier package published and self-tested.**

This round is verifier authorship/publication only. It is **not WP-07 product
acceptance**.

The package was derived from the authenticated DRAFT-8 public specifications before
inspecting current product engine implementation. No Digital-Tape product file was
modified.

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
`tests/allocator_cow_draft8/`

Package publication commit:
`b0271d0805e1193de354f9244d1830bc163c7054`

Immutable package tree:
`41d07601186856afccde00107a85f27e2423bb2a`

The publication diff from verification main
`d8fb31b2a3a5fbf5555b19c2158f5727114186bb` contains exactly nine package files:

- `ADAPTER.md`
- `COVERAGE.md`
- `README.md`
- `fixture.py`
- `generator.py`
- `oracle.py`
- `runner.py`
- `selftest.py`
- `synthetic_adapter.py`

## Fixed verifier-owned campaign

Production has no count or seed override.

- RNG: `splitmix64-v1`
- master seed: `573037a110c02026`
- sequences: **10,000**
- total random actions: **65,026**
- edit actions: **59,423**
- reset actions: **5,603**
- canonical plan SHA-256:
  `dd2a25b5d45ee5fe343cf48d2168ffa275bbb5adb6f3cd398559ae56529da9cd`

Mode census:
- overwrite: 19,880
- overdub: 19,792
- splice: 19,751

The generator also exercises all nine symbolic seek/input shapes, all eight positive
feed-size buckets, and all six service-budget buckets. Each appears thousands of times.

## Independent COW ownership oracle

The verifier does not accept an adapter-decoded ownership result.

The fuzz fixture has `a_high_water = 3` and deliberately gives Side B legal
references to A-owned chunks 0, 1 and 2. Two B entries share chunk 0 while occupying
adjacent non-overlapping physical intervals.

From raw B0/B1 bytes, Verification independently:
- verifies index CRC;
- validates entry_count, total_frames and extent bounds;
- checks every half-open physical-frame interval for pairwise disjointness;
- selects the live B generation under §5.3;
- derives
  `free_next = max(a_high_water, max(live_B.last + 1))`.

A below-`a_high_water` **reference** is therefore accepted.

For writes/allocations, the later adapter must retain every scoped
`dev_write(lba,count)` callback. Verification maps the raw LBA range to chunk ids.
Every positive random recording is fully serviced and committed, so its reserved COW
chunks necessarily materialize as chunk-region writes before commit. Those raw chunk
write destinations are the observable allocation destinations for this campaign.

Any destination below `a_high_water` fails.

## Behavioral remount/free_next proof

No private product `free_next` variable is trusted.

After every generated edit or reset:
1. the product must unmount/remount;
2. the adapter returns raw B0/B1 metadata;
3. Verification derives the expected `free_next`;
4. a one-frame noncommitting recording probe is serviced far enough to perform its
   chunk write;
5. the **first** chunk write must land on exactly the independently derived
   `free_next`;
6. the probe aborts before index commit and the product remounts before continuing.

The next action's raw pre-media snapshot must equal the preceding committed post-media
snapshot, so the probe itself cannot silently alter the committed index state.

This directly exercises invariant 12 at the public/device boundary.

## Every committed index

After every successful generated edit/reset and remount, the adapter returns the exact
raw 64-byte B-slot header and exact CRC-covered entry bytes for both B slots.

The verifier rejects any structurally valid slot that fails full §5.2 validity,
including interval overlap, even if a lower-sequence slot could otherwise remain live.

Thus an invalid new commit cannot hide behind mount fallback.

## Reset: zero-copy and sub-second

The ordinary fuzz reset actions require:
- `TAPE_OK`;
- elapsed monotonic time < 1,000,000,000 ns;
- zero chunk-region writes;
- post-reset live B entries exactly equal Side A's unchanged entries.

A separate deterministic stress fixture gives Side A the maximum **4,096 entries**.
All are one-frame mutually disjoint intervals inside A-owned chunk 0.

The later product adapter must:
- run an isolated `tape_reset_side_b`;
- use a hard one-second watchdog;
- measure the API call with `CLOCK_MONOTONIC`;
- report timer resolution, platform, kernel and CPU model;
- retain every write callback;
- return raw post-remount B-slot bytes.

Verification requires:
- elapsed < 1 s;
- no chunk-region write;
- live B index with all 4,096 legal references.

A fast reset that copies audio fails. A zero-copy reset taking >=1 s also fails.

## Binding contract

Software should import exact package tree
`41d07601186856afccde00107a85f27e2423bb2a` byte-for-byte under Structural Rule 1.

Software may then add only mechanical product adapter/build/evidence glue implementing
`ADAPTER.md`.

The adapter supplies raw facts:
- complete scoped write callbacks;
- raw B0/B1 index metadata;
- public API results and accepted frame counts;
- resolved seek values;
- monotonic reset timing/environment.

It must not:
- regenerate or skip verifier actions;
- parse/select the live index as an authoritative result;
- report a private allocator variable instead of raw evidence;
- suppress/coalesce write events so covered LBAs are lost;
- alter seed/count/thresholds;
- treat event overflow, timeout, process death, malformed output or EOF as success.

The production runner itself has no acceptance count/seed option.

## Self-test disposition

GitHub Actions:
- workflow run: `35950354749`
- job: `107477357602`
- conclusion: **success**

WP-07-specific output:

- PASS deterministic 10000-sequence generator
  `dd2a25b5d45ee5fe343cf48d2168ffa275bbb5adb6f3cd398559ae56529da9cd`
  / 65,026 actions / 59,423 edits / 5,603 resets
- PASS legal shared below-high-water reference control
- PASS below-floor allocation/write negative control
- PASS wrong remount free_next negative control
- PASS interval-overlap negative control
- PASS reset chunk-movement negative control
- PASS reset timing negative control
- PASS fewer-than-10000 negative control
- PASS malformed-provenance negative control
- PASS streaming protocol smoke
- PASS all WP-07 allocator/COW package self-tests

These controls demonstrate that the oracle does **not** conflate legal shared references
with forbidden allocation/write ownership.

## Acceptance boundary

This publication is not product evidence.

If a later exact product candidate passes this immutable package and independent
Verification authenticates the binding/raw artifact, this tranche is intended to close
the remaining frozen WP-07 acceptance criterion unless a spec-grounded omission is
found.

No additional frozen WP-07 criterion was identified during this authorship round.

## Explicit exclusions

This package does not claim or accept:
- WP-09 recording/golden/audio correctness, even though record APIs are exercised;
- overdub sample arithmetic or exact rendered PCM after edits;
- WP-10 crash/torn-write durability;
- WP-12 re-spool/promote correctness;
- WP-12a long-operation continuation/re-entry/FAULTED behavior;
- WP-13 embedded-resource readiness;
- unrelated work-package acceptance.

Issue #59 may close as completed when this publication PR is ready for PM review.
