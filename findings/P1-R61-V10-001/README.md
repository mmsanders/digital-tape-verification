# Verification #141 evidence

Disposition: [exact Product #362](../P1-R61-V10-001-DISPOSITION-2026-10-02.md).
All committed evidence files are below 1 MiB; `SHA256SUMS` binds the retained files.
The large residue and S1 streams use the Product release assets and exact-head CI
artifact, rather than duplicate raw evidence in the Git tree.

## Actually executed

On a clean Product checkout at `db31c2919523fa821cf665058f4f883bf7403aae`:

```sh
make -C engine clean all
make -C tests/wp10_residue_adapter clean all
make -C tests/wp10_backlog_r54_adapter clean all
make -C tests/wp10_final_adapter clean all
make -C tests/format_dup_identity_adapter clean all
python3 -B tests/wp10_residue_d10/audit.py
python3 -B tests/wp10_residue_d10/selftest.py
python3 -B tools/ci/verify-wp13-carryover-gate.py
```

Set `TASK_EVIDENCE` to an empty, absolute reproduction directory outside Product.
The canonical runs were:

```sh
python3 -B tests/wp10_residue_adapter/run_product.py --evidence "$TASK_EVIDENCE/residue" \
  --retained tests/wp10_residue_adapter/evidence/p1-r60-product --jobs 5
python3 -B tests/wp10_residue_adapter/run_product.py \
  --replay tests/wp10_residue_adapter/evidence/p1-r60-product --out "$TASK_EVIDENCE/residue-offline"
python3 -B tests/wp10_backlog_r54_adapter/run_product.py --evidence "$TASK_EVIDENCE/s2" \
  --retained tests/wp10_backlog_r54_adapter/evidence/p1-r60-product
python3 -B tests/wp10_final_adapter/run_product.py --evidence "$TASK_EVIDENCE/s1" \
  --retained tests/wp10_final_adapter/evidence/p1-r55-product \
  --superseded tests/wp10_residue_d10/SUPERSESSION.json
python3 -B tests/format_dup_identity_adapter/run_product.py --evidence "$TASK_EVIDENCE/r29"
```

All pass. `residue-host.json` records the independently executed exact head and
toolchain. Retained replay manifests correctly keep the original binding commit
`f31ef48`; its relevant sources are identical to the disposed head.

## Independent supplementary checks

Use a separate Verification checkout at input main
`d99044b55ab17c09d5413040f3f4dc5ff27fd757` for the audit (it authenticates that
input snapshot explicitly). Copy `independent_audit.py`, `s3_probe.py` and
`wp13-exact-candidate.zip` to
`TASK_EVIDENCE`. The audit consumes the fresh S1/S2 directories generated above.
Unzip the WP-13 artifact into `TASK_EVIDENCE/wp13-ci`, then:

```sh
python3 -B tests/embedded_readiness_draft9/runner.py \
  --evidence "$TASK_EVIDENCE/wp13-ci/evidence.json" \
  --result "$TASK_EVIDENCE/wp13-independent-result.json"
python3 -B "$TASK_EVIDENCE/independent_audit.py" /absolute/Product /absolute/Verification
python3 -B "$TASK_EVIDENCE/s3_probe.py" /absolute/Product
```

The audit authenticates history, declarations, supersession ranges, all S1 byte
comparisons and 48 resurrected cells, S2's trace-only changes, all WP-13 artifact
members, both spec bundles, all 16 source hashes and the independent six-gate replay.
The S3 probe observes all 4,032 cases using the real unchanged public binding and
validates each with the independently published R29-B oracle. Its raw stream is
retained here as `s3-observations.jsonl.gz` (gzip -n -9).

`wp13-local-collection.log` is the failed local collection due to missing Clang;
it is not passed evidence. The exact-head CI artifact and independently reproduced
result supply the carried WP-13 check. The ZIP hashes to the CI upload digest.

## Remote evidence

- [Exact-head engine run](https://github.com/mmsanders/Digital-Tape/actions/runs/37045342906):
  residue, S1, S2, R29-B and WP-13 jobs successful. The only failed job is the
  excluded golden suite awaiting WP-11 listening/fixtures.
- [Residue job](https://github.com/mmsanders/Digital-Tape/actions/runs/37045342906/job/111051227879).
- [WP-13 artifact](https://github.com/mmsanders/Digital-Tape/actions/runs/37045342906/artifacts/11243914278):
  the exact downloaded ZIP is retained here.
- [Residue release asset](https://github.com/mmsanders/Digital-Tape/releases/download/evidence-p1-r60-wp10-residue/wp10-residue-d10-product-observations.jsonl.gz).
- [Accepted S1 release asset](https://github.com/mmsanders/Digital-Tape/releases/download/evidence-p1-r55-wp10-final/wp10-final-r54-product-observations.jsonl.gz).

Closure reconciliation is in `wp10-ledger-d10-disposed.json`; historical acceptance
is carried within its original boundaries. No Product status, spec, verifier oracle
or package source was changed by this publication.
