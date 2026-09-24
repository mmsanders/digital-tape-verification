# P1-R27 Verification return — exact WP-13 embedded-readiness product evidence

Date: 23 September 2026  
Authority: independent Verification, issue #64

## Disposition

**PASS — complete frozen WP-13 package acceptance is satisfied.**

Exact Digital-Tape PR #206 head
`80112aab895e5b97818151438aa7c7d0a118668a` may proceed unchanged to PM
routing.

Verification requests:
- no product behavior change for WP-13;
- no fresh product run solely because PR #205 was superseded;
- no additional WP-13 criterion.

This finding does **not** merge product PR #206.

## Exact candidate / Structural Rule 1

- product base:
  `92d6a3402d4908322c191bd3464011ae97f94114`
- verifier-import commit:
  `7bdfddb73cfa8e2021719a506eb02ceeaf2663bb`
- product-binding commit/head:
  `80112aab895e5b97818151438aa7c7d0a118668a`
- final product tree:
  `d932b35160345586a412f1d7a6eda300903156e1`

Independent commit-delta inspection confirms:

1. base → import commit changes only `tests/IMPORTS.json` and the seven files under
   `tests/embedded_readiness_draft8/`;
2. import commit → binding commit changes only:
   - `.github/workflows/ci.yml`
   - `tests/embedded_readiness_adapter/README.md`
   - `tests/embedded_readiness_adapter/collect_product_evidence.py`;
3. neither commit changes any `engine/` file.

Structural Rule 1 is therefore mechanically satisfied.

## Verifier identity

Verification publication:

- merged Verification PR #61:
  `3cdffae0671fa29f6d361a72c449f50331b26f4d`
- package publication commit:
  `82847985cd41e2b4b2fc086079ead7e5f2f7669e`
- immutable package tree:
  `46c8aa37f1f882e6a371fae7cdb5b96a28ada109`

The imported product subtree at `tests/embedded_readiness_draft8/` has exactly the
same tree SHA. All seven imported verifier blobs match byte-for-byte.

## Software collector / CI audit

No material binding defect was found.

The exact WP-13 CI job explicitly checks out the PR head:

`ref: ${{ github.event.pull_request.head.sha || github.sha }}`

and supplies the same value as `PRODUCT_COMMIT`. The collector then refuses if
workspace HEAD differs.

The collector invokes the ordinary product build:

- `make -C engine clean`
- `make -C engine all`

The retained build log shows the normal engine configuration on all 11 engine source
objects:

- `-std=c99`
- the product warning / `-Werror` set
- `-fno-common`
- `-g -Os`
- `-fstack-usage -fcallgraph-info=su,da`

No alternate optimization/macro configuration is substituted. The collector explicitly
fails if `-flto` is present rather than silently disabling LTO.

The resulting archive contains exactly the 11 expected engine objects:

- `chunks.o`
- `commit.o`
- `crc32.o`
- `mount.o`
- `ops.o`
- `play.o`
- `promote.o`
- `raw_ops.o`
- `record.o`
- `respool.o`
- `tapefs.o`

The exact product tree contains exactly the corresponding 11 `engine/src/*.c`
translation units.

The retained source inventory contains all 16 `.c/.h` files in `engine/src` and
`engine/include`. Verification independently fetched those exact candidate files and
recomputed every SHA-256 plus the engine Makefile SHA-256. **All 17 hashes match the
retained inventory/provenance exactly.**

Thus the raw reports and source scanner are bound to the exact candidate bytes, not a
different build/source tree.

## Corrected artifact authentication

Exact Actions run:

- run: `35950794760`
- job: `107478694346`
- conclusion: **success**

Corrected artifact:

- name: `p1-r27-wp13-embedded-readiness-evidence`
- ID: `10788656588`
- ZIP SHA-256:
  `0cc19676b8e658bf042b537386344bafea6dc931e2af58698640b31780b0f843`

Verification independently downloaded the ZIP and reproduced:

- `evidence.json`:
  `ee8008d6ed94ee582f999cd6b652c3bc7eea64955cfcbc6e79ca139fba7043f8`
- `result.json`:
  `2641575f756dccde1a885b9165138d151b6161d7fc7f320075b01bcf91958913`
- `PROVENANCE.json`:
  `25a5f11558c82e885654b68f970a4cbf2119556f7bce0db8e833c1debd183b44`
- `manifest.json`:
  `0932c9b40acbec99ad1e6c22ded431229d1e8a93654185f8522942d4ee4a3729`
- `raw/build.log`:
  `25c844ac28c6df3e24a12258e81fd063183edfa77343055d539f3e92f6c33ec3`
- `raw/engine-source-sha256.json`:
  `f4fc932bb68b373a8b727f43c2a68647796fcaa4f17b6232486b7b01942b6815`

The artifact has 105 files total. Its manifest names 104 payload files (excluding the
manifest itself), and Verification independently checked every listed byte count and
SHA-256: **all match, with no missing or extra payload paths**.

The corrected artifact retains, with distinct filenames:

