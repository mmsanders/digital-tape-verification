# P1-R22-V — blind disposition of the clean PR #112 two-case packet

**Disposition: the two exact recorded observations are narrowly accepted. READY
FOR PM REVIEW.**

The clean packet authenticates, both retained adapter executions exit zero, the
unmodified verifier-owned replay returns PASS, and a separate traversal of the raw
calls, callback events and before/after media finds the required transition for each
assigned case. No unexpected public call or write, forbidden-region access,
nonzero callback result, trace overflow, hidden retained-media mutation or evidence
tamper was found.

This accepts only the two observations named below. It does not accept PR #112,
product or adapter source, either candidate-only refusal policy, any unexercised
branch, or the verifier package as product behavior.

## Authority, blindness and immutable inputs

- Assignment: `mmsanders/digital-tape-verification#18`, observed open with the
  `verification-lead` label; no scope-changing PM or Michael comment was present.
- Input verifier main: `f00da3ffbaab62833cce52b29c4999934a37a9d2`, tree
  `dd2031338601186690474567544a4eaa154a75ec`.
- Product PM routing main: `662b07b0bb231f04e12542b905402ef9b980766e`,
  tree `08800dd3169d638306a1b21d6f69a68b2dff8ab3`.
- Evidence commit: `15fbcfae0085d5e2f2cb983959fe063c2233fa40`, tree
  `8f048f0296b7ffdcec216d26236d8d59ad392aa4`.
- Sole parent / pre-run code: `20505f4254b36c2100b9b1ec8f78aff8e95e252c`,
  tree `305525d207ba60750f45229838c20599fd6fc4be`.
- Assigned clean base: `86a1ba0874812ef4ca052a4dbc6baad2b16addb6`;
  it is the sole parent of the pre-run code.
- Complete run packet tree: `21354797871a34e19d907fba34ed1e8539bf9209`;
  exact `product-evidence/` child tree:
  `68e35dba49412ee971ce13efa08dc72dc8da638b`.
- Verifier package tree at both verifier input and evidence commit:
  `3667a2830ba80dbcedad03b97870d1127001ab59`.

The current Verification charter, issue workflow and P1-R22 PM disposition were
read before evidence inspection. Product engine and adapter source, PR #112's diff,
conversation, reviews and private tests, and implementer interpretations were not
inspected. The evidence commit changes only the named packet and leaves product and
adapter source unchanged from its sole parent. The current heads of PRs #20, #64
and #96 are not ancestors of the pre-run code.

## Evidence authentication

- Manifest: Git blob `16508c77b70347c8b5cabf43c934619f05e77794`,
  SHA-256 `e0af6d607d21579309ad97abcb89f69be6721e3d63c9226ee9af36799c565f44`.
- Run log: Git blob `c86c2bee4cf417ca7dd485c5cc2834a7b4929509`,
  SHA-256 `e61a5ddfbb6bd3ead1400812fd683617ed1819936e6d80eacb7dcc3bb1bea03f`.
- Recorded adapter executable SHA-256:
  `b075255359fc3f641fac9b62c6ec3923986f66009e30b77e44832f0147cf0ee7`.
- The packet binds the pre-run tree, adapter tree
  `6f6df812ae346933dff91aebb739feb0e2f0a113`, adapter-source blob
  `b920d111428f5407e604f0d5db12da331c4eed6c`, and candidate engine tree
  `65a72f78572223364c51e265fd68bffdda2b6518`.
- Manifest-bound verifier hashes reproduce: runner
  `d7e3ffe198d196e8024edef02abe0fbe9219b374cfe64d64f8fabfe907f1fadb`,
  hardening `0e88b276a1e94920f4df9f6ebf686cbd08f19f3986b63806cea04d83573ee0dc`,
  oracle `3e213af2a2bf5a439fe0aebcc83b7c2ccd1437692107fbc5a6bd6634500dcca5`.
- Frozen bytes reproduce: TapeFS
  `3bffa0ec46d7ba3779b02cbee6fac1edaf5094553f78270ee379759655147cbb`,
  Engine API `537eadc423e1a7bde726d689206b8fe93bef164d57e48e8ff71e07eaf8a7e3a1`,
  acceptance `7f78fba7b66b4fc6e96d15399c62468249bb30fbccbb59bf9f57b4532f56b6b7`.

The unmodified replay authenticates every manifest-described file, both archive
and decompressed media hashes, generated inputs, adapter statuses, observations,
saved results and oracle verdicts. It returns PASS for both cases.

