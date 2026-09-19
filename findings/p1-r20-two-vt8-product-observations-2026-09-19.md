# P1-R20-V — blind disposition of two exact VT8 product observations

**Disposition: the two exact recorded observations are narrowly accepted. READY
FOR PM REVIEW.**

Both retained adapter executions exit zero, authenticate and replay PASS under the
unmodified verifier-owned package. Independent raw traversal finds every required
public result, callback ordering/range and retained media transition present and
correct for each exact case, with no unexpected calls, forbidden writes, callback
errors or event overflow.

This accepts only the observations named below. It does not accept product or adapter
source, PR #96, the verifier package as product behavior, or any excluded behavior.

## Authority, blindness and immutable inputs

- Assignment: `mmsanders/digital-tape-verification#16`, observed open with the
  `verification-lead` label; no scope-changing PM or Michael comment was present.
- Input verifier main: `d6c8c99c06e84705ffdb340554f407027e05419b`, tree
  `4519825fdd7b4d53f9368d361ddfb430b0beef3b`.
- Product PM routing main: `2193eafdcd9feb831e551ffe37f0c8a7590f5ab3`,
  tree `48123936a54bbe8b0cae7d2b3cef315ba81297c8`.
- Evidence commit: `088226a3c324a97fe19d4a4285a80af037b097d5`, tree
  `11a022128d4fe6773b241ac70aeed16220072b10`.
- Sole parent / pre-run code: `e1aaf5f3f441e5126e821a0bd2cfa54a98894294`,
  tree `0d340e1583fece209a2fc2516aeba8b1efb3610b`.
- Complete run packet tree: `27edc792ee80dda7e4684e949783791e93a3a490`;
  its exact `product-evidence/` child tree is
  `ef10906c1ffb01d7c507b40a6b135778788c302c`.
- Verifier package tree at both verifier input and evidence commit:
  `3667a2830ba80dbcedad03b97870d1127001ab59`.

The current Verification charter, issue workflow and P1-R20 PM disposition were
read before evidence inspection. Product engine and adapter source, the Software
return, Software issue return, PR #96 diff/conversation/reviews/private tests and
implementer interpretations were not inspected. Git tree identity alone confirms
that the engine tree remains `7f73812ff5ade35d95b848c0df1fd0458aad22ca`
and the adapter tree remains `6f6df812ae346933dff91aebb739feb0e2f0a113`
from the sole parent through the evidence commit.

## Evidence authentication

- Manifest: Git blob `bbee3baa4f99af993d22cae20bddff5a2259297c`,
  SHA-256 `8166e9d35103ea205e741691b889db4db61d48c5bee3249ce659ee9470a356eb`.
- Run log: Git blob `995b0d933f3be4557c96043734b965053b15cc15`,
  SHA-256 `1604cedc5582bc14fb208b0580b16a5177af258c343b0cd54aeb913db6e4ab16`.
- Adapter binary identity recorded by the packet:
  `9dc0522ea21fb6a16943a206aa309984b0f783b00a07d4495d024ecdbb158fac`.
- Manifest-bound verifier files reproduce exactly: runner
  `d7e3ffe198d196e8024edef02abe0fbe9219b374cfe64d64f8fabfe907f1fadb`,
  hardening
  `0e88b276a1e94920f4df9f6ebf686cbd08f19f3986b63806cea04d83573ee0dc`,
  oracle `3e213af2a2bf5a439fe0aebcc83b7c2ccd1437692107fbc5a6bd6634500dcca5`.
- Frozen spec bytes reproduce: TapeFS
  `3bffa0ec46d7ba3779b02cbee6fac1edaf5094553f78270ee379759655147cbb`,
  Engine API
  `537eadc423e1a7bde726d689206b8fe93bef164d57e48e8ff71e07eaf8a7e3a1`,
  acceptance
  `7f78fba7b66b4fc6e96d15399c62468249bb30fbccbb59bf9f57b4532f56b6b7`.

The unmodified `replay.py` authenticates every manifest-described file, both gzip
and decompressed media hashes, exact generated inputs, adapter status, observation
identity, saved result and offline oracle verdict. It returns PASS for both cases.

## `VT8-001-RB-ALLSLOT`

Case evidence tree: `f0b89524dd0a0fe664a3f1a05ac63d64e49ca3a7`.

| Artifact | Git blob | SHA-256 |
|---|---|---|
| adapter status | `44f1b3e1bda26c688e00ba2668a6781d30845c4f` | `06717e5ef3448ec0e988de82ec13c7b6a037599201c1cf3fa7c879838ec67ef0` |
| input archive | `3641698234a7703bde8338689a372677ecbedc88` | `9f55906803926a7474ac663f2558eb7c26cd32758d70fad6f41663a7bb41c897` |
| observation | `23c88e63f415aaf11199fd0e0583a6f393247866` | `57047481adc2e8cababd329935cf812f7aca5896dc2e98583ab3a11ea50eb29b` |
| output archive | `402a48bcdc7a752c0d1f66002953f75517f82a1c` | `c8332228be6d09b1bf3e7019bba01faeec0613c26869d77e7ee02151aa842840` |
| saved result | `91ec4c81080d930665e28a1b291857d163375700` | `29a7785e58098e8eb7d21f8521e24546c65d79e0017c6ec28d7da54665596973` |

Raw input/output SHA-256 values are respectively
`b39dd5a9aa0a160f1ab923ab76cdb9bbef54f042a525178cfff833b99377bd07`
and `c1f12d43f12a65d99b06e6486abfa2a93a0945e26fdb4a18303978a2b5e08627`.

