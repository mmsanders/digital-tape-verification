# Verification318: Software578 / PR580 actual-return disposition

25 October 2026 PDT. **CHANGES REQUIRED; no Product merge clearance.**
Candidate `18f424f66bbd0ad9c9f74c930d524627a3a6cf82`, Product main
`1cf5577099ecc4445e8465bfb9addb1d780008eb`, Verification input
`f652bc5255dd866db55f2d44ffca2f407c3cab0f`. Michael manually requested
"Review the latest software work". Canonical four/current318 (updated
2026-10-25T15:08:50Z), paired578/PM576 scope updates read. Separate ChatGPT
Work/Codex context; existing granular approval settings, no settings change,
elevation, local Windows app/child/UI/device run or subworker.

## Findings (consolidated correction response 1)

### V318-01 / P2: shutdown can miss a newly admitted discovery run

At the exact candidate, `host/app/src/bridge.rs:48` reads `stop_polls`, then
line50 ticks with `stopped=false` and calls `discover`. Line65 registers a new
current ticket and a fresh false cancellation flag without rechecking stop.
`shutdown` at lines155-160 sets stop, invalidates/cancels only an already
registered ticket, releases the locks, and joins the poller.

A permitted thread interleaving is:

1. Poller reads stop=false at a due tick; it is paused before `discover` registers.
2. Shutdown sets stop=true, finds no active cards ticket/cancel flag, and joins.
3. Poller resumes line65, registers a fresh uncancelled current run and calls
   `run_cards`; that child may publish while shutdown is waiting.

Shutdown therefore fails the frozen stop-polls -> invalidate-current -> cancel ->
terminal -> cleanup sequence for this interleaving. A slow child can consume its
full ten-second timeout instead of being cancelled by shutdown. Make stays false;
this is a lifetime/quit defect, not evidence of a device write.

The returned shutdown control deliberately waits until its typed child is already
polling before shutdown; it cannot expose registration crossing the stop boundary.
This finding is a source-level concurrency proof, **not an observed native race**.

Required correction: serialize stop/admission and cancellation registration so
either a run is registered before shutdown's cancellation pass, or a stopped
coordinator refuses it; no new current publication may cross that boundary.
An extra unsynchronized read alone does not establish this ordering.

### V318-02 / P2: discovery diagnostics have no reachable Show details

APP-1 (`docs/WP15-APP-CONTRACT.md:85`) expressly records unprobed counts for
Show details. The frozen318 expectations likewise preserve counts/raw diagnostics.
The actual returned `raw/discovery.raw.json` already demonstrates the gap:

| Controlled case | Current card line | Raw details | View details_available |
|---|---|---|---|
| zero-unprobed | Put a card in. | Card check: 0 offered, 3 not checked. | false |
| enum-unavailable | generic failure sentence | exit1 / CARDS_ENUM_UNAVAILABLE plus stderr | false |

`state.rs` stores cards details in `finish_cards`, but `App::view` sets
`details_available` only from INGEST's `self.details`. Discovery changes neither
the main view nor message. Even setting that flag alone is insufficient: the
unchanged production `frontend/screen.mjs:94` hides Show details unless the main
state is Problem. With no music error these rows remain Empty (or Ready with
valid music). `Bridge::raw_details` can return the text only if called directly;
the user cannot reach it through the app control. Model raw capture is not a
renderer/control test.

Required correction: connect current discovery diagnostics/counts to the existing
copyable details affordance, including zero-offered/unprobed and discovery failure
with otherwise valid/empty music. Preserve one-line card hints, no lists/paths on
the card line, current state and permanently disabled Make. Do not substitute an
IPC injection or native-UI claim for this component correction.

## Frozen exact-delta regression expectations before correction

These specialize the already published lifetime/raw/details requirements; no
new feature, timing tolerance, runtime provider or test framework is issued.

