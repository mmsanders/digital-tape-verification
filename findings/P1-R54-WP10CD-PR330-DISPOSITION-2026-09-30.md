# P1-R54-V-WP10CD — Product PR #330 (WP-10 backlog r54) disposition

**Verdict: PASS** for exact Product head `4f062b76c47ca53a643a60827ef652c5ad20c065`, tree
`ec6463d8fbaeb9f8f250377f67828e4e55646b3d`, bounded to the three published r54 rows (68,854 cases).
All four binding choices ruled below. One verifier-owned coverage gap (V-R54-02) and two notes.

Issue: Verification #120 (body 2026-09-30T16:59:07Z, no scope comments); issuer PM Product #305.
Inputs: Product main `66c6abc6`, Verification main `0ac2f8ed`. `engine/` built and executed, never
opened (a full-Clang engine build was not attempted beyond observing its GCC-only flag in compiler
output).

## Identities

| Object | Value | Checked |
|---|---|---|
| Head / tree / base | `4f062b76…` / `ec6463d8…` / `66c6abc6…` | `git rev-parse` |
| Import `dee538e40d1a081d6cd3e47c7d73f38e2081750b` | `tests/wp10_backlog_r54` = `d6e9a2427ed9b6c4b703c65dc44eb7e13224cabc` = my #116 publication `dea9b521ccee76a69cfd0d517903eb27474d41fc`; parent is main `66c6abc6`; touches only that tree + `tests/IMPORTS.json` | `git rev-parse`, `diff-tree` |
| Ordering | publication 2026-09-30T14:53:37Z < import 16:16:12Z < binding 16:29:57Z; no `engine/` change on the branch (`054d27ab…`) | commit dates, `HEAD:engine` |
| Binding `4f062b76` | touches only `tests/wp10_backlog_r54_adapter/` and one CI job | `diff-tree` |
| Adapter | `wp10r54_adapter.c` `836a0ef9…`; aggregate `a87e0fc8…` (build-identity) | recomputed by runner |
| Retained evidence | JSONL `3a0cff6118e938cf6a59ef2c3b85149a67885b27c63a33a18deed36f8ab9347e` (71,735,125 B); gzip `b4492d4bda9b4b2700c0f755c72e4d89034da0dae27c7760b0f0f5e9699ca631` (1,030,787 B); build-identity `d1f0a25b…` | `SHA256SUMS` |

## Runs (Linux, GCC 13.3.0 / Clang 18.1.3, Python 3.11.15)

1. My package at `dea9b521`: `audit.py` PASS; `selftest.py` PASS — census 4,112 / 64,734 / 8, case set
   `68083302…aaf3`, clean synthetic 68,854/68,854, 16 re-run classes over 5 shapes with every §9.5
   row reached, 7 causal controls killed.
2. Build at exact head (GCC) and fresh canonical run with `--retained`: JSONL **and gzip** byte-identical
   to retained; replay PASS 68,854.
3. **Independent replay of the retained Product gzip** with my `replay.py`/`oracle.py` at `dea9b521`:
   **PASS 68,854** (row1 4,112 = 2,056/2,056; row2 64,734 = 32,367/32,367; row3 8). Manifest in
   `evidence/P1-R54-WP10CD/replay-manifest.json`.
4. Product controls `negative_controls.py`: per-case 4,112 / 64,734 / 8 PASS, 0 FAIL; **12/12 killed**
   (row1: repair trace, repair writes candidate, read-only not flagged, repair not finished; row2: re-run
   incomplete, other chunk, other media, Side B invalid; row3: label not copied, high-water floor, B0
   written as Side A, other audio).
5. **Clang:** GCC-built engine + Clang-built adapter regenerates the identical JSONL. (The engine's own
   build uses a GCC-only flag, so "GCC and Clang" can only mean the adapter toolchain.)
