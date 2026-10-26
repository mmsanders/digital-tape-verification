# Human564 partial-evidence index

Independent Verification328 pre-run human-visible index; no collector or UI model.

See [method and limits](../../findings/P2-328-HUMAN-METHOD-2026-10-26/README.md) and [operator sheet](../../findings/P2-328-HUMAN-METHOD-2026-10-26/OPERATOR.md).

Run python -B tests/windows_human_flow_r1/contract.py for16 synthetic corruption/attribution/staleness/partial-claim negatives; --emit gives an all-UNEXECUTED index; --input only validates index structure, never original authenticity. Original317 bytes/oracles remain unchanged.
