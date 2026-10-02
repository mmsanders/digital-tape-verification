# P1-R55-V-STR: three strengthening rows, and maintenance of the #99 package

**Ready for PM review.** This publishes three new rows, each able to see a defect its accepted row
cannot, plus a maintenance-only update to `capacity_wp09_r52`. No accepted subtree changes an
assertion, and no Product binding exists yet.

## Inputs

- Issue: Verification #126, body as of 2026-09-30T19:15:06Z. There are no scope comments.
- Taken up after the PM-issued dispositions #127 and #128, as the issue's priority rule requires.
- Product main: `2e54e0fc`.
- Frozen DRAFT-9 hashes, reconfirmed:

  | Spec | SHA-256 |
  |---|---|
  | TapeFS | `3f08ec6d…a19d` |
  | Engine API | `38381732…baea6` |
  | Acceptance | `ae77d13c…825d` |

- No `engine/`, Product adapter, or implementation issue or PR was opened while authoring.

## Publication

Commit **`7a914cd7c76bcc933e896a26fa0b3b7349c11b2d`** (tree `d415ef55…`) on `claude/wizardly-bardeen-4asv8m`. It
goes to `main` via PR #125.

### New package `tests/strengthen_r55`

**Subtree:** `72d24675fc40432c29d7f225bac3169124e5d12f`.

**File SHA-256s:**

| File | SHA-256 |
|---|---|
| `oracle.py` | `87d81918…85fc` |
| `rows.py` | `1a6ca0fa…33ca` |
| `pins.py` | `ab1e336e…2652` |
| `selftest.py` | `c9b9a34c…47b1` |
| `synthetic_adapter.py` | `88109c7f…ecf9` |
| `replay.py` | `9c7cbc08…a82c` |
| `audit.py` | `9d70629e…9299` |
| `ADAPTER.md` | `83861e43…c89f` |

**Case set:** `9ee1c5d6…ebea`. Synthetic evidence: gzip `82c302cb…d065`, manifest `2baf30b8…4342`.

**Pins** (Git blob): `wp10_final_r54` `model.py` `2b1c8c8d`, `dupmodel.py` `53d0b75e` and `deps.py` `41d1e5ed`;
`capacity_wp09_r52` `oracle.py` `df7f6095` and `synthetic.py` `edf6d9b0`.

**Rows:**

| Item | Row | Cases | Controls killed, each on its exact set |
|---|---|---:|---|
| 1 (V-R54-02, #120) | `WP10.dup.destination_shape.copied_audio_every_block` | 12 | `copy_only_first_block`, `copy_skips_second_block`, `copy_skips_last_block`: 10 multi-block cases each |
| 2 (#121) | `WP06f.sideA_liveB.respool_pass2_run` | 1 | `pass2_onto_then_live_chunk` (rule b), `pass2_declines` (rule c), `pass1_below_floor` (rule b) |
| 3 (#107 finding 1) | `WP09.capacity.fixture_a_slot_premise` | 27 | `a0_at_sequence_3`, `a1_structurally_valid`, `a_slots_not_snapshotted`: 27 each |

**Row 1.** Six source lengths (1 block, a block boundary, 8 blocks, a whole chunk, a chunk boundary, and 3 chunks)
are copied onto a blank destination and onto a reusable one.
- Every frame is a coordinate-unique, non-zero pattern. The reusable destination carries a disjoint pattern.
- The raw copied frames and both sides' renders must equal the source timeline.
- Only the layout is spec-forced (`{0,0,frames}`, §9.5). Partitioning is not pinned (#115).

**Row 2.** Side-A mount; `a_high_water` 2; A `{0,0,10}`; live B `[{2,0,10},{3,0,10}]`; floor 4; `len` 1.
- (a) Pass 1 lands at or above the floor.
- (b) Every chunk write is disjoint from the then-live set, rebuilt from raw commits.
- (c) Pass 2 **runs**: at or above `a_high_water`, strictly lower, one run of `len`, and committed to the other slot.
- Then: one entry, a bit-identical render, and no superblock write.

**Row 3.** From raw `raw_before` bytes, A0 is an empty Side-A index at sequence 1, A1 is invalid, and
`cartridge_sequence` is 3. The unchanged #99 oracle is then replayed on the four-key subset.

### `tests/capacity_wp09_r52`: new subtree `4c754247d2769a9033d7b921cbd248e3e943b62a` (was `85043f53`)

This is maintenance only, with no assertion change (commits `a15f08e` verbatim, then `aeaf3e2`).

**Changed:**
- `ADAPTER.md` (`6115da81…3076`) now specifies the full §4 superblock, an empty A0 at sequence 1 and an invalid A1.
- `synthetic.py` (`ab7c5224…23c6`) writes a complete §4 superblock. It previously wrote `block_count` as a u64 at
  offset 36.
- The synthetic evidence and manifest are regenerated.

**Unchanged:** `oracle.py` (`e1cd2f71…`, equal to the accepted manifest's `oracle_sha256`), `replay.py`, the
self-test assertions and `plan.json` (`ceacb2e0…`). Every accepted Product replay stands. The A-slot check is the
new row 3, not an edit here.

## Runs, reproduced from a clean checkout of `7a914cd`

- `strengthen_r55`:
  - `audit.py` PASS;
  - `selftest.py` PASS: 40/40 clean synthetic cases, 9 controls killed on exact sets;
  - offline `replay.py` PASS on 40 cases.
- `capacity_wp09_r52`:
  - `selftest.py` PASS: 27 cases, 7 controls;
  - `sha256sum -c` OK.
- **CI:** `.github/workflows/verifier-wp10-packages.yml` now covers `strengthen_r55`, plus a
  `capacity_wp09_r52` job for its self-test and checksum. Before this, that package ran in no CI.

**Next owner:** PM, to route the Software bindings. V-R55-01, the row-3 enumeration floor from #128, is outside
this issue and is left for PM to route.
