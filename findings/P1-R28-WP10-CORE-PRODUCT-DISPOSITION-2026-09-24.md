# P1-R28 Verification return — exact WP-10 core crash evidence

Date: 24 September 2026  
Authority: independent Verification, issue #68

## Disposition

**PASS — the bounded WP-10 core crash tranche is accepted.**

Exact Digital-Tape PR #217 head
`14873bc2df31a5dac26692f838866619305bc50c` may proceed unchanged to PM
routing.

This finding does **not** merge product PR #217 and does **not** complete all frozen
WP-10.

## What this tranche closes

This accepted bounded tranche closes the published PR #63 crash package for:

1. record-commit crash enumeration in:
   - overwrite;
   - overdub;
   - splice;
2. reset-B crash enumeration in:
   - healthy live-B state;
   - degraded/equal-sequence B state;
3. §8 stage clearing through:
   - `tape_arm`;
   - `tape_reset_side_b`;
   - `tape_respool`;
4. V7-001 two-interruption closure for all three stage-clear entry paths across the
   four one-copy/stale-partner recovery seeds.

## Exact candidate / ordering

- product base:
  `553a73668f10c4c08c58f4a753776c798e1d88c5`
- verifier import:
  `75945543e62a9afe4cd54c0c580be4463e63e87f`
- mechanical binding:
  `7919f07f11ec932cdd0f48b783fe6a0512c8a5ee`
- reset-B stage-clear implementation:
  `f2bbb682a8ef1ecc0d4e9830874c467ccbac50b5`
- provenance-only correction / final head:
  `14873bc2df31a5dac26692f838866619305bc50c`
- final product tree:
  `6063510dc3a8f0e3d20b128c46da8b10b4ec21fa`

Independent commit-delta inspection confirms:

1. base → verifier import changes only `tests/IMPORTS.json` plus
   `tests/crash_core_draft8/*`;
2. verifier import → mechanical binding changes only CI plus
   `tests/crash_core_adapter/*`;
3. binding → implementation changes only `engine/src/ops.c`;
4. implementation → final head changes only
   `tests/crash_core_adapter/run_product.py`.

No verifier-owned byte changes after import.

## Verifier identity

Published by Verification PR #63:

- merge:
  `50bc25c79d8fffb993ba403481ba42c0b52209c5`
- publication:
  `18ff453e80fa245ad2d10066a1df262b443905b7`
- immutable package tree:
  `d99aa7d095ea9ee7228d6bddddd682848dfb8a55`

The product-imported subtree has exactly the same tree SHA and all verifier package
blobs match byte-for-byte.

## Independent case-set reproduction

Verification independently reimplemented the published planner.

Reproduced exactly:

- first-interruption cases: **16,448**
- V7-001 closure cases: **12,312**
- total: **28,760**
- flush-required: **14,380**
- write-through: **14,380**
- canonical case-set SHA-256:
  `6c924fd7bdd54b180084fe58cc50ef49d96fc068b968b8022383685ecf235c96`

Per-family totals reproduce:

- `record_commit:overwrite`: 2,056
- `record_commit:overdub`: 2,056
- `record_commit:splice`: 2,056
- `reset_b:healthy`: 2,056
- `reset_b:degraded_equal`: 2,056
- `stage_clear:arm`: 6,160
- `stage_clear:reset_b`: 6,160
- `stage_clear:respool`: 6,160

For every first-interruption scenario and durability mode, the verifier enumerates:
- before each of two target writes;
- all 511 nontrivial torn prefixes for each write;
- after each complete write, before its following flush;
- fault at each of two target flushes.

For V7-001 closure, each of three callers × four recovery seeds × two durability
modes enumerates the next partner write at landed lengths 0…512.

## Software fault-device audit

No material binding defect was found.

The exact worker keeps distinct:
- **working** media;
- **durable** media.

Reads use working bytes.

Ordinary successful writes update working bytes; in write-through mode they also
update durable bytes immediately.

A successful flush copies working media to durable media.

### Torn writes

