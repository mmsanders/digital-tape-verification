# P1-R54-V-WP12D: Product PR #328 disposition (WP-12/WP-12a closure gaps)

**Verdict: PASS** for exact Product head `c126515d631338b63798613025985f73c1a8d355`, tree
`2a25a33c95f3e821640cf24abd31924b28404e58`. Scope: the three published gap rows, **7/7 cases**.

- Issue: Verification #123, body dated 2026-09-30T16:59:42Z, with no scope comments.
- Issuer: PM Product #305. This PR supersedes held #317.
- Inputs: Product main `66c6abc6` and Verification main `0ac2f8ed`.
- `engine/` was built and executed but never opened.

## Identities

| Object | Value | Checked |
|---|---|---|
| Head / tree / base | `c126515d…` / `2a25a33c…` / `66c6abc6…` | `git rev-parse` |
| Import `1c1c036e5050eb10db3532fd6fc8571b250414c7` | Sets `tests/wp12_closure_r53` = `5641e39d5b72f367468e2a8d121f6a0e6106fc2f`, which equals my #115 publication `c65ed4357c9d4b9fe915910e0a669d335e611a80`. Touches only that tree and `tests/IMPORTS.json`. Parent is `66c6abc6`. | `rev-parse`, `diff-tree` |
| Ordering | Publication 2026-09-30T14:35:19Z < import 15:36:30Z < binding 15:39:08Z. `engine/` is unchanged (`054d27ab…`). | commit dates |
| Ledger / plan | `795c05fe…76d4` / `55e36eac…97dc` | `audit.py`, replay |
| Pinned blobs | `respool_draft8/oracle.py` `3c63f190…` and `promote_draft8/fixture.py` `51c676bf…` are equal at the head, at main `66c6abc6`, and in `fixtures.py`. | `rev-parse HEAD:` / `66c6abc6:` |
| Adapter | `wp12c_adapter.c` `05d906fb14f224c77cd721cccfdc3be466faed0b0bcf73a02d98ad9f539098f3` | `sha256sum` |
| Retained evidence | JSONL `3e1fe20d…9ec2`; gzip `5e611991603a66b9c5b78d310b2104df827f41564eaa2d960d1aac8bb18f7c0e`; build-identity `80759ec7…9066`; census `87f390f4…b0ff` | `SHA256SUMS` |

## Runs (Linux, GCC 13.3.0, Python 3.11.15)

1. **My package at `c65ed435`.** `audit.py` passes: 36 rows, of which 28 are accepted, 3 are published,
   2 are unreachable and 3 are vacuous. `selftest.py` passes: 7 synthetic cases and 7 causal controls.
2. **Exact-head build and fresh canonical run with `--retained`.** The JSONL is byte-identical and
   replay passes 7/7.
3. **Independent replay of the retained Product gzip** with my oracle at `c65ed435`: **PASS 7/7**
   (`evidence/P1-R54-WP12D/replay-manifest.json`).
4. **Product controls.** All 7 cases pass `oracle.check`. **11/11 mutations were killed.** The
   mutations were: PCM changed; last frame dropped; render I/O; service touching the faulted device (×2);
   `arm` accepted after a fault (×2); `fault_call_index` mislabelled (×4).
5. **Early carry-over signal.** The same head, with #318's `engine/` `81ad8ec2` built in (not read),
   regenerates identical JSONL. This is only a signal; the CI `--retained` run after merge remains the
   authority.

CI runs were not readable from this session, because Digital-Tape API access is withheld by design.

### Census from the retained evidence

**Render cases.** For each case, the pre, post-same-session and post-remount renders are identical.
Each ends with `tell` equal to the timeline length.

| Case | PCM | Frames | Re-spool calls |
|---|---|---:|---:|
| RENDER-TWOPASS | `3b4b1554…` | 262,144 | 129 |
| RENDER-DECLINE | `a163f051…` | 10 | 1 |
| RENDER-FRAGMENTED | `38ce20b1…` | 28 | 1 |

**Fault cases.**

| Case | Calls | `fault_call_index` | The single failing callback | Failing call → | F cells FAULTED | Allowed OK | Device hash at fault = before unmount |
|---|---:|---:|---|---|---:|---:|---|
| F-RESPOOL-WRITE | 2 | 1 | write LBA 14368 (call 1, event 1) | `TAPE_ERR_IO`, `more_work` false | 11 | 4 | yes |
| F-RESPOOL-HEADER-FLUSH | 65 | 64 | flush after the B1 header write at LBA 392 (call 64, event 3) | `TAPE_ERR_IO`, false | 11 | 4 | yes |
| F-PROMOTE-WRITE | 3 | 2 | first write, LBA 5120 (call 2, event 0) | `TAPE_ERR_IO`, false | 11 | 4 | yes |
| F-PROMOTE-FLUSH | 3 | 2 | first flush (call 2, event 1) | `TAPE_ERR_IO`, false | 11 | 4 | yes |

Every F cell and every allowed cell has zero callbacks. `dup` touched no destination.

## Binding review

**Fixtures.** Device images are written block for block from my package's builders: `fixtures.py`, and
the pinned `respool_draft8` and `promote_draft8` builders. The oracle recomputes
`fixture_metadata_sha256` itself, so a wrong fixture cannot pass.

**Injection.** `should_fail` implements ADAPTER.md literally:
- It fires once, only while a long operation is running (`call_index ≥ 0`).
- `first_on_continuation` is the first callback of the planned kind with `call_index ≥ 1`.
- `first_after_write` is the first flush after the exact `(lba, count)` write.
- A refused write leaves media untouched.

If the plan's failure is never reached, the operation completes and my oracle goes red. The fallback
therefore cannot hide a miss.

**Recording.** Only `tape_render`'s own callbacks are listed per render, which is the contract's
`block_events`. The adapter emits no verdict fields.

**Budget-1 promote shape.** Calls 0 and 1 each read one block before the first write or flush on call 2.
This matches Engine API §9, under which reads are budgeted work. My contract deliberately fixes no call
index, and the oracle requires `fault_call_index ≥ 1` to name the failing call.

No finding.

## Exclusions

The 28 carried ledger rows are not re-run. Also excluded:
- the vacuous and unreachable rows;
- the PM finding "audio must not stop";
- complete WP-12/WP-12a, WP-10 and WP-11;
- hardware and release;
- any acceptance of engine behaviour beyond these seven observations.

**Next owner:** PM. When this merges after #318, the `--retained` CI regeneration carries this
disposition across.
