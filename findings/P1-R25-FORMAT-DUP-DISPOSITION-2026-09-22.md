# P1-R25 Verification return — format/dup refusal evidence

Date: 22 September 2026  
Authority: independent Verification, issue #47  
Product implementation source/diff inspected: **no**

## Disposition

**PASS for the published 17-case format/dup/empty-promote refusal tranche.**

Exact Digital-Tape PR #185 head
`88bd04d2388520150c2e81d0f9f15c1551ae3751` may proceed to PM routing for
this narrow tranche with **no product behavior change requested**.

This does **not** accept the deliberate post-precondition `TAPE_ERR_BUSY`
coverage hold as normative format/dup success behavior. Destructive success
construction remains untested and excluded.

## Immutable identities

- product base: `5f030877b31e73408c99bb47f381f7bc3de0abdb`
- product head: `88bd04d2388520150c2e81d0f9f15c1551ae3751`
- candidate tree: `b5a7a279a78a3411c370cd29ab9a0eb52c21f56a`
- verifier publication: `982bac2cfb63ca3037d59be3887b2d66de065a34`
- verifier/product `tests/format_dup_draft8` tree:
  `83a6d03942d59ecbf6d0c2d0ad646c92d2da0459`
- exact-head adapter source Git blob:
  `418df1519a8d6624620cb815d19732c0282fa1fa`
- independently recomputed adapter source SHA-256:
  `984f77eb5b1e74564a3570bcfd26e4243b7f9abdd892c1b640b0adcf6b17d8a2`

The adapter SHA-256 exactly matches the retained evidence manifest.

## Exact product evidence

- Actions run/job: `35825358142` / `107065764327`
- artifact: `p1-r25-format-dup-product-evidence`
- artifact ID: `10735046993`
- downloaded artifact ZIP SHA-256:
  `891ff8080634ab15537233d25e09d04811d7f23e558da868d362d548532fe5a4`
- `manifest.json` SHA-256:
  `d6bceb366a6ac344ee4f8d13f8b1a69fc871b8e872229c30975e07f785494032`
- `result.json` SHA-256:
  `b112f1c5ed5dee054e150122f922613f1b03ad906d2803aa7e3d68c046a42ff1`
- unchanged oracle SHA-256:
  `deb5ecc2edbad5452913802db1852c18173127010c13b55a8911fa74809fa80a`
- deterministic observation-set SHA-256:
  `fcca89e4a9b19618041b49932ace227d4b068b00fbfb80253b97c7c68f4af6ac`

Verification independently reproduced the observation-set digest from the
downloaded artifact over the sorted `CASE_ID:SHA256(observation.json)\n`
records.

## Adapter / runner mechanical-fidelity audit

No material observation defect was found.

The Software adapter preserves the verifier's case configuration and precedence
boundary:

- format rows call the raw `tape_format` once with the verifier-defined
  writability, advertised block count and nominal length;
- duplicate rows mount the source on Side A, use the verifier-defined raw
  destination device, then call `tape_dup` once with positive budget;
- `DUP-ALIAS` and `DUP-ORDER-ALIAS` actually use the same backing/device
  context for source and destination;
- alias rows make the source writable so item 1 alias refusal, rather than
  destination read-only, can win;
- ordering rows retain their combined alias/read-only/geometry conditions;
- `PROMOTE-EMPTY` mounts Side B and calls `tape_promote` once with a
  positive budget.

Callback capture is complete for the operation-under-test boundary:

- source and destination callbacks feed one global chronological event array;
- events retain phase, device, operation, LBA and count;
- reads and writes are recorded **before** zero-count/out-of-range refusal;
- flushes are retained;
- callback overflow forces adapter failure;
- mount/unmount callback traffic is deliberately excluded exactly as the
  published adapter contract specifies.

The exact-head regression self-check constructs rejected out-of-range read and
write callbacks and requires both to remain in the trace. CI reports:

