# Verification318 — PR580 correction response 1

25 October 2026. **CHANGES REQUIRED; no Product merge or live enumeration admission.**

Michael manually requested “Review the latest software work”. Product main
`1cf5577099ecc4445e8465bfb9addb1d780008eb`; candidate
`18f424f66bbd0ad9c9f74c930d524627a3a6cf82` (PR580); Verification publication
`f652bc5255dd866db55f2d44ffca2f407c3cab0f`. Canonical four/live318/578/PM576
read; existing Started318 comment6401385230 records this review activation.
Current reviewer is the separate ChatGPT Work/Codex context with granular tool
approvals. Ordinary read/fetch/download/publication approvals were used without
changing permissions. Software truthfully reports Claude Code/Opus5.5/auto mode.
No native app, offered child, device or metadata enumeration ran in this review.
Both listeners remain paused. This is a correction handoff, not final acceptance.

## F1 — Discovery details are unreachable, then polling collapses open details

The returned raw `zero-unprobed` and `enum-unavailable` rows contain nonempty
aggregate/error details but the actual view is `empty`, `details_available=false`.
`state.rs:162` calculates availability from ingest `self.details` alone, ignoring
`self.cards.details`. `Bridge::raw_details` combines them but no user route exposes
the discovery-only text. In the unchanged production renderer,
`screen.mjs:94` additionally hides Show details unless the state is Problem.
Discovery changes the card line, not that state: changing availability alone is
insufficient. The same gate also hides aggregate unprobed counts after a successful
Ready ingest. APP-1 §3 explicitly records unprobed for Show details; §6 requires
truthful discovery failures/details. Published318 README already requires this.

`details.mjs` ran the exact candidate production renderer over the retained actual
component views in a tiny test DOM. `DOM-RESULT.json` shows the button hidden for
both rows. A separately labeled diagnostic with availability true isolates the
second gate. These are test-DOM observations, not Windows capture/input or native
UI acceptance. No production source was modified.

Polling also adds repeated render calls to an existing behavior: render unconditionally
clears/hides the details panel (`screen.mjs:95–96`). Once details are reachable,
an ordinary poll emission collapses a panel a grown-up is reading/copying. The
diagnostic opens a Problem panel and delivers the same view again, observing it
hidden. Correct the combined state/render binding so aggregate discovery details
and failures are reachable in applicable Empty/Ready/Problem states, raw diagnostics
remain plain/copyable, and routine poll updates do not dismiss the user's panel.
Keep no lists/path presentation and permanently disabled Make. Exercise actual
production state→renderer→details action, not only a `card_line` snapshot reference.

## F2 — Shutdown can miss a poll before cancellation registration

Source-level interleaving in `bridge.rs` (not a claimed actual Windows race run):

1. Poll thread passes `stop_polls.load` at48, with the next tick due, then pauses
   before `discover` registers its ticket/cancel token at65.
2. Shutdown sets stop at156 and takes publication/core at157–159. No active ticket
   or cancellation token exists yet, so it invalidates/cancels nothing; it joins
   the poller at160.
3. Poll thread resumes at50/65, registers a fresh uncancelled current ticket and
   invokes `run_cards`. There is no stop recheck during registration/launch. This
   run may execute for its full10s bound and `publish_cards` accepts it after stop,
   because83 only checks current ticket, not stopped lifetime.

This contradicts the frozen shutdown/stopped/current-only expectations. Synchronize
stop/start registration and invalidate the lifetime so shutdown cannot miss newly
admitted work or accept its result. Also honor cancellation before launching the
owned child. Keep child-terminal before cleanup/join and replacement ordering.
Return a deterministic test of the boundary between due decision and registration,
plus the already-registered in-flight case, using the actual production admission/
publication path. No real executable/device run is needed to test this ordering.

The returned shutdown test deliberately waits until `Blocked::poll` has run before
shutdown, and its worker is manually started through `Bridge::channel` (no production
poller). It proves that already-registered typed child path. It does not cover the
gap above. Schedule's isolated `stopped` inputs do not exercise Bridge's admission
race; trace strings/qualifier booleans cannot fill that gap. The existing tests are
not relaxed or retrospectively extended as a new pre-code guarantee. Both findings
are violations of already-published requirements, not new design scope.

## What independently checked successfully

