# Verification352 — Software612 correction1 source PASS

**F352-1/F352-2 resolved in exact source/component scope.** Michael manually
selected this review. Product main/basea993ba79d32ebde232072485fd1c8b83a95690d5;
Verification main637a9c90de6f4405539b499802191bc44eb807ef. Canonical four/live352
updated2026-10-28T03:38:20Z and Software return6461166586 read; Started6461301768.

Cleared source **7d1fd9791c62bbda09fee5a61a49075428583ae0**, Product PR615.
Correction is one commit on reviewed44300ea3; original import1945218e still
precedes implementation and imported cards-1 treec3b0d52cc6dc30b8ee6dfc17250bef914e8e9b27
is unchanged. Host/app treee658e8b227c8df08ed9cb0dbabc31852cdc48fa8.
Original findings/publication637a9c90 remain immutable; this disposition supersedes
their source hold ONLY for this exact correction and coverage.

## Independent source disposition

| Finding | Corrected source and detecting evidence | Disposition |
|---|---|---|
| F352-1 wait/reap | Watched retains actual failed try_wait/wait text; a failed wait after stop is also retained. cards_terminal stops incomplete before writing a fictional terminal; ordinary exited/unknown code separately adds cards-exit-unknown. No exit/status is invented. | PASS covered source |
| F352-1 pipe/read/join | reader returns prefix plus actual read error; joined returns an explicit reader failure instead of silently complete empty bytes. Ran retains these receipt-only facts. cards_capture writes cards-missing with actual error/available-prefix count/hash, never a complete blob or invented original_bytes. Report read errors are also retained. | PASS covered source |
| F352-2 creation | create_staged records actual failed stage and whether the job directory was already created. A later failure stops incomplete before a false not-created receipt. create remains an equivalent Result<Job,io::Error> wrapper for other callers. | PASS covered source |
| F352-2 removal | removal reports Removed / ownership Refused / actual remove_dir_all Failed(error). Guard refusal stops incomplete; actual attempted failure uses the returned OS error, not exists() guesses. remove remains the same boolean-policy wrapper for other callers. | PASS covered source |

The partial-job and refused-cleanup cases use the existing incomplete path, as the
previous review expressly allowed. No new record fields, new schema permission or
weakened oracle is needed. The normal records are not fabricated after a sink stop.
Component fault switches remain cfg(test), not shipping environment flags or an
alternate production route. Six new tests drive the real production run seams.

Creation call order, ownership checks and deletion policy are unchanged. In
particular remove_dir_all may partially delete an owned directory before failing,
including removing its marker. A resulting unowned remnant is NOT later deleted
by clean_stale. This disclosed existing policy is not repaired or promoted to a
stronger cleanup guarantee here; the new receipt truthfully records failure.
A partial job with a valid marker remains eligible for the existing stale cleanup.

Default OFF now passes no observation hook: no receipt-only env hashing, wall
spawn/end time or OS-start observation is gathered on that path. This is a source
fact, not a whole-machine timing/native absence measurement. Main diagnostics opt-in
and bounded sink limits remain unchanged. No new scheduler/observer is introduced.

The original accepted production poller wiring, S2 pinned resolution/argv/cwd/
CREATE_NO_WINDOW, 2000ms-after-run schedule, single-flight,10s supervisor, shutdown/
join, judgment and UI text carry. Reader buffers and Product results on the error
paths remain what they were before, with errors now exposed to receipts. The emit
Result and previously approved594 index/projection plumbing remain within scope.

## Actual retained component evidence

Run **40636090229**, cards job122643278579, artifact **12793413199/evidence612**,
96739-byte transport, API-reported digest
`sha256:8ca3d61a9351b8e75fc8b0cd2fbdc03dcd4ec16da5f0b2b1f5451c421c9c300f`.
Downloaded once through gh; no payload executed. Manifest in RESULT.json pins
each extracted artifact file. The digest above is API metadata, not falsely a
locally measured extracted-directory hash. Raw originals remain in the retained
artifact/local private copy; this publication redacts job paths in its summaries.

