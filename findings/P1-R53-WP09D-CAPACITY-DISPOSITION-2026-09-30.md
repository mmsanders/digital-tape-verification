# P1-R53-WP09D: independent disposition of Product PR #311 (WP-09 capacity short accept)

**Verdict: PASS** for exact Product head `92f9280cf99232627d4117385ba67de50ed30f49`, tree
`296c16047c66269ce22ee83532e17d140cacc337`. This is bounded to the #99 package `tests/capacity_wp09_r52`.
It is not merge authority. Next owner: PM.

Issue: Verification #107, issued by PM Product #305 after the Software #306 return. Frozen DRAFT-9 inputs:
TapeFS `3f08ec6d…a19d`, Engine API `38381732…baea6`, acceptance `ae77d13c…825d`.

## Blindness

I read only the binding under review: `tests/capacity_wp09_adapter/**`, its CI workflow result and
its retained evidence. `engine/` was compared by tree SHA only and never opened. Software's
`case-census.json` is observed facts and carries no authority; Software's verdict strings were not
consulted.

## Mechanical authentication

| Item | Independently observed |
|---|---|
| Base | Product main `39d2076fa204991ec9c0d43f00b502942556bf9a` |
| Import commit | `aba7735e388e219f4804658c5be3f8cc43258a1f`, sole parent `39d2076`; touches only `tests/IMPORTS.json` and `tests/capacity_wp09_r52/**` |
| Binding commit | `92f9280`, sole parent `aba7735`; touches only `tests/capacity_wp09_adapter/**` and `.github/workflows/ci.yml` |
| Verifier subtree at head | `85043f530c95257721347a6d991a0d205b299e4f` = Verification #99 publication `87ae5746f6892a41d2660d5ef05c4a97b2ea8cf5` |
| `engine/` tree, head = main | `054d27ab6e3e72f61118ff7d99e19e48741d05b2` |
| `spec/` tree, head = main | `f1e55ae9c7ee46d1e47285d9b8a22a914da6cbd8` |
| Check runs at head | 158 success, 2 failure. Both failures are `golden suite (awaiting WP-11 fixtures)`, by design |
| Capacity job | `independent WP-09 R52 capacity short accept — product replay` succeeded in runs 36643896048 and 36643890633. On ubuntu it rebuilt from source and logged "regenerated JSONL is byte-identical to the retained evidence" |

I recomputed these hashes from the downloaded bytes, and every one matches `build-identity.json`:

| File | SHA-256 |
|---|---|
| `capacity_adapter.c` | `0e40300cbb657f389744853b088fb8952172a4fc4f2f9eee577725c4a4795120` |
| `run_product.py` | `009bea2f161a2ccb207b17d8aa6d1d15450ff1ddb5b5085418e0f8c0f14270e6` |
| `Makefile` | `81e6c4b41d7034bc2324ec09c5b1e0def23b38ccc4aef7db9b2d7c19d9ee2b10` |
| `plan.json` (LF blob) | `ceacb2e064ef3550774064e94580397f213614fa834d7b82b0fdcb2a91b44501` |
| `observations.jsonl.gz` | `a43dbfa7caf49023fda09c902b3509ab28b8c7946cb569d927435e7f6bc07bf9` |
| `observations.jsonl` | `30cef46bd2777f6e4fb8dd5cea255aed8071c6fc53f2e21c1eb09408ba71bc58` |
| `build-identity.json` | `d59b7e3af6c092fa347ae4b584cb83fc88e13743aab61a994af4b8b00b16a586` |
| `case-census.json` | `53b6b19f8ccc8cb7244d68416e6736635594f8bc188286e84808227f0360958a` |

The retained `SHA256SUMS` verifies all four evidence files.

## Independent replay

I extracted the unchanged #99 package from `87ae5746` with CRLF conversion disabled; its own
`SHA256SUMS` verifies. I replayed the retained Product gzip with `--adapter-kind product` bound to
the exact commit, tree and adapter source above.

- **PASS 27/27**: overwrite, overdub and splice × start, middle and end × the 1/17/4095-frame accepted prefix.
- Canonical plan `620b89127250357738fd3f29fce75e99db464f38ddce797b74b9106d1f4ab278`.
- Oracle `e1cd2f715b3d7aca8a210f8ae00052ef5c7ea04d3c46d8d2aef5cac591ada56b`.
- Replay `da91b577917b9e7ae6bfdae44cb968495b831af68c931c53e99312a21efec3b6`.
- `observations_sha256` `30cef46b…`.

The package's own self-test still kills 7/7 controls.

The replay therefore confirms each assertion Software claimed:

