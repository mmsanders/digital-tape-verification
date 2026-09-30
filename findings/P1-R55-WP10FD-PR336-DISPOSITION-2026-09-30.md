# P1-R55-V-WP10FD: disposition of Product PR #336 (WP-10 final backlog `wp10_final_r54`)

**Verdict: PASS** for exact Product head `68f919684f5ea8ea9877092d0e019cd1353142ba`, tree
`379b9fe4eac7f3f6c2db6e74da302beb7dedcc02`, on **207,584 / 207,584** cases. The V-R54-03 count is **48**,
exactly the published cell set.

The two rulings the issue asks for:
- **(a)** My published row-3 oracle does **not** pin the injection count or coordinates. I record that as
  verifier-owned finding **V-R55-01**. The Product evidence is independently shown to sit at the
  spec-forced floor, so it does not affect this verdict.
- **(b)** The release-asset evidence **meets** the offline-replay rule of CLAUDE.md §4.

## Inputs

- Issue: Verification #128, body as of 2026-09-30T21:42:22Z, with no scope comments.
- Issuer: PM Product #305, pass 7.
- The candidate's base is `d1ef2029`, where #318 and #330 are integrated and the engine is `81ad8ec2`.
- `engine/` was built and run but never opened.

## Identities

| Object | Value | Checked |
|---|---|---|
| Import `f5ffeef9faa2c9295a45a48a1498adc26e5cb1a6` | `tests/wp10_final_r54` = `598ebcd8f0914040558f565809b90bdb22bb8221`. This equals my #118 publication `7c0410e`, which predates the import. Parent `d1ef2029`. Touches only that tree and `tests/IMPORTS.json`. | `rev-parse`, `diff-tree` |
| Binding `68f9196` | Touches only `tests/wp10_final_adapter/` and one CI job. No `engine/`, `spec/` or `firmware/` change. | `diff-tree` |
| Adapter aggregate | `5dace9f0…cbda` | `build-identity.json` |
| Retained evidence | JSONL `3ba932d24221f9c7612170e6db23f9c84c9036fb4888f25966ec61fbc7201be3` (211,457,333 B). Release asset `wp10-final-r54-product-observations.jsonl.gz` = `1e3fc6737e51ef724fae145340cc19508adc42feafe80992e829d368f0c9bf98` (3,055,904 B). Build identity `5c4e6ae4…65d6`. | `SHA256SUMS`, the fetch below |

## Runs (Linux, GCC 13.3.0)

1. **Release asset.** I fetched it from `github.com/mmsanders/Digital-Tape/releases/download/evidence-p1-r55-wp10-final/…`. The download returned HTTP 200 and 3,055,904 bytes, with SHA-256 `1e3fc673…`, equal to the committed value. Its decompressed JSONL is `3ba932d2…`, also equal.
2. **Fresh canonical run at the exact head with `--retained`.** It produced 207,584 cases. The JSONL is **byte-identical** to the retained Windows evidence. Only the gzip container differs (`dbab7a45…`, from the local compressor), and the runner does not compare it. The runner's replay passed, with findings 48.
3. **Independent replay of the fetched asset** with my `oracle.py` at `7c0410e` (subtree `598ebcd8`): **PASS 207,584**.
   - Rows 1–2: 19 contract cases.
   - Row 3: 24,672 injections.
   - Row 4: 207,560 injections, 103,780 per mode.
   - Findings: `v_r54_03_resurrected_previous_superblock` = 48.

   The replay manifest is `evidence/P1-R55-WP10FD/replay-manifest.json`.
4. **Product controls: 10 / 10 killed.**
   - Rows 1–2: wrong result, a write on refusal, a changed Side A slot.
   - Row 3: wrong audio, a missing crash record, changed Side A audio.
   - Row 4: trace, durable state, a written source, first-run state.

I could not read CI run 36775870458 from this session, which has no Digital-Tape API access by design. Steps 1–4 reproduce it.

## Ruling (a): can a binding that skips a write shrink row 3's enumeration unseen?

**Against the oracle as published, yes.**
- `row3_injections` is derived entirely from the reported `clean.events`. The oracle requires only self-consistency: the crash list matches that trace, and each crash fires at its `prefix_len`.
- Control: I took the real RS-TWOPASS record, deleted one reported write, and dropped its 1,026 crash records with consistent renumbering. The oracle **accepted** it, with 6,168 → 5,142 records. (The Product control `row3_missing_crash` drops a record without its write, which is why it is caught.)
- An *engine* that really skips a write is still caught, because the clean run must re-render bit-identically. What goes unseen is an *adapter* that under-reports one. I publish no expected count because #115 leaves write partitioning unpinned.

**V-R55-01 (verifier-owned, not a condition of this PASS).** The row-3 oracle should pin the spec-forced floor. Per commit under tapefs §8, that is:
- at least ⌈T·4/512⌉ chunk writes;
- at least one entries write and exactly one header write;
- three flushes, in the §8 order.

It should also pin the commit count to the set §9.4 allows for each fixture: RS-TWOPASS, RS-FRAGMENTED and RS-CHUNK-CROSSING must commit twice; RS-ONE-COMMIT once; RS-REFERENCES-A once or twice. I recommend PM route this as a small follow-on strengthening row.

**Why this PASS stands anyway:**
- **The trace matches the floor exactly.** The Product clean traces sit at the spec-forced floor in every fixture:
  - RS-TWOPASS, RS-FRAGMENTED, RS-CHUNK-CROSSING: 2 commits = 6 writes (2 chunk, 2 entries, 2 header) and 6 flushes.
  - RS-REFERENCES-A, RS-ONE-COMMIT: 1 commit = 3 writes and 3 flushes.
  - Every per-commit data floor is 1 block.

  No write could have been removed without falling below what §8/§9.4 force.
- **The log sits below the adapter's own logic.** `wp10f_adapter.c` logs every read, write and flush inside the device callback. It derives `prefix_len` from the same device counter (`ncb`) that fires the injection.
- **Regeneration is byte-identical** on a second toolchain.

## Ruling (b): release-asset evidence and the offline-replay rule

**It meets the rule.** CLAUDE.md §4 requires, for raw evidence over 1 MiB:
- a release asset;
- the SHA-256 committed beside the run;
- a fetch-and-verify step shipped with the relocation.

Each is satisfied:
- **SHA-256 committed.** `SHA256SUMS` holds the asset, JSONL and build-identity digests.
- **Fetch and verify.** `run_product.py --replay` fetches the asset when it is absent. It refuses a digest mismatch before writing, then re-verifies the decompressed JSONL and `build-identity.json`. The CI job runs that replay.
- **Reproduced here.** I independently fetched the asset and it hashes to the committed values.

Minor notes, not conditions:
- The asset is not registered in the repository's standard `tools/fetch-evidence.sh`, so a reader who uses only that tool will not find it.
- A release asset can be deleted. Availability, not integrity, rests on the release. My fetch and hash are recorded here.

## Exclusions

- Complete WP-10: V-R54-03 still needs the DRAFT-10 spec fix (PM #308).
- WP-11, hardware and release.
- No acceptance of engine behaviour beyond these 207,584 observations.

**Next owner:** PM.
