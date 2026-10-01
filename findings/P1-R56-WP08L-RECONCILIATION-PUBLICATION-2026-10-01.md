# P1-R56-V-WP08L: WP-08 coverage reconciliation against DRAFT-9, and genuine-gap publication

**Return:** a criterion ledger of 14 rows and a new blind package, `tests/wp08_mapping_r56`, for the two partial
rows. It has 2 rows and 62 cases, and 6 controls each killed on a derived exact set. This is authoring and
reconciliation, not a Product PASS.

## Inputs

- Issue: Verification #129, body as of 2026-10-01T00:04:09Z, with no scope comments. Issuer: PM Product #305.
- The issue's priority note was honoured: #131, the PM-issued disposition of the #340 binding, was returned first.
- Product main at reconfirmation: `1e6764e` (≥ `9497005`).
- Verification main: `0ac2f8e`. My verifier work is on the PR #125 branch.
- Frozen DRAFT-9 hashes, reconfirmed against Product main `spec/`:
  - TapeFS `3f08ec6d…`
  - Engine API `383817326705…`
  - Acceptance `ae77d13c…`
- **The DRAFT-9 change does not reach WP-08.** I compared the specs bundled with `playback_complete_draft8`:
  - The acceptance WP-08 row is byte-identical to DRAFT-8.
  - engine-api §5, §6 and §8 are unchanged. V9-001 touches only §3 and invariant 15.

  So DRAFT-8-era WP-08 dispositions still bind.
- No `engine/`, Product adapter, or Product implementation PR or issue was opened. I read only Product
  docs (`STATUS.md`, `DECISIONS.md`, `VERIFICATION-INTEGRATION.md`, run READMEs) and `tests/IMPORTS.json`
  for disposition records.

## Publication

| Object | Value |
|---|---|
| Commit | `5b7c3641e972bdbf080885ac01142927434487fa` (2026-10-01T02:48:20Z), parent `3120a1d` |
| Whole tree | `6f3ef7d2f75bbe56e8e1714d2150874674c66d72` |
| `tests/wp08_mapping_r56` subtree | **`466bf8193e53a39a4e5a51710ede9cd2b2458858`** |
| Case set | `9eca914a4f2ed87db31bb5cd1212b89dec52731e37cdd76e1fb8aa2af8424e30` (row 1: 60, row 2: 2) |
| `oracle.py` | `7eab5a76bbadefd569e77e0986bfd9645bcbaf1d0a94b469029b2ba83b63ea9c` |
| `rows.py` | `f918fc56142822f9864f02f1eee8ee63f4c6fc5b2c244e5000b981b7b3b261a0` |
| `replay.py` | `f18a941a7c22a5615233f3855328291a96745683ce9524416f9132baa886ac2d` |
| `selftest.py` | `0ef5498113a51abe2d886cafb3cd6ec4f960154eb97f333f6f48f8424c9e623d` |
| `pins.py` | `45229260a6dfcf587c7af69bbb77a3cb7203d07af43907e736695ac76e22f759`. It pins `wp10_final_r54` `model.py` `2b1c8c8d`, `dupmodel.py` `53d0b75e` and `deps.py` `41d1e5ed` by blob. |
| `wp08-ledger.json` | `a6fb617214d861cbaebdd49938b3032ff424e84d7f819cc3cdb82d8f9064c9d5` |
| `ADAPTER.md` | `ce3360714d203b3c8bc5f6d741ed54d92a039b989b2b79d8df27bab48ef4afe7` |
| Fixture image | `rows.image()`, SHA-256 `e29689a6f41227e89a5ec781e3429f5ed7cde66fbd2fa9f8ecec6295daefac8e` (7,169 blocks) |
| Synthetic evidence | gzip `ffc7f2781e7dcbbd3d6186b42df5b1448cce21dfa0baf79bcdb29bed555ffc1b`, deterministic (`mtime=0`). Replays 62/62. |
| CI | The `wp08_mapping_r56` matrix leg in `.github/workflows/verifier-wp10-packages.yml` runs audit, self-test and synthetic replay. |

A clean worktree at the commit reproduces the audit, the self-test and the replay (`evidence/P1-R56-WP08L/`).

## Ledger (summary; `tests/wp08_mapping_r56/LEDGER.md` is authoritative)

**Accepted dispositions mapped:**