6. **Early carry-over signal:** the same head with `engine/` replaced by #318's `81ad8ec2` (built, not
   read; `libtape.a` `cf3a3506…` vs `dceeb377…`) regenerates the identical JSONL. This is signal only;
   the post-merge CI `--retained` run is the carry-over authority, as the issue states.
7. Durability-subset census (`evidence/P1-R54-WP10CD/subsets.py`): flush-required row-2 crashes landed
   none-kept 4,176, mixed 2,569, all-kept 1,046 (24,576 had a single permitted image); row 1 none-kept 4,
   all-kept 4. Every observed image is permitted.

CI runs were not readable from this session (no Digital-Tape API access by design); steps 2–6 reproduce
them locally.

## Binding-choice rulings

1. **Source fixture builder — mechanical for every published assertion; bears on the *strength* of one
   (V-R54-02).** Label, frame count, `a_high_water`, fresh UUID/generation and slot side/sequence are
   all computed by my oracle from `ROW3_SOURCES` / `dup_ops`, and `source_label_hex` is checked against
   that table, so a wrong builder cannot pass. Source UUID/generation/Side-B contents are unasserted (dup
   copies Side A and writes fresh identity). The zero audio for EMPTY / ONE-CHUNK / CHUNK-PLUS-ONE matches
   my own model (`row3_expected` uses `ZERO`) but makes the row-3 render equality insensitive — see V-R54-02.
2. **Same-`struct dev` re-run on settled durable bytes — mechanical and conforming.** It models power
   return exactly (reads see only durable bytes), keeps the durability mode, disarms the injection
   (`dev_reset`), performs no format, and uses a fresh source instance. This is ADAPTER.md's "same
   destination device … no format in between".
3. **`dst_chunk_lbas` — bears on the assertion (it is its observable); definition is conforming and
   conservative.** It records every read *and* write block ≥ `LBA_CHUNK_BASE` (2048) before any range
   check; excluding the mirror (LBA 6144 = `block_count − 1`, verified against the pinned model) is
   necessary because the re-run must write it, and the mirror lies outside the chunk store, so no chunk
   access is hidden. Observed: `[2048]` in all 64,734 cases, and the control that adds 3072 is killed.
4. **Row-3 `raw_after` LBAs (0, 6144, 8, 264) — mechanical.** They equal `model.TRACKED` P, M, A0h, B0h.

## V-R54-02 (verifier-owned coverage gap, not a binding defect)

Row 3's "copy renders the source's audio" is weak: ONE-CHUNK and CHUNK-PLUS-ONE sources are all-zero audio
(source PCM `07854d2f…` / `ff98aae9…` = SHA-256 of zeros), and so is every destination block beyond chunk 0
block 0. An engine that failed to copy chunk-0 blocks 1–255 or chunk 1 would still pass row 3. Row 2 covers
only the one-block 128-frame copy. Clause: my own ADAPTER.md row 3 / COVERAGE "rendered audio equal to the
source's". Remedy is mine: publish nonzero, position-dependent audio across every source block (and a
nonzero pre-image on the reusable destination) as a follow-on row. It is reported into #118's backlog and
does not condition this PASS, which is scoped to the package as published.

## Notes

1. The adapter README says flush-required cuts "discard every unflushed write". The code (`dev_settle`)
   keeps an index-selected subset, as step 7 shows. Documentation only; the behaviour is better than
   described.
2. `build-identity.json` records `git rev-parse HEAD:engine` — the committed tree, not the compiled one.
   Step 6 compiled `81ad8ec2` while the file still named `054d27ab`; only `host.json`'s
   `engine_archive_sha256` distinguished them. Harmless on CI's clean checkout; for a gate that now relies
   on provenance (#119 ruling b), consider refusing to run when `engine/` differs from `HEAD`.
   Same pattern exists in the #318 runners.

## Exclusions

Complete WP-10, #329's rows, the three remaining backlog rows, WP-12/WP-12a, WP-11, hardware, release; no
acceptance of engine behaviour outside the 68,854 observations.

**Next owner:** PM. On merge after #318, the `--retained` CI regeneration carries this disposition.
