# P1-R25 Verification return — NOT_MOUNTED state-sweep evidence

Date: 23 September 2026  
Authority: independent Verification, issue #50  
Product implementation source/diff inspected: **no**

## Disposition

**PASS for the published 34-case WP-06h NOT_MOUNTED state sweep.**

Exact Digital-Tape PR #190 head
`242f6d8f9de67dcca50f0f973a09988607429662` may proceed to PM routing for
this narrow tranche with **no product behavior change requested**.

This is not merge authority or complete WP-06/source/golden acceptance.

## Immutable identities

- product base: `e3c90e09dae7b4210d03daaf1cd3d125a219479e`
- product head: `242f6d8f9de67dcca50f0f973a09988607429662`
- candidate tree: `9a237c8c533712c246ad52b33c2b6b3fb465b334`
- verifier publication: `2f0fe952244bf40b4658f6a94904470349871c17`
- verifier/product `tests/notmounted_draft8` tree:
  `f5ea4a64044cb5741565a36249f15756b2524015`
- verifier/product `wp06h_probe.c` blob:
  `eca8c29a1aa2b5a8e15343b8b6a95ca5ffd6ba20`

Product PR #190 changes only:
- `.github/workflows/ci.yml`
- `tests/notmounted_adapter/Makefile`
- `tests/notmounted_adapter/README.md`
- `tests/notmounted_adapter/run_product.py`

No engine path and no verifier-owned package path changes.

## Exact product evidence

- Actions run/job: `35872842489` / `107221086394`
- artifact: `p1-r25-notmounted-product-evidence`
- artifact ID: `10755609092`
- downloaded ZIP SHA-256:
  `584fa4f5404e29064e57716b26381efd5a2db20a8f67bd8b3c7174a11f6e2cbc`
- `observations.jsonl` SHA-256:
  `0ef1617d2cff64321269d3c1eb728aefa99512974b51ab4642bce70d77ee88d8`
- linked product probe SHA-256:
  `4a515f1c60e743ad98cd8cb0f25c48befa63839db4dbf605a5110b712fcc9d3a`

The downloaded artifact contains exactly the expected provenance row plus 34
case rows.

## Mechanical binding audit

The Software Makefile compiles exactly
`tests/notmounted_draft8/wp06h_probe.c` as the probe source and links it to
the real product library. The product and verifier repositories contain the
same probe blob.

The Software wrapper:
- authenticates the imported verifier subtree against
  `f5ea4a64044cb5741565a36249f15756b2524015`;
- invokes the unchanged verifier-owned `runner.py`;
- retains the complete verifier JSONL;
- hashes the linked executable and observations;
- does not translate expected results or synthesize verdict observations.

## Probe semantics audited

Each case runs in a fresh process and therefore cannot inherit prior probe state.

For BEFORE cases the call shape is exactly:
1. `tape_init`;
2. one isolated ordinary API probe.

For AFTER cases the call shape is exactly:
1. `tape_init`;
2. successful `tape_mount(..., Side A, ...)`;
3. successful `tape_unmount`;
4. one isolated ordinary API probe.

The 17 ordinary APIs are exactly:

- `tape_seek`
- `tape_set_rate`
- `tape_render`
- `tape_service`
- `tape_status`
- `tape_get_info`
- `tape_tell`
- `tape_arm`
- `tape_feed`
- `tape_commit`
- `tape_abort`
- `tape_set_side`
- `tape_reset_side_b`
- `tape_promote`
- `tape_respool`
- `tape_dup`
- `tape_unmount`

### Distinct valid duplicate destination

The verifier-owned probe allocates independent source and destination
`device_t` objects. It initializes a separate `dst_dev` with:
- its own `ctx = dst`;
- the same valid block count as the fixture source;
- non-NULL read/write/flush callbacks.

The probed `tape_dup` therefore exercises the **unmounted source** refusal
against a distinct, otherwise valid raw destination. It is not accidentally
testing destination alias, read-only or geometry refusal.

Both DUP evidence rows report:
- `TAPE_ERR_NOT_MOUNTED`;
- zero source callbacks/writes;
- zero destination callbacks/writes.

### tape_tell sentinel

The verifier-owned probe initializes the caller-owned output to:

`0x1111111111111111`

immediately before calling `tape_tell`, and records the actual value
immediately afterward.

Both TELL rows retain:
- `out_frame_before = 0x1111111111111111`;
- `out_frame_after = 0x1111111111111111`;
- `TAPE_ERR_NOT_MOUNTED`.

The sentinel evidence is observed, not synthesized by the Software wrapper.

## Independent replay of raw observations

Verification ignored Software's retained `status=PASS` and `errors=[]`
fields and independently applied the unchanged WP-06h semantics to all 34 raw
stdout observations.

Checks independently confirmed:
- exactly 34 cases;
- exact verifier case order;
- exact 17-operation set in BEFORE and AFTER phases;
- one successful init in every row;
- no mount/unmount setup calls in BEFORE rows;
- successful Side-A mount then successful unmount in every AFTER row;
- exactly one isolated probe call;
- every probe result is `TAPE_ERR_NOT_MOUNTED`;
- both TELL sentinels remain unchanged;
- fixture and output hashes are identical in every retained row.

### Exact case disposition

| Case | Disposition |
|---|---|
| NM-BEFORE-SEEK | PASS |
| NM-BEFORE-SET-RATE | PASS |
| NM-BEFORE-RENDER | PASS |
| NM-BEFORE-SERVICE | PASS |
| NM-BEFORE-STATUS | PASS |
| NM-BEFORE-INFO | PASS |
| NM-BEFORE-TELL | PASS |
| NM-BEFORE-ARM | PASS |
| NM-BEFORE-FEED | PASS |
| NM-BEFORE-COMMIT | PASS |
| NM-BEFORE-ABORT | PASS |
| NM-BEFORE-SET-SIDE | PASS |
| NM-BEFORE-RESET-B | PASS |
| NM-BEFORE-PROMOTE | PASS |
| NM-BEFORE-RESPOOL | PASS |
| NM-BEFORE-DUP | PASS |
| NM-BEFORE-UNMOUNT | PASS |
| NM-AFTER-SEEK | PASS |
| NM-AFTER-SET-RATE | PASS |
| NM-AFTER-RENDER | PASS |
| NM-AFTER-SERVICE | PASS |
| NM-AFTER-STATUS | PASS |
| NM-AFTER-INFO | PASS |
| NM-AFTER-TELL | PASS |
| NM-AFTER-ARM | PASS |
| NM-AFTER-FEED | PASS |
| NM-AFTER-COMMIT | PASS |
| NM-AFTER-ABORT | PASS |
| NM-AFTER-SET-SIDE | PASS |
| NM-AFTER-RESET-B | PASS |
| NM-AFTER-PROMOTE | PASS |
| NM-AFTER-RESPOOL | PASS |
| NM-AFTER-DUP | PASS |
| NM-AFTER-UNMOUNT | PASS |

**Result: 34/34 PASS.**

## Routing

PM may route exact product PR #190 onward for this published WP-06h tranche.
Verification requests no product behavior change.

## Explicit exclusions

Still excluded:
- `tape_init`;
- `tape_mount`;
- `tape_format`;
- destination-side `tape_dup`;
- crash/continuation behavior;
- complete WP-06/source/golden acceptance.

Issue #50 may close as completed.
