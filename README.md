# digital-tape-verification

Verification Lead repository for Digital Tape.

Current assignment: [Verification #143](https://github.com/mmsanders/Digital-Tape-Verification/issues/143), WP-11 independent publication followed by exact-head Software #366 disposition. Stage 1 package and paper ledger delta are in [the R63 publication](findings/P1-R63-WP11-STAGE1-PUBLICATION-2026-10-02.md); Product execution and Michael's listening remain pending.

## Publication rule

`main` is the authoritative publication point for verifier findings, current status, PM handoff notes, and verifier-owned acceptance plans. **Completed findings must land on `main`; a review branch is never the only authoritative location of a completed pass.**

The canonical product specification remains `mmsanders/Digital-Tape` `main`, authenticated by `spec/VERSION.md`. Any spec copies stored here are historical or courtesy inputs and do not override that publication point.

## Independence boundary

Pre-test verification does not inspect engine implementation, implementation branches or diffs, implementation issues, or unlanded implementation artifacts in order to derive expectations. Independent PR review is a separate post-authoring lane governed by `procedures/independent-pr-review.md`; implementation details learned there must not feed back into verifier expectations or tests that have not already been authored.