**Adapter status and replay:** `VT8-ADAPTER-STATUS-1`, normal exit 0; saved result,
manifest and unmodified offline recomputation all PASS with no errors.

**Public contract:** the exact ordered results are mount Side A `TAPE_OK`, public
info `side_b_valid=false`, reset Side B `TAPE_OK`, unmount `TAPE_OK`, and remount
Side B `TAPE_OK`. No extra public call appears.

**Trace and media:** input structural sequences are `[10, 900, 500, 500]`, with
live A0 and degraded equal-sequence B. Reset writes exactly B0 entry block 265,
flushes, writes header block 264, and flushes. All callback rc values are zero; all
mount/remount reads stay within metadata; `get_info` and unmount issue no I/O; no
chunk or superblock write appears. The retained media changes only B0 header bytes
(the rewritten entry block is byte-identical), preserves both superblocks and the
other three slots, produces sequences `[10, 900, 901, 500]`, copies the live-A entry
`(0,0,128)` with Side-B ownership, makes B0 live/selectable and retains
`free_next == H == 3`.

**Disposition:** the exact reset-side-B observation is accepted.

## `VT8-001-REC-ALLOCSEQ`

Case evidence tree: `e155ca0d7bdf9b5586abf2d3f8d3c6689accc617`.

| Artifact | Git blob | SHA-256 |
|---|---|---|
| adapter status | `44f1b3e1bda26c688e00ba2668a6781d30845c4f` | `06717e5ef3448ec0e988de82ec13c7b6a037599201c1cf3fa7c879838ec67ef0` |
| input archive | `21e2597498b586d6f2c549bf9dd04a7a191f4ee7` | `876c55a06620ef62e5cbcce102d9e70ed2a428cfac9d604ef7b7d52fe1ff6bde` |
| observation | `4358d331d353201c0c649ccb88e6188252d3d02b` | `2231de5dac266be14d192261ecb457b30bb7b61171cf87fe79694879c92bc12d` |
| output archive | `d46259a6244dd181a8c0dccd9743285aee15f218` | `c8bb23dd86dacdbca420c7a559f8b700ce40107829df3c72f3119d36e93836ca` |
| saved result | `2c5c10f049c9c9de2a272c6e11d1bf050d9d4727` | `3adb94cd3e17d0dec410e777765fb4beef0154660c2fca0832a37f12d9b1a0a2` |

Raw input/output SHA-256 values are respectively
`b3d87522ef3d8789b52916985beea8cdd25a517dc93063095be2abdbb6e7a4d7`
and `3e447210d5207de737a335e15546501bb14e73642a46d1fbf0a8790d48870e7f`.

**Adapter status and replay:** `VT8-ADAPTER-STATUS-1`, normal exit 0; saved result,
manifest and unmodified offline recomputation all PASS with no errors.

**Public contract:** the exact ordered results are mount Side B, seek frame 128, arm
`TAPE_REC_SPLICE`, feed requested/accepted 128, one service call with positive
eight-block budget and `more_work=false`, commit, unmount, and remount Side B; every
result is `TAPE_OK`. No extra public call appears.

**Trace and media:** input structural sequences are `[10, 700, 20, invalid]`, with
live B0 and `a_high_water == free_next == 3`. Seek, arm, feed and unmount issue no
I/O. Service writes exactly one block at LBA 5120 inside allocated chunk 3, flushes
before metadata, then performs one permitted chunk read at 2048. Commit writes B1
entries at 393, flushes, writes the header at 392 and flushes. All callback rc values
are zero; metadata reads remain in range; no service write is below H/outside chunk
3; commit writes no chunk data. The retained media preserves both superblocks and
A0/A1/B0, changes only B1 blocks 392–393, produces sequences
`[10, 700, 20, 701]`, commits entries `[(0,0,128),(3,0,128)]`, makes B1 live and
advances `free_next` from 3 to 4.

The sparse VO08 envelope retains superblocks/index slots rather than audio payload
bytes; the accepted chunk transition is therefore the exact zero-rc, in-range,
pre-metadata-flush callback observation, not a payload-content claim.

**Disposition:** the exact recording/allocation observation is accepted.

## Commands and results

```text
git rev-parse / show -s / ls-tree on exact verifier, routing, parent and evidence refs
  -> all named commits/trees authenticate; evidence has exactly the named sole parent;
     engine and adapter trees are unchanged by identity
sha256sum on manifest, run log, verifier sources and every case artifact
  -> all manifest/file/source/spec identities reproduce
python3 tests/ops_draft8/replay.py <exact product-evidence directory>
  -> both cases REPLAY PASS; bundle complete, hash-bound and DRAFT-8 authenticated
temporary verifier-owned raw traversal over status/calls/events/media
  -> both exact checks PASS; no unexpected call/write, forbidden region, nonzero rc
     or event overflow
make -C tests check
  -> exit 0; fault device, crash, audio, ops, three-family playback and complete
     playback suites pass
git diff --check
  -> PASS
```

## Exclusions and unchanged holds

No product/adapter implementation acceptance, source review, PR review/merge or
product modification occurred. Other arm or splice modes, partial drain, multi-chunk
allocation, short accepts, refusals, injected faults, warm start, abort, zero-frame
behavior, crash/recovery, quarantine, promote/re-spool/duplicate/format, performance,
atomicity, PCM, goldens, listening, WP-07 and the package remain excluded.

PRs #20, #64 and #96 remain held. DRAFT-8 and WP-08 remain frozen; WP-11 remains
red and listening-held. All safety, fabrication, charging, physical-work, purchasing
and Michael-reserved approvals remain unchanged. Next owner is PM for this narrow
two-observation disposition.
