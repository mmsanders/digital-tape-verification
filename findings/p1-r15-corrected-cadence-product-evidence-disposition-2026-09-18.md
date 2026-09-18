# P1-R15-V corrected-cadence product-evidence disposition

**Disposition: ACCEPT narrowly for the exact ten recorded playback families and
the exact 289 mount records; READY FOR PM REVIEW.** Corrected evidence cures
`P1-R12-V01`. One non-blocking packet-identity finding, `P1-R15-V01`, rejects the
run-tree value quoted in issue #12 but does not invalidate the correctly identified
inner product-evidence tree. No product, adapter, probe or firmware source was
inspected or executed.

## Authority and exact inputs

- Assignment: `mmsanders/digital-tape-verification#12`, observed open with the
  `verification-lead` label and update timestamp `2026-09-18T13:55:02Z`; no scope
  update followed the start comment.
- Product main named by the issue: `888f4dafcddcc4d7b96e8ec8e250dd5bb4062b63`.
  Current fetched product main at activation: `9143fd94626d5fba80976ba1c47ad28c2fd49a36`.
- Verifier input/main: `e3a25bf3b9eda6581b5de524e5bd5fa2c032e0da`.
- Pre-run product commit/tree: `b94ee2e33fd7fb8f6691e76a83d2392b6717e8a7` /
  `9a801f8b7e61f498e4a0459a640bc1aacf706c66`.
- Evidence commit/tree: `9204512b7f3f06ce6ce202db9f1e2a92e56e8d0b` /
  `78ecbe71ec38d854f77989408bd3f0b8a15fe623`. The evidence commit's sole parent is
  the named pre-run commit.
- Actual `docs/verification/runs/2026-09-14-r14/` tree:
  `ea34ba25cd5b67e739038b59f14dbecf69747d0f`.
- Product-evidence tree: `365dc5e83263e9c3a16d224c986e64c7895ab5cb`.
- Staged verifier-package tree: `2852667b98209f84143d96c5515c8819794c09f0`.
  Its 18 files match the corresponding files in verifier evidence commit
  `05e193209542d204669b32f485dad21007a084ee`, package tree
  `467a34bb0a84672c5bdef9059f2dd326d6435eb6`. Product main imports that same
  package tree; verifier main adds only its return outside the package.
- Manifest / observation / result SHA-256:
  `1e7f3aa6668ef91b652710247ac7a90ce8ebdc1d1350b483fd7b075834b07e72`,
  `4be2a12ca7c638ce256f6b09c2bda99a09e4fd42b63bad182491d8d084f0c7a8`, and
  `1fb3437a3fffb668ce92e3e6391f4d06d1ead07b8b24889a0264c9fe0d75f742`.
- Frozen WP-08 / TapeFS / Engine API / acceptance SHA-256:
  `ff519e960ed3db6e401baebd12f33d5527f83f0e4dfec12484f498470198a96a`,
  `3bffa0ec46d7ba3779b02cbee6fac1edaf5094553f78270ee379759655147cbb`,
  `537eadc423e1a7bde726d689206b8fe93bef164d57e48e8ff71e07eaf8a7e3a1`, and
  `7f78fba7b66b4fc6e96d15399c62468249bb30fbccbb59bf9f57b4532f56b6b7`.

The manifest binds exactly 30 non-manifest files. Independent enumeration found no
extra or missing path and every hash matches. Manifest and observation agree on
`kind=product` and adapter ID
`software-lead-complete-playback-public-api-probe-v1`. Source/build declarations are
present and hash-bound. The retained execution is `exited`, exit code 0, timeout 900
seconds; `adapter-exit.txt` is exactly `0\n` and stderr is empty.

## P1-R15-V01 — supplied run-tree identity is stale

**Non-blocking routing/provenance correction.** Issue #12 names run tree
`db88b71a833f07d24c443b989998a649c0405527`; the named evidence commit actually
contains `ea34ba25cd5b67e739038b59f14dbecf69747d0f` at the named path. The two trees
differ only in `README.md`: the stale tree includes two self-referential rows naming
the pre-run tree and evidence commit/tree, while the committed tree omits them.

The evidence commit/tree, sole-parent relationship, product-evidence tree, staged
package tree and every raw-evidence digest independently authenticate. Therefore the
incorrect outer run-tree value is rejected and corrected above, while the exact inner
product-evidence disposition remains possible. PM should use `ea34ba25...` in durable
status and future routing.

## Independent playback audit

The unmodified offline replay passes. The corrected verifier package also passes
deterministic authentication, all ten synthetic families, 22 behavioral controls
including both old-cadence controls, the retained P1-R4 18-control package, saved
replay, evidence-integrity controls, and the full verifier suite.

Separate raw-record traversal, not the saved count file, checked every public call
and all callbacks. Callback indices are ordered and in range; every callback is a
positive-count read with result 0 attached only to `tape_mount` or `tape_service`.
No callback is attached to render, seek, rate, status, info, tell, side-switch or
unmount. All public-call results, arguments, state fields and ordering match the
frozen contracts and the independently authored package.

| Family | Public calls | Callbacks | Frames | Disposition |
|---|---:|---:|---:|---|
| `empty_zero` | 6 | 8 | 0 | accepted raw call/state observation |
| `empty_nonzero` | 6 | 8 | 0 | accepted raw call/state observation |
| `nonempty_zero` | 7 | 14 | 0 | accepted raw call/state observation |
| `one_intmax` | 7 | 12 | 1 | accepted, byte-exact PCM |
| `reverse_zero` | 7 | 15 | 1 | accepted, byte-exact PCM |
| `intmin` | 8 | 15 | 2 | accepted, byte-exact PCM |
| `scrub_forward` | 1,414 | 90,003 | 88,200 | accepted exact corrected schedule and PCM |
| `scrub_reverse` | 1,415 | 90,056 | 88,200 | accepted exact corrected schedule and PCM |
| `side_playing` | 14 | 16 | 2 | accepted, byte-exact PCM |
| `side_idle` | 11 | 15 | 1 | accepted, byte-exact PCM |

