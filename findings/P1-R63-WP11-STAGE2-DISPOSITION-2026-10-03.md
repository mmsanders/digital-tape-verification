# WP-11 R63 Stage 2 disposition — 3 October 2026

This file preserves the completed [Verification #143 Stage 2 return](https://github.com/mmsanders/digital-tape-verification/issues/143#issuecomment-5965215837) verbatim below. It records the disposition already made; this cleanup does not rerun or broaden acceptance.

## Subsequent closure

Michael [approved all ten references](https://github.com/mmsanders/Digital-Tape/issues/367#issuecomment-5966118444) after the return. Product #369 was merged at `d93ca4e` with the disposed tree unchanged, as recorded in [Product STATUS](https://github.com/mmsanders/Digital-Tape/blob/594aa59048893b8009145517ce186205536ef93d/docs/STATUS.md). The historical pending-listening and open-PR statements below describe the time of the return.

The immutable Stage 1 ledger remains at `tests/wp11_ledgers_r63/ledger.json`. Its `listening_held` and `stage2_pending` entries are closed by this return plus Michael's approval; do not rewrite that imported ledger. WP08-L04 closes on the exact candidate's source-structure confirmation. Phase 1 is complete within its engine/laptop boundary. Hardware, media qualification, target measurements and release remain excluded. Operations freeze awaits PM declaration at Phase 2 kickoff.

## Original Stage 2 return (verbatim)

## Stage 2 disposition — PASS exact Product #369 head `b61a9e961f22fba9134dc5f1db0d5d19da3016d8`

I reopened #143 because it had been closed after Stage 1 without a Stage 2 disposition. I have now disposed the exact Software return required by this issue.

**Candidate:** Product PR #369, branch `software/366-wp11-tooling`, base `41d546f4d799dbe8642135cc228ac50de2869b9c`, exact head **`b61a9e961f22fba9134dc5f1db0d5d19da3016d8`**, tree **`8645a50eed19dbbf4ec9c1cd0b7920cb7d2d4e60`**. PR remains open/draft and is not merged.

### 1. Identity and order — PASS

Exact chain:
1. `5d34a08e70d88ec31ab18d58b1bf523496f7c873` — `host/*`
2. `ef47a4e1a4757ecd555f41516cf98eed42ac295f` — test-only hook
3. `c27e525a20cc95429df2843dc01550b098edee8a` — Stage-1 CI/tooling
4. `8281b50f6e86137702241012d5f7b1fc4b232fa7` — pre-import move of the old Product golden-runner contract
5. `9eb60c1387d83c796031005d84b242ec28db4ec6` — verifier import
6. `b61a9e961f22fba9134dc5f1db0d5d19da3016d8` — binding only

At the import commit, the three subtrees are byte-identical to Verification publication `cdf89f5f0ab0aa8cc94c13fbf0f98fea484975a4`:

| subtree | Product @ `9eb60c1` | Verification @ `cdf89f5` |
|---|---|---|
| `tests/golden` | `999cd1be3c86960bf607eed6da71d918c8e503de` | same |
| `tests/wp11_portability_r63` | `8cdd5a13e7384fff9617a75cc6768a55d589b742` | same |
| `tests/wp11_ledgers_r63` | `bad836c8324a49b9d1bdcc46ab3e45071435c13a` | same |

The final binding commit changes only CI/binding/asset-plumbing files; it does not edit any imported verifier subtree.

**ADR-158 test-hook exception accepted for this round.** The hook is the explicit PM-issued item 3 interface that Verification Stage 1 authored against before inspecting implementation. It is test instrumentation, not an engine behavior change. From base `41d546f` to this head:
- `engine/src` tree is unchanged: `90afee5345ef9ae571d21a949b65d01909c3862b`;
- `engine/include` tree is unchanged: `d7708e188a6be43fa8c7260a8626afe3c1f04873`;
- `engine/Makefile` is unchanged: blob `041ed14ec884fe15cf01d97b7c06073219f2a702`;
- only `engine/test/tape_test_hooks.{h,c}` is new.

The current Structural Rule 1 checker does not recognize these R63 package names. That is **not a blocker for this exact candidate** because the order and identities are manually authenticated here and the exception is ADR-158-authorized, but PM should treat generalizing the checker (preferably from `tests/IMPORTS.json`, with the ADR-158 test-only exemption explicit) as CI hardening rather than relying on package-name patterns.

### 2. Golden equality — PASS machine gate, human listening still held

The imported MANIFEST is unchanged and every command uses `build/host/tapectl`. The runner executes the manifest command and byte-compares its WAV against the verifier reference.

Exact-head CI: **10/10 bit-identical**
- play-1x-quiet
- play-1x-fortissimo
- scrub-forward
- scrub-reverse-1x
- scrub-reverse-2x
- splice
- overdub
- overwrite
- reset-b
- promote

I also inspected `tapectl`: the relevant commands compose the public engine API (`tape_mount`, `tape_service`, `tape_render`, `tape_feed`, `tape_commit`, `tape_promote`, `tape_respool`, etc.); no interpolation, saturation, splice, or overdub behavior is reimplemented there.

This is **not yet human golden acceptance**. Product #367 is still open and has no Michael APPROVE/REJECT reply. WP-11's listened-golden requirement therefore remains held.

### 3. Test hook / §8 reachability — PASS

`engine/test/tape_test_hooks.c` includes the exact unmodified `engine/src/play.c` and the wrapper is only:

`return play_interpolate(a, b, f);`

The exact `play.c` function is the §8 arithmetic, and `tape_render` calls that same static `play_interpolate` for both channels. A scan of all eleven `engine/src/*.c` files finds the interpolation implementation only in `play.c`.

The hook object is linked **ahead of** `libtape.a`. Because it compiles all of `play.c`, it already defines the external symbols that `play.o` would supply, so normal static-archive extraction does not pull `play.o`; the ARM link/run succeeds with that construction. I accept this as reaching the engine's own §8 code, not a copied oracle.

This post-publication source inspection also closes the old WP08-L04 source-structure limitation for **this exact candidate**: §§6.2/6.3/8 playback arithmetic has one engine implementation in `play.c`, and the Stage-2 differential reaches that implementation.

### 4. Portability — PASS

Exact-head CI ran the unchanged Verification harness with the README flags and passed **11,572,876 / 11,572,876 comparisons in each configuration**, seed `0x63d10a5e`:

- host GCC 13.3;
- `arm-none-eabi-gcc` 13.2.1, Cortex-M3 Thumb, executed under `qemu-arm`;
- the WP-11 permitted static-assert alternative.

**ARM/newlib include path: accepted as mechanical binding.** Ubuntu's ARM compiler/newlib packaging otherwise pairs the compiler's freestanding `stdint.h` with newlib `inttypes.h` missing the 64-bit PRI macros. The script discovers the installed newlib include directory from that toolchain and adds it with `-isystem`; it changes no verifier source, case, value, range, or expected result and the engine/hook/harness all compile under the same target headers.

**Configuration (c): accepted.** DRAFT-10 acceptance WP-11 explicitly permits “a static assertion on `INT_MAX` plus a compile-time check that the operands are cast before subtraction.” The gate compiles assertions for `INT_MAX`, 64-bit `int64_t`, and 16-bit `int16_t`, then inspects clang's AST for `play_interpolate` and requires explicit `int64_t` casts on both `int16_t` operands before subtraction. Its causal control changes the expression to `(int64_t)(b - a)` and goes red. This meets the specified alternative; a physical 16-bit target is not additionally required.

### 5. Mutation gate — PASS 7/7

I reviewed all seven patches against acceptance WP-11. They are faithful behavioral mutations, and exact-head CI independently catches each:

| # | disposition | first catching verifier suite |
|---|---|---|
| 01 chunk-boundary off-by-one | PASS | `format-dup-package` |
| 02 commit before chunk durability | PASS | `record-package` |
| 03 sequence not incremented | PASS | `golden` |
| 04 wrong CRC byte range | PASS | `golden` |
| 05 Side-B allocation one below `a_high_water` | PASS | `record-package` |
| 06 overdub clamp replaced by cast | PASS | `golden` |
| 07 warm start accepts wrong UUID | PASS | `transport-package` |

For **05**, changing all three relevant floor guards is correct for a mutation test: the earlier one-site draft was behaviorally unreachable, while the current patch actually permits the prohibited one-below-floor allocation.

For **07**, removing the UUID guard is a faithful instance of accepting the wrong `(uuid, side, frame range)` tuple. The landed verifier transport package separately contains the required NULL/data-NULL/zero-frames/short-buffer/past-end/near-`UINT32_MAX`/exclusive-end/wrong-UUID/wrong-side/valid cases, so the broader warm-validity fixture requirement is present.

The benign comment-only control survives all 28 suites; the mutation gate correctly treats that survivor as red. Therefore the gate is shown able to detect a coverage gap rather than merely going green unconditionally.

### 6. Ledger import/self-check — accepted

The Product-side `tests/wp11_ledgers_r63` subtree is byte-identical to the published Verification tree. Its full `audit.py` necessarily reads verifier-repository `findings/` and therefore does not run meaningfully in Product.

That is acceptable: the full audit already ran green on the Verification publication before merge:
- 63 rows bijective;
- WP-12/12a = 31 covered, 2 unreachable by spec, 3 vacuous, **0 open**;
- `open_behaviour_gaps = 0`;
- listening-held = WP08-L01, WP08-L14, WP09-L01.

On Product, exact subtree identity plus verifier-publication authentication protects those bytes; parsing `ledger.json` is sufficient as the local self-check.

### 7. Release assets — PASS

All four `wp11-r63-canonical-v1` assets in Product's `RELEASE-ASSETS` match `tests/golden/SOURCES.json`, and the release server reports the same SHA-256 digests:
- music original `1c1be6b3…`
- voice original `0a9b05a0…`
- music canonical `5587b827…`
- voice canonical `b8aded0b…`

Exact-head `wp11-release-assets` fetched and hash-verified all four successfully.

### 8. Folded Phase-1 ledger after this PASS

- **WP-12 / WP-12a:** closed at the machine-evidence level: 36 rows, 31 covered + 2 unreachable + 3 vacuous, zero open.
- **WP-08:** all machine/behavior rows are covered; WP08-L04's prior source-structure limitation is now confirmed on this exact candidate. **WP08-L01 and WP08-L14 remain listening-held** pending Michael #367.
- **WP-09:** all machine/behavior rows are covered. **WP09-L01 remains listening-held** pending Michael #367.
- **WP-11:** golden byte equality PASS 10/10; portability PASS on host + embedded + static-assert alternative; mutation PASS 7/7. **The only remaining WP-11 hold is Michael's human listening sign-off on #367.**

### Exact-head CI

On `b61a9e961f22fba9134dc5f1db0d5d19da3016d8`:
- engine workflow **PASS**
- evidence integrity **PASS**
- verifier publication **PASS**
- repo hygiene **PASS**
- WP-11 golden **PASS**
- all three portability jobs **PASS**
- mutation gate **PASS**
- release-assets gate **PASS**

## Disposition

**PASS — exact Product #369 head `b61a9e961f22fba9134dc5f1db0d5d19da3016d8` is ready for the next owner under ADR-158.**

No Product merge is performed here. Hardware, media qualification and Product release remain excluded. Golden/listening acceptance is still reserved to Michael #367.

Next owner: **PM after Michael's #367 reply**, per ADR-158.