- `TAPE_ERR_CARTRIDGE_FULL` with positive short accepts of 1/17/4095 and zero feed I/O;
- premature commit `TAPE_ERR_BUSY` with zero callbacks;
- service allocating exactly `[3, total_chunks)`;
- the B1 commit as entries → flush → header → flush;
- a fresh remount selecting sequence 4;
- exact remounted PCM;
- public `free_chunks` 0.

## Controls

Verification wrote its own controls (`P1-R53-WP09D-verif-controls.py`). Each mutates the real
Product observations, and each must turn **every one of the 27 cases** red through the unchanged
oracle. All 9 were killed, 243/243 reds, each for its intended reason:

| Control | Oracle reason |
|---|---|
| `feed_io` | positive capacity short accept |
| `accepted_plus_one` | positive capacity short accept |
| `premature_commit_ok` | commit did not wait for owed frames |
| `allocation_into_live_b` (chunk 2) | service allocation census |
| `missing_commit_flush` | commit write/flush count |
| `pcm_bit_flip_with_spoofed_pass` | exact remounted PCM (the label has no authority) |
| `stale_free_chunks` | public info after |
| `committed_sequence_5` (CRC recomputed) | committed slot/sequence |
| `fixture_generation_edit` (CRC recomputed) | ordinary record changed superblock |

Software's non-canonical `negative_controls.py` also reproduces 10/10 against the unchanged oracle.

## PM question: is the fuller Product fixture mechanical?

**Ruling: mechanical fixture completion. It cannot change whether correct code passes.** One of
its values, A0's sequence, is assertion-relevant; Software's choice is the one the oracle's premise
requires, and it is verified from the hash-bound source.

- **The superblock is not outside the snapshot.** `raw_before` and `raw_after` carry both complete
  512-byte copies, bound by `fixture_sha256`. The oracle parses only magic, CRC, `sb_generation`,
  UUID, `total_chunks` and `a_high_water`. The other fields Software fills fall into two groups:
  - **Spec-forced for any mount to succeed:** the version, the §1 constants at offsets 36–47,
    `index_slot_bytes`, the §3 LBAs, mirror at `block_count − 1`, and `nominal_length_s` 9/12/15 s.
    These are needed for tapefs §4.1 phase-2 admission, including GEOMETRY_OK equality with stored
    `total_chunks` 4/5/6.
  - **Inert to every #99 assertion:** label, `format_epoch`, UUID choice, and `sb_generation` 7. The
    oracle only checks that generation is unchanged, and stage-0 recording never consults it.
  - A fixture missing the forced fields fails mount with `TAPE_ERR_GEOMETRY` for every conforming
    engine. It cannot make a correct engine fail a #99 assertion, or a wrong one pass.
- **The empty Side-A index is required by tapefs §4.2 step 1:** a mount whose Side A has no
  selectable index fails whichever side is requested. It is inert to allocation, because `free_next`
  = max(`a_high_water` 2, live-B last + 1 = 3) = 3 either way.
- **But its sequence is assertion-relevant.** The oracle expects the commit at sequence 4, which
  assumes `cartridge_sequence` (§5.5: the maximum over every structurally valid slot, including A)
  is B0's 3. Any A slot at sequence ≥ 3 would make a correct engine commit above 4 and fail the
  oracle. Software's A0 is at sequence 1, with A1 zero from `calloc`'d media. That appears only in
  `capacity_adapter.c` (`put_slot(LBA_A0, 1u, 0u, NULL, 0u)`), whose SHA-256 is bound to the replay
  manifest, and CI regenerated this evidence byte-identically from it. The premise therefore holds
  for this candidate.

## Verifier findings (non-blocking; for PM to route as #99 package maintenance)

1. **#99 `ADAPTER.md` under-specifies the fixture.** It omits the Side-A index (tapefs §4.2 step 1)
   and the §4 superblock fields that phase-2 admission requires, so the fixture it literally
   describes is unmountable. It also leaves the A-slot sequences unconstrained, although the
   oracle's expected commit sequence 4 depends on them (§5.5), and `raw_before` does not include A0
   or A1, so the oracle cannot see them. **Recommended amendment:**
   - specify a full §4 superblock, an empty A0 at sequence 1 and an invalid A1;
   - add A0 and A1 to `raw_before`, so the premise is checked from raw bytes rather than adapter source.
2. **#99 `synthetic.py` writes `block_count` as a u64 at superblock offset 36**, where tapefs §4
   places `sample_rate`, `channels` and `bits_per_sample`. This is synthetic-only: the oracle never
   parses those bytes, so no verdict is affected. Software's README reports it correctly.

## Not ruled

The render read-amplification observation in Software's return and README is outside this tranche,
as the issue directs. Also excluded: the 10,000-edit history, full WP-09 or WP-10, WP-11 listening,
hardware and release.