## `VT8-001-RB-ALLSLOT`

Case tree: `f0b89524dd0a0fe664a3f1a05ac63d64e49ca3a7`.
The retained adapter status is normal exit 0. The ordered calls are exactly mount
Side A, get info (`side_b_valid=false`), reset Side B, unmount and remount Side B;
all return `TAPE_OK`.

The input slot sequences are `[10, 900, 500, 500]`. Reset writes B0 entry block
265, flushes, writes B0 header block 264 and flushes. The retained medium changes
only block 264 because the rewritten entry block is byte-identical; both
superblocks and every other slot remain unchanged. The result sequences are
`[10, 900, 901, 500]`, B0 is live/selectable with copied entry `(0,0,128)`, and
`free_next == H == 3`. All metadata reads are in range.

**Disposition:** the exact reset-side-B observation is accepted.

## `VT8-001-REC-ALLOCSEQ`

Case tree: `e155ca0d7bdf9b5586abf2d3f8d3c6689accc617`.
The retained adapter status is normal exit 0. The ordered calls are exactly mount
Side B, seek frame 128, arm `TAPE_REC_SPLICE`, feed 128/128 frames, one service
call with budget 8 and `more_work=false`, commit, unmount and remount Side B; all
return `TAPE_OK`.

The input slot sequences are `[10, 700, 20, invalid]` with
`a_high_water == free_next == 3`. Service writes one block at LBA 5120 in derived
chunk 3 and flushes before metadata. Commit writes B1 entries at 393, flushes,
writes its header at 392 and flushes. The retained medium changes only blocks
392-393; both superblocks and A0/A1/B0 remain unchanged. The result sequences are
`[10, 700, 20, 701]`, B1 is live with entries
`[(0,0,128),(3,0,128)]`, and `free_next` advances from 3 to 4. The only service
read is permitted LBA 2048; all other reads are in-range metadata reads.

The sparse VO08 envelope retains superblocks and index slots rather than audio
payload bytes. Acceptance of the chunk transition is therefore the exact zero-rc,
in-range, pre-metadata-flush callback observation, not a payload-content claim.

**Disposition:** the exact recording/allocation observation is accepted.

## Candidate-only refusal policies

The issue identifies two candidate policies that are not frozen requirements and
must not silently become acceptance semantics:

- splice-only `tape_arm`; and
- `TAPE_ERR_BUSY` on stage-1 media rather than clearing it.

Neither contaminates these exact paths. The recording case asks only for
`TAPE_REC_SPLICE` and receives `TAPE_OK`; overwrite, overdub and every other arm
mode remain unexercised and unaccepted. Independent decoding of both primary and
mirror superblocks gives stage 0 before and after both cases, and no call returns
`TAPE_ERR_BUSY`; stage-1 clearing behavior is therefore unreachable, unexercised
and unaccepted. No product-source inference was used for either conclusion.

## Verification commands and results

- Exact Git commit, parent, tree and ancestry checks authenticate the assigned
  chain and exclude PR #20/#64/#96 ancestry.
- SHA-256 and Git-blob checks reproduce all manifest, verifier, spec and case
  identities, including archive and decompressed-media hashes.
- `replay.py` on the exact packet returns PASS for both cases and authenticates the
  complete DRAFT-8 packet offline.
- A separate raw traversal of statuses, calls, events and decoded media returns
  both exact checks PASS, with no unexpected write/call, forbidden region,
  nonzero callback result, overflow or hidden retained-media mutation.
- `make -C tests check` exits 0: fault-device, crash, audio, ops, adapter-status,
  evidence/replay, three-family playback and complete-playback suites all pass.
- `git diff --check` passes.

## Exclusions and unchanged holds

No product or adapter source acceptance, PR review/approval/merge, or product
modification occurred. PR #112 remains unapproved and unmerged. Other recording
modes, stage-1 clearing, partial drain, multi-chunk allocation, short accepts,
refusals, injected faults, warm start, abort, zero-frame behavior, crash/recovery,
quarantine, promote/re-spool/duplicate/format, performance, atomicity, PCM,
goldens, listening, WP-07 and the verifier package remain excluded.

PRs #20, #64 and #96 remain held. DRAFT-8 and WP-08 remain frozen; WP-11 remains
red and listening-held. All safety, fabrication, charging, physical-work,
purchasing and Michael-reserved approvals remain unchanged. Next owner is PM for
this narrow two-observation disposition.
