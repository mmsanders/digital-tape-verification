# Digital-Tape Verification

Independent tests, oracles and dispositions for Digital Tape.

**3 October 2026: Phase 1 complete; preparing for Phase 2.** All nine Phase 1
engine packages are independently accepted within their recorded boundaries.
Verification #143 passed exact Product #369 head `b61a9e9`; Michael approved all ten
golden references on #367. See [current capability status](CAPABILITY-STATUS.md)
and the [durable Stage 2 disposition](findings/P1-R63-WP11-STAGE2-DISPOSITION-2026-10-03.md). Phase 2 awaits Michael's go.

The current cleanup is authorized directly by Michael and tracked in
[Product #378](https://github.com/mmsanders/Digital-Tape/issues/378). No Phase 2 verification assignment is implied.
Fresh work comes from Michael or the live
[verification-lead queue](https://github.com/mmsanders/Digital-Tape-Verification/issues?q=is%3Aissue+is%3Aopen+label%3Averification-lead).

## Start here

- [Agent entry point](AGENTS.md): canonical agreement and role boundary.
- [Tests and package index](tests/README.md): all 37 preserved publication trees.
- [Findings index](findings/README.md): dated dispositions and supersession notes.
- [Historical PM decisions](pm/README.md) and [PM log](PM-NOTES.md).
- [Historical spec copy](spec/README.md): root DRAFT-5 is not current authority.
- [Checks and review procedures](procedures/README.md).

## Publication and provenance

`main` is the authoritative publication point. Completed findings and packages
must land on `main`; an open PR is proposed work, not a publication (ADR-157).
Normal verifier publications use a merge commit after CI passes. This cleanup is
returned as a PR for Michael's review, as requested.

The canonical specification is [Product spec/VERSION.md](https://github.com/mmsanders/Digital-Tape/blob/main/spec/VERSION.md),
currently DRAFT-10. Package spec copies, package READMEs and ledgers describe their
original publication. Their bytes and identities remain pinned even when a later
finding closes an old hold. Current status belongs outside those imported trees.

## Independence

Author expectations and tests before inspecting implementation for that behavior.
Post-authoring exact-candidate dispositions may inspect the covered implementation
under the live assignment, as #143 did; this never licenses looking at uncovered
behavior to shape new tests. [Advisory PR review](procedures/independent-pr-review.md)
is a separate lane and cannot substitute for independent acceptance.

Phase 1 completion is engine/laptop acceptance. Hardware and media qualification,
target wake latency, audio cap, copy time and Product release remain excluded.
