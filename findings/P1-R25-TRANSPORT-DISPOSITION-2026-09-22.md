# P1-R25 Verification return — transport/warm product evidence

Date: 22 September 2026  
Authority: independent Verification, issue #40  
Product implementation source/diff inspected: **no**

## Immutable identity / provenance

- Verification base for this return: `e9e6ec76f511099ae7e61e8167776bf430b87b8c`
- Original transport verifier publication: `5d97073ca03014e9d4055014f294709a78506b9e`
- Original verifier `tests/transport_draft8` tree: `05aafde29e3d8048bec669053b1bafcd0104cbd3`
- Product PR #171 base: `1db7135a587d02a76a4b5700bc31986f2fef1b20`
- Product PR #171 head: `dbd5a23291521cfe21da571fa97e14b806ace500`
- Product-imported `tests/transport_draft8` tree: `05aafde29e3d8048bec669053b1bafcd0104cbd3` — exact tree match
- Final-head workflow run: `35794299660`
- Transport job: `106969864466`
- Artifact: `p1-r25-transport-product-evidence`, ID `10723796203`
- Downloaded artifact ZIP SHA-256: `8226d421a6b6c2928f7107bfd01bd8a8233f3cfb331f6f88fdd46b16a02980ec` — exact match to GitHub artifact digest
- Extracted `observations.jsonl`: 29,395 bytes, SHA-256 `7fe8a9096ac57abd7ed62c22ace39b432de52801207f9ae396edf08ae57a7997` — exact match
- Verifier-owned replay CI: run `35795221347`, job `106972857735`, success

A compare of product base→head shows exactly five changed paths:
`.github/workflows/ci.yml`, `tests/transport_adapter/Makefile`,
`tests/transport_adapter/README.md`,
`tests/transport_adapter/run_product.py`, and
`tests/transport_adapter/wp_transport_probe.c`.
No `engine/` path and no verifier-owned package path changed.

## Adapter / runner mechanical-fidelity disposition

**No material observation defect found.**

Verification audited the Software-owned probe and runner because those bytes
define the observation boundary. The audit found:

- The probe enumerates exactly the verifier's 16 published case IDs in the same
  order.
- Set-side mount sides, transition targets, seek/rate values, armed mode, and
  all ten warm descriptor shapes match `oracle.make_cases()` / `ADAPTER.md`.
- The probe invokes only frozen public tape APIs; it does not inspect private
  engine state.
- Every block-device read/write/flush callback is appended with the currently
  active public-call phase.
- `tape_render` records `events_from_call` by direct callback-count delta.
- Event overflow sets `event_overflow=true`, forces adapter failure, and the
  runner independently rejects a non-false overflow flag.
- Call-trace saturation also forces adapter failure via the probe's
  `g_call_count >= MAX_CALLS` terminal check.
- The write and flush callbacks are observable and are not filtered. They
  return failure rather than silently mutating the verifier-owned VO08 image.
- The runner generates each input directly from `case.pre`, decodes the
  actual output, invokes unchanged `oracle.check`, and hashes the actual input
  and output bytes.
- The runner requires observation format, `adapter_kind=product`, list-shaped
  calls/events, and non-overflow before accepting a case.
- Evidence JSONL retains the raw product observation for every case.
- The runner's stored `errors` field is **not** treated as independent
  Verification authority.

The warm mount record's descriptor fields are copied from the exact local
descriptor that is passed to the public `tape_mount` call. Its
`warm_start_used` field is populated from the subsequent public
`tape_get_info` result (the API's observable source for that state) and the
separate info call is retained as well. This does not synthesize an expected
verdict.

The published oracle prohibits write callbacks and byte changes. The exact
product trace also contains **zero flush callbacks**; this stronger observed
fact is recorded below but no new verifier criterion was invented.

## Verifier-owned retention / replay

Verification retained the exact artifact JSONL losslessly under:

`tests/transport_draft8/evidence/p1-r25-product/observations.jsonl.zlib.b64`

The text is a zlib-compressed/base64 encoding of the exact downloaded JSONL.
The decompressed bytes are authenticated against the authoritative JSONL
SHA-256 before replay.

`tests/transport_draft8/replay_product_evidence.py`:

1. authenticates the retained compressed bytes and exact JSONL SHA-256;
2. requires exactly the 16 verifier case IDs in published order;
3. ignores Software's stored verdict/error list;
4. regenerates every verifier fixture from the unchanged package;
5. requires each retained input hash to equal the verifier fixture;
6. requires each retained output hash to equal that same verifier fixture,
   which is valid because every published transport/warm case requires
   byte-identical final media;
7. authenticates `adapter_kind=product`, observation format, and no event
   overflow;
8. reapplies the unchanged `oracle.check` to the raw product calls/events.

Repository CI independently reports:

- `observed_write_callbacks=0`
- `observed_flush_callbacks=0`
- **16/16 independently replayed cases PASS**

## Exact case-by-case disposition

| Case | Verification disposition |
|---|---|
| SS-PLAYING-A-TO-B | PASS |
| SS-IDLE-A-TO-B | PASS |
| SS-SAME-A | PASS |
| SS-DEGRADED-B | PASS |
| SS-DEGRADED-SAME-A | PASS |
| SS-ARMED-BUSY | PASS |
| WARM-NULL | PASS |
| WARM-DATA-NULL | PASS |
| WARM-ZERO-FRAMES | PASS |
| WARM-SHORT-BUF | PASS |
| WARM-PAST-END | PASS |
| WARM-U32-OVERFLOW | PASS |
| WARM-RESUME-OUT | PASS |
| WARM-UUID | PASS |
| WARM-SIDE | PASS |
| WARM-VALID-METADATA | PASS |

The positive warm row proves the published metadata acceptance path reaches
`warm_start_used=true`; the negative rows independently preserve their exact
descriptor shapes and cold-mount behavior.

## PM routing disposition

**Yes.** The exact final-head evidence is complete and trustworthy enough for PM
to route Digital-Tape PR #171 onward for the published 16-row transport/warm
tranche. Verification requests **no product behavior change**.

This is not authority to merge #171 and is not full WP-08/package acceptance.

## Explicit exclusions

This disposition preserves the published exclusions:

- byte-exact or listened warm-buffer sample identity (WP-11);
- broader playback/rate goldens;
- crash injection;
- long-operation continuation/state behavior;
- promote behavior;
- respool behavior;
- format behavior;
- dup behavior.

## Stop condition

No blocker remains in issue #40's assigned scope. PR #41 publishes the retained
evidence/replay and this immutable return. Issue #40 may close as completed.
Closure is not product merge or full WP-08/package acceptance.
