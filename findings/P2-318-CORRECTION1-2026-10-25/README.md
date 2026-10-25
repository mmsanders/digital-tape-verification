# Verification318 correction review — Software578 / PR580

25 October 2026. **PASS for the exact covered discovery source/component delta;
Software may integrate PR580 at f9306c2c through normal current-base protections.**
The one separately described metadata-only command below is conditionally admitted.
It has not run. No native app/UI, physical, safety or full-package acceptance follows.

Michael manually requested “Okay check again”. Current Product main is
`1cf5577099ecc4445e8465bfb9addb1d780008eb`; candidate
`f9306c2c5a42ebd039edd67b0b7cef6a7d434b2b`; Verification input
`55ecd4b056d644e0ca6fca3e64085a676c94e4d5`. Canonical four and live318/578/580
read. Started PR580 comment6402664360; Software return6402307067.
No issue reopened, new assignment, chat/subworker or listener. This is the manually
requested disposition of the already authorized correction response1. Existing
granular tool approvals were used only for ordinary fetch/download/publication;
no permission/settings change. Reviewer remains separate from Claude Software.

## Two published findings resolved

**V318-01:** `Core.stopped` is now checked while registering discovery under the
same core lock shutdown uses to set stopped/invalidate/cancel. Either registration
precedes that cancellation pass or it is refused. The production poll step still
does its preliminary fast exit but cannot turn that into a late current ticket.
The publication/core locking and current-ticket rejection serialize publications
against shutdown's invalidation. The flag belongs to Core and is not reset by
App::start_over. The only pause hook is cfg(test), no shipping selector.

`raw/correction1.json` records a due production poll step paused before registration,
shutdown completed, then resumed: refused=true, registered=false, no active ticket,
zero child callbacks/current publications/emissions after resume. The test calls
actual `poll_once` and `discover`, not an independent copy of the admission rule.
The unchanged capture retains the opposite already-registered blocked-child order:
stop/invalidate/cancel/terminal/stale-drop/owned cleanup. The test poll thread is
manually owned and joined; it does not model a real running Windows child or
claim a native race reproduction. Software's local disabled-recheck negative result
is an author report; independently reviewed source/order and authenticated hosted
records establish this disposition, not an unaudited mutation-log claim.

**V318-02:** current Cards.diagnostic now reaches View.card_details_available.
Failure/timeout and unprobed>0 offer details independently of INGEST's Problem
state. Fresh success clears this diagnostic and replaces stale failure details.
The production renderer preserves its INGEST rule while allowing card diagnostics
in Empty/Ready. Make remains disabled and no list/path is put on the card line.

The actual backend capture contains12 views: Empty/valid music × one64,
zero-unprobed,one-plus-unprobed,unavailable,timeout,fresh-success-after-failure.
All8 diagnostic views expose exact current details;4 plain successes hide the
control. The separately returned Edge/headless document outputs match these views,
the exact renderer hash and details callbacks, with0 page errors/list items and
Make disabled. They are test-document observations, not native Digital Tape UI.
The old renderer misses all8 diagnostic rows. Its non-diagnostic rows remaining
hidden are expected; “0 of12” in the producer's prose is not the failure count.

Verification independently mounted the exact corrected/old production modules
in a logical test DOM over all12 retained views: corrected8/8 diagnostics show
and return exact text, old0/8 do,4 successes remain hidden. The diagnostic is
`render.mjs`; no app/IPC/OS input or browser process was run by Verification.
CSS geometry was not independently measured; returned Edge records supply their
own stated class. An open details panel still resets on render as before; persistent
reading across poll updates is outside this two-finding component clearance and
is not certified as native usability. No broader UI/G4 claim is made.

## Exact source, CI and evidence identities

- The correction is one commit after disposed18f424f6. The two regression
  expectations were published at55ecd4b0 before correction implementation.
  Frozen import tree `ec9cda078291e24230302b732fe40d97b412a184` and IMPORTS.json
  unchanged. No verifier assertion/value/case was relaxed. Spec tree
  `e07292dc75ea183602aacd2cd668036934506c2c` unchanged.