Independent audit.py invoked the untouched cards-1 oracle on **all20 envelopes:
7complete/13incomplete**, matching each expectation. It separately checked six new
fault originals for the exact missing/stopped/failed representation, and seven
child observations (including both poll_once runs). PID, OS-start, argv/cwd,
no-console and retained raw-role hashes match. Read-error stderr reason carries
the expected19-byte prefix hash; it is NOT stored as a complete stderr blob.
The wait-failure transcript ends after launch with actual-error incomplete. Guard
refusal has no false cleanup-attempt record; actual sharing violation is attempted
failed cleanup with OS error32. Partial create is session/contract/incomplete only.

Retained test log: **15/15 c612 cases**, no UNEXECUTED. Injected reader panic is the
intended captured fault, not an unexplained test failure. Source inspection confirms
tests assert original preservation, ownership sentinel, no fabricated attempts,
actual OS error, unchanged View/judgment and existing stale-cleanup rules. Local
six reverted-fix negative runs are Software's reported evidence; no raw logs for
them are in this artifact and they are not claimed independently replayed here.
The separately retained15-case assertions and independent original-byte checks
establish the reviewed correction coverage. No additional native trial is inferred.

Probe binary pin for this COMPONENT build:
`56494c967d5134d74e0d6abd2515480e24d15abbaab0551b4d2ba43fda625ae6`;
source blob90916b64e93749ec0bd824ec7c0bd60c6b9bd8ea remains identical to the
previous helper source. This is never a shipping child pin or app candidate.

At the last Product CI census during review:117SUCCESS/3pending (WP10 residue and
WP14 macOS/Windows packaging), no reported failure; the new cards-1 job was SUCCESS.
Source review PASS does not bypass those checks. **Normal current-base CI, required
reviews/protections and mechanical identity verification must pass before merge.**
Verification publication's own CI is a separate integrity/regression fact.

## Express clearance and next owner

Software may integrate **exact7d1fd979** through normal current-base protected
CI/reviews, preserving the cleared host/app/child/judgment scope. No Product code
was merged by Verification. Any functional change/rebase conflict affecting that
scope returns for review; no implicit acceptance of a different tree.

After that protected integration, the already-issued PM611/612 replacement-candidate
stage may proceed under the published candidate.py expectations: at mostTWO actual
candidate compilation attempts total, ONE uploaded new candidate, all attempts/
exits/artifacts/logs/source clearance and integration refs recorded; normal CI
builds listed separately. Original585 is not rebuilt; unchanged authenticated
INGEST3895f3f3 and S2 tapectl44ef2686 are reused, not compiled. The closed five-member
archive and truthful new app/source/README/external inventory/test-sheet hashes
remain mandatory. Candidate preparation is limited to the already-covered profile/
packaging adapter, not new Product behavior. No extra PM decision is required for
these issued stages. Stop after second failure or material scope change.

**No actual new candidate has been audited or accepted here.** Its byte/archive-only
review stays pending on352; candidate attempts0/2 and uploads0/1 at this return.
No app, S2, INGEST, workload, capture or observer was executed by Verification.
First-party receipts remain component/source facts, not native/G1/device absence
or visible GUI proof. Native runtime/human admission remains UNISSUED.7/12,
353's closed SplitIo blocker, originals/STOPs and native/session/A6/INGEST/fullAPP/G2
holds carry.352 remains open awaiting the bounded integration/candidate handoff;
both listeners stay PAUSED, manual stop.

## Offline reproduction

Fetch scoped artifact12793413199 using:
`gh run download 40636090229 --repo mmsanders/Digital-Tape -n evidence612 -D <owned-dir>`.
Run adjacent audit.py with `--evidence <owned-dir> --out <new-result.json>`.
It reads retained bytes only. `--self-check` checks publication integrity only;
it does not replace the separately recorded actual20-envelope replay.