| Key | Package | Disposition |
|---|---|---|
| R15 | `playback_complete_draft8` | P1-R15 / ADR-150 |
| R25 | `transport_draft8` | P1-R25 |
| V95 | `crossrun_wp08_r44` | Verification #95 |
| V122 | `portability_wp08_r52` | Verification #122 |

**`playback_draft8` has no accepted Product evidence.** Its three-family bundle (draft PR #64) was held
unbound and never dispositioned (P1-R7).

| Status | Rows |
|---|---|
| covered | L02 ramp table; L05 `INT32_MAX`; L06 empty; L07 rate 0; L08 reverse from 0; L09 `INT32_MIN`; L11/L12 `set_side` (i)/(ii); L13 render zero I/O |
| **partial + gap** | **L03** V4-010 run-boundary seeks; **L10** V5-005 reverse-from-end golden |
| listening-held | L01 1.0× against `tests/golden/`; L14 listened goldens (WP-11, Michael) |
| unreachable (blind) | L04 "§6.2/§6.3/§8 are the only implementation". This is a source-structure claim; behavioural equivalence is V122, and the full §8 domain is the WP-11 portability gate. |

**Why L03 and L10 are genuine gaps.** Every accepted WP-08 fixture (V95, V122) puts each run at `start_frame` 0
of its own chunk, in ascending chunk order, at most 7 frames long, on Side B. An engine with any of the
following defects passes every accepted WP-08 observation:

- it ignores `start_frame`;
- it sorts entries physically (for example, an in-place disjointness sort, which §5.1 invites);
- it wraps a chunk-spanning run inside its first chunk.

Side-A boundary seeks are never exercised either. The R15 side families only render Side A forward from 0.

## Package rows

The fixture is one C69-layout cartridge carrying five physical runs:

| Run | Entry | Shape |
|---|---|---|
| E0 | `{3,1000,300}` | Block-unaligned start |
| E1 | `{3,100,50}` | Shares chunk 3 below E0 |
| E2 | `{1,131000,200}` | Spans the chunk 1 → 2 boundary |
| E3 | `{4,127,3}` | Starts on the last frame of a block |
| E4 | `{0,5,6}` | Lowest chunk, odd offset |

Side A plays them in the order `E2 E0 E4 E3 E1` and Side B in the order `E0 E1 E2 E3 E4`. `a_high_water` is 5.

1. **`WP08.seek_boundary.mapped_runs`**: 60 cases = 2 sides × (4 run boundaries + 1 intra-run chunk crossing) ×
   {−1, 0, +1} × ±1.0×.
   - Each case is: seek, set the rate, service to completion, `render(4)`.
   - The output must be the exact four timeline frames (from the pattern and tapefs §5.1), with tell `N±4`,
     flags false, and render making zero callbacks.
2. **`WP08.reverse_end.mapped_timeline`**: 2 cases, one per side.
   - Each case is: `seek(559)` (which clamps to `max_pos`), −1.0×, then serviced `render(32)` calls.
   - The output must be the exact reverse of all 559 frames: 17 full renders and one of 15, with tell after each
     render, and `at_start` only after frame 0 is emitted.

**Controls**, each killed on an exact set derived from the mapping rather than from the oracle:

| Control | Cases killed |
|---|---|
| `ignore_start_frame` | 62 |
| `chunk_crossing_wraps` | 21 |
| `sort_entries_by_physical` | 62 |
| `side_a_plays_b_index` | 31 (Side A only) |
| `reverse_crossing_stale` | 6 |
| `render_reads_device` | 62 |

**Spec-forced pins only.** Lawful engine freedoms still pass (`evidence/P1-R56-WP08L/oracle-latitude.log`):
service reading one block per call, and a 4,096-frame fill window. Block choice, order, per-call split and
service-call count are not pinned (#115).

## Size and exceptions

There are 2 rows and 62 cases, which meets the "≥ 3 rows or ≥ 25 cases" floor on cases. No padding.

- **Fractional rates across mapped boundaries.** Considered and excluded: V95 already crosses physically
  discontiguous runs at fractional rates, and the mapping defects are rate-independent.
- **A Product binding of `playback_draft8`.** Not proposed: the new rows strictly contain its mapping shapes.

## Exclusions

Product binding and disposition (PM routes), listened goldens and WP-11, complete WP-08 acceptance, hardware and
release. DRAFT-10 (#308) is untouched: no row here needs a spec change.

**Next owner:** PM.