- Exact imported discovery subtree `ec9cda078291e24230302b732fe40d97b412a184`,
  import96717de5 precedes implementation8b7bca75 then evidence-path-only18f424f6.
  Tests predate uncovered implementation; no new blindness exception.
- GitHub checks on exact head: **120 completed successes**, checked across both
  pages. Build/component workflow40203652448 job121199903495 is successful;
  normal main remains1cf5577. CI success does not dispose the two defects.
- Both downloaded archive SHA256s match GitHub's returned immutable digests.
  Child493712bytes has SHA256
  `3cd678cbae5da79a1da99e6bfb2fb91d7ab711568e2557d133e245b4aa8b8ee9`.
  Version `tapectl-wp15-s2+18f424f66bbd`; explicit non-test target and actual
  compiler command include `TAPECTL_BUILD_ID=18f424f66bbd`. No test child built.
- `child-build.json` source/blobs/engine match Git identities. Accepted
  discover_win/discover.c/h/report.c/h carry unchanged; tapectl.c's already
  crosswalked cards dispatch remains unchanged. Engine tree `d96b4245` unchanged.
  No offered executable was invoked; no reproducible-compilation claim.
- Independently reapplied the frozen qualifier to retained `discovery.json`:
 23 normalized rows pass. Compared each raw typed exit/stdout/report/model nonce/
  version with the independent emitted case and actual serialized view. Requests
  use three distinct random nonces; pinned Command construction and typed outcome
  tests remain component observations. They do not run the Windows child.
- Failure clears hint; current tickets reject duplicate/invalidated completions;
  regular/slow logical schedules and existing timeout/in-flight shutdown order
  pass within their exercised boundaries. Make remains false, old child/bundle
  untouched. The request builder is no-shell/cards-only/owned report and cwd;
  CREATE_NO_WINDOW is scoped to discovery.

The raw component code records only `view.card_line` plus an unchanged renderer
source reference as `card_line_actual_render_refs`; it does not mount the renderer.
The independent diagnostic adds that missing review observation and finds F1.
No app-device-open absence/G1 claim follows from source scans or booleans.

## Evidence, next owner and live hold

Original artifacts are retained under
[build40203652448](https://github.com/mmsanders/Digital-Tape/actions/runs/40203652448):
child12602239554 archive SHA256
`532a2b481a18ae52f0c2d8c439375805028ecc65995173e44c58f0f8e01ed710`;
evidence12602169841 archive SHA256
`0ce7a42c20d3feca255869bcdf0edca87c9235e15446c897d53f3e31542557fa`.
`RESULT.json` retains per-file lengths/hashes and precise failed-view witnesses.
No binary is copied into this publication. `audit.py --repo PRODUCT_CLONE
--artifacts OWNED_REVIEW_DIR` reproduces the offline hashes/case comparison after
expanding the two named archives there; it exports only exact source text for
diagnosis. Run `details.mjs` beside those exports/archives for the DOM diagnostic.
The scripts never invoke tapectl or an app. `RESULT.json` was generated before
making audit paths configurable; its candidate/evidence inputs are unchanged.

**Next owner Software578:** one consolidated exact-delta correction for F1/F2,
then updated source/controlled raw evidence/current-base CI/provenance, keeping
the frozen oracle unchanged. At most two consolidated correction responses total;
this is response1. Existing accepted backend/INGEST/S2/internal Make facts carry
without unchanged replay. No broad redesign, provider, packaging-only or new
campaign is requested. Verification318 remains open for that bounded return;
no listener or dependency polling. Software owns normal protected integration
only after express exact-head clearance, which is NOT granted to18f424f6.

**Live metadata stays HELD.** The accepted metadata-only source crosswalk/build
is substantiated; the proposed run relies on the prior564 token record rather
than a fresh current execution context, and the app integration still needs the
above corrections. No token capture/child invocation is requested by this review.
If still proposed after correction, supply current ordinary context, absolute
owned executable/report/cwd paths and bound fresh-nonce argv for a specific
separate admission. No repeat build of unchanged host code is demanded merely
for a new app-source head: preserve and explicitly map the actual child source.
No raw-data/read/write-mode/unmount/card handling, native observer, UI/control,
S3/elevation/physical/A6/INGEST/fullAPP/G2 clearance. Original STOPs and quarantine
remain explicit. Return this correction directly to578/318 and PM576, then stop.
