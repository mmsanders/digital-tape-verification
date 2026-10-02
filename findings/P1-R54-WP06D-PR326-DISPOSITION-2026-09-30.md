# P1-R54-V-WP06D — Product PR #326 (WP-06 closure gaps, R53-corrected) disposition

**Verdict: PASS** for exact Product head `c5ac824b8f96be1bc16851988f4bff686b153c17`, tree
`c23dc1c37d70253745241c6f44f3514766fe508d`, **7/7 rows**. Re-spool floor ruling: **not vacuous** — the
row is exercised as frozen, and on this fixture the pass-2 decline is positively asserted; only the
pass-2 *run* branch from a Side-A mount is unexercised (verifier-side follow-on, not a condition).

Issue: Verification #121 (body 2026-09-30T16:59:21Z, no scope comments); issuer PM Product #305;
supersedes held #312. Inputs: Product main `66c6abc6`, Verification main `0ac2f8ed`. `engine/` built and
executed, never opened.

## Identities

| Object | Value | Checked |
|---|---|---|
| Head / tree / base | `c5ac824b…` / `c23dc1c3…` / `66c6abc6…` | `git rev-parse` |
| Import `051d292c3646b7a31a43fe5462ef3dbec022c2f0` | `tests/wp06_closure_r52` = `b216baa2a9c160b2a14b3eac25567c5a260eed2f` = my #108 publication `6b92e5f43de89efa71069084028376cdbc636bf4`; touches only that tree + `tests/IMPORTS.json`; parent `66c6abc6` | `rev-parse`, `diff-tree` |
| Ordering | publication 2026-09-30T03:18:58Z < import 15:28:33Z < binding 15:31:28Z; `engine/` unchanged (`054d27ab…`) on the branch | commit dates |
| Plan / ledger | `db9f826a…8119` / `93f9c89e…71bd6` | `audit.py`, replay |
| Adapter | `wp06c_adapter.c` `0af5652252d7b51d74dc87523bb439a7232c0a0028d0027e54ae91cbacf96fc9` | `sha256sum` |
| Retained evidence | JSONL `c494589e…5b07` (8,935,011 B); gzip `389d7340acf57800685757ec4d1aba3252b8a1d45718d682690b2514b1c45b83`; build-identity `a74a70c0…59e1`; census `6ad4daa8…fd61` | `SHA256SUMS` |

## Runs (Linux, GCC 13.3.0, Python 3.11.15)

1. My package at `6b92e5f4`: `audit.py` PASS (45 ledger rows, 7 observable, 2 contract-blocked);
   `selftest.py` PASS (7 synthetic positives, 13 row-specific red controls killed).
2. Exact-head build and fresh canonical run with `--retained`: JSONL byte-identical; replay PASS 7.
3. **Independent replay of the retained Product gzip** with my oracle at `6b92e5f4`: **PASS 7/7**
   (`evidence/P1-R54-WP06D/replay-manifest.json`).
4. Product controls: 7/7 cases pass `oracle.check`; **9/9 mutations killed** (Side-A refusal wrote; full
   re-spool accepted; arm did not clear stage; reset left degraded; remount selected stale B; phase 1 onto
   live-B chunk 3 on each floor row; promote phase 2 removed; re-spool index write without `data`).
5. Early carry-over signal: same head with #318's `engine/` `81ad8ec2` (built, not read; different
   `libtape.a`) regenerates identical JSONL. The post-merge CI `--retained` run remains the authority.
6. Re-spool pass-2 injection census (below; `evidence/P1-R54-WP06D/respool_pass2.py`).

CI runs were not readable from this session (no Digital-Tape API access by design).

## Adapter review

Public header only; a flat caller-owned device logs every read/write/flush with a global ordinal and
result; metadata and mirror writes carry their bytes; fixtures are written and snapshots read directly
from media outside callback accounting; no selected-slot, phase or verdict fields. Long operations are
driven to `more_work == false` under one step. Fixture superblocks fill every §4 field with a
geometry-exact `nominal_length_s`. Nothing here can make a wrong engine pass an assertion.

## Ruling: F-LIVEB-RESPOOL-FLOOR is not vacuous

Fixture `sideA_live_dense_fragmented_B`: `total_chunks` 12, `a_high_water` H = 2; A `[{0,0,N}]`; B
`[{0,0,N},{2,0,N},{3,0,10}]`, so floor = 4, `[H, floor) = {2,3}` densely live-B, and `len` = 3.

Observed `exercise` writes: 2,049 single-block chunk writes into chunks 4–6 (2 × 1024 + 1), flush, B1
entry block (LBA 393), flush, B1 header (LBA 392), flush. No further chunk writes.

- **The frozen row is pass 1.** acceptance WP-06f: "a `respool`/`promote` issued from that Side-A mount
  **allocates above it** … since the failure mode is allocating over Side B's live chunks." tapefs §9.4
  makes pass 2 "opportunistic space reclamation, **not a correctness requirement**." Rule (a) — pass-1 one
  run of `len` at or above the floor — and rule (b) at every pass-1 write are exercised on real Product
  callbacks, and the Product control moving the first copy onto live-B chunk 3 is killed.
- **The decline is asserted, not merely permitted.** After the pass-1 commit the live set is `{0,4,5,6}`.
  §9.4 pass 2 needs a len-3 run with start ≥ 2, strictly below 4, disjoint from that set; `[2,5)` and `[3,6)`
  both hit chunk 4, so none exists and re-spool must stop. I injected a pass 2 at every one of the ten
  possible len-3 destinations into the real Product observation; the unchanged oracle rejected **10/10**
  (invariant 10 for `[0,3)`, `[2,5)`…`[6,9)`; below `a_high_water` for `[1,4)`; not strictly lower for
  `[7,10)`…`[9,12)`). On this fixture the only passing outcome is exactly the observed decline.
- **What stays unexercised is the pass-2 *run* branch from a Side-A mount** — rule (c) and rule (b)
  applied to a lawful pass-2 write — because `floor − H = 2 < len = 3` makes it geometrically impossible.
  My #108 package permits that (`if later:`); it does not require the fixture to admit pass 2. That is my
  package's choice, not Software's. The run branch itself is WP-12's V3-003 case, carried by accepted
  re-spool evidence, but not from a Side-A mount over a live-B floor.

**Recommendation (verifier-side, not a condition):** add a second floor fixture with `floor − H ≥ len`
(for example B `[{2,0,10},{3,0,10}]`, H = 2, floor = 4, `len` = 1: pass 1 to `[4,5)`, then pass 2 must
run into `[2,3)`), so the Side-A-mount run branch is exercised too. Routed to the #118 backlog.

## Exclusions

The two contract-blocked WP-06e rows (PM #308), complete WP-06, WP-10, WP-11, hardware and release; no
acceptance of engine behaviour beyond these seven observations.

**Next owner:** PM. On merge after #318, the `--retained` CI regeneration carries this disposition.
