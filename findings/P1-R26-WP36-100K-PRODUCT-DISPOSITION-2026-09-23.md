# P1-R26 Verification return — exact WP-36 100,000-sequence product evidence

Date: 23 September 2026  
Authority: independent Verification, issue #56

## Disposition

**PASS — frozen WP-36 acceptance criterion satisfied.**

Exact Digital-Tape PR #200 head
`1ce0c4c92196b0b44e83ba7a975995531e12fd7c` may proceed unchanged to PM
routing. Verification requests **no product behavior change and no new product
run** for WP-36.

This finding does not merge product PR #200.

Together with the previously accepted deterministic five-case source-slot
precursor, this exact 100,000-sequence real-product run completes the published
WP-36 package acceptance. Verification identifies **no remaining WP-36
criterion** in the frozen acceptance target.

## Exact candidate / Structural Rule 1

- product base:
  `482eb864036d6221fda2936429addd3189254aa5`
- verifier-import commit 1:
  `c9c8a107a365ffefe5be2d87fad292b09a879723`
- product-binding commit/head 2:
  `1ce0c4c92196b0b44e83ba7a975995531e12fd7c`
- final product tree:
  `0bb82c263b3d92bc040f9d4437be124479ec7aa2`

Independent commit-delta inspection confirms:

1. base → commit 1 changes only `tests/IMPORTS.json` plus the eight files under
   `tests/wp36_fuzz_draft8/`;
2. commit 1 → commit 2 changes only:
   - `.github/workflows/ci.yml`
   - `tests/wp36_fuzz_adapter/Makefile`
   - `tests/wp36_fuzz_adapter/README.md`
   - `tests/wp36_fuzz_adapter/run_product.py`
   - `tests/wp36_fuzz_adapter/wp36_fuzz_product_adapter.c`;
3. neither commit changes any `engine/` path.

Structural Rule 1 is therefore satisfied mechanically.

## Verifier identity

Published verifier package:

- Verification PR #55 merge:
  `9aea515b67a1cbcfe3c09176a37eb5519c8cd391`
- package publication:
  `c65df73abaf2624e99ac3c06b8c864a445d81ec2`
- immutable package tree:
  `9ac9c43962b49c98f7007983921be9500a51cb5a`

The imported product subtree at `tests/wp36_fuzz_draft8` has exactly the same
tree SHA and all eight file blobs match the publication byte-for-byte.

## Product-adapter contract audit

No material adapter defect was found.

The exact product adapter source SHA-256 independently recomputes to:

`f1a81fc35911f5c70d056a0ffbc152b78f882a7aac9c134ac947d5c13b5805a9`

matching retained provenance.

The adapter satisfies the published `ADAPTER.md` boundary:

- the mounted source device has literal `dev.write = NULL`;
- there is no non-NULL swallowing/counting/rejecting source-write wrapper;
- the adapter compilation fails if `NDEBUG` is defined;
- its Makefile includes `-UNDEBUG`;
- the verifier fixture is loaded once and is exposed read-only;
- each streamed sequence starts a fresh engine instance and fresh play/record
  rings;
- every verifier operation token is parsed and executed in received order;
- operation arguments are not regenerated or rewritten;
- the reported operation count must equal the received count;
- callback-counter overflow is surfaced and rejected by the verifier;
- malformed lines, setup failures, protocol EOF and nonzero adapter exits fail
  closed;
- `DONE` is required for normal process completion.

The unchanged verifier runner independently enforces:

- product handshake;
- source binding exactly `NULL`;
- assertion mode exactly `debug`;
- sequence index and per-sequence seed identity;
- complete operation execution;
- no counter overflow;
- successful mount/unmount for every sequence;
- only `TAPE_OK` and `TAPE_ERR_UNDERRUN` operation results;
- result-count sum equal to the generated operation count;
- timeout/EOF/malformed/process-failure rejection.

## Active debug `dev_write` assertion

The exact CI job performs:

`make -C engine clean`

followed by:

`make -C engine all CFLAGS=-UNDEBUG`

The Actions log shows the actual engine compiler commands containing
`-UNDEBUG`. The product adapter is likewise compiled with `-UNDEBUG`.

A narrow instrumentation audit of the exact frozen `engine/src/dev.h` helper
confirms that, when `NDEBUG` is absent, `dev_write` executes:

`TAPE_TRAP_IF(d->write == NULL)`

where `TAPE_TRAP_IF` expands to `__builtin_trap()`.

Thus any attempted internal source `dev_write` during this run would terminate
the real product process before a source write callback could occur. The
unchanged verifier runner treats that process death / assertion / premature EOF
as failure.

This makes normal completion of all 100,000 sequences a direct observation
that the frozen debug assertion **never fired** and no forbidden source
`dev_write` path was reached.

The verifier package's own negative controls also demonstrate fail-closed
behavior for:
- assertion/crash;
- non-NULL source binding;
- fewer than 100,000 sequences;
- malformed/missing provenance.

## Exact authenticated Actions run

- Actions run: `35921840634`
- job: `107387445081`
- job conclusion: **success**
- linked debug adapter SHA-256:
  `9c7edd910f7d3274f1f8cdb5b327cf0bb218684c0a6a6295f0c55dc40975d2a5`