- Exact-head checks independently read across both pages:120 completed successes.
  Build/component run [40225724763](https://github.com/mmsanders/Digital-Tape/actions/runs/40225724763)
  includes correction capture and production Tauri binding compile; not a GUI run.
- Source tree host/app/src `8d001caa859381bd71b848b06ec1f8235ead6039`;
  frontend `870b02fb59514d083149d2a30b21503557ca2930`. Renderer SHA256
  `496b3249ae20039ec323080e7d4528659f77023edbc0d168fcb825d9ce097b77`.
- Evidence artifact12610469346/archive SHA256
  `671e6bfc6b5eb8ee680db7f32b3765bf6f3f72622cabf35c8b4ffd379e533f7a`.
  correction1.json SHA256
  `2a36fcddd7508f52382db62610004e9b47a8c547daf53a5dcca9088e8cebe74f`.
  Original records retained under raw/ with byte hashes in manifest.json.
- Child artifact12610149859/archive SHA256
  `83fa0d72d76948615613c388187a114d9fd03107b85d7842f37ead558f0f3b9b`.
  Actual downloaded tapectl.exe493712bytes SHA256
  `44ef26869ba2d01a8a183660a2c7a050d0e7e9ff37c40b727131512739ea6ded`;
  version `tapectl-wp15-s2+f9306c2c5a42`, source full candidate above. No invocation
  by Verification. Supersedes the previously offered3cd678cb child; original564
  bundle remains untouched. No reproducible-compilation assertion.
- Explicit non-test Make target, HEAD_ID and actual compiler macro retained.
  Engine tree `d96b4245e04d74078f8938744b1394c3018516f7` unchanged; accepted
  metadata enumerator49e0f7e9, policy and report blobs unchanged. No host/engine
  change between18f424f6 and this head. Already accepted S2/backend/INGEST/internal
  Make source facts carry at their prior exact boundaries, not newly replayed.
- Independently authenticated both archives/child, build crosswalk and inline DOM
  outputs; frozen qualifier passes all23 current-head rows. Raw exits/stdout/report
  equal the independent typed fixtures, and model nonce/version remain explicitly
  synthetic. The child Command construction/nonce tests do not execute tapectl.
  review.py repeats retained authentication/qualification, render.mjs checks actual
  production presentation functions. Neither establishes runtime device-open absence.

## Specific single metadata-only admission (unexecuted)

Only the offered child/source/version above, as declared in Software6402307067:

```text
exe: C:\Users\mrtro\claude\software-only\live578\tapectl.exe
cwd: C:\Users\mrtro\claude\software-only\live578\job
argv:
C:\Users\mrtro\claude\software-only\live578\tapectl.exe cards --report C:\Users\mrtro\claude\software-only\live578\job\cards-154abcdcabdabea5199b812735fbe464.jsonl --report-nonce 154abcdcabdabea5199b812735fbe464
```

Software reports current ordinary unelevated mrtro/Claude Code desktop/Opus5.5/auto
context and an empty owned job; its `net session` refusal is corroborating caller
evidence, not an independent token audit or substitute permission grant. Use the
existing ordinary context only; do not elevate or change settings to satisfy this
admission. Immediately bind the actual executable hash/current context/expanded
argv/cwd and confirm this report name has never been used. If any identity/context/
path condition differs, or required tool approval is denied/unavailable, stop that
action and return the difference; do not switch providers or repeat the attempt.
Normal exact tool approval may be requested where the actual task sandbox requires
it. Existing auto mode is recorded truthfully, not described as a per-command prompt.

At most ONE process attempt. The already accepted cards dispatch uses OS inventory/
zero-access metadata queries only, not raw-data/partition reads, write-mode access,
writes, unmounts or a destructive session. The crosswalk/production no-test build
substantiates this narrow path. No app launch, production poller session, other CLI
command, card handling, observer/VHD, native provider or retry is admitted. Keep
original stdout/stderr/exit/report and invocation/context/hash receipt, including
failure/refusal/partial records, for independent review; do not publish device paths
in public prose. Do not delete or replace raw evidence. An offered count is a hint,
never safe-card authorization or proof of absent process device access/G1.

This is permission to collect one bounded fact when Software is manually activated;
it is not evidence the fact occurred. No new app candidate startup/native controls,
real IPC/app-driven INGEST, physical/A6/session/S3/elevation/Make/fullAPP/G2 is
accepted. No engine/format/firmware/hardware/install/security change. Original STOPs,
the pre302 quarantine and all undisposed holds survive.

## Return and stop

Software owns normal protected integration of this expressly cleared exact source.
A moved Product head/base requires a mechanical current-base/source/CI identity
crosswalk, not implied blanket clearance or replay of old accepted campaigns.
Return this immutable disposition directly to580/578/318 and PM576.318 stays closed;
do not reopen it or create a new self-assigned task. Next owner Software for manual
integration/optional specifically admitted collection; its result needs separate
review. Listeners remain PAUSED. No automatic next assignment or busy polling.