At the selected target write, a torn case copies exactly the verifier-selected prefix
length into **both working and durable** bytes and returns failure. The remainder stays
at its previous durable content.

This matches the package's block-level torn-write durability model.

### After-write boundary

For `after_write`, the worker performs the full write, sets an
`after_write_pending` flag, and returns success.

The **next flush callback fails before copying working to durable**.

Therefore:
- write-through mode retains the completed write durably;
- flush-required mode does not.

The worker does not incorrectly model this as a 512-byte torn write.

### At-flush boundary

For `at_flush`, the selected flush returns failure before working bytes are copied to
durable.

Again, the two durability modes intentionally differ exactly as the verifier model
requires.

### Crash remount

After injection, the worker snapshots raw **durable** bytes and then performs a fresh
remount only after copying durable bytes back into working media and initializing a
fresh engine/rings instance.

The crashed working image is discarded.

## Baseline authentication

The retained `baselines.json` contains exactly **20** baseline/seed traces, matching
the verifier runner's required baseline-key count.

Verification independently recomputed every canonical baseline JSON SHA-256 and
matched all 20 hashes in `summary.json`.

Every baseline has:
- exactly two target one-block writes;
- exactly two target flushes;
- exact frozen target LBAs and block hashes.

### Record / reset baseline

Record-commit and reset-B baselines are exactly:

`target write 0 -> flush 0 -> target write 1 -> flush 1`

at the expected inactive index-slot entry/header blocks.

### Stage-clear baseline

Every stage-clear baseline has:
- exactly two superblock writes;
- exactly two flushes;
- `post_clear_reached = true`;
- no post-clear probe write landed.

For `arm` and `respool`, the next post-clear write class is `chunk`.

For repaired `reset_b`, the next post-clear write class is **`index`**.

The healthy first reset-B stage-clear baseline is:
- partner/mirror LBA 7168;
- flush;
- candidate/primary LBA 0;
- flush;
- then first index write reached but not landed.

Closure seeds whose current surviving candidate is the mirror correctly reverse the
order:
- partner primary LBA 0;
- candidate mirror LBA 7168.

Thus the retained baselines directly confirm partner-first/candidate-last behavior.

## Narrow reset-B implementation audit

The previous implementation refused stage-1 reset-B with `TAPE_ERR_BUSY`.

The repaired `engine/src/ops.c` change:

1. preserves all reset-B zero-write refusal precedence;
2. preflights one index `sequence`;
3. when stage 1 applies, preflights one `sb_generation`;
4. selects the B destination and computes the next index sequence;
5. calls `tape_sb_clear_stage(t)` **before the first B-index write**;
6. propagates helper failure;
7. then follows the prior reset-B index commit path unchanged.

The existing `tape_sb_clear_stage` helper independently audited at the exact head:

- increments `sb_generation` by one;
- clears `promote_stage`;
- clears `promote_staging_chunk`;
- leaves `a_high_water` unchanged;
- recomputes the superblock CRC;
- writes `sb_partner_lba`;
- flushes;
- writes `sb_candidate_lba`;
- flushes;
- only then updates in-memory superblock/candidate/partner state.

This is the exact §4.6 partner-first/candidate-last primitive the verifier package
models.

## Exact Actions run / artifact

- run: `36020396752`
- job: `107703515169`
- job conclusion: **success**

Artifact:

- ID: `10816547623`
- name: `p1-r27-wp10-core-crash-evidence`
- ZIP SHA-256:
  `ee7eabf782d1d1d44da10eb1f794822b0b866e2f90a1c3ea1b420df1a502068f`

Verification independently downloaded the artifact and reproduced:

- `PROVENANCE.json`:
  `0ce1639d32903f5d5ff4268006779a29aea8942012e7c6ec02466fd0bd4acc6c`
- `summary.json`:
  `57df0666512cd1aae28f898e62c059be7c6abf255602acaae81c5453eb5d783c`
- `software-summary.json`:
  `a967c768eeecf39916157a24e8a9358d1c724650fff3184cc6104918b2a64ce1`
