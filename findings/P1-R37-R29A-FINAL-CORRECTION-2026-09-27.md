# P1-R37 Verification return — final R29-A correction and PR #257 binding audit

Date: 2026-09-27 UTC  
Issue: [Digital-Tape-Verification #84](https://github.com/mmsanders/Digital-Tape-Verification/issues/84)  
Frozen authority: TapeFS DRAFT-8  
Verification input: `74a2f96d5fa50972f2a20bc391fc6bd363554cb1`  
Product input: `867fd4ab3a447aca0a2b7bcc37aae444edce5e15`  
Audited product PR #257 head/tree: `8a4894a37cbc1780f47d600aec746acb51f59ade` / `d121e6695b7d62cb886c32ecff02ab503295afeb`

## Corrected immutable verifier package

Publication commit: `9a036f1dd5645acdf7c52866bd10c78e14cc2d49`  
Package tree: `197d2f2adbc9dba40d78bc1a1cd37c162858784b`  
Planner: 44,204 crash + 103 contract = 44,307 cases  
Planner SHA-256: `71be17545262d3b35fed9213b9305f71e4c8956693fbf4ec8f6d06f9f7ba80aa`

The package self-test and the unrelated re-spool package self-test both pass.
The promote self-test now includes red controls for allocating-branch
reintroduction, roomy-media masquerading as exact tail, shared-sequence
membership drift, closure mount repair/run-start drift, adapter-supplied counter
span drift, and Faulted ring-window accounting.

## F1 — unreachable allocating decline: CONFIRMED

For a valid live-B index, §5.1 makes the physical-frame intervals pairwise
disjoint. Every interval ends below `free_next * CHUNK_FRAMES`, so their summed
length satisfies `B.total_frames <= free_next * CHUNK_FRAMES`. Therefore
`len = ceil(B.total_frames / CHUNK_FRAMES) <= free_next`. The allocating branch
sets `S = free_next`; hence allocating `S < len` is unreachable on mountable
media.

Four old canonical cases are removed:

| Old index | Old case | Disposition |
|---:|---|---|
| 44228 | exact headroom, `fresh_alloc_decline` | removed: unreachable |
| 44237 | short sequence, `fresh_alloc_decline` | removed: vacuous |
| 44238 | short generation, `fresh_alloc_decline` | removed: vacuous |
| 44249 | `fresh_decline_seq_FFFFFFFB` | removed: unreachable |

The compact reindex is exact: old 44229–44236 become old−1; old 44239–44248
become old−3; old 44250–44310 become old−4. Reachable decline remains explicit:
first-use/adopt-in-place uses `S=0 < len`, and the row-1 RESUME-at-step-5 seed
retries the decline clearing write.

## F2 — exact tail: CORRECTED

Case 44220 now uses a dedicated four-chunk allocating seed. Before phase 1 it
has `free_next=3`, `len=1`, `total_chunks=4`: exactly one free tail chunk. The
row-4 seed has consumed that chunk, so `free_next=total_chunks=4` and the exact
device size is 6,145 blocks. Re-run must adopt the durable run at chunk 3 and
perform only the low phase-2 chunk write. The old 10,241-block seed and a false
`TAPE_ERR_CARTRIDGE_FULL` are both red controls.

## F3 — shared sequence: CORRECTED

Case 44252 reports the fixture's exact structural membership A=10/8,
B=500/499. This changes the documented A1 member from 9 to 8. The structural
maximum remains 500 and the required running commits remain 501, 502, 503,
504. The oracle now checks exact membership, not only the maximum.

## Product binding audit B1–B6

The audited old evidence is run 36290894614, job 108540634099, artifact
10921583978. Its ZIP SHA-256 is
`2b6a844806ebeaca57214252cd6e2d02cb336bf8ec694bd8eafca75b2b470edc`;
the diagnostic record SHA-256 is
`7c5e2a1993703accba8103967e76b17e95118e83e60061802509c1964e4f4f01`.
It ran all 44,311 old cases, validated 44,309, and failed only old 44228 and
44249. That run is diagnostic input, not reusable acceptance evidence.

| Binding | Disposition | Independent basis and red control |
|---|---|---|
| B1 closure mount repair | **PASS** | The worker marks mount scope, returns rc 5 before applying a repair write, and emits the setup trace. The corrected oracle requires `TAPE_OK`, a refused setup write, no successful setup write, exact run-start bytes, and exact pre-target bytes. A landed repair is red. |
| B2 step-4 in-flight closure | **PASS** | Step 4 starts from the ordinary allocating fixture with only the verifier seed's superblock pair substituted; the engine reaches phase-1 copy and steps 2–3 itself. `run_start_snapshot` and the immediately-before-partner `pre_snapshot` are now both byte-exact requirements. A direct-seed start is red. |
| B3 operation snapshot accounting | **PASS** | `progress_blocks` is assigned only from the progress callback. Event count and chunk LBAs filter the own device and promote call scope; service reads occur outside that scope. Oracle prefix/advance and unchanged-state controls consume the numeric facts, not the operation token label. |
| B4 Faulted render/ring | **PASS** | The separate 20,000-frame Playing fixture exceeds the 16,384-frame ring; `tape_arm` supplies the own-device write failure. The oracle now requires mount/Playing/IO/FAULTED raw facts, per-call `before = rendered + after`, exact PCM byte length, `ring_window_after ∈ {ring_after, ring_after+1}`, empty device trace, and terminal underrun. Bad window accounting is red. |
| B5 counter domains | **PASS** | The worker emits every call's counters and chronological block events. Verification now derives the entry→header and partner→candidate spans itself from raw write kinds; adapter-provided `index_only`/`superblock_only` labels are not evidence. Re-labelling the raw header event is red. |
| B6 crafted counter media | **BLOCK** | The old adapter emits `setup_media` names and mounted counter values but no raw setup snapshot or byte-difference proof. A name is not evidence that only sequence/generation/CRC bytes changed or that relative ordering was preserved. Software must emit the full setup snapshot (or an equivalent retained byte manifest) for every crafted family; Verification must compare it to the verifier base with only those fields normalized. |

## Exact file changes from old package tree

Old package tree: `2eb707d7e8ea721085164b85f5e2f397e115a036`.

| File | Old blob | New blob |
|---|---|---|
| `ADAPTER.md` | `adab9b8d078fdd6e3c2ed13ec114915dbf531c41` | `023787163c8674be7378bac953f3d3dec8c71b8e` |
| `COVERAGE.md` | `a0f9fd52805ca25bae53edc4ccb7fa4253f10be9` | `c079bd77a465468e5628841a23c1ed8667c44a3c` |
| `README.md` | `df32abc415ef6da8a4a3c6c3e0a5b037719095ec` | `139af831c1a8d7789d08d7fd5cc331161d7adff9` |
| `fixture.py` | `cad3a6f51bd3d6baf7b781b32f379a6bb53a1117` | `51c676bf4d788216d239da071c0679c600a811ce` |
| `oracle.py` | `06ba3d5c1d273b106824d614192b632d337a97f9` | `d604e3322e5058a50ce2e328057b84fa752d1a64` |
| `planner.py` | `a277b357da38fdf5afefd15971f5939e20232228` | `19b42229885514e31d1874d0ee2d5ac420ade3db` |
| `selftest.py` | `3ffc4879eea476312f297d201c6fced50c1620e2` | `6fdc10c25650093911966aa5cc7c5d7ea3255fd0` |

`Makefile`, `media.py`, `runner.py`, and `synthetic_adapter.py` are unchanged.

## Disposition and required next run

**Verifier package: PASS / ready for PM review. Product acceptance: BLOCKED.**

The engine implementation from exact PR #257 head may be reused mechanically;
this finding identifies no engine change. The old import commit, imported tree,
adapter digest/census, B6 evidence path, case-indexed results, canonical run,
diagnostic sweep, failure reproducer and artifact are not reusable.

Software must start a fresh Structural Rule 1 return: import package tree
`197d2f2a…` byte-for-byte as the first commit on the PM-issued base, then add only
the binding/implementation commit. Update the handshake to 44,307 cases and the
new digest, remove the four obsolete cases/media, consume the new exact-tail seed,
and add raw B6 setup-media evidence. Run all 44,307 canonical cases plus the
diagnostic sweep and evidence-integrity job on the resulting exact held head.
No result from PR #257 may be counted by prefix because all cases after the first
removal were reindexed and the oracle/binding controls changed.

This disposition does not merge PR #257, edit Product, reopen DRAFT-9 or R29-B,
or accept WP-11, hardware atomicity, complete WP-10/WP-12, consumer use, or
release use.
