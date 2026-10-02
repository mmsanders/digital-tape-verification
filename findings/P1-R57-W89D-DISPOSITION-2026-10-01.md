# P1-R57-W89D: Product PR #346 disposition and record bundle identity (Verification #132)

**Verdicts**

- **PASS 70 / 70** for exact Product PR #346 head `7a64891e63427a79d9f6755fac4e87dd1d37c343`, tree
  `0bf553e05dfa37c81e60a2ac4a5e9d833cb50f53`.
- **ACCEPT** the record bundle `tests/record_adapter/evidence/p1-r25-product/observations.jsonl` =
  `c461e9e00d47e6ae9c47827fbba68a2a796aed9b418f3aad94c6b34e3591db8f`.

Neither verdict is merge authority. Next owner: PM.

## Blindness

I read only the bindings under review: `tests/wp08_mapping_adapter/**`, `tests/wp09_gaps_adapter/**`,
the `tests/record_adapter/run_product.py` diff, the `ci.yml` diff, the retained evidence and the CI
logs. `engine/` was compared by tree SHA only and never opened.

## 1. Mechanical authentication of #346

| Item | Observed |
|---|---|
| Base | `480121099e33b6caf2a9f3169f39538135d0f6c6` |
| Import commit | `acdf00438ede16b7280e590134c767527cccf781`, sole parent base. It touches only `tests/IMPORTS.json`, `tests/wp08_mapping_r56/**` and `tests/wp09_gaps_r56/**` |
| Binding commit | `7a64891`, sole parent `acdf004`. It touches only `ci.yml`, `tests/IMPORTS.json`, `tests/record_adapter/run_product.py`, `tests/wp08_mapping_adapter/**` and `tests/wp09_gaps_adapter/**` |
| Imported subtrees at head | `wp08_mapping_r56` `466bf8193e53a39a4e5a51710ede9cd2b2458858` = Verification `5b7c3641`; `wp09_gaps_r56` `d8d6d6f8a9df02cb6125b73bedbde422afe5d909` = Verification `508ada85` |
| `engine/` tree | `81ad8ec2a35506042a44cb031726291f4bcd19be` at head, equal to current main `8ae6b63` |
| CI run 36819807308 | Every relevant job green, including the WP-08 mapped-run job, the #130 rows job and the WP-09 record job. The only failing job is `golden suite (awaiting WP-11 fixtures)`, by design |

I recomputed every source hash and every retained-evidence hash from the downloaded bytes. All
equal the build identities and `SHA256SUMS`:

| Bundle | JSONL | gzip | build identity | adapter C source |
|---|---|---|---|---|
| `wp08_mapping_adapter` | `6098222435464a3861643e2d90e1ae9f7d3dc213bfe2445c8fa7065e1a26c003` | `136c77ed0c9f299ebb11e991e37fc7cef2005b9865bb6c09ca9e13ef620b82a2` | `864dd874de069d4dda45a73916181497d59366be61097f49010a90ab1f012de4` | `4868944216f8c3d70452e27c26b268913af70148537ebdfe8f9802b8b509ce03` |
| `wp09_gaps_adapter` | `4c93da494e2f4523c64d8217180620dc3e379c3419d89cb512958bb0318c79d2` | `ba361839e5caf7056915cda61dbbd50efbb05c846e6d29dfde0aca0bdada1b3e` | `354e82ce59c1eb283b384f392f3b0302abb4ed6c9468610581a2ca8c2763faf1` | `fb6718e3e6a0c7e7980f51e7f5bcb2ec62274c0de4421f9b46e62662339cce49` |

The runners (`528185a1…43b3`, `727f756a…1537`) and Makefiles (`67349d06…f09f`, `8f8cbe37…b892`)
also match.

## 2. Independent replay through the unchanged oracles

I extracted the full `tests/` tree at publication `508ada857a5badf376da4428e87791333f1f0657`,
byte-exact with CRLF conversion off, so every pin resolves. Each audit passes, and each Product
replay is bound to the exact commit, tree and `adapter_source_sha256`:

