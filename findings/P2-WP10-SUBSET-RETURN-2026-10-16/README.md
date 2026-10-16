# Verification186: bounded binding review and long-epoch scale decision

Michael's16October activation, after169/435 and ready146 native returns.
Input Product mainc6ff868086e3333bb7568e60d3a2f4ec60fd3344; Verification
maina9d407c, then187/188 publicationse8211ad/f168a2e. Authority186/ADR183,
independent package183/184. Exact Product443 candidate:
c8ad365479e853c4ee3847d8a9f6470b24ef7719.

**HELD for corrected observation binding and bounded long-epoch return.**
No engine defect, complete operation-package acceptance, batching permission,
media qualification or Product integration authorization is inferred here.
No Product engine implementation inspected; no Product adapter imported into the
independent replay. Published model and original raw-state parsers are reused.

## Authenticated identities and bounded evidence

Imported tests/wp10_subset_r1 subtree
c6cb573d654d337fef2f616f11cce0cee74e8968 equals Verification's publication,
import54b3dd7 precedes binding changes. Original suites unchanged. Engine A8
is exactlyd96b4245e04d74078f8938744b1394c3018516f7; no engine/firmware/host/port
diff. Five exact-head workflows independently SUCCESS: engine38842418382,
evidence38842418334, hygiene38842418489, publication38842418505,
subset38842418556. CI does not accept the behavior.

Artifact12023520803 (wp10-subset-small), ZIP SHA256
e4e2419ec6983a64b0318b2cacbbb4c949847d771c8ca45d0bb38fe04e0ae2f4
is authenticated. Inner SHA256SUMS authenticates every OTHER member. Its own
self-entry is incorrectly the empty-file digeste3b0c442…b855: generation redirects
into SHA256SUMS before find enumerates it. This self-reference does NOT verify;
the outer authenticated ZIP binds the checksum file. Fix generation to exclude
the checksum file; do not quietly report sha256sum -c as passing. replay.py
explicitly excludes and documents that invalid self-entry.

Independent replay checks actual full/prefix trace hashes, every initial-image
hash, callback-unit IDs/512-byte payloads/grouping/acknowledgements, successful and
failed barrier epochs, actual masks/landing orders against our planner, every
projection's full byte-image SHA256 and referenced fresh remount, and second-cut
base hash identities (1659 first-cut coordinate/mask/order links checked). Snapshots' canonical metadata hashes authenticate separately.
No binding PASS string substitutes for this computation. Census and detailed
replay results are retained here.

| Binding | Executed runs | Projections | Max epoch | Unreachable coordinates |
|---|---:|---:|---:|---:|
| core |393|632|2|0|
| promote |1266|1935|2|0|
| format/dup |938|2016|4|0|
| load |1121|44214|8|404|
| respool decline |27|36|1|0|

Independent full projection replay reports zero errors.
All these small-epoch plans are exhaustive within the published <=8 bound.
Core/promote include actual2-event epochs in failed-I/O/closure cases, despite
Software's return prose saying0–1. No repeated-LBA event occurs in these campaigns;
separate binding proofs are not a repeated-LBA operation campaign.

Raw snapshot corroboration independently reconstructs the projected primary,
mirror, slot prefixes and retained chunk bytes/hashes:100 core snapshots,
409 promote,286 format/dup and16 respool-decline snapshots. Original independent
raw-state parsers corroborate100 core mount results,818 promote mount results
and818 promote PCM hashes, and286 format/dup mount/selected-UUID results.
DRAFT10's BAD_MAGIC/CRC unmountable equivalence is preserved. These are bounded
raw-byte/parser observations, not all operation-specific crash-table outcomes.

## V186-01: load observations share a mutating remount image

The load route writes the projection to one copy, then runs verify, dumpA, dumpB
sequentially on that same file. Fresh processes do not restore durable bytes.
Six retained remount records have image_sha256_after != projection_sha256:
projection8b5178590292df5725cb3ae3d7f4108afe70855a964f9b7b1afac38ad4ac3b87
or9d404d620567b654a539c2cf3ed1f38b5143e492f1e174b42eb1e1917daab327.
verify reports NEEDS_REPAIR; dumpA reports one flush. Thus dumpB is not a fresh
observation from the selected crash projection. load-remount-mutations.json
retains all six actual records. This is a binding/provenance defect, not an
inference that repair itself or the engine is wrong.

