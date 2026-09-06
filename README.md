# digital-tape-verification

Verification Lead repository for Digital Tape.

## Publication rule

`main` is the authoritative publication point for verifier findings, current status, PM handoff notes, and verifier-owned acceptance plans. **Completed findings must land on `main`; a review branch is never the only authoritative location of a completed pass.**

The canonical product specification remains `mmsanders/Digital-Tape` `main`, authenticated by `spec/VERSION.md`. Any spec copies stored here are historical or courtesy inputs and do not override that publication point.

## Independence boundary

Pre-test verification does not inspect engine implementation, implementation branches or diffs, implementation issues, or unlanded implementation artifacts in order to derive expectations. Independent PR review is a separate post-authoring lane governed by `procedures/independent-pr-review.md`; implementation details learned there must not feed back into verifier expectations or tests that have not already been authored.
