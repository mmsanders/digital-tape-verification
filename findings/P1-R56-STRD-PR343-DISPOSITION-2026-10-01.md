# P1-R56-V-STRD: disposition of Product PR #343 (strengthen_r55, 40 cases)

**Verdict: PASS** for exact Product head `f2bff1f93a089e0f46ae3817efc410e1e81564d3`, tree
`f3bf97544d57e1d2ab779b0d37d0ed982c260e32`, **40 / 40**: row 1 12, row 2 1, row 3 27.

**PM question 1 (mechanical `str55_capacity.c`, real A-slot bytes): confirmed.**
**PM question 2 (capacity carry-over to `4c754247`): confirmed, no objection.**

## Inputs

- Issue: Verification #131, body as of 2026-10-01T02:20:56Z, with no scope comments.
- Issuer: PM Product #305.
- The candidate supersedes `475cd9a9`, which was not disposed.
- The candidate's base is `00c69783` (Product main at import). Product main at disposition was `1e6764e`, which merged #342 (evidence pins).
- `engine/` was built and executed, never opened. I read only the adapter, runners, CI job and evidence.

## Identities

| Object | Value | How checked |
|---|---|---|
| Import `6feb6fe3fff9f14a794421015fad791a33a2619d` (2026-10-01T00:59:16Z) | Parent `00c69783`. Touches only `tests/strengthen_r55`, `tests/capacity_wp09_r52` and `tests/IMPORTS.json`. Subtrees `72d24675…` and `4c754247…` equal my #126 publication `7a914cd7` (2026-09-30T23:45:14Z), which precedes the import. | `rev-parse`, `diff --name-only` |
| Binding `f2bff1f` | Touches only `tests/strengthen_r55_adapter/` (new), `tests/capacity_wp09_adapter/run_product.py` and one CI job. No `engine/`, `spec/` or `firmware/` change. `engine/` = `81ad8ec2a35506042a44cb031726291f4bcd19be`, unchanged from the base. | `diff --stat` |
| `capacity_wp09_adapter/run_product.py` change | Provenance only. It now requires the maintenance tree `4c754247` at HEAD, requires `oracle.py`, `replay.py`, `selftest.py` and `evidence/plan.json` to be blob-identical between `85043f53` and `4c754247`, and requires import `6feb6fe` to be an ancestor. No observation or replay logic changed. | `diff` |
| Adapter sources | `str55_adapter.c` `825c4376…`, `str55_capacity.c` `9b726452…`. My recomputation of the aggregate is `18ed2389…3558`, equal to the build identity. | `sha256sum`, recomputed |
| Retained evidence `p1-r56-product` | JSONL `877a5dc7aa8f9ae5687202138eee6e1c84c0b7a7bc6935cac12f7e9464672aa8` (14,784,212 B), gzip `f6c975da…63b2` (972,402 B), build identity `27871c5d…929d` | `SHA256SUMS` |

## Runs (Linux, GCC 13.3.0, Python 3.11.15)

1. **Fresh canonical run at the exact head, with `--retained`.** The fresh JSONL is **byte-identical** (`877a5dc7…`) and the fresh `build-identity.json` is byte-identical (`27871c5d…`). Its replay passes 40.
   - The fresh gzip is `81735b11…` rather than `f6c975da…`. That is gzip header metadata only: both decompress to `877a5dc7…`, which is the pinned identity.
2. **Independent replay of the retained gzip.** I used my unchanged `replay.py` and `oracle.py` from my publication worktree at `7a914cd7` (subtree `72d24675`), bound to the retained gzip SHA, adapter `18ed2389…`, and the exact commit and tree. Result: **PASS 40** (row 1 12, row 2 1, row 3 27). The fresh gzip also passes 40.
3. **Product `negative_controls.py`: 9 / 9 killed**, with a clean census of 0 failing cases.
4. **My own controls: 6 / 6, each on its exact set** (`evidence/P1-R56-STRD/verifier_controls.py`). Every mutation is resealed where a digest would otherwise catch it.

   | Control | Row | Killed / expected |
   |---|---|---|
   | `v1_copy_block0_only`: the realistic V-R54-02 mutant. Only block 0 is copied; later blocks keep the destination's pre-image (zero or old album). | 1 | 10 / exactly the 10 multi-block cases. The two 128-frame cases survive, as they must. |
   | `v2_pass2_commit_before_data`: the pass-2 index commit precedes its chunk write. | 2 | 1 / 1 |
   | `v3_pass2_below_high_water`: pass 2 lands in chunk 1. | 2 | 1 / 1 |
   | `v4_superblock_write`: a stray LBA-0 write during re-spool. | 2 | 1 / 1 |
   | `v5_a1_valid_seq5`: A1 becomes a valid Side-A index at sequence 5. | 3 | 27 / 27 |
   | `v6_a0_not_empty`: A0 carries one entry. | 3 | 27 / 27 |

