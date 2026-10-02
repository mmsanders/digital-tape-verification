# P1-R54-V-WP10D: final WP-10 backlog publication and closing ledger

**Ready for PM review.** This publishes the four remaining WP-10 rows, the closing 62-row ledger and one
PM finding, **V-R54-03**. There is no Product binding yet.

## Inputs

- Issue: Verification #118, body as of 2026-09-30T15:02:17Z, no scope comments. Issuer: PM Product #305.
- Taken up after the PM-issued dispositions #119–#124, as its priority note directs.
- Product main `66c6abc69d83cff10da32a6b446690fcd0b927fb`. Verification main
  `0ac2f8eda377264c97c798b34a2ee4fdc421025d`. Source backlog: #116 publication `dea9b521`,
  `backlog-update.json` `77389e67…9820`.
- Frozen DRAFT-9 hashes, reconfirmed against Product main:

  | Spec | SHA-256 |
  |---|---|
  | TapeFS | `3f08ec6d11070c1e10edcf7cacbcd93ff694257f042b71b53200e158621fa19d` |
  | Engine API | `383817326705d98bda6a96480f8185e911113927d35c53c02d1458adb72baea6` |
  | acceptance | `ae77d13c868fd39a882b5bd3ebf459557792432ce895bc7bf58be7fc2c33825d` |

- No `engine/`, Product adapter, or Product implementation issue or PR was opened while authoring.

## Publication

Package: `tests/wp10_final_r54` at commit **`7c0410e0042d00c05b72affccd4de0a03ce8abd6`**, subtree
**`598ebcd8f0914040558f565809b90bdb22bb8221`**. The commit lives on `claude/wizardly-bardeen-4asv8m` and
reaches `main` through PR #125.

| File | SHA-256 |
|---|---|
| `oracle.py` | `b720b5b1…4c851b` |
| `model.py` | `7714fe5e…fea66a` |
| `selftest.py` | `c1b24b0b…3abda2` |
| `synthetic_adapter.py` | `a11391bd…8f231c` |
| `replay.py` | `a7221191…0efa72` |
| `audit.py` | `33262544…b8e17e` |
| `ADAPTER.md` | `f861b2d9…8e5d4df` |
| `coverage-ledger.json` | `4ab66f55…4ce80c` |

`deps.py` is `e424efda…` and is byte-identical to the #110 copy. `dupmodel.py` is the #116 `model.py`, blob
`53d0b75e`.

Synthetic evidence: gzip `222524428680ad785912a2e8ba90a8689edf5d61daef70c27e30a9387df8aa7b` (3,053,266 B,
under `tests/`, outside the `docs/` 1 MiB gate); manifest `a54a5fa1…bba36`. Case set
`159b4ac64a5e653df2625a025f5f8cf13bcb90fed9a11905a1733f7a97167cd1`.

**Runs, reproduced from a clean checkout of `7c0410e`:**

- `audit.py`: PASS. The ledger has 62 rows.
- `replay.py`: PASS on 207,584 observations. The `findings` counter
  `v_r54_03_resurrected_previous_superblock` reads 48.
- `selftest.py`: PASS in 4 min 42 s.
  - The identity census covers 298,604 permitted re-run images. The finding is forced in exactly 48 cells.
  - The clean synthetic run passes 207,584 of 207,584.
  - All 9 controls are killed:
    - rows 1–2: exact kill sets of 3, 6, 3, 5 and 1 cases;
    - row 3: `commits_before_copying` in 5 fixtures and `pass1_onto_live_b` in 1;
    - row 4: `rerun_skips_barrier` kills 173,654 cases, and still 173,613 with trace binding off;
      `rerun_final_keeps_old_uuid` kills 16,448, and 16,112 with trace binding off.

**CI.** A new workflow, `.github/workflows/verifier-wp10-packages.yml`, runs audit, self-test and replay
for `tests/wp10_backlog_r53` and `tests/wp10_final_r54` on PRs. It does not change the draft8 workflow,
which only globs `*_draft8`.

The package covers these rows and cases:

| Row | Cases | Controls killed |
|---|---|---|
| `WP10.counters.v5_015.reset_b_and_stage_clear_generation` | 13 contract cases: 8 one-short refusals and 5 exact-threshold successes | 3, each on its exact case set |
| `WP10.headroom.zero_needed_reserved.empty_respool_each_counter_each_value` | 4 cells and 2 converses | 2, each on its exact case set |
| `WP10.op.respool.post_crash_render` | 5 fixtures; the synthetic binding yields 24,672 exhaustive injections | 2 |
| `WP10.dup.rerun_crash` (new) | 207,560 (103,780 per mode) over 16 representatives | 2, both also with trace binding off |

NOTHING-TO-DO promote at the reserved values already has accepted evidence (R29-A, 4 cases), so it is not
re-authored.

## PM finding V-R54-03

A torn exhausted-generation fallback can resurrect the previous superblock. The full statement is in the
package's `COVERAGE.md`.

**How the state is reached.**

1. **First power cut.** The destination is at `sb_generation` `0xFFFFFFFD`. The §9.5 zeroing fallback's
   candidate zero write tears after 1 byte. This leaves a block whose magic fails, while bytes 1–511 of the
   old superblock survive.
2. **Re-run.** The re-run sees no valid superblock and takes the blank path, with no barrier. It copies the
   source and writes the fresh mirror at generation 1.
3. **Second power cut.** The re-run's final primary write tears after 1–12 bytes. These bytes are identical
   in both superblocks, so the tear restores the previous block with a valid CRC.
4. **Mount.** §4.1 selects generation `0xFFFFFFFD` over 1, and the cartridge mounts **under the previous
   UUID while playing the source's copy**.

**Scope.** Every conforming engine reaches this state in exactly 48 cells:
- 2 exhaustion shapes × 2 durability modes × 12 landed values;
- each cell has a single permitted image;
- the self-test proves the set is exact over all permitted images.

The oracle still requires the model-predicted outcome in these cells and counts them. It fails any other
identity violation.

**Conflict.** The clauses in tension are tapefs §9.5 item 5 and the §4.5 fallback, tapefs §4.1, and
acceptance WP-10's "no injection point yields a cartridge that mounts under the destination's previous UUID".

**Suggested fix (PM's decision).** Treat a destination as blank only when both superblock blocks are all
zero. Otherwise, zero both superblocks before step 2.

## Closing ledger

All 61 rows of #105's ledger, plus `WP10.dup.rerun_crash`, are closed and none is uncovered:

- 48 accepted;
- 7 published with the Product binding disposed PASS (#119, #120);
- 7 published with the Product binding pending: #329's rebind after #124, and the 4 rows here.

**Next owner:** PM, who issues the Software binding of `tests/wp10_final_r54` and rules on V-R54-03.

**Exclusions:** WP-12/WP-12a, WP-11, hardware and release. No complete WP-10 claim is made.