`PASS rejected format/dup callbacks remain observable`

The Software wrapper authenticates the imported verifier tree and delegates
fixture generation, execution and verdicting to the unchanged verifier
`runner.py`. It does not rewrite the case expectations.

## Independent artifact replay

The exact downloaded artifact contains:

- the unchanged verifier package;
- per-case input and output VO08;
- raw stdout and parsed observations;
- adapter exit records;
- hash-bound manifest and result.

Verification executed the bundled unchanged offline replay against those exact
bytes with Python bytecode generation disabled to avoid the previously
documented verifier-tool `__pycache__` self-contamination.

Result:

`REPLAY PASS /mnt/data/fmtdup47`

No verifier oracle or evidence byte was altered.

All 17 retained observations happen to have zero operation callbacks and zero
writes. This is stronger than required for several rows, but Verification does
**not** promote that observation into a new acceptance rule. Only the published
six `DEVICE_ADDRESSABLE` geometry rows normatively require an empty callback
trace; all refusal rows require zero writes and prohibit premature destination
superblock classification reads.

## Exact case disposition

| Case | Verification disposition |
|---|---|
| FMT-RO | PASS — `TAPE_ERR_READ_ONLY` |
| FMT-GEOM-0 | PASS — `TAPE_ERR_GEOMETRY`, required zero callbacks |
| FMT-GEOM-1 | PASS — `TAPE_ERR_GEOMETRY`, required zero callbacks |
| FMT-GEOM-BASE | PASS — `TAPE_ERR_GEOMETRY`, required zero callbacks |
| FMT-GEOM-FIT | PASS — `TAPE_ERR_GEOMETRY` |
| FMT-ORDER-RO | PASS — read-only precedence |
| DUP-ALIAS | PASS — `TAPE_ERR_INVALID_ARG`, `more_work=false` |
| DUP-RO | PASS — `TAPE_ERR_READ_ONLY`, `more_work=false` |
| DUP-GEOM-0 | PASS — `TAPE_ERR_GEOMETRY`, required zero callbacks |
| DUP-GEOM-1 | PASS — `TAPE_ERR_GEOMETRY`, required zero callbacks |
| DUP-GEOM-BASE | PASS — `TAPE_ERR_GEOMETRY`, required zero callbacks |
| DUP-GEOM-FIT | PASS — `TAPE_ERR_GEOMETRY` |
| DUP-TOO-SMALL | PASS — `TAPE_ERR_DEST_TOO_SMALL` |
| DUP-ORDER-ALIAS | PASS — alias precedence |
| DUP-ORDER-RO | PASS — read-only precedence |
| DUP-ORDER-GEOM | PASS — geometry precedence |
| PROMOTE-EMPTY | PASS — `TAPE_ERR_INVALID_ARG`, `more_work=false` |

**Result: 17/17 PASS.**

Every tracked OUTPUT.vo08 is byte-identical to its corresponding verifier input,
as required by the zero-write refusal package.

## BUSY coverage hold

The partial product implementation intentionally returns `TAPE_ERR_BUSY`
after all currently covered destructive raw-operation preconditions pass rather
than beginning unverified destructive format/dup work.

That behavior is **outside this 17-case verifier package**. This disposition
neither approves nor rejects it as the eventual normative success-path
behavior. It remains a product-development hold.

## Routing

PM may route exact Digital-Tape PR #185 onward for the published refusal /
precedence tranche. Verification requests no product behavior change for these
17 cases.

Do not infer acceptance of destructive format/dup success behavior.

## Explicit exclusions

Still excluded:

- destructive format/dup cartridge construction;
- raw destination-superblock success classification;
- UUID / epoch / label identity commits;
- duplicate audio-copy success;
- crash/interruption closure;
- generation fallback success;
- destination remount success classification;
- continuation / argument-stability / re-entry / progress behavior;
- complete package/source/golden acceptance.

Issue #47 may close as completed.
