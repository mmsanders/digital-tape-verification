# Digital-Tape Verification

Independent tests, oracles and dispositions for Digital Tape.

**Phase1 is complete; Phase2 desktop tooling is active.** All nine Phase1 engine
packages are independently accepted within their recorded boundaries. Current
acceptance, native/physical limits and source identities are in
[CAPABILITY-STATUS](CAPABILITY-STATUS.md), [dated findings](findings/README.md) and
[Product STATUS](https://github.com/mmsanders/Digital-Tape/blob/main/docs/STATUS.md).
Old “pending/awaiting go” text in package publications is historical, not a new gate.

Live work comes from Michael or the
[verification-lead queue](https://github.com/mmsanders/Digital-Tape-Verification/issues?q=is%3Aissue+is%3Aopen+label%3Averification-lead).
Product #378 authorized the completed close-out cleanup; it is not a current assignment.
This navigation refresh changes no independent publication, oracle or disposition.

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
Normal verifier publications use a merge commit after CI passes. Navigation-only changes carry no acceptance claim and do not alter published package bytes.

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
