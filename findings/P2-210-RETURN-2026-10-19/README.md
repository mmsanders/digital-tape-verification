# Exact743f829 narrow return disposition — 19 October 2026

**Bounded PASS** for the actual source/PCM observations, seven pilot host faults,
and five fresh per-command rows. This is not overall443, native, physical or
arbitrary-subset acceptance. Verification210 remains OPEN for the separately
published bounded next-stage plan and its pre-routed actual return.

Product head `743f82939a8fc99e64b384db45430824b68482d1`, PR471, Software467.
Engine `d96b4245e04d74078f8938744b1394c3018516f7` and independent model
`c6cb573d654d337fef2f616f11cce0cee74e8968` carry unchanged. Imported narrow
package tree `52837b6adc2bf6f3c7a99f1ee4eccf9526526155` matches the publication.
Software run39272699754/job118128898836 succeeded; original returned ZIP
12195144813 (3426393 bytes) has SHA256
`fab32f07de942096becfc8ad2101cbfa131e6b20d914245426933c4bdacd4d3a`.
INPUTS.json authenticates it and four retained load archives, preserved byte-for-byte.
REVIEW.json records every independently reconstructed result.

## Independent qualification and bounds

The unchanged narrow replay passes14 rows (two selected destination PCM bindings,
seven faults, five command projections). The two destination images represent81
retained contexts; no original campaign was rerun. Both100-frame destination A/B
outputs equal actual source A PCM; source B remains the discriminator. Independent
raw/label/PCM predicates carry from the published package.

Seven actual source shapes have a NULL source-write callback, TAPE_OK,13 reads,
zero non-read source events, complete38-event logs below8192 capacity, and identical
before/after source bytes. The actual non-NULL mutant has no source write either;
the independent binding predicate rejects its non-NULL capability. No invented
source-write event is used as a negative control. The audit covered only test
adapters, transport and host fault seams; no uncovered engine/source/codec
implementation was inspected to author tests.

The test-only failed-write/flush seam invalidates a copied OS handle at the selected
ordinal and records the real failed OS call. Shipping logic is unchanged. Working
snapshots reconstructed independently from initial bytes and only successful raw
write payloads match all nine submitted images (seven pilots and two controls).
This describes actual working-image effects, not physical persistence.

| Fault | Calls / barriers | Resulting mounted state |
|---|---|---|
| W0 |1 /0|empty/empty; input unchanged|
| W7 |8 /0|empty/empty|
| W8 |9 /1|empty/empty|
| W352 |353 /51|new/new; NEEDS_REPAIR|
| F1 |16 /2|empty/empty|
| F26 |216 /27|empty/empty|
| F51 |353 /52|new/new|

All seven commands exit1 at the requested real failure. The complete control exits0,
353 writes/52 barriers; native-flush-error control exits1 at F0,8 writes/1 barrier.
Postfailure states satisfy the unchanged199 operation-specific load predicate.
The404 previously missing coordinates now have **7 executed,397 unexecuted,
0 proved unavailable**. No all-coordinate acceptance follows.

Each of five command rows starts each verify/dumpA/dumpB on a fresh pristine copy.
Verify binds NULL write, changes no bytes and exits1/NEEDS_REPAIR on the two repair
images. Each writable dump there performs exactly one512-byte primary-superblock
write at whole-device offset17825792 and a successful fsync. Independent full-byte
comparison proves it copies the exact original mirror and changes nothing else;
PCM remains the expected source audio. Other three command images stay unchanged.

The four retained shards were inventoried, not re-executed: all10 repair contexts
map to the same two submitted repair images. Five command selections came from
load0. The global four-shard first empty/empty image is instead
`0008cb2d55e007ffece5a69c7e87290d153d9ffec2a58f295544562836ff3c88`.
The existing empty neighbour remains valid. Its global-minimum neighbour is the
first fixed item in the new plan; do not claim that projection has a new actual
command observation already.

## Bounded next publication

`tests/wp10_subset_extension_r1` is a separate Stage3 plan/order-generator identity.
It fixes the global empty neighbour, next32 fault coordinates,24 residue/operation
pairs and three long-copy fixtures/six coordinates with finite extra order classes.
The other365 load faults remain explicitly deferred. Exact lanes, coordinates,
seeds, original operation predicates, capability stops and resource gates are in
PLAN.json and README.md. No case execution precedes main publication plus normal CI.
No existing accepted receipt or old package byte changes.

Current actual CI CPU is5.31s; earlierCI7.71s and local development approximately31s
are reported, not an independently measured cumulative ledger. Reported total is
approximately44.02s and new compressed raw approximately6.7MB. Reconcile actual
aggregate accounting and estimate before every next case under the unchanged
7200CPU-second/2GiB aggregate cap. Stop with precise partial/unexecuted map before
exceeding it; never silently remove difficult coverage to claim PASS.

## Reproduce and transport

Run from the repository root:

```sh
python3 -B findings/P2-210-RETURN-2026-10-19/review.py --artifacts /tmp/210-review --out /tmp/210-review/REVIEW.json --release https://github.com/mmsanders/digital-tape-verification/releases/download/evidence-210-return-2026-10-19-743f829
cmp /tmp/210-review/REVIEW.json findings/P2-210-RETURN-2026-10-19/REVIEW.json
python3 -B tests/wp10_subset_extension_r1/selftest.py
```

The release retains five original hash-bound ZIPs and REVIEW.json. The paired
`package-210-extension-<source-head>` release supplies compact deterministic ZIP,
per-file SHA256 provenance, source commit and git subtree. Exact identifiers are
returned directly on210/467 after normal CI and merge. No Product code is merged.
PM472/S3,208 Linux correction, closed209, Ready206/Michael447/A6 and all existing
physical/security/native/engine/format/timing holds remain unchanged.
