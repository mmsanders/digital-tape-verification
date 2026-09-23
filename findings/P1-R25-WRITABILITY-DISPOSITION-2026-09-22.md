# P1-R25 Verification return — writability product evidence

Date: 22 September 2026
Authority: independent Verification, issue #46
Product implementation source/diff inspected: **no**

## Disposition

**PASS for the published eight-case WP-06a writability tranche.**

Exact Digital-Tape PR #184 head
`87e84702df5f717a4ac14a65ea69455b637721b7` may proceed to PM routing for
this narrow tranche with **no product behavior change requested**.

This is not merge authority or complete WP-06/source/golden acceptance.

## Immutable identities

- product base: `5f030877b31e73408c99bb47f381f7bc3de0abdb`
- product head: `87e84702df5f717a4ac14a65ea69455b637721b7`
- candidate tree: `37a43cd3368334f184ef03287614df71cb94ea51`
- verifier publication: `d875730ee5cedc6b88e40fcfe30aa4d81918f549`
- verifier/product `tests/writability_draft8` tree:
  `786221daaf80d15406d9cccf19691c2337ff5908`
- verifier/product `wp06a_probe.c` blob:
  `93af890d7829c785d528f18abf8a9aa0c46e16dc`

PR #184 changes only CI and Software-owned writability binding files. No engine
or verifier-owned package path changes.

## Exact product evidence

- Actions run/job: `35825346042` / `107065729158`
- artifact: `p1-r25-writability-product-evidence`
- artifact ID: `10734823509`
- downloaded ZIP SHA-256:
  `5159c76c2154508a00e489e4f14f211806cf725dd5e7f9bf2a03b7fd856970ae`
- `observations.jsonl` SHA-256:
  `3a5413f50245f12ebed80322d18a43b0d2b0f14e2b60d6cb41da3036de117b35`
- linked product probe SHA-256:
  `c7316e7aa20d50900c27dff14309bcc401b4d86374f03ed75908a4b438ac584d`

All hashes were independently reproduced from the downloaded artifact where
applicable.

## Mechanical binding audit

The product Makefile compiles **exactly**
`tests/writability_draft8/wp06a_probe.c` as its sole probe source, with only
the public-header macro and engine include/library linkage supplied by Software.

The source blob in the product tree is byte-identical to the verifier-owned
source blob. The Software wrapper verifies the imported verifier subtree before
execution and invokes the unchanged verifier-owned `runner.py`; it does not
translate expected observations.

The verifier-owned probe:
- supplies a non-NULL device write callback;
- records every read/write/flush callback before returning;
- mutates its retained VO08 media image only through successful
  `write_cb` calls;
- serializes that same image to OUTPUT.vo08 after the public calls.

Therefore, in this package, a raw observation with zero write callbacks also
proves that the output VO08 media remained byte-identical to the input image.
The unchanged verifier runner independently checked that byte identity during
the exact-head execution.

## Independent raw-observation replay

Verification ignored each Software-saved `errors=[]` / `status=PASS` field
and re-applied the published observation semantics directly to the raw stdout
JSON.

Across all eight rows:
- `adapter_kind=product`;
- `device_write_nonnull=true`;
- `event_overflow=false`;
- exactly one successful init, mount, info and unmount;
- `tape_info.writable=false`;
- `version_minor=1`;
- zero `write` callback events;
- no unexpected flush activity was observed.

Exact dispositions:

| Case | Disposition |
|---|---|
| W06A-ARM | PASS — `TAPE_ERR_READ_ONLY` |
| W06A-RESET-B | PASS — `TAPE_ERR_READ_ONLY` |
| W06A-PROMOTE | PASS — `TAPE_ERR_READ_ONLY` |
| W06A-RESPOOL | PASS — `TAPE_ERR_READ_ONLY` |
| W06A-FEED | PASS — `TAPE_ERR_BUSY` |
| W06A-COMMIT | PASS — `TAPE_ERR_BUSY` |
| W06A-REPAIR-INVALID | PASS — mount succeeds, `needs_repair=true`, zero writes |
| W06A-REPAIR-STALE | PASS — mount succeeds, `needs_repair=true`, zero writes |

**Result: 8/8 PASS.**

The two repair rows demonstrate repair suppression on effectively read-only v1.1
media: the repair need remains publicly visible and no repair write occurs.

## Routing

PM may route exact product PR #184 onward for this published WP-06a tranche.
Verification requests no product behavior change.

## Explicit exclusions

Still excluded:
- WP-36 NULL-source behavior;
- raw `tape_format` / `tape_dup` behavior;
- crash/continuation behavior;
- broader WP-06/source/golden acceptance.

Issue #46 may close as completed.
