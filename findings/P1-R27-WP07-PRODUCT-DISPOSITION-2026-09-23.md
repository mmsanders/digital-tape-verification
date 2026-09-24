# P1-R27 Verification return — exact WP-07 allocator/COW product evidence

Date: 23 September 2026  
Authority: independent Verification, issue #65

## Disposition

**PASS — complete frozen WP-07 package acceptance is satisfied.**

Exact Digital-Tape PR #210 head
`4686d132c15a3bf591c36d0a058a7b6f4e567f85` may proceed unchanged to PM
routing.

Verification requests:
- no product behavior change for WP-07;
- no fresh campaign solely because Software PRs #208/#209 were superseded;
- no additional WP-07 criterion.

This finding does **not** merge product PR #210.

## Exact candidate / Structural Rule 1

- product base:
  `92d6a3402d4908322c191bd3464011ae97f94114`
- verifier-import commit:
  `7ac78154a4024288ef34c21b8fd0d5c95b3bace2`
- product-binding commit/head:
  `4686d132c15a3bf591c36d0a058a7b6f4e567f85`
- final product tree:
  `e8a9dd6aab768c13a536b3fd4a0330069fa5e53b`

Independent commit-delta inspection confirms:

1. base → import commit changes only `tests/IMPORTS.json` plus the nine files under
   `tests/allocator_cow_draft8/`;
2. import commit → binding commit changes only:
   - `.github/workflows/ci.yml`
   - `tests/allocator_cow_adapter/Makefile`
   - `tests/allocator_cow_adapter/README.md`
   - `tests/allocator_cow_adapter/adapter.py`
   - `tests/allocator_cow_adapter/run_product.py`
   - `tests/allocator_cow_adapter/wp07_product_worker.c`;
3. no `engine/` or verifier-owned file changes occur in the binding commit.

Structural Rule 1 is therefore satisfied.

## Verifier identity

Published verifier package:

- Verification PR #62 merge:
  `5c56d457faed0fb81feef8e89c29adec966ee3a3`
- package publication:
  `b0271d0805e1193de354f9244d1830bc163c7054`
- immutable package tree:
  `41d07601186856afccde00107a85f27e2423bb2a`

The imported product subtree at `tests/allocator_cow_draft8/` has exactly the same
tree SHA and all nine blobs match the publication byte-for-byte.

## Software binding audit

No material adapter/worker defect was found.

### Fresh fixture and fresh engine instance

The verifier runner generates the two fixtures itself and authenticates the adapter
handshake against verifier-owned fixture SHA-256s.

The Software shim passes those exact fixture paths to the worker. Every random
sequence launches a **fresh worker process**, and the worker:
- reloads the exact fuzz VO08 bytes;
- zero-initializes its virtual media structure;
- initializes a fresh device;
- zero-initializes the engine instance, playback ring, recording ring and PCM buffer;
- calls `tape_init` and cold `tape_mount(..., TAPE_SIDE_B, 0, ...)`.

Every later remount also reinitializes the engine/rings before mount. Thus the
verifier's "fresh sequence" and cold-remount boundaries are genuine.

### Raw write capture

The exact worker's device write callback executes:

`record_write(lba, count)`

**before** range checking, block allocation, or copying data into the backing media.

Therefore an attempted write cannot disappear from evidence merely because it was
out-of-range or otherwise rejected.

The fixed event buffer exposes overflow explicitly; overflow terminates/fails the
worker/verifier path rather than silently truncating evidence.

### Raw B-slot evidence

The worker snapshots B0/B1 directly from the backing virtual media. It emits:
- exact first 64 header bytes;
- exact `12 * entry_count` entry-array bytes when the header has index magic and a
  bounded entry count.

It does not select a live slot, derive `free_next`, decide ownership, or emit an
allocator verdict. Those decisions remain in the verifier-owned oracle.

### Edit and probe execution

For each verifier-owned edit plan the worker:
- obtains public `total_frames`;
- resolves the exact symbolic selector;
- calls the requested public record mode;
- feeds the exact requested positive frame count;
- services with the generated positive block budget until completion;
- commits;
- unmounts and cold-remounts;
- emits raw post-remount B slots;
- runs the verifier-required one-frame overwrite allocation probe;
- services the probe, aborts before index commit, unmounts and cold-remounts again.

The Python shim does not regenerate or reorder actions. It validates plan syntax and
mechanically forwards the verifier-owned values.

### Reset hard watchdog / timing

The exact worker wraps every `tape_reset_side_b` call with:
- `CLOCK_MONOTONIC` before/after measurement;
- a one-second `ITIMER_REAL` watchdog;
- a SIGALRM handler that exits the worker with code 124.

