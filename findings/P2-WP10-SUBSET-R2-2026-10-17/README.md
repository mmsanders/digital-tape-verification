# WP-10 return 2: fresh load observations pass; core boundary planner held

**Disposition:** V186-01 fresh-image correction and checksum correction PASS
within the bounds below. The bounded long-epoch return is **HELD on V186-02**:
setup I/O shifts operation-relative coordinate selection in four core closure
seeds. No engine defect or complete operation-package acceptance is asserted.

Michael manually resumed Verification on 17 October UTC. Product main input
`c6ff868086e3333bb7568e60d3a2f4ec60fd3344`; Verification main input
`1a6b1be6e52d3b747cd6deb48b4131ae127f09b0`. Required onboarding and the live
role queue were read. Verification #186 last updated `2026-10-16T15:31:43Z`;
its closed correction/scale stop is preserved. This is Michael's direct
resumption of Software #440's new return comment 6228016490, not a stale-event
reactivation. Verification #146 remains the residual native A6 assignment;
Software #439 and435 had no newer returns after our PR #190 disposition.

Exact candidate: Product #443 `33df48ea62c64f5c031c5d8403404a6e665368fb`.
The heavy campaign ran at `9095b41fc549ca650beb0ec71ecde944fd637067`;
its diff to the candidate changes only `.github/workflows/wp10-subset.yml`.
The reviewed driver/bindings are identical at those two commits.
Imported `tests/wp10_subset_r1` tree remains
`c6cb573d654d337fef2f616f11cce0cee74e8968`; import 54b3dd7 still precedes
binding changes. A8 engine tree remains
`d96b4245e04d74078f8938744b1394c3018516f7`. No engine implementation was read.
The four C observation workers are unchanged from the prior disposition.

DRAFT-10 authority is unchanged: tapefs SHA256
`2a6a9f7b6fe1e5f9e3fe068b3c6460a81256276082bb7e336c01dbf1e9c17eba`,
engine-api `aa042e41e35b02bf2bb6b3896e59340a947720c27dc5fc52a24d657ccd66b33a`,
acceptance `50aa63bd751fdc6b4636de0eb48253887be19b7ec2841768449217b4e9b9e547`.
No issued oracle, test package or Product implementation is changed here.

## Authenticated evidence and what was checked

All thirteen ZIP hashes match their Actions metadata. `artifacts.json` preserves
IDs, names, sizes, complete digests, commit bindings and expiration dates.
All 1,959 indexed inner files authenticate; every bundle lists every other member
and excludes SHA256SUMS itself. This closes the prior checksum-index finding.

Five exact-head PR workflows independently SUCCESS: subset 38986135965,
engine 38986136059, integrity 38986135970, hygiene 38986136106,
publication 38986135848. All eight heavy jobs in dispatch 38975105003 SUCCESS.
That dispatch's old combined small job was cancelled at its two-hour limit;
it is not counted as a passing run or used here. The subsequent exact-head
small and four load jobs supply those packets. Green CI is not acceptance.

| New heavy family | Actual retained runs | Projections | Sampled-plan runs | Max pending epoch |
|---|---:|---:|---:|---:|
| Core stage-clear/respool, five seeds |885|112,127|518|1024|
| Respool v3 passes 1/2 |486|70,740|326|2048|

The complete operations have 1028 units for every core seed, 4100 for respool
pass 1 and 2050 for pass 2. A failed setup repair adds one trace event in four
core seeds; it does not make their operation 1029 units. Earlier Software prose
describing both respool passes as 4100 units does not match the actual pass 2.
Second operations use their own actual histories, sometimes with different sizes.

Independent replay uses only Verification's published model. It checks initial
image and trace hashes, callback grouping, IDs, 512-byte payloads and acknowledgments,
successful/failed barrier epochs, every selected plan/mask/order, complete
projection-image hashes and remount references. `replay-result.json` records the
per-part result: all 1,371 new heavy runs / 182,867 projections and all
2,624 unchanged non-load small runs / 4,619 projections replay with zero errors.
Long epochs use all 201 plans from seeds 1, 183, 3647685189;
small epochs are exhaustive. Coordinate selection remains SAMPLED.
The eight heavy jobs total about 43.9 runner-minutes including build, from their
Actions start/end timestamps; this is not a measurement of process CPU time.

`audit-result.json` independently derives operation-relative boundary sets from
retained actual traces and checks all 21 first/second scenario/base plans. All 14
second bases are distinct within their seven scenarios, match retained first-cut
coordinate/mask/order/image records and the second run's initial bytes, and use
the prescribed first-distinct/later-only selection. All first-operation barrier
entry/error coordinates are present. The fixture base and both second bases have
the prescribed unit cuts for respool pass 1/pass 2 and the ordinary core seed.
The eight affected core contexts are described below.

The original 3,745 runs / 48,833 projections are carried forward from PR #189 by exact
coordinate/input/epoch/actual-trace-hash/plan/projection equality, including
multiplicity: zero added or missing math records in all five small families.
Thus unchanged load 32 MiB images are not needlessly rehashed. The new non-load
small packet is also replayed independently in this round. Prior snapshot/parser
facts retain their exact bounds; no new operation-row verdict is inferred from
successful projection hashing.

**Correction to our prior prose:** PR #189's statement that no repeated-LBA event
occurs in the small campaigns was wrong. The retained original records have 24
such event occurrences in core and 24 in promote, in the setup/error paths;
new packets match them exactly. Their masks/orders were already included in the
successful full projection replay. The new heavy core records have 12 repeated-LBA
event occurrences; respool v3 has zero. These counts do not establish comprehensive
repeated-LBA operation coverage. The old publication remains immutable.