Each scrub direction contains all 16 authoritative rates and 698 render requests:
35 requests in each of rows 0–14 and 173 in row 15. Immediately before **every**
render is a completed `tape_service(block_budget=1024)` sequence whose final call has
result 0 and `more_work == false`. Both directions therefore have 698 qualifying
service completions, render exactly 88,200 frames, and have no short render.
`P1-R12-V01` is cured in this exact observation.

The former observation hash was `24a35a3c...7ce4`; the corrected hash is
`4be2a12c...c7a8`. The saved result remains exactly `1fb3437a...f742` because the
service-only cadence correction changes call/callback records but not rendered PCM.
That unchanged result was recomputed from first principles and is valid.

All seven outputs match verifier candidates byte-for-byte:

| Family | SHA-256 |
|---|---|
| `one_intmax`, `reverse_zero` | `911beffad40098d1dc520cbe58946c7179d7f8d9334f9813aabb223bf11ccc47` |
| `intmin` | `d844e1554b5c802b4cc27c59d7503f3117296f7928d3d24dc87679a3e32a27dd` |
| `scrub_forward` | `41e882e74e3c64d929fcc76ad47b52f72ce9ed1541e971497b3c9a04fb46006b` |
| `scrub_reverse` | `5f1794e8dcd7c1b3e2c390a1aef33039f5b88b20f682c56c4aa6f94051bd8fa1` |
| `side_playing` | `8cde253ff03900ec30ecc695b700913a442ede54fd8b45a1dd06a6fe6e0206e1` |
| `side_idle` | `3f9f540229960d11ed73b7ff1fae0b6f26f723ea5c80d238976fc4c902cea28b` |

This is byte comparison only. The PCM is unlistened, unaccepted as a WP-11 golden,
and not a human-listening claim.

## Independent mount audit

The current raw log SHA-256 is
`af6474c48169e90ee1242d128f525fa2add295644a7124e53e51d73cb55a7a41`.
It contains one provenance header plus 289 unique case records in the exact
independent case set. Fixture hashes, allowed results, parsed stdout, callback
accounting/ranges, stored errors and stored status all independently recompute:
**289 pass, 0 fail**. The three named boundary cases are:

| Case | Expected / actual | Writes | Flushes |
|---|---:|---:|---:|
| `M-stage-row3-side0` | `0` / `0` | 0 | 0 |
| `M-stage-row3-side1` | `0` / `0` | 0 | 0 |
| `M-stage-unmatched-row3-H-boundary` | `8` / `8` | 0 | 0 |

After the provenance header, all 289 JSON records are byte-identical to the earlier
independently accepted P1-R12 log (tail SHA-256
`aa0e047760d726df058b800448ad62f5ff29fc3a546d2aa1234cf58b0c48fe65`).
The earlier probe SHA-256 was `57b8274e...ed7`; the current header binds the exact
current executable as `c0e98c56...2f1`.

The changed executable hash is not treated as equality. For this narrow regression,
the provenance is sufficient because the immutable packet identifies the exact
pre-run commit, the evidence commit is its sole child, the product mount-package tree
`4aaa1499429cbdc658065ac336ecab4783d1d730` exactly matches verifier main, the three
declared engine-source SHA-256 values independently match the pre-run commit, the
same packet binds the current engine archive/current playback build, and the mount
header binds the exact current probe. The run is accepted only as the 289 recorded
observations. No reproducible-binary, source-design, helper, allocator, complete
WP-06/WP-08, implementation-wide or merge acceptance follows.

## Commands and results

Executed against clean archives of the frozen public contracts, verifier-owned
packages, raw evidence and Git identity metadata:

```text
git cat-file / rev-parse / ls-tree <exact refs and paths>
  -> commit, parent, tree, package and evidence identities above
sha256sum <spec, WP-08, manifest, observation, result, PCM and mount logs>
  -> all assigned inner-evidence hashes match; P1-R15-V01 on outer run tree
PYTHONDONTWRITEBYTECODE=1 python3 input/package/replay.py <product-evidence>
  -> REPLAY PASS
PYTHONDONTWRITEBYTECODE=1 make -C tests check
  -> full verifier suite PASS
PYTHONDONTWRITEBYTECODE=1 make -C tests/mount_draft8 check
  -> ten independent mount-package tests PASS
PYTHONDONTWRITEBYTECODE=1 python3 p1r15_audit.py
  -> 30/30 manifest files; ten families pass; 698/698 corrected cadence in each
     direction; seven PCM comparisons pass; 289/289 mount records pass and match
     the earlier accepted records after the provenance header
cmp <current mount records after header> <prior records after header>
  -> byte-identical
```

## Boundary, holds and next owner

This accepts only the exact raw observations at the hashes above. PR #77, #64 and
#20 remain draft and held; no merge is authorized. No allocator, recording,
crash/recovery, warm-start, complete state/operations, performance, hardware/card,
purchase, qualification, fabrication, charging or safety acceptance follows.
Frozen hashes, exclusions and Michael-reserved approvals remain unchanged.

**Next owner: PM.** Authenticate this return, correct the stale outer run-tree value,
and decide any separately authorized product routing. Closure of issue #12 records
Verification's stop, not PM acceptance or permission to merge.