**Direct Software440 correction:** use a separately restored pristine projection
for EACH verify/dumpA/dumpB process. Bind each command's before/after image hash,
actual engine/native trace and output. Permit lawful mount repair only according
to its original operation oracle; record it explicitly, never let that mutation
supply the other side's starting bytes. Preserve already authenticated traces/
projections and only rerun affected observations as needed. Audit the other worker
bindings for the same shared-state issue; their byte/parsing observations above
do not waive fresh-state provenance. No engine/port/shipping-binary change.

Also the load cut histories are projections of a complete actual trace, not
actual interrupted host executions. Keep that truthful label. The cross-binding
prefix checks are useful but do not prove the host route itself under every cut.
No write-error seam and only first-barrier error are honest404 unreachable
coordinates, not executed error coverage. Full acceptance cannot count them.

## Long-epoch scale: bounded campaign authorized, not175 CPU-hours

Do NOT launch the proposed full175CPU-hour campaign on this return.186 explicitly
permits naming a boundary subset. For every core stage-clear/respool closure seed
and both respool_full v3 passes, use this deterministic unit-boundary set for an
operation with U actual units (deduplicate and clamp into0..U):

-0..8 and max(0,U-8)..U;
-2^k-1,2^k,2^k+1 for every power of two <=U;
-1024j-1,1024j,1024j+1 for every positive1024j<=U;
-every actual metadata/identity/index write boundary and its two adjacent units;
-every barrier entry and its two adjacent unit boundaries.

Run the COMPLETE successful operation and error at every barrier. For copy-write
errors, use calls containing the selected unit boundaries; include every metadata/
identity/index-write error. Multi-unit calls must preserve their real grouping
and include selected internal unit cuts. For each scenario select two DISTINCT
first-cut durable bases with recorded projection/mask/order (including a later-only
projection when distinct), destroy all RAM, and apply the same bounded plan to each
second operation's ACTUAL trace. If fewer than two distinct bases exist, record
that fact with the enumerated image identities; do not duplicate a base as coverage.

At each cut use exhaustive plans for epochs<=8; otherwise ALL201 sampled plans
from seeds1,183,3647685189, retaining full replayable event/mask/order identities.
Report unit-coordinate coverage and duplicates separately from persistence plans.
Label long-copy unit-coordinate coverage SAMPLED; never call it every-boundary
or full WP10 acceptance. Keep errors actually unreachable as missing coverage.
Use compact hashed raw observations as already issued, without changing oracles.

This bounds the next evidence tranche and can expose later-only/order/resume
failures without spending175CPU-hours upfront. Software should report measured
cost/coverage; broader coverage and any batching readiness remain undisposed.
The full original per-operation predicates still apply to every selected image.
No universal old-card-unchanged rule is added for destructive operations.

## Direct return and replay

Software440 receives V186-01, checksum correction and the exact bounded scale
plan; PM384 receives current bounds, exclusions and next owner.186 returns at
this concrete correction/scale stop. Remaining operation-specific row judgments,
long-epoch runs, repeated-LBA operation coverage and missing load fault coverage
are not PASS. No corrected engine or batching design is requested.

Fetch/authenticate artifact12023520803 and unpack to EVIDENCE. Then:

```
python3 -B findings/P2-WP10-SUBSET-RETURN-2026-10-16/replay.py EVIDENCE --out replay-result.json
python3 -B findings/P2-WP10-SUBSET-RETURN-2026-10-16/snapshot_check.py EVIDENCE core --out core-snapshots.json
```

Repeat snapshot_check for promote,dup,respool-decline. Use replay.py --links-only
to regenerate second-cut-links.json without repeating full image hashing. Replay imports only our
published model; snapshot checks import the named original verifier raw parsers.
P1–P7 binding proof summaries are retained in the authenticated packet, not promoted
to independent proof execution here. Original model selftest/audit passes. Raw
Actions evidence needs durable hashed retention before its90-day expiry.
All frozen/physical/WP14/WP16/WP15/write/async/recording/firmware/media holds survive.