- `baselines.json`:
  `96287bf5b58f13a8a1b18b57d0a1467d28b3f0a4fb4695c81944f7f1898adbba`
- build log:
  `75da8250844bc5064f2f0647f4efe418104f15b5108f9a39be15dd4069b595c4`
- empty adapter stderr:
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

Retained provenance correctly binds:

- product base:
  `553a73668f10c4c08c58f4a753776c798e1d88c5`
- verifier import:
  `75945543e62a9afe4cd54c0c580be4463e63e87f`
- product commit:
  `14873bc2df31a5dac26692f838866619305bc50c`
- product tree:
  `6063510dc3a8f0e3d20b128c46da8b10b4ec21fa`
- verifier publication:
  `18ff453e80fa245ad2d10066a1df262b443905b7`
- verifier tree:
  `d99aa7d095ea9ee7228d6bddddd682848dfb8a55`
- runner exit: **0**
- failure reproducer: **none**

The retained adapter/worker/Makefile bytes independently reproduce the exact PR-head
Git blobs:

- `adapter.py`:
  `e24ac6b3f6f877d39697bd74a2bc7f925c6873c4`
- `wp10_core_worker.c`:
  `c4f423b2974b2c1bc0957ea09273efd89445940c`
- `Makefile`:
  `da1f7a8c95a38ca855047c43d894d6bfac3b7baf`

## Exact completed campaign

Retained evidence reports:

- completed injection cases: **28,760 / 28,760**
- first-interruption: **16,448**
- closure: **12,312**
- flush-required: **14,380**
- write-through: **14,380**
- runner exit: **0**
- failed case: **none**
- failure reproducer: **none**

The family/mode/scope census in `software-summary.json` matches the independently
reproduced planner exactly.

## Logical outcome replay

The retained logical-outcome census sums independently to **28,760**, exactly the
completed case count.

Every retained logical fingerprint has a mountable `TAPE_OK` outcome under the
verifier's durable-byte parser.

For the five record/reset first-interruption families, the aggregate fingerprint count
is **10,280**, equal to 5 × 2,056.

For the three stage-clear families including V7-001 closure, the aggregate is
**18,480**, equal to 3 × 6,160.

Across those 18,480 stage-clear cases the only selected superblock states are:

- generation **10**, stage **1**, `a_high_water = 3`; or
- generation **11**, stage **0**, `a_high_water = 3`.

There is **no selected generation below 10**, no lowered water line, and no
unmountable/stale-rollback fingerprint.

This is the bounded-tranche safety property V7-001 is meant to close.

## Evidence-retention boundary

As designed by the published verifier package, successful per-case compact snapshots
are streamed through the immutable verifier oracle and then discarded. The success
artifact retains:
- exact case/census identity;
- all stable clean baselines;
- aggregate logical outcome census;
- exact binding/build/provenance identities.

A failing case would retain its exact case and compact snapshots in
`failure-reproducer.json`; none exists.

Therefore the ZIP alone is not a second offline copy of all 28,760 raw snapshots.
Acceptance is based on:
- independent authentication of the immutable verifier runner/oracle;
- independent audit of the exact product fault adapter;
- independent reproduction of the entire case planner;
- authenticated exact-head Actions execution;
- retained baseline and aggregate outcome evidence.

## Bounded WP-10 conclusion

**This bounded core WP-10 tranche: PASS.**

Exact Digital-Tape PR #217 may proceed unchanged.

This does **not** mean complete WP-10 acceptance.

## Remaining WP-10 / adjacent crash work

Still outside this accepted tranche are at least:

- full promote crash enumeration;
- format/duplicate crash identity-assignment coverage;
- full re-spool crash enumeration;
- remaining shared-sequence/headroom/counter-boundary crash families;
- broader WP-12a continuation/re-entry/FAULTED coverage where applicable.

Those families must be separately published/bound/dispositioned before full frozen
WP-10 can close.

Issue #68 may close as completed.