For ordinary generated sequences, that process death causes the persistent adapter to
fail and therefore causes the unchanged verifier runner to fail closed.

For the isolated reset-stress worker, code 124 is explicitly returned as
`timed_out=true`, which the verifier rejects.

An outer Python subprocess timeout is also present and cannot turn a timeout into a
pass.

## Exact Actions run / artifact

- run: `35953473330`
- job: `107486738997`
- job conclusion: **success**
- product head:
  `4686d132c15a3bf591c36d0a058a7b6f4e567f85`

Artifact:
- ID: `10789492652`
- name: `p1-r27-wp07-allocator-cow-evidence`
- ZIP SHA-256:
  `cc277bc3f32d7834840ba03285d9ec891d07b474e6a8948a375689bc302f0da6`

Verification independently downloaded it and reproduced:
- `summary.json`:
  `7bdc04ab4ee9b6242e499b90614b544e59852beef60b30f90ac122440dfa3808`
- `reset-timing.json`:
  `1fbc9dd29f25058e440f2669275471af4e2d2be34e7219bbc26ffe44fc351321`
- `PROVENANCE.json`:
  `24784ee08a1968d35698219851574abbc7add117bd609f353e7935c5fd006fa4`
- `build.log`:
  `02c1564c49055a5622ea1f91ab529acedc05d985bbb964dd339c8fff0da2ced0`
- empty `adapter.stderr.txt`:
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

The retained adapter files are exact candidate bytes. Independent Git-blob
recomputation over the retained artifact gives:
- `adapter.py` blob
  `1250623533f3d78db10ec6f30f425bd8e1796e98`;
- `wp07_product_worker.c` blob
  `cc7e0698ed6f54a61e866ed366c001a2e6aad6c3`;
- `Makefile` blob
  `ffe80479c4dd96e84d965ca4571ceddf5bdf583b`.

Those exactly equal the corresponding paths at product head #210.

Retained SHA-256s likewise reproduce:
- Python adapter source:
  `590862baecc3c54e3daaf103d89d1c9b24fa65472f84fbd6f82b10ef3ce269fd`;
- C worker source:
  `704bcc35ff7bad009f1af6a62c7aa25971c164778547b6220cb24c1138b8d9b0`;
- retained adapter build log:
  `02c1564c49055a5622ea1f91ab529acedc05d985bbb964dd339c8fff0da2ced0`.

The Actions log records the linked worker SHA-256
`063401e716f7f2727e36cf5f7238838f7996cafe9cbd305f653b3ea224278ec4`
and engine archive SHA-256
`518907a3ca91e3c04636e5aec3b6a9afb79601ef0db0d133a0210707aa1c10f3`,
matching `PROVENANCE.json`.

## Independent fixed-generator reproduction

Verification independently reimplemented the published SplitMix64-v1 generator rather
than trusting the saved summary.

Reproduced exactly:

- RNG: `splitmix64-v1`
- master seed: `573037a110c02026`
- sequence count: **10,000**
- action count: **65,026**
- edit count: **59,423**
- reset count: **5,603**
- minimum actions/sequence: **4**
- maximum actions/sequence: **9**
- canonical plan SHA-256:
  `dd2a25b5d45ee5fe343cf48d2168ffa275bbb5adb6f3cd398559ae56529da9cd`

Every saved mode, selector, feed-size, service-budget and sequence-feature census value
matches the independent generator reproduction exactly.

Every sequence ends in an edit as designed.

## Reset sidecar authentication

The full `reset-timing.json` sidecar contains exactly **5,603** ordinary reset
records.

Verification independently generated all 10,000 plans and compared the expected reset
coordinates against the sidecar:

- expected reset `(seq_index, action_index)` pairs: **5,603**
- retained reset pairs: **5,603**
- duplicate retained pairs: **0**
- missing/extra/reordered pairs: **0**

Thus the sidecar covers every generated reset exactly once.

Timing environment:

- clock: `CLOCK_MONOTONIC`
- timer resolution: **1 ns**
- platform: `Linux-6.17.0-1022-azure-x86_64-with-glibc2.39`
- kernel: `6.17.0-1022-azure`
- CPU model: `AMD EPYC 9V74 80-Core Processor`

Ordinary reset measurements:

- timeout count: **0**
- minimum elapsed: **6,199 ns**
- maximum elapsed: **103,516 ns**
- all **5,603 / 5,603** are strictly below 1 second

The 5,603 reset records contain exactly **11,206** raw write callbacks:
- B0/B1 entry/header metadata LBAs only;
- **zero callbacks overlap the chunk store beginning at LBA 2048**.

Thus ordinary reset directly satisfies both the sub-second and no-audio-chunk-movement
requirements on every generated reset in this campaign.

## 4,096-entry reset stress

