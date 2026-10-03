# Historical evidence replay tool

`replay_p1_r25_respool_evidence.py` independently audits the exact R25 re-spool
observations named by its arguments/defaults. It is a dated replay utility, not
an all-package verification command or current development assignment.

Use it with the authenticated Product evidence identified in
[the R25 disposition](../findings/P1-R25-PROMOTE-RESPOOL-DISPOSITION-2026-09-22.md).
Product's `tools/fetch-evidence.sh` and `tools/ci/` live in Digital-Tape; they are
not missing scripts in this repository. See [the test index](../tests/README.md)
for current package checks.
