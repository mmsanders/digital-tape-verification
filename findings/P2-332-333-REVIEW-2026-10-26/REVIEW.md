# Exact Software review — Verification332/333, 26 October 2026

Inputs Product9af79191671b4ce47732dc6cb3da269741ea5e4d,
Verificationd916750db4974467b9cc79a6e5f242b5baa2ecff; canonical four/live issues read.
Michael explicitly selected this review. No Product, helper, GUI, INGEST, poller,
observer, device, physical or native run was performed by Verification.

## Software595 / PR598 — EXACT-SOURCE INTEGRATION-ONLY CLEARANCE

Head **2416972fda46e64954787ea0989432016efd3cc4**, import
ba938decf61ff8bd850dd4472f8c9329cc0c181d, base9af79191, rootde1aaa230509e703941a71b396d2ff5dac26bd38.
SOURCE598.json records independent Git-object authentication: exact full host tree
835078995d4e9cc2424f9ea8d6f11304b45f783f, published Stage1 tree609a4c819076a2b85b26cc4f3cd254b92caef6de,
unchanged S1bdd861b693516db2e5244660b3e99ee400d506de, workflowblobd49e5983dbcca7492c067ec96a48371240a3e48d.
All217 changed paths are inside the declared six-item envelope. Two-commit ordering
is exact; IMPORTS preserves all old entries and adds the exact original Stage1 entry;
CODEOWNERS adds only its one line; evidence-integrity equals the original454 blob.
The independently expected workflow bytes match exactly, including just the two
manual-dispatch gates. No app/source algorithm/assertion/pin changes or old stacks.

Live full PR checks: **122 SUCCESS,2 SKIPPED**. Seven returned workflows all SUCCESS;
ingest run40394290783 includes vendor integrity, three builds/small identity runs
and byte identity. Its two skips are exactly Stage1/rehearsal; neither dispatched.
Evidence-integrity40394290812 and verifier-publication40394291681 are SUCCESS.
The previous I1–I8/own-HOST/S1 ledger carries unchanged; no corpus/accepted experiment
was rerun by Verification. The declared platform-only normative diff carries.

**Software may integrate precisely this source through current-base normal CI,
reviews and protections.** This is not a Product merge by Verification. If main
moves, preserve the exact cleared subtrees and disclose overlap; behavior/assertion
changes need independent coverage. Old459/454 may be retired as superseded ONLY
after protected integration authenticates this scope, preserving all historical refs.
No binary replacement or conflation of3895f3f3 with d923613b. Rung3 requires actual
integration and applicable green gates; this review alone advances no rung. Rung4,
Windows failed/zero-access own-HOST, physicalA6 where applicable, S3/fullAPP/G2 remain.

## Software594 / PR599 — HELD, first consolidated correction

Head **8a586742def0d8d1c254cb557e3fa48bb70a21c6**, import
a188888741b3be776111d264eadd493c48f4ab90, base9af79191. Exact r1 tree08b6d314
was imported before covered code. All120 other live PR checks SUCCESS; the one
failure is diagnostics run40398030607's original-oracle step. Component44/44 and
source-boundary checks are actual CI success, not independent source clearance.

Artifact12686538809 / evidence594.zip SHA256
**e71ffd6f7c877019499d1121fa8e79c029bd767bc41f928aaf855d7f4cc62f13**
is retained unchanged here. It contains CI-owned harmless-fixture paths only, not
Michael's private music. REPLAY.json records independent OFFLINE replay of22
envelopes:8 complete,13 incomplete,1 torn-invalid. Cumulative chain now passes with
original full epoch integers.32 captured blob/audio facts match available independent
harness originals. Success/refusal OFF/ON and five sink-fault projections match;
actual positive then7 PID/nonce/generation/seq/hash/wait/cleanup mutations are checked
without normalization. These are bounded consistency facts, not blanket acceptance.

The two reported oracle defects are Verification's errors; r2 fixes them, preserves
r1 and adds causal regressions. No divided timestamp or reshaped argv is accepted.

**F332-1 — limit termination/footer bound.** diagnostics.rs Inner::blob returns
`missing` for an oversized blob and continues collecting. The ORIGINAL C22 sequence
after over-limit stdout is blob,blob,audio,cleanup,reset,session-end. APP-1A §8 and
C22/C24 require collection to stop on limit failure with best-effort incompleteness;
runtime cleanup must continue outside the sink. Fix this, preserving child outcomes.
Inner::footer also lacks LINE_LIMIT checking; a long accumulated flaw reason can
write a >64KiB footer while total stays <16MiB. Apply the bound to EVERY JSONL line,
with honest incomplete/missing-footer handling. Add focused production boundary
controls, not a new full-campaign run. Existing C22 test expects the weaker sequence;
do not retain that as an acceptance assertion.

**F332-2 — actual executable/source binding and unknown identity.**
Provenance::of_running_app accepts BUILD.json source_head solely when child pins
match. Those pins stay identical across different app heads: a stale sidecar can
therefore misattribute the current exe. Compare the measured running app SHA to the
unique digital-tape.exe entry in BUILD.files as well; otherwise source is unknown/
incomplete. The existing packager already records this entry. The Session flawed
predicate must also reject unavailable/invalid app path or SHA rather than writing
a complete footer with an empty hash. Source association remains first-party and
requires external archive/runtime authentication for future native admission.

**F332-3 — cancelled report absent.** capture's `None if r.cancelled => {}` adds no
missing/flaw; gap skips cancelled terminals. A child cancelled before it creates its
report can therefore produce complete=true despite missing report facts. Record
the absence honestly and make the chain incomplete, retaining streams/terminal and
normal outcome/cleanup. Add the before-report cancellation boundary case. Existing
C06/C07 cover only cancellation after a report is present.

**C02 remains UNEXECUTED.** Runner_console_window=false and both actual helper
console observations=false, including the flag-removed run. This is not the required
positive contrast. C01 confirms no console association for that helper run, and
source uses CREATE_NO_WINDOW, but a gate with no effective positive control cannot
establish the missing policy contrast. Return actual C02 from the already published
permitted console-attached helper method if available, otherwise preserve this
precise component blocker. No new native window/provider/security workaround or
Michael564 rerun is requested or licensed.

Required next Software594 response: import corrected r2 first, fix these bounded
source/case defects, return exact new head/import + impacted originals + normal CI.
Rejudge unchanged originals offline; no unchanged actual campaign. This is response1
of maximum2 consolidated corrections. No599 merge/source clearance, no585 final build
yet. The path uses real native/command boundaries and shared Bridge/worker; originals
are captured after wait/before deletion, held relative non-reparse handles protect
receipt writes, and no shipping helper/diagnostic default-on switch was found.
Those positive source facts do not waive the listed defects or future native gates.

Original564/328/331 remains partial and immutable, F328-1's old PID unknown. Both
listeners PAUSED; direct GitHub return/STOP, no human repeat or new runtime admission.