- verifier runner exit: `0`
- product tree printed by evidence wrapper:
  `0bb82c263b3d92bc040f9d4437be124479ec7aa2`
- provenance validation: **PASS**

Exact-head verifier self-tests report:

- deterministic 100000-sequence generator: PASS;
- sequence reproducer determinism: PASS;
- streaming protocol smoke: PASS;
- assertion/crash negative control: PASS;
- non-NULL source-binding negative control: PASS;
- fewer-than-100000 negative control: PASS;
- malformed provenance negative control: PASS;
- summary source-binding negative control: PASS.

## Retained artifact authentication

Artifact:

- name: `p1-r26-wp36-100k-product-evidence`
- ID: `10777367138`
- ZIP SHA-256:
  `8260bc149fdf93c28130b70bb7b92f18b85d3ca04b8cbdead671a880ed0de4e3`

Verification independently downloaded the artifact and reproduced:

- `summary.json` SHA-256:
  `c8d5836b960bf1ba0f2c331f4dcea3901bb0c8062185c2f13ea44295955afa8a`
- `PROVENANCE.md` SHA-256:
  `e4d4b8ed5c5fbd47e0d280fbac38e2bcdf90fd54a0e123d67da12c749baca953`
- `adapter.stderr.txt` SHA-256:
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

`adapter.stderr.txt` is exactly zero bytes. No failure reproducer is present,
consistent with a normally completed run.

## Independent generator / census reproduction

Verification independently reimplemented the exact published generator from its
fixed constants and SplitMix64-v1 algorithm rather than trusting the saved
summary.

Reproduction result:

- RNG: `splitmix64-v1`
- master seed: `5730365a5eed2026`
- sequence count: **100,000**
- canonical plan SHA-256:
  `6a6637336eff798e6c7824af76e3d4f227eefcd9ff35e7850a14fd14a1d22bae`
- generated operations: **1,997,914**
- independently regenerated coverage census: **byte-for-value identical to
  retained `summary.json` census**

The eight exact operation counts reproduce as:

| Operation | Count |
|---|---:|
| seek | 249,810 |
| tell | 250,411 |
| set_rate | 249,690 |
| render | 249,525 |
| service | 248,859 |
| status | 249,711 |
| info | 250,140 |
| set_side | 249,768 |

Coverage also independently reproduces:

- mount Side A: 49,965;
- mount Side B: 50,035;
- stopped-state exposures: 875,044;
- forward-playing exposures: 562,886;
- reverse-playing exposures: 559,984;
- exact-end seeks: 31,629;
- beyond-end seeks: 85,619;
- INT32_MAX rates: 31,257;
- INT32_MIN rates: 31,317;
- same-side `set_side`: 124,596;
- cross-side flips: 125,172.

Thus the campaign genuinely exercises both mount sides, stopped/forward/reverse
transport, all eight public transport/state operations, same-side and cross-side
transitions, boundary/beyond-end seeks, and signed rate extremes.

## Exact product disposition

The retained real-product summary reports:

- completed sequences: **100,000**
- normal exit: **true**
- assertion/crash: **false**
- handshake: `product / NULL / debug`
- read callbacks: **1,374,848**
- flush callbacks: **0**
- `TAPE_OK`: **1,919,142**
- `TAPE_ERR_UNDERRUN`: **78,772**

The two accepted result counts sum to:

**1,919,142 + 78,772 = 1,997,914**

which exactly equals the independently regenerated operation count.

Because the verifier rejects any OTHER result, incomplete sequence, failed
mount/unmount, process death, assertion, malformed protocol or premature EOF,
the complete accepted result is:

**100,000 / 100,000 sequences PASS; 1,997,914 / 1,997,914 generated operations
executed; zero observed assertion/crash.**

## WP-36 acceptance conclusion

The frozen acceptance criterion is:

> 100,000 random transport input sequences against a source-slot device with
> `write == NULL`; zero forbidden source `dev_write` reachability; debug
> assertion never fires.

This exact evidence satisfies each part:

1. the verifier-owned reproducible generator produced exactly 100,000 random
   transport sequences;
2. the exact real-product adapter used literal source `write = NULL`;
3. the frozen debug `dev_write` trap was active in the clean-linked engine;
4. all 100,000 sequences and 1,997,914 operations completed normally;
5. no assertion/crash occurred.

The already-accepted deterministic five-case precursor remains valid
supplemental source-slot coverage and need not be re-accepted here.

**Complete WP-36 package acceptance: PASS.**

Verification identifies **no still-missing WP-36 acceptance criterion**.

## Routing

PM may route exact Digital-Tape PR #200 at
`1ce0c4c92196b0b44e83ba7a975995531e12fd7c` onward unchanged.

Verification requests:
- no product behavior change;
- no repeat product run for WP-36.

## Explicit exclusions

This WP-36 acceptance does not imply acceptance of unrelated work packages,
including:
- WP-11 golden/listening acceptance;
- WP-10 crash/durability acceptance;
- WP-07 random edit / allocator fuzz;
- WP-12a continuation/re-entry/FAULTED behavior;
- other package/source acceptance outside WP-36.

Issue #56 may close as completed.
