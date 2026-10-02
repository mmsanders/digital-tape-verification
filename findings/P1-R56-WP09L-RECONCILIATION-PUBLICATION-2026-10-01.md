# P1-R56-V-WP09L: WP-09 coverage reconciliation against DRAFT-9, genuine gaps, V-R55-01

**Return:**
- a WP-09 criterion ledger of 12 rows, plus V-R55-01;
- the answer to the `record_draft8` provenance question: **no** disposition accepted `c461e9e0…` exactly;
- a new blind package, `tests/wp09_gaps_r56`, with 2 rows and 8 cases.

The package is authoring and reconciliation, not a Product PASS. The accepted `wp10_final_r54` subtree is
unchanged (`598ebcd8`).

## Inputs

- Issue: Verification #130, body as of 2026-10-01T00:04:12Z, plus PM's scope comment of 2026-10-01T02:20:26Z.
  Issuer: PM Product #305.
- Priority: #131 (the PM-issued #340 disposition) and #129 were returned first.
- Product main `1e6764e`; Verification main `0ac2f8e`.
- DRAFT-9 hashes were reconfirmed against Product `spec/`. The acceptance WP-09 row, and the WP-06 commit
  bounds it exercises, are byte-identical to DRAFT-8. So are engine-api §7, §8 and §11.
- No `engine/` was opened. Product engine identity was checked by tree hash only.

## Publication

| Object | Value |
|---|---|
| Commit | `508ada857a5badf376da4428e87791333f1f0657` (2026-10-01T02:58:33Z), parent `ad9b6c2` |
| Whole tree | `42901094c14516fbfa90a7df46e94bd390b34378` |
| `tests/wp09_gaps_r56` subtree | **`d8d6d6f8a9df02cb6125b73bedbde422afe5d909`** |
| Case set | `5b14062694cfc1ef219612d8086bac56e0a1536680c129537548b687cfbc5fe0` (row 1: 3, row 2: 5) |
| `oracle.py` | `f8909a5c886074cd2e9c6ab48b0635b56059a47f5efd78904439d0ade6180c3b` |
| `rows.py` | `0396cbc6093eed61639bacb2a8cd3ee0baa2324fa9e488d56fb3a9c6cfb5936b` |
| `replay.py` | `fa0b77b7eb2f2521c70e7c94b18ac6f7647a69124e3d054a9bff97c40578a81c` |
| `selftest.py` | `0fe70eb4e53d9b0314a953391c8c1a6acb575c50ff1d635f82db57ffbc9f5582` |
| `pins.py` | `689757c37bde14f78ff2bc9b484c48addccaf6d379d5e3147816eb9854cb5faf` |
| `wp09-ledger.json` | `c33f4829f595b704299b70542e972916ab659b86315ed7872476e40b77d8c156` |
| `ADAPTER.md` | `eca13b54ee91a40771c3a589f3cd5c0c83d19be084bf28b8d29fc81712a5d7a0` |
| Row-1 fixture image | `rows.overdub_image()`, SHA-256 `32f719d90f3285c90c01d9c60c7d801401f074c20a2eaaba96fa220f89cf59da` |
| Synthetic evidence | gzip `32ca117bdfdaa82fa6bf822df92bc2edb016c0cf013cb210d2190089f250d013`, deterministic. Replays 8/8. |
| CI | The `wp09_gaps_r56` matrix leg in `verifier-wp10-packages.yml` runs audit, self-test and synthetic replay. |

**Pins** (by Git blob), all from #118 `wp10_final_r54`:

| File | Blob |
|---|---|
| `model.py` | `2b1c8c8d` |
| `dupmodel.py` | `53d0b75e` |
| `deps.py` | `41d1e5ed` |
| `oracle.py` | `db7509a9` |
| `evidence/synthetic/observations.jsonl.gz` | `faf6d486` |

A clean worktree at the commit reproduces the audit, the self-test and the replay (`evidence/P1-R56-WP09L/`).

## Ledger (summary; `tests/wp09_gaps_r56/LEDGER.md` is authoritative)

**Accepted dispositions mapped:**

| Key | Package | Disposition |
|---|---|---|
| RD | `record_draft8` | P1-R25; exact bytes `a88850df…` |
| HI | `history_wp09_r44` | Verification #96 |
| CAP | `capacity_wp09_r52` | Verification #107, carried over per #131 |
| STR3 | `strengthen_r55` row 3 | Verification #131 |
| SEQ | `sequential_wp06_r44` | Verification #98 |

| Status | Rows |
|---|---|
| covered (10) | L03–L06 splice at t=0, mid-run, exact run boundary and end; L07 armed BUSY; L08 zero-accepted no-op 3×3; L09 ≤ 97 blocks; L10 exactly two flushes; L11 no-op writes and flushes nothing; L12 CAP premise |
| **partial + gap (1)** | **L02** full-scale overdub saturation |
| listening-held (1) | L01 golden WAVs (WP-11, Michael) |
| gap (verifier-owned) | **V-R55-01** |