| Package | Rows | Result | Case set |
|---|---|---|---|
| `wp08_mapping_r56` | `seek_boundary.mapped_runs` 60 + `reverse_end.mapped_timeline` 2 | **PASS 62** | `9eca914a4f2ed87db31bb5cd1212b89dec52731e37cdd76e1fb8aa2af8424e30` |
| `wp09_gaps_r56` | `overdub.full_scale_saturation` 3 + `respool_render.trace_floor` (V-R55-01) 5 | **PASS 8** | `5b14062694cfc1ef219612d8086bac56e0a1536680c129537548b687cfbc5fe0` |

The V-R55-01 row rides on the #336 bundle's JSONL `3ba932d2…`, which the build identity names. That
is the exact bundle Verification #128 accepted (PASS 207,584, comment on #128).

CI's Product-evidence controls (8/8 and 5/5) are consistent with the packages' own control
semantics. Both CI legs also report byte-identical regeneration against the retained bundles on
`81ad8ec2`.

## 3. Record runner change: redirect only

Before #346, CI ran
`run_product.py --evidence tests/record_adapter/evidence/p1-r25-product`. That **rewrote the retained
bundle in place on every run**, which is how `c461e9e0…` came to differ from the accepted
`a88850df…`. The binding changes it to `--evidence tests/record_adapter/evidence/product` (a fresh
directory) with `--retained tests/record_adapter/evidence/p1-r25-product`.

The new code only reads `retained/observations.jsonl` and compares bytes. On a difference it prints
`REGRESSION … (not resealed)` and fails. `--retained` without `--evidence` is a usage error. The
retained bytes are never written. **Confirmed: redirect only.**

## 4. Record bundle identity: ACCEPT `c461e9e0…`

1. **Authenticated.** `c461e9e0…` is byte-identical on main `8ae6b63adf94e6041526bd543a52dfee9edffb5d`,
   base `4801210` and head `7a64891`.
2. **Diffed against the accepted bytes.** `P1-R57-W89D-record-identity.py` compares against
   `a88850df…` read from the committed blob. All 26 records match in order. The only differences are
   on `WP09-ARMED-BUSY`:
   - `errors`: `["armed BUSY/abort path issued block I/O"]` → `[]`;
   - `expected_blocked`: `true` → `false`.

   These are Software-runner presentation fields; the old ones are stale output from before the
   PR #39 oracle correction. Every call, event, `input_sha256` and `output_sha256` is identical.
3. **Replayed through the corrected oracle.** The unchanged `tests/record_draft8/replay_product_evidence.py`
   (PR #39, merged `e9e6ec7`) ignores stored Software verdict fields, with only its pinned bundle
   SHA substituted by the authenticated `c461e9e0…`. Result: **26/26 PASS**. The printed
   `product_commit=9d3649d8…` line is a static label of the original P1-R25 disposition, not this
   bundle's provenance.
4. **Current-engine regeneration.** In CI job 110232735235 of run 36819807308, the record runner
   regenerated `observations.jsonl` on `engine/` `81ad8ec2` as
   `c461e9e00d47e6ae9c47827fbba68a2a796aed9b418f3aad94c6b34e3591db8f`, byte-identical to the retained
   bundle, with 26/26 cases passing.

**Ruling: ACCEPT** the exact bytes `c461e9e0…` as Product evidence for the `record_draft8` rows. The
integration may move the record bundle into `product_evidence_pins`.

Reproduce:

```sh
python3 findings/P1-R57-W89D-record-identity.py observations.jsonl
```

The script is `779f9b63114fb36f732585a476495967d3c6e76fa7c6c9e93b2dd80f41e1497d`.

## Exclusions

Complete WP-06 and WP-10 (DRAFT-10, #308), WP-11 and listening, hardware and release. No complete-WP
claim is made.
