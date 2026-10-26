# Verification324 final exact-head disposition

26 October 2026 PDT. Manual Stage B request from Michael: check latest Software
work and decide approval. Inputs Product main `920f3d0594180ec00fa9e5ac165c06cfa1b76061`
and Verification main `0b1ed4f394a300513a6ced15d3e8c2f7c299f893`.
Live [324](https://github.com/mmsanders/digital-tape-verification/issues/324),
[584 return6419498762](https://github.com/mmsanders/Digital-Tape/issues/584#issuecomment-6419498762),
canonical four and required current scope read. Started6419606056.

## Disposition: PASS / exact component source cleared for protected integration

[Product PR587](https://github.com/mmsanders/Digital-Tape/pull/587) exact head
**3104e04e99a25933a34f0eae38fef6fd39b26802** is independently cleared for its
issued editing/details/concurrent-update component scope. Software owns integration
through normal current-base CI/reviews/protections. Verification does not merge
Product code or waive protected ownership/reviews. At review PR was OPEN/CLEAN,
merge-base=current main920f3d05, all120 checks SUCCESS, no pending/failed/skipped
checks. A changed source/base needs the ordinary exact-scope crosswalk/gates.
This publication becomes final only when merged on Verification main with green CI.

The reviewed production fix is label ownership across stale snapshots, preservation
of text/selection on rejected edits, an authoritative Start-over reset count,
unchanged open details preservation, and latest-only asynchronous details results.
`screen.mjs` blob77bf12f1, `app.mjs`756d680a, `state.rs`be93b550;
full16-entry source list is retained. `bridge.rs` adds only a cfg(test) adapter
module. No engine/firmware/tapectl/native discovery implementation delta.

## Independent expectation and repair provenance

- Original32-case r1 published by PR326/38c20dea, subtree
  478499b20c603965d5cc6bc838c6e909c0a7c4c3; Product import81d8dd97 precedes
  implementation2decba2f. Original r1 files/receipt remain untouched.
- PR327/0b1ed4f3 independently corrects six unsupported Windows selection-direction
  readback literals in new r2, subtree80ad54526d09ee763b04c4351d363831b8a39478.
  Product2859ebfc imports exactly that subtree and receipt, no other change.
  This Verification-owned correction followed covered source inspection; no
  retrospective test-first claim. All behavior, cases, ordering, actual selection
  preservation, UTF8/value/focus/details/reading requirements remain frozen.
- Final3104e04e only repairs workflow and deletes unsafe diagnostic-summary helper.
  `git diff 2decba2f 3104e04e -- host/ tools/app/interactions-dom.cjs` is empty.
  No new frontend behavior or tuned assertions. Both original and corrected test
  publications remain independently immutable.
- Workflow uses the exact r2 summary with direct ASCII-safe file output and checks
  each new control/emit/adapter/summary exit. Positive qualifier exit is captured
  immediately and nonzero throws, before later probe/list operations. The previous
  LASTEXITCODE mask is gone. Negative qualifier must fail and old score must be lower.

## Original evidence authenticated and independently replayed

[CI40341696181](https://github.com/mmsanders/Digital-Tape/actions/runs/40341696181),
job121637811427 SUCCESS on exact3104e04e. Artifact12660660080,
`software584-interaction-evidence`,49970bytes, archive SHA256
**e89e776a51a4459d0214246568bf8698e86379589e33c22ff04f3e0e9b54f70a**.
All12 original members are retained unchanged in `raw/`, with per-member bytes/SHA256
in manifest.json. Each is below1MiB. Download authentication and read-only Git audit
verified the exact base/import trees, unchanged reviewed source/harness,16 source
blobs, and actual served app/screen/style hashes against candidate and old main.

The strict positive qualifier exits0: **32/32**, covering12 editing,10 details,
10 ordering/lifetime cases. Both current and old records have all32 actual raw
captures/steps/RPCs/emissions; result captures match raw, frozen step order matches,
no page errors. Independent replay reproduces producer summaries exactly.
Negative control: pre584 renderer/binding from920f3d05 with the SAME current
coordinator and adapter scores **18/32**, qualifier nonzero. It is a renderer causal
control, not a full old binary. Earlier retained run scored19/32; this run additionally
loses E-ascii-caret text (`Roa Trip` versus `Road Trip`) during old snapshot delivery.
The unchanged adapter/raw show the existing timing-dependent stale-edit defect,
not altered expectations; other13 failing case identities are retained.

`review.py` reauthenticates originals, compares raw/result/order, reruns independent
qualification/summaries and proves a stale-label mutation is rejected. It executes
no Product or browser. Earlier failed CI/raw/partial cp1252 summary in the preceding
finding remains unchanged and is not replaced by this passing record.

## Method and limits

Observed by Software CI: isolated headless Edge155.0.4283.62 on hosted Windows
Server2025, production `mountApp`/`mountScreen` and actual Rust `Bridge`, wired by a
unit-test-only host facade. Keyboard/paste actions are browser test input; details
selection/scroll are DOM observations. Typed child outcomes and controlled
clock/completion releases exercise actual coordinator methods, not a reference UI
model. Unit-test adapter is excluded from shipping. No new shipping fake flag.

Verification independently inspected exact source/delta/adapter and retained raw,
ran only offline Python replay. No local browser/app/child/device/native run.
This is component coverage, not Windows11 native-window/real OS input/Tauri IPC,
OS clipboard, app-driven INGEST, physical/device safety or full-package acceptance.
Accepted backend286/297/discovery318 and one consumed metadata323 result carry by
identity without replay. Native/session/A6/INGEST-own-host/G1/S3/Make/elevation/
fullAPP/G2 holds, original STOPs and pre302 quarantine/process debt survive.

Next owner Software584: integrate ONLY exact cleared PR587 scope through normal
protections, then return integration identity. This supplies324 source clearance;
585/325 may use the actually integrated cleared outcome for its separately issued
ONE build/archive task. No artifact is preaccepted; UI METHOD HELD, no launch or
poller admission. Verification325 remains open for a later manual artifact review.
Close324 after merged disposition/direct584/PM583 handoff, then STOP.
Listeners remain PAUSED; no automatic next issue or chat activation.