- Deterministically pause a due poll after its preliminary stop read and before
  registration. Complete shutdown's stop/cancel pass, resume the admitted path,
  and observe zero new child callbacks/current publications. Also retain the
  existing opposite order: registered blocked child is invalidated/cancelled,
  reaches terminal and is cleaned before replacement/quit. Use controlled
  barriers and the production registration/completion path, no live child.
- Exercise the actual production backend view through the unchanged or corrected
  production renderer: zero offered/unprobed3, unavailable exit1, timeout and
  valid music plus discovery failure. The existing details control must be
  reachable when these diagnostics are available and display the current raw
  diagnostic/count. Fresh success must not keep an old failure. Make stays false;
  no disk lists or paths on the card line. A native UI claim remains unexecuted.

Independent expectations must be published on Verification main before correction
implementation. The old windows_discovery_r1 package/tree is immutable: add
new supplemental evidence/bindings rather than editing its bytes.

## Checks that passed and their limits

- Pre-code publication `f652bc52`/tree `ec9cda078291e24230302b732fe40d97b412a184`
  is imported byte-identically at `96717de5e6085d6a9dfc13ef197e227244df3280`,
  before implementation `8b7bca75`; `18f424f6` changes workflow output location.
- All120 candidate check runs were independently read across two API pages:
 120success. The new build/controlled workflow is
  [40203652448](https://github.com/mmsanders/Digital-Tape/actions/runs/40203652448),
  job121199903495. Build, backend unit tests and Tauri compilation succeeded.
- Downloaded evidence archive12602169841 SHA256
  `0ce7a42c20d3feca255869bcdf0edca87c9235e15446c897d53f3e31542557fa`.
  Original text/JSON bytes are retained in raw/; review.py authenticates them and
  independently reapplies the frozen qualifier. All23 modeled rows and declared
  schedules pass. They do not cover the two integration gaps above.
- Downloaded child493712bytes SHA256
  `3cd678cbae5da79a1da99e6bfb2fb91d7ab711568e2557d133e245b4aa8b8ee9`;
  artifact12602239554/archive SHA256
  `532a2b481a18ae52f0c2d8c439375805028ecc65995173e44c58f0f8e01ed710`.
  Child version `tapectl-wp15-s2+18f424f66bbd` maps to the full candidate SHA.
  Explicit non-test target/HEAD_ID is in retained build command/logs. The child
  was downloaded/hash-checked, never executed by Verification.
- Engine tree remains `d96b4245e04d74078f8938744b1394c3018516f7`.
  discover_win.c `49e0f7e9`, policy and report blobs equal accepted10faee59.
  Current tapectl.c `d76fe3f6` cards dispatch crosswalk matches the preflight.
  Existing accepted metadata-only source boundary carries; not blanket acceptance
  of unrelated commands or a native runtime/G1 proof.
- Source review confirms pin resolution beside executable, fresh report nonce,
  accepted report parser reuse, strict current-report/complete-stdout hint,
  decimal GB display, generic clearing and Make=false. These facts carry into
  the correction review; no unchanged campaign replay is requested.

## Live admission and return

**No live enumeration is admitted by this return.** The source/binary identity
is substantiated, but the app remains held and the offered local plan references
the old564 token rather than a complete current concrete invocation/context.
After the exact-delta correction, return the then-selected child hash/source,
absolute exe/job/report/nonce-expanded argv and current ordinary unelevated
context for one specific metadata-only admission. Preserve the old authenticated
564 bundle. This is a bounded preflight hold, not a new prompt rule or request to
repeat any startup/permission experiment. No app launch is issued here.

Next owner Software/PM: route these two corrections to existing PR580 with the
published supplement; Software owns Product integration after explicit clearance
and normal current-base protections. Maximum two consolidated exact-delta
responses remains. Verification returns/closes318 after publication and stops.
No automatic lead activation/listener/next task. No native/physical/A6/INGEST/S3,
shipping Make/elevation, fullAPP or G2 acceptance. Old307 historical limitation
and other carried holds are unchanged.