**Why L02 is a gap.** Across Product-accepted evidence, PCM is compared at the HI checkpoints and the CAP remounts.

- HI's checkpoint renders show 45 saturated mixes. Only **one** of them is full-scale against full-scale: −32768 + −32768, at checkpoint 9200, frame 10.
- **No positive** full-scale against full-scale (32767 + 32767) is ever verified on Product.
- RD A13 is reference arithmetic only, and CAP mixes small values.

I counted these by replaying HI's published edit plan through its own model and tagging mixes that survive to a
checkpoint.

## Provenance answer (PM scope comment): **no**

- **What I accepted.** P1-R25 (Verification #38; PR #39, merged at `e9e6ec7`) accepted exactly
  `a88850df6554df973fdda6071f65184fcd9012b8886c253dafbff4fc9e0966fc`. Its replay authenticates that SHA by name.
- **What Product main retains.** Stream `c461e9e00d47e6ae9c47827fbba68a2a796aed9b418f3aad94c6b34e3591db8f`
  (blob `b83eb2d4`, Product `e4858b8`). Before this return, no Verification finding, test or commit named it.
- **The difference** (`evidence/P1-R56-WP09L/record-provenance-diff.log`). The 26 records match in order. The only
  differences are two Software-runner presentation fields on `WP09-ARMED-BUSY`, both of which my replay ignores:
  - `errors`: `["armed BUSY/abort path issued block I/O"]` → `[]`;
  - `expected_blocked`: `true` → `false`.

  The engine tree is `0d98ecb0` at both `9d3649d8` and `e4858b8`.
- **Recommendation.** Record the RD rows as **published, Product evidence not exactly accepted**. No disposition was
  run here, as directed.
  - **Behaviour.** A fresh *behavioural* disposition is not needed to establish the facts.
  - **To pin.** Either pin the accepted `a88850df…`, or route a narrow identity disposition of `c461e9e0…`:
    authenticate it, diff it, and replay it with the corrected oracle.
  - **Currency.** Both bundles predate the current engine `81ad8ec2`. Product CI regenerates the bundle without a
    `--retained` byte-identity check. Making it current takes a Software rebinding with `--retained`, followed by a
    disposition of those exact bytes.

## Package rows

1. **`WP09.overdub.full_scale_saturation`**: 3 Product cases (start, middle, straddling the end).
   - Each case is: overdub 16 frames into a 48-frame Side B; commit; remount; render the whole side.
   - `rows.COMBOS` carries every rail pair on both channels: full against full on both signs, one past each rail,
     exactly on each rail, opposite full scale, and mid-scale overflow.
   - The straddle case also checks §11 pass-through of full-scale appended frames.
   - Controls, each on its exact set:

     | Control | Cases killed |
     |---|---|
     | `overdub_wraps` | 3 |
     | `negative_rail_32767` | 3 |
     | `positive_overflow_wraps` | 3 |
     | `append_mixed_with_last_frame` | 1 |
2. **`WP10.respool_render.trace_floor` (V-R55-01)**: 5 fixtures.
   - The input is the **unchanged** #118 row-3 observation. The oracle reruns the pinned #118 check, then requires
     the tapefs §8 floor on every commit: chunk data ≥ ⌈4T/512⌉ blocks → flush → entry block 1 of the inactive
     slot → flush → exactly one header block → flush.
   - It also requires the §9.4 commit count for each fixture:

     | Fixture | Commits |
     |---|---|
     | RS-TWOPASS, RS-FRAGMENTED, RS-CHUNK-CROSSING | 2 |
     | RS-ONE-COMMIT | 1 |
     | RS-REFERENCES-A | 1 or 2 |
   - **Under-reporting control.** Every one of the 48 single under-reported events (24 writes, 24 flushes) goes red.
     The pinned #118 oracle **accepts 43** of them; the 5 it catches are the final flushes. That reproduces V-R55-01.
   - **Pass-2 control.** Dropping pass 2 goes red on exactly {TWOPASS, FRAGMENTED, CHUNK-CROSSING}, and the #118
     oracle accepts all of those.
   - **Authoring sanity check, not a disposition.** The floor holds on the accepted Product row-3 clean traces
     (my #128 regeneration, whose JSONL is byte-identical to the retained Product evidence).

## Size and exceptions

The gaps plus V-R55-01 total **2 rows**, below the 3-row floor. The exception is recorded; nothing is padded. Every
other WP-09 clause has accepted Product coverage, and one overdub fixture already carries every sign pair on both
channels.

## Exclusions

Product bindings and dispositions (PM routes), WP-11 listening, complete WP-09 and WP-10, hardware and release. No row
needs DRAFT-10.

**Next owner:** PM.
