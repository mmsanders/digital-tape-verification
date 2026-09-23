# P1-R25 Verification return — corrected promote + respool evidence

Date: 22 September 2026  
Authority: independent Verification, issue #44  
Product implementation source/diff inspected: **no**

## Disposition

**PASS for the published narrow promote and respool evidence tranches.**

The prior Verification #42 blocker is closed at exact product head
`262db463680798c63fde8b18232e60bdbda15f0a`.

Independent results:

- corrected promote: **16/16 PASS**;
- common-head respool: **8/8 PASS**;
- no remaining adapter observation blocker was found;
- Verification requests **no additional product behavior change** before PM
  routing of Digital-Tape PR #180.

This is narrow evidence disposition only. It is not product merge authority and
not full package/source/golden acceptance.

## Exact candidate / immutability

- Product PR: `Digital-Tape#180`
- Exact head: `262db463680798c63fde8b18232e60bdbda15f0a`
- Candidate tree: `d1fabb1147758a7384e79dcc779f6c3d3a889e8a`
- Pre-repair #180 head: `214cc02bc973fecf5188427552f55e57ae82e2ef`

Independent compare of pre-repair → corrected head shows only:

- `.github/workflows/ci.yml`
- `tests/promote_adapter/wp_promote_probe.c`

changed. No engine bytes changed in that repair.

At exact corrected head, Git tree metadata independently confirms:

- `engine/src/promote.c` blob:
  `875973114eaa6cf909fad5db4797a1d0988688f3`
- `engine/src/respool.c` blob:
  `c30b65a7f9ecffabd4873959dd9dec8757b9d36b`
- `tests/promote_draft8` tree:
  `2b79e0b07016da3521917c5a276e36994ccccfa6`
- `tests/respool_draft8` tree:
  `caf607917240c5a96fd32f526ee8e2a4761ebb24`

Verifier publications remain:

- promote:
  `e5e06b06f1aa0755a3b0b15133f1ce680e17f7af`
- respool:
  `6519220f161254c0453a30858eb3e7073e2eb82b`

Verification did not open or inspect product engine implementation source or
implementation diffs. Adapter/runner inspection was limited to the
Software-owned observation boundary.

## Prior #42 blocker — independently closed

Verification #42 blocked the old promote evidence because the adapter returned
from rejected/out-of-range read/write callbacks before recording them.

At corrected #180, `mem_read` and `mem_write` now call
`trace_extent(...)` **before** the bounds check and before returning `-1`.
Therefore every invoked read/write callback is observable even when the device
rejects the requested range.

The new regression self-check is meaningful rather than ceremonial:

1. constructs a one-block traced device;
2. calls `mem_read(lba=1,count=1)`, which is out of range;
3. calls `mem_write(lba=1,count=1)`, also out of range;
4. requires both callbacks to return `-1`;
5. requires exactly two retained events;
6. requires event 0 to be the rejected read with exact LBA/count;
7. requires event 1 to be the rejected write with exact LBA/count;
8. fails on overflow or any missing/wrong event.

Exact-head CI job `107056879078` reports:

`PASS rejected read/write callbacks are retained before refusal`

Independent SHA-256 of the exact-head corrected adapter source is:

`2371430e4e4e40d8e7349cd38bdcf050749f1756e14cab378ae3b301b267eb7f`

which exactly matches the corrected promote evidence manifest.

The #42 complete-callback / do-not-filter blocker is therefore **closed**.

## Corrected promote evidence authentication

Authoritative exact-head evidence:

- workflow run: `35822408762`
- promote job: `107056879078`
- artifact: `p1-r25-promote-product-evidence`
- artifact ID: `10733633872`
- downloaded artifact ZIP SHA-256:
  `fc34a1c02e3aae0ad752a5df19a633605befcf0776b8c3ea8cea442f86763c6b`
- manifest SHA-256:
  `881fdaf684dd26742f126649976088f79fabba1f4457d37f0f7b52ff6f17cad6`
- `result.json` SHA-256:
  `0adac30b74b7de59d012b7a86afe3f87f22755d86a4cc794b8549f37a8f2eaa7`
- unchanged oracle SHA-256:
  `b9ef4b3098869e50d9ed8639578726c395c51cd8b419e877f2af58ada712c78f`
- adapter source SHA-256:
  `2371430e4e4e40d8e7349cd38bdcf050749f1756e14cab378ae3b301b267eb7f`

The artifact manifest binds product commit
`262db463680798c63fde8b18232e60bdbda15f0a` and verifier publication
`e5e06b06f1aa0755a3b0b15133f1ce680e17f7af`.

Verification independently reproduced the supplied deterministic
observation-set hash:

`83c8475b1f1a507a8118b06fd5b040fb09c4b9465c12a5826fb75eff4704023e`

from the downloaded artifact using sorted records encoded as:

`CASE_ID + NUL + SHA256(observation.json) + LF`.

The artifact contains the verifier package/spec bytes plus per-case input/output
VO08, raw stdout/observation, adapter exit and hash-bound manifest.

### Independent promote replay

Verification executed the artifact's bundled unchanged verifier replay against
the exact downloaded artifact. Because the previously documented verifier
replay tool creates `__pycache__` inside its own evidence tree under ordinary
Python startup, replay was executed with bytecode generation disabled
(`PYTHONDONTWRITEBYTECODE=1 python3 -B`) so the replay does not
self-contaminate the hash-bound tree.

Result:

`REPLAY PASS .`

No oracle or evidence bytes were altered.

### Promote case disposition