## V186-01 closed: load commands have independent pristine inputs

All 31,216 retained load remount rows, 93,648 command records, have the selected
projection hash as EACH command's before-image hash. Mutation flags and the
`mutated_by` list agree with individual before/after hashes. The reviewed binding
writes a separate pristine projection file immediately before each verify,
dump_A and dump_B subprocess. It records each command's output, engine bind/mount/
info observations, seam hash, write/flush counts and after-image hash.

Both previously problematic hashes are present:
`8b5178590292df5725cb3ae3d7f4108afe70855a964f9b7b1afac38ad4ac3b87` and
`9d404d620567b654a539c2cf3ed1f38b5143e492f1e174b42eb1e1917daab327`.
Ten rows across the new shard-local caches reference them. In each, verify's
read-only binding reports repair needed and leaves its image unchanged; BOTH
dump_A and dump_B start from the original hash and separately record one write,
one flush and the repaired after-image hash. DumpB no longer consumes dumpA's
repair. Their separate outputs are retained by digest. The ten rows are cache
occurrences of two projection identities, not ten distinct failing images.

Other worker bindings were audited within the previously covered observation
seams: core/dup/respool perform one side's mount; promote remount_render copies
the input image separately for A and B. No same-image cross-command handoff is
present there. This is a bounded fresh-input/provenance PASS, not independent
acceptance of every mount repair or audio output. Seam summaries and hashes are
retained; the full per-command native seam JSON is not in these bundles, so its
event-level details cannot be replayed from its digest alone. Full repair-state
judgment remains separate.

Host load still has 404 unreachable fault coordinates and uses projections of a
complete actual trace for cuts, not actual interrupted host executions. Neither
is promoted to executed fault coverage by this correction.

## V186-02: setup callbacks shift operation coordinates

The bounded planner counts ALL trace writes to derive U, metadata/call positions
and barrier neighbourhoods, but the worker's cut/error arguments are operation
relative. Four closure seeds have one failed repair write with phase=setup before
the 1028 operation writes: mirror_only, primary_only,
mirror_newer_primary_stale and primary_newer_mirror_stale.

| Context | Required missing coordinate | Spurious coordinate |
|---|---|---|
| First operation, each of four seeds |cut_op_unit 1020; error_op_call 1019|cut_op_unit 1029; error_op_call 1028|
| Byte-restored first second-base, each of four seeds |cut_op_unit 1020|cut_op_unit 1029|

The spurious error 1028 is not an error observation: all four workers report
error_fired=false and TAPE_OK. Requested cut 1029 similarly never fires.
The retained complete trace has 1029 W events, but only 1028 have phase=op.
Its correct last-eight interval is 1020..1028, not 1021..1029. All extra end-U
records at 1028 are distinguished from the out-of-range 1029: a valid end boundary
can have no subsequent callback at which to emit CUT, which is not this finding.

Concrete sources: heavy-1/core-respool/part-001-01 primary_only,
heavy-4/part-004-01 primary_newer_mirror_stale,
heavy-2/part-002-02 mirror_newer_primary_stale and heavy-7/part-007-01 mirror_only
contain the unfired error 1028 rows (see artifact names in artifacts.json).
`audit.py` computes the missing and extra sets without importing Product's
planner. `audit_selftest.py` proves the phase-counting regression is detected and
checks multi-unit call grouping/internal cuts. This is an observation/planning
defect, not an engine or normative crash-oracle defect.

**Direct Software #440 correction:** derive operation coordinate/call/barrier
ordinals only from phase=op, with a mapping back to original trace IDs/calls.
KEEP setup callbacks in the durability replay, including failed repair events;
do not erase them to make counts agree. Check planned coordinates against actual
operation counters, and make missed requested faults explicit. Fill only the
missing first cut 1020 / error 1019 and affected second cut 1020 observations and
their prescribed persistence plans; reuse the already authenticated histories,
images and unchanged observations. Reissue accurate plan/coverage summaries and
confirm second-base selection under the corrected plan. No full 175 CPU-hour rerun,
engine change, assertion relaxation or batching is requested.

## Reproduce and stop

Fetch each Actions artifact in artifacts.json using its ID, verify the complete
ZIP digest, and unpack into ROOT/<artifact-name> (do not merge shard directories).
Fetch the original artifact 12023520803 with the hash in PR #189 for optional prior
math carry-forward. From this repository root:

```sh
python3 -B findings/P2-WP10-SUBSET-R2-2026-10-17/audit_selftest.py
python3 -B findings/P2-WP10-SUBSET-R2-2026-10-17/audit.py ROOT --prior ORIGINAL --out audit-result.json
python3 -B findings/P2-WP10-SUBSET-R2-2026-10-17/replay.py ROOT --exclude-load --out replay-result.json
```

Raw ZIPs remain in Actions with their metadata expiration dates (January 2027).
Their committed hashes are the citations; durable retention is required before
expiry. This publication adds only the report, replay/audit sources/results and
an exact path selector to the existing normal publication CI. No new gate or
changed acceptance criteria is introduced.

Return directly to Software #440, Verification #186 and PM #384. Stop at V186-02's
concrete correction. Full operation-specific crash-row judgments, broad long-copy
coverage, complete load fault coverage and batching readiness remain undisposed.
All WP14/native/physical, WP16 full-package, WP15, frozen-format, write/async/
recording, <30s target, firmware, hardware/media/atomicity and purchase holds survive.
