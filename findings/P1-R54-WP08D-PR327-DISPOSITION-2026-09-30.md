# P1-R54-V-WP08D: disposition of Product PR #327 (WP-08 two-toolchain playback)

**Verdict: PASS** for exact Product head `32173accde31efb151ff59545b135a78ab8ec9bf`, tree
`e602ac078d34da6b6fd247ace6d9d37c27a4d14d`, on **41/41 vectors**. The GCC and Clang streams are
byte-identical.

**Ruling on `block_count`: mechanical.** The value is single-sourced, and the engine's own mirror
read authenticates it.

Issue and inputs:
- Verification #121 → #122, body as of 2026-09-30T16:59:31Z, with no scope comments.
- Issuer: PM Product #305. This PR supersedes held #316.
- Inputs: Product main `66c6abc6` and Verification main `0ac2f8ed`.
- `engine/` sources were compiled by each toolchain and executed, but never opened.

## Identities

| Object | Value | Checked |
|---|---|---|
| Head / tree / base | `32173acc…` / `e602ac07…` / `66c6abc6…` | `git rev-parse` |
| Import `8e204a41eaec9ba89ab15439516d9142f32b698b` | Sets `tests/portability_wp08_r52` = `d803deeff4356b6f70ff7f255c9bd6f31aa09790`, equal to my #114 publication `b843298b55a17d450905bc1ae56c4092f9cffa14`. Changes only that tree and `tests/IMPORTS.json`. Parent is `66c6abc6`. | `rev-parse`, `diff-tree` |
| Ordering | Publication 2026-09-30T14:31:25Z < import 15:33:31Z < binding 15:34:59Z. `engine/` is unchanged on the branch (`054d27ab…`). | commit dates |
| Adapter | `wp08p_adapter.c` `0246a30b55d14239ebeb9c1a0e8c71550a8fed82dcdbda8c618eada75e27b38c` | manifest |
| Retained evidence | Stream `8a2369d663a06cad91c205397d6a3a4e0af81706129328843b08613b09bcdd8b` (186,344 B). `gcc.jsonl.gz` = `clang.jsonl.gz` = `b100b564…e950`. Manifest `b7740435804669bc37a84c2deff1264682c7f3f58eaf3f910ba124714e876a82`. Plan `6a8a87b1…b763c`. | `SHA256SUMS` |

## Runs (Linux, GCC 13.3.0, Clang 18.1.3, package flags `-std=c99 -O2 -Wall -Wextra -Werror -fno-strict-overflow`)

1. **My package at `b843298b`.** `selftest.py --gcc gcc --clang clang` passes: 41 cases, byte-identical,
   17 red controls killed.
2. **Fresh run at the exact head.** Each compiler builds `engine/src/*.c` plus the adapter. The GCC and
   Clang streams are byte-identical to each other and to the retained streams.
3. **Independent replay of the retained Product streams** with my `oracle.py` at `b843298b`, driven by
   `evidence/P1-R54-WP08D/indep.py`. My `replay.py` binds the verifier reference adapter's hash, so it
   does not apply to Product evidence. The replay requires GCC ≡ Clang, then runs `parse_jsonl`.
   Result: **PASS 41**.
   - Census: `block_count` is 12,289 on all 41 vectors.
   - Mount reads both superblock copies on 41 vectors; service reads on 39 (the two empty timelines do not).
   - Writes/flushes: 0. Seek/rate/render callbacks: 0.
4. **Product controls: 13/13 killed.** The mutations were:
   - PCM nibble, tell drift, `at_start`, short render, render I/O;
   - the `d5772c8` land-and-stop defect on the literal golden;
   - mount write, service flush, mount skipping the mirror;
   - service read outside the device, seek callback, non-addressable `block_count`;
   - one-byte Clang divergence.
5. **My own `block_count` controls** (`evidence/P1-R54-WP08D/block_count_controls.py`). Shifting
   `block_count` by +1, −1 or +4096 in the real Product records is rejected on **41/41** vectors each
   time. At +1 and +4096 the mount no longer reads `block_count − 1`. At −1 the mirror read falls
   outside the fixture.
6. **Early carry-over signal.** The same head, with #318's `engine/` `81ad8ec2` compiled by both
   toolchains, regenerates identical streams. This is only a signal; the post-merge CI `--retained` run
   remains the authority.

I could not read the CI runs from this session, because Digital-Tape API access is withheld by design.

## Ruling: the top-level `block_count` field is mechanical

My ADAPTER.md requires the field ("Record the fixture device's `block_count` at the top level"). The
oracle uses it to bound every permitted read and to recognise the mirror superblock read at
`block_count − 1`. So it bears on assertions, and it is mechanical only if it cannot differ from the
device the engine actually used. Both conditions hold:

- **Single source.** In `wp08p_adapter.c`, one variable, `g_block_count`, supplies every use of the
  value:
  - the emitted field;
  - `tape_dev.block_count`;
  - the callback bounds checks;
  - the superblock mirror-LBA field (offset 84);
  - the placement of the mirror block.
- **Self-authenticating.** Step 5 shows that any other value fails against the engine's own recorded
  mirror read.

Mechanical under CLAUDE.md §3.2. It cannot change whether correct code passes.

## Adapter review

- The adapter uses only public calls and a flat caller-owned device.
- Every callback is recorded unfiltered against the call that caused it.
- The fixture builds every §4 superblock field and places runs at chunk 2k+1 from frame 100, so they are
  physically scattered and off chunk start.
- Raw superblock, B0 header+entries, B1 and run PCM are emitted as top-level additions, which my
  contract permits.
- Plan rows are emitted verbatim into a generated header.
- The adapter emits no verdict fields.

## Note

`manifest.json` records `engine_tree` from `HEAD:engine`. In step 6 it still named `054d27ab` while
`81ad8ec2` was the source compiled. This is the same provenance note as #120: harmless on CI's clean
checkout, but the label does not prove what was compiled.

## Exclusions

- The WP-11 portability gate (embedded target, narrow `int`, differential).
- Listening and goldens.
- Complete WP-08, WP-10, hardware and release.
- Any acceptance of engine behaviour beyond these 41 vectors.

**Next owner:** PM. When this merges after #318, the `--retained` CI regeneration carries this
disposition forward.