## Row 2: pass 2 actually ran

These are the raw callbacks in the retained observation, on the C69 layout (chunk base 2048, 1,024 blocks per chunk, B0 264, B1 392, mirror 7168):

| # | Write | Meaning |
|---|---|---|
| 1 | LBA 6144 | Chunk 4, which is the floor: pass 1. |
| 2 | LBA 393, then 392 | B1 entries and header: the pass-1 commit. |
| 3 | LBA 4096 | Chunk 2: pass 2. That is ≥ `a_high_water` 2 and < 4. |
| 4 | LBA 265, then 264 | B0 entries and header: the pass-2 commit to the other slot. |

Each write is followed by a flush. There is one `tape_respool(64)` call (`more_work` false) and no superblock write. The Side-B remount is one entry of 20 frames, rendering `02ecadf9…`, which the oracle derives from the fixture timeline. So pass 2 ran, and rules (a), (b) and (c) hold on raw bytes.

## Ruling, PM question 1: `str55_capacity.c` is mechanical, and the A-slot bytes are media

**The diff is mechanical.** Against the accepted #311 `tests/capacity_wp09_adapter/capacity_adapter.c` (last changed `92f9280`), the only differences are:

- the header comment and usage name;
- the adapter name string;
- one `bool a_slots` parameter on `raw_state`, which adds `raw_slot("A0")` and `raw_slot("A1")` to `raw_before` only.

`raw_after` keeps its four keys. The fixture builder, driver and every other line are byte-identical.

**The bytes come from media.** `raw_slot` hex-dumps `blk(lba)`, which is `g_media + lba·512`. That is the same buffer the engine's public read callback serves (line 114), and it is dumped before the operation. The adapter builds the fixture, as every binding does. It never supplies A-slot values to the observation separately from what is on the device:

- A0 is written by `put_slot(LBA_A0, 1, 0, …)`. The observed header reads `TAPEIDX\x01`, sequence 1, side 0, count 0.
- A1 is the `calloc` zero block, which is structurally invalid.

My row-3 oracle checks both from the raw bytes, and v5 and v6 show that it would see a different premise.

## Ruling, PM question 2: the capacity carry-over

**Confirmed.** I have no objection.

- **The decision code is unchanged.** Between `85043f53` and `4c754247`, the blobs `oracle.py` (`df7f6095`), `replay.py` (`d5b19d24`), `selftest.py` (`cd2599ee`) and `evidence/plan.json` (`7e590d29`) are identical. Only `ADAPTER.md`, `README.md`, `synthetic.py` and the synthetic evidence and manifest changed.
- **The evidence and adapter are unchanged.** The retained `capacity_wp09_adapter/evidence/p1-r53-product` tree `32532e47…` was last changed at the #107-accepted binding `92f9280`. The capacity adapter source is likewise unchanged (aggregate `0e40300c…`).
- **I reproduced it at the exact head:**
  - offline replay of `p1-r53-product`: PASS 27;
  - fresh capacity canonical run with `--retained`: byte-identical JSONL `30cef46b…`, PASS 27;
  - my own capacity `replay.py` from `7a914cd7` on that JSONL: PASS 27.
- **The #107 A-slot premise is now settled.** Row 3 of this package observes the real A0/A1 bytes for all 27 cases, and they satisfy it.

## Integration note

Product #342 (`product_evidence_pins`) is on Product main (`1e6764e`). When PM integrates this bundle, it must add the `p1-r56-product` pin. That is PM's routing, not part of this verdict.

## Exclusions

Complete WP-06 and WP-10 (parked on DRAFT-10, PM #308, V-R54-03), V-R55-01, WP-11, hardware and release. CI on the PR was not read from this session, which has no Digital-Tape API access by design; the runs above reproduce it. This PASS accepts no engine behaviour beyond these 40 observations.

**Next owner:** PM.