- 11 per-object `readelf -SW` reports;
- 11 per-object `readelf -sW` reports;
- 11 per-object undefined-symbol reports;
- 11 per-object defined-symbol reports;
- 11 per-object `size -A -d` reports;
- 11 per-object relocation reports;
- 11 `.su` files;
- 11 `.ci` files.

Therefore PR #206 fixes the PR #205 case-insensitive filename collision cleanly. A new
engine behavior run is not required merely to repair that retention defect.

## Independent six-gate replay from raw evidence

Verification did not rely on Software prose or the saved `overall_pass` field.
The following values were independently recomputed from retained raw reports.

### G1 — RAM sum

Independent section parsing over all 11 engine objects gives:

- `.data` family: **0 bytes**
- `.bss` family: **0 bytes**

The verifier-owned `instance_size_probe.c` is part of the authenticated verifier
tree. Its retained build log links that exact probe against the just-built
`build/engine/libtape.a`, and its raw output is:

- `tape_instance_size() = 157600`

Independent total:

**0 + 0 + 157600 = 157600 bytes**

Limit: **204800 bytes**

**G1 PASS.**

### G2 — read-only data

Independent section-family parsing gives:

- `.rodata` / equivalent frozen family total: **1040 bytes**

Limit: **32768 bytes**

The retained symbol tables identify the three allocated read-only OBJECT symbols as:
- `crc_table`: 1024 bytes
- `SB_MAGIC`: 8 bytes
- `IDX_MAGIC`: 8 bytes

**G2 PASS.**

### G3 — allocator symbols

Verification independently scanned all 11 retained undefined-symbol reports.

No reference occurs to the forbidden allocator/free family:
`malloc`, `calloc`, `realloc`, `reallocarray`, `free`,
`aligned_alloc`, `posix_memalign`, `memalign`, `valloc`, `pvalloc`,
`strdup`, or `strndup`.

**G3 PASS.**

### G4 — maximum engine stack

The retained metadata contains **68 function records** in the `.su` set and
**68 function frame records** in the `.ci` set.

Verification independently compared their function/size/kind multisets:
**they match exactly**.

Independent call-graph audit finds:

- dynamic/unknown frames: **none**
- unresolved internal edges: **none**
- recursive cycles: **none**

Independent longest-path calculation reproduces:

**1536 bytes**

on:

`tape_mount -> resolve_superblock.constprop -> tape_sb_parse -> tape_crc32 -> tape_crc32_update`

Limit: **8192 bytes**

The compiler call graph contains 18 indirect-call placeholder edges. Verification
independently inspected every one: each is labelled at one of exactly the three
permitted `engine/src/dev.h` call sites (read line 50, write line 59, flush line 64).
No other unknown indirect edge is excluded from the engine stack graph.

**G4 PASS.**

### G5 — indirect-call confinement

Verification independently inspected the authenticated exact-head source inventory.

A fresh source scan finds exactly three member-call expressions:

- `dev_read -> read` in `engine/src/dev.h`
- `dev_write -> write` in `engine/src/dev.h`
- `dev_flush -> flush` in `engine/src/dev.h`

No fourth member-call site exists.

The public header also contains `tape_progress_fn`. Verification checked its exact
candidate uses: `tape_promote` and `tape_dup` receive a `cb` parameter but
explicitly discard it with `(void)cb`; it is **not invoked**.

An independent relocation backstop over all 11 retained `objdump -r` reports finds
no engine-function address stored in data/read-only-data sections.

Together with the compiler call-graph check above, this reproduces the verifier
classification:

- permitted sites: exactly 3
- violations: **0**
- ambiguous/unresolved: **0**

**G5 PASS.**

### G6 — no engine-owned mutable state

Verification independently parsed every retained `readelf -SW` and
`readelf -sW` pair and classified all allocated OBJECT/TLS symbols by ELF section
writability.

Result:

- mutable allocated OBJECT/TLS symbols: **0**
- COMMON symbols: **0**
- read-only OBJECT symbols: **3**

This check includes local file/function statics, so it does not depend on exported
symbol visibility.

**G6 PASS.**

## Verifier result replay

The independently reconstructed raw values agree exactly with
`WP13-EMBEDDED-EVIDENCE-1`.

The unchanged verifier-owned oracle therefore produces:

- six gate rows: **PASS**
- schema errors: **none**
- `overall_pass = true`

The retained verifier runner exit is **0**.

## Complete WP-13 acceptance conclusion

The frozen WP-13 package contains these six resource/structure gates. All six are
authenticated and independently reproduced on exact product head
`80112aab895e5b97818151438aa7c7d0a118668a`.

Verification identifies **no remaining spec-grounded WP-13 acceptance criterion**.

**Complete frozen WP-13 package acceptance: PASS.**

PM may route exact Digital-Tape PR #206 onward unchanged.

## Explicit exclusions

This finding does not imply acceptance of unrelated work packages, including:
- WP-07 allocator/COW behavioral fuzz;
- WP-10 crash/durability families;
- WP-11 golden/listening acceptance;
- WP-12 / WP-12a promote/re-spool continuation behavior;
- hardware/firmware timing or media-atomicity requirements.

Issue #64 may close as completed.