| Case | Verification disposition |
|---|---|
| PR-EMPTY | PASS |
| PR-EMPTY-HIGH-COUNTERS | PASS |
| PR-DEGRADED | PASS |
| PR-NOTHING | PASS |
| PR-NOTHING-HIGH-COUNTERS | PASS |
| PR-ADOPT-COMPLETE | PASS |
| PR-ADOPT-SEQ-EXHAUSTED | PASS |
| PR-ADOPT-GEN-EXHAUSTED | PASS |
| PR-ADOPT-DECLINE | PASS |
| PR-DECLINE-SEQ-EXHAUSTED | PASS |
| PR-DECLINE-GEN-EXHAUSTED | PASS |
| PR-ALLOC-COMPLETE | PASS |
| PR-ALLOC-SEQ-EXHAUSTED | PASS |
| PR-ALLOC-GEN-EXHAUSTED | PASS |
| PR-FULL | PASS |
| PR-FULL-HEADROOM-FIRST | PASS |

**Promote result: 16/16 PASS.**

## Respool adapter audit

Verification audited
`tests/respool_adapter/wp12_respool_probe.c` and its Software runner against
the published `respool_draft8` contract.

No material observation defect was found.

Key fidelity points:

- the Software runner obtains the case set/order from the unchanged verifier
  package rather than maintaining an independent expected-case list;
- all eight published cases are executed in verifier order;
- `WP12-DEGRADED` mounts Side A; the other cases mount Side B;
- `WP12-EMPTY` performs the required promote→respool asymmetry through public
  APIs;
- each semantic respool case uses exactly one
  `tape_respool(..., block_budget=65535, ...)` call;
- public results and `more_work` are retained rather than synthesized into an
  expected value;
- callbacks are recorded in order with phase/op/LBA/count/return code;
- rejected out-of-range read/write callbacks are recorded **before** returning
  `-1`;
- allocation failure inside a valid-range write is also retained as a rejected
  write callback;
- flushes are retained;
- event overflow sets `event_overflow=true` and forces adapter failure;
- the predetermined script has at most four public calls, well below the
  16-call storage bound;
- input and output VO08 hashes are retained;
- the runner invokes the unchanged verifier `check` over the actual decoded
  output and raw calls/events.

Software's stored `errors=[]` values were not used as independent
Verification authority.

Independent SHA-256 of the exact-head respool adapter source is:

`a5ac8d8fbdc0fa5a1e85ba7f8f26a0396b67fc469b72ede3f94de9283c22b904`.

## Respool evidence authentication

Authoritative exact-head evidence:

- workflow run: `35822408762`
- respool job: `107056879100`
- artifact: `p1-r25-respool-product-evidence`
- artifact ID: `10733568919`
- downloaded artifact ZIP SHA-256:
  `8cb54b51b66356e089be6c7a54f86006d0454c330458855f54c638e3c84f77e4`
- `observations.jsonl` SHA-256:
  `5db21452b759b2f113508d6731ae90ac99bcf80e5c8a223ae521009d1d30c81c`
- `PROVENANCE.md` SHA-256:
  `7d7b2d58e60c353be01ae9f7c4f38d3c43edcdda1ce442936be3819ef5b7ab10`

The provenance binds:

- product commit `262db463680798c63fde8b18232e60bdbda15f0a`;
- verifier tree `caf607917240c5a96fd32f526ee8e2a4761ebb24`;
- verifier publication `6519220f161254c0453a30858eb3e7073e2eb82b`;
- unchanged respool oracle.

The raw artifact contains exactly eight rows in published verifier order. Every
adapter exit is 0, every observation is `adapter_kind=product`, and every
`event_overflow` is false.

### Independent respool replay

Verification independently regenerated each verifier fixture and expected
post-media from the unchanged `respool_draft8` oracle, authenticated each
retained input/output SHA-256, ignored Software's stored verdict strings, and
reapplied the unchanged verifier semantics to the raw call/callback traces.

Result:

**8/8 independently replayed cases PASS.**

A verifier-owned reusable replay utility is published at:

`tools/replay_p1_r25_respool_evidence.py`

It is bound to the exact JSONL SHA-256 above and imports the unchanged
`tests/respool_draft8/oracle.py`.

### Respool case disposition

| Case | Verification disposition |
|---|---|
| WP12-EMPTY | PASS |
| WP12-TWOPASS | PASS |
| WP12-DECLINE | PASS |
| WP12-FULL | PASS |
| WP12-DEGRADED | PASS |
| WP12-SEQ-EXHAUSTED | PASS |
| WP12-ONE-COMMIT | PASS |
| WP12-STAGE-CLEAR | PASS |

**Respool result: 8/8 PASS.**

## PM routing disposition

**Yes.** Exact product PR #180 at
`262db463680798c63fde8b18232e60bdbda15f0a` can proceed to PM routing for
these published narrow promote/respool tranches.

Verification requests **no further product behavior change** based on this
evidence.

This disposition does not itself authorize merging #180.

## Explicit exclusions

This return deliberately does not extend beyond the assigned tranches.

Still excluded:

- promote §9.3.3 crash / RESUME closure;
- promote stored-position integration;
- promote callback re-entry and progress-callback semantics;
- WP-12a continuation / BUSY / re-entry / argument-stability / FAULTED
  behavior;
- WP-10 crash closure;
- bit-exact or listened audio acceptance;
- broader randomized edit/history testing.

## Published evidence linkage

Verification-side provenance is recorded at:

`findings/evidence/P1-R25-ISSUE44-PROVENANCE.md`

The authoritative raw retained evidence remains the exact GitHub Actions
artifacts identified above.

## Stop condition

No blocker remains in issue #44's assigned scope. This finding is the immutable
evidence-linked return. Issue #44 may close as completed.

Closure is not product merge or full package/source/golden acceptance.