The retained stress record reports:

- elapsed: **174,513 ns**
- `timed_out = false`
- raw writes:
  - `lba=393, count=96`
  - `lba=392, count=1`

Those are exactly the inactive B slot's 96 CRC-covered entry blocks followed by its
header block. Neither range overlaps the chunk store.

The unchanged verifier oracle consumed the worker's raw post-remount B slots and
accepted only after independently selecting/parsing the live B index and observing:
- **4,096 entries**;
- total frames 4,096;
- all references legal below the stress fixture's `a_high_water`.

The compact success artifact retains the resulting `entry_count=4096` and timing;
the successful raw slot transcript itself is intentionally not retained by this package.

Therefore the maximum-entry reset stress is both sub-second and zero-copy.

## Allocator/COW acceptance from the 10k run

The unchanged verifier-owned runner/oracle processed every per-action raw observation
live during the exact Actions run. A sequence fails immediately on:
- wrong fixture/sequence identity;
- action mismatch;
- media-continuity mismatch;
- malformed/invalid/overlapping index slot;
- any chunk write below `a_high_water`;
- edit first allocation not equal to independently derived pre-action `free_next`;
- post-remount probe first allocation not equal to independently derived post-action
  `free_next`;
- short feed or API failure;
- reset chunk movement;
- reset >=1 s or timeout;
- event overflow;
- process failure, malformed output or timeout.

The retained successful aggregate is:

- completed sequences: **10,000 / 10,000**
- normal exit: **true**
- failure reproducer: **none**
- allocation probes: **65,026**
- edit observations: **59,423**
- reset observations: **5,603**
- chunk allocation/write observations mapped by the verifier: **826,479**
- legal below-`a_high_water` reference snapshots accepted: **59,955**

The count of allocation probes equals the independently reproduced total action count,
so every generated action reached its remount/free-next behavioral probe.

The edit/reset observations equal the independently reproduced generator census
exactly.

Because the immutable verifier runner is fail-closed on the raw conditions above, the
normal completion establishes for this exact campaign:

1. no observed Side-B allocation/write destination below `a_high_water`;
2. every generated edit began allocation at verifier-derived `free_next`;
3. after every committed edit/reset and cold remount, the one-frame behavioral probe
   began allocation at the verifier-derived remount `free_next`;
4. raw B-slot continuity held between actions;
5. every structurally valid committed B index passed CRC, bounds, total-frames and
   half-open physical-frame interval disjointness;
6. legal below-water Side-B references were accepted rather than misclassified as
   allocation ownership.

### Compact-evidence boundary

The package deliberately retains aggregate success evidence instead of all 65,026
successful per-action transcripts. Therefore Verification cannot re-run the entire
per-action oracle offline from the ZIP alone.

That is not a new omission: it is the verifier package's published evidence-retention
design. Independence is preserved here by authenticating:
- the immutable verifier tree;
- exact adapter/worker source;
- exact candidate/run identity;
- the fail-closed runner/oracle;
- the independently reproducible generator/census;
- the complete reset timing/write sidecar;
- the successful exact-head Actions execution.

A failed case would have retained its exact plan/observation as
`failure-reproducer.json`; none exists.

## Superseded Software attempts

PRs #208 and #209 were closed unmerged.

Their issues were evidence-retention/provenance defects:
- #208 did not retain the complete ordinary reset timing sidecar;
- #209 did not record an actual CPU model string.

PR #210's exact artifact contains the complete sidecar and a concrete CPU model. The
verifier and product engine semantics were not widened to obtain this evidence.

A new 10,000-sequence run is therefore not required solely because those earlier
Software attempts existed.

## Complete WP-07 acceptance conclusion

The frozen WP-07 package criterion covered by Verification publication #62 is:
- 10,000 random edit sequences exercising allocator/COW behavior;
- no Side-B allocation/write below `a_high_water`;
- legal below-water references allowed;
- remount `free_next` re-derived correctly;
- committed indices preserve physical-frame disjointness;
- reset-B moves no audio chunks and completes in under one second, including the
  maximum-entry-count stress shape.

This exact product evidence satisfies all of those conditions.

Verification identifies **no remaining spec-grounded WP-07 acceptance criterion**.

**Complete frozen WP-07 package acceptance: PASS.**

PM may route exact Digital-Tape PR #210 onward unchanged.

## Explicit exclusions

This finding does not imply acceptance of unrelated work packages, including:
- WP-09 recording/audio golden correctness;
- WP-10 crash/torn-write durability;
- WP-11 golden/listening acceptance;
- WP-12 / WP-12a promote/re-spool behavior beyond this package's remount probes;
- WP-13 resource/structural readiness;
- hardware media-atomicity requirements.

Issue #65 may close as completed.
