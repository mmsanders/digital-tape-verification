# P1-R1-V — VT8 hardened verifier return

## Disposition

The bounded Verification assignment from issue #3 is ready for PM review. This return corrects verifier-package gaps; it does **not** claim a new product-engine run or broader product acceptance.

Source verifier baseline: `689c41909e6bbec499aeb0243008222d7a1c9f64`.
Hardened source commit: `dcc4d7cdb357cf0b082071390c762c25b650f617`.
Hardened source `tests/ops_draft8/` tree: `4a862fa69ccb2fc4c9afe59c9c9161c3470f9263` (previous published package tree `c8a43df69a6be8e2c34bf79a1d79933abf48286a`).
Product input at activation: `40507bf44db2f2743abddcc0188674938f4db89e`.

## Assignment findings

- **P1-R1-V01 — resolved in verifier source.** Recording commit I/O is now checked as the exact inactive-slot sequence `entries write → flush → header write → flush`, with exactly two commit flushes. A reordered post-header flush mutation is rejected. Recording also requires a successful service durability flush after the final chunk-data write and before commit metadata begins.
- **P1-R1-V02 — resolved in verifier source.** The checker now inspects the whole scripted callback trace, not only service writes. `tape_feed`/seek/arm/unmount I/O is rejected, callback ranges use widened arithmetic, nonzero callback returns fail, and the public-call results/arguments needed to prove the intended path are persisted and checked. The PM feed-write reproducer is rejected.
- **P1-R1-V03 — resolved for verifier evidence machinery.** Runner evidence persists lossless deterministic-gzip input/final VO08 media with archive and decompressed-raw hashes, full callback and public-call observations, stdout/stderr, result records, adapter synthetic/product identity, adapter source/build identity, verifier source identity, and exact authenticated DRAFT-8 spec bytes. `replay.py` recomputes the verdict offline without invoking an engine/adapter and fails closed on missing/tampered evidence.
- **P1-R1-D01 — resolved as plan hygiene.** The three DRAFT-6 WP plan files are explicitly historical rather than current acceptance authority, with their prior full text retained in Git history. `tests/NEXT-TRANCHES.md` supplies a DRAFT-8 dependency-ordered proposal: playback/goldens → recording/random edits → complete crash closure including V7-001 two-interruption coverage → long operations/state matrix. It is planning only, not a self-assignment.

The original independent `oracle.py` media expectations and fixture generation were left unchanged. Hardening is layered in `hardened.py`, preserving the implementation-blind source of expected media behavior.

## Verification of the verifier

The hardened self-test accepts both conforming synthetic observations and rejects the original six mutations plus the P1-R1 ordering/whole-trace controls, a chunk-durability-barrier mutation, callback out-of-range/nonzero-rc controls, and a falsified public `tape_feed` accepted count. Spec-byte tampering is rejected. Synthetic runner plumbing is 2/2; offline replay passes; deleting required evidence or tampering a persisted output archive causes replay failure.

The saved synthetic bundle is under `tests/ops_draft8/evidence/p1-r1-synthetic/`. Its media raw SHA-256 values preserve the previously published fixture/result bytes:

- reset input `b3fef55d0f9abed54e58318d2f2fa6ae39d309f75c53a3434ede9a43fed7e56d`
- reset output `14f42962b872b9e06631e2cd7a402866717493f21ca3df01143922803e4687fe`
- record input `dd232f04e0c823bab7fa5397df290f75e56e0842335d32ad145072058e8cf43b`
- record output `9944d1740449d81c7678ed5c2d8e246147cad3a7834a6db8244cd30155af0dff`

The bundle includes the authenticated DRAFT-8 Git blobs from `tests/mount_draft8/spec/`; the verifier repository root `spec/` remains historical DRAFT-5 and is not used as DRAFT-8 authority.

## Boundary and next owner

No product engine source, implementation diff, or private implementer expectation was inspected. No product adapter was executed in this return. Therefore this work establishes only that the independent VT8 package/evidence path is ready for mechanical import and a subsequent real-product observation run. Full WP-07/WP-10/WP-11/WP-12a, operations/state freeze, crash safety, PCM goldens, hardware/media atomicity and all documented exclusions remain open.

Next owner is PM: review this immutable verifier return. After exact mechanical import/integration, real product observations should be returned to Verification for independent disposition.
