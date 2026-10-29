# Software624 correction1 — e36ea492 still held on a required-volume-query failure

28 October 2026 PDT. Michael resumed Verification with “Review software work.”
Input Product main `262466d354dac779b0fda9d712a2d75b73eeec33`, Verification main
`a534012bfd6af76a391dfaef8f824b5d8e5d43c5`; Software
[correction return6485708801](https://github.com/mmsanders/Digital-Tape/issues/624#issuecomment-6485708801),
exact **`e36ea4922ef845dd6754456db874541a71992ebc`**, Product PR626.
Current issue/scopes, agreement, charter and STATUS carry; main refs fetched.
No Product edits, native app launch, physical card, lead wakeup or subworker.

**FINDINGS — this head is not cleared for integration or C2.** F364-2 and F364-3
are satisfied within the CI/component scope below. F364-1 is improved for the
tested disk-length/open-geometry cases, but remains open for the Windows mounted-
volume census. The independent regression below reproduces the missed query.
Stage1's physical/CI observations and WP-16 acceptance stand. The newly reproduced
gap is in the shared Windows probe also used by standalone provision, so **A4 and
full WP-14 acceptance are now qualified at this required-query failure path pending
correction**. This supersedes only the unconditional A4/full-package status, not
the passed physical records or other ledger rows. No physical rerun is requested.

## [P1] F364-1 remains: failed Windows mount-path query is treated as no mount

At [probe_win.c:189](https://github.com/mmsanders/Digital-Tape/blob/e36ea4922ef845dd6754456db874541a71992ebc/host/port/probe_win.c#L189),
`GetVolumePathNamesForVolumeNameW` failure and a successful empty path list share
one `continue`. The mounted target volume disappears from `n_mounted`, and
`query_error` is not set. Make's new error gate therefore has nothing to stop on.
The same census loop skips `volume_disks` failure at lines185–187, and does not
distinguish an error from normal end of `FindNextVolumeW` at line199. These are
queries needed to establish the “no foreign mounted volume” safety fact, not
optional post-authorization monitoring.

APP-1A §7 requires a failed required query to stop with HOST_QUERY_FAILED/exit1;
unknown safety facts never become safe. WP-14 A4 still outranks the app. The
correction's new `query_error` field cannot meet that rule while these failures
are omitted. This is the remaining part of the original F364-1, not a new tracing
or method-qualification requirement.

The census skip predates this correction and is present in the shared probe on
Product main. This review identifies it while checking F364-1's claimed coverage;
it is not a newly introduced regression or a claim that earlier tests exercised it.
Unknown mount facts must fail closed in standalone commands as well. Make
additionally owes the APP-1A HOST_QUERY_FAILED outcome.

### Independently reproduced on exact candidate source

[CI40805800367](https://github.com/mmsanders/digital-tape-verification/actions/runs/40805800367)
compiled `tests/c1_volume_query_r1/probe.c` over the exact candidate's `probe_win.c`,
`safety.c` and `mbr.c`. The probe-only driver never calls Make, provision or unmount.
The hosted setup creates/formats one fresh private VHD and binds its returned disk
identity before probing; no physical disk/card is selected.

The positive run observes its real NTFS mounted volume. The control repeats the
same probe with only the mount-path API wrapped to pass a zero-size result buffer
to the **real Windows API**. Windows actually returns error234 / ERROR_MORE_DATA.
That exercises the same failed-query branch as an undersized path buffer; it does
not invent a query result or inject a report ID.

| Observation | Actual result |
|---|---|
| Baseline mounted volumes | 1 |
| Controlled real API failures | 1, OS error234 |
| Mounted volumes after that failure | **0** |
| `query_error` recorded | **false** |
| Pure policy with the observed facts and removable=true (explicit model input) | Before: REFUSE_FOREIGN_MOUNT (5); after failed query: REFUSE_NONE (0) |
| Required-query fail-stop criterion | **FAIL** |

The final row is a pure-policy counterexample with an explicitly substituted
removable fact. The VHD itself remains virtual/refused by the shipping policy.
No destructive Make was attempted, no physical-card write is claimed, and no
claim is made that Windows would permit every later raw write. The defect is that
the application safety policy can authorize a raw-access attempt from incomplete
mount information. OS write protection is not a replacement for that policy.

The workflow is green because it **reproduces this known failing criterion**;
RESULT.json explicitly has `required_query_fail_stop_pass:false`. It does not
label the Product as passing. The ordinary VHD positive ensures the census sees
the volume before the fault. Actual regression bytes and hashes are retained.

**Correction requested, same Software624 branch/task:** preserve required census
query failures (including mount-path retrieval, extent lookup and abnormal
enumeration termination) as query errors before authorization. Keep a legitimate
successful empty path list distinct. Required buffer sizing may be handled or
fail closed with its OS error. Ensure the shared policy cannot authorize from the
incomplete census, including standalone provision; known-fact command behavior
must stay unchanged. Return the failing-query/known-fact neighbors and
HOST_QUERY_FAILED report/app mapping in CI; no physical run or kernel observer.
The existing independent boundary-query oracle remains authoritative.

## Completed correction coverage

| Item | Independent assessment |
|---|---|
| F364-1 disk-length and authorized-open geometry | PASS for these cases: 3 query rows per platform, correct HOST_QUERY_FAILED/1 versus known policy refusal/3; exact report/OS-error binding; no subsequent device work. Recording either actual query-failure observation as exit3 is rejected by the same independent oracle. This does not cover the omitted census failures above. |
| Existing S3 outcomes | Unchanged `wp15_cards_make_r1/runner.py` independently authenticates/rejudges **31 Linux + 10 Windows Server** actual rows, equal to producer judgments. |
| F364-3 lawful own-p1 | PASS: real Linux mount/unmount, one retained session, success and byte/stdout equivalence. Independent supplement admits only successful own-p1 unmount; marking it failed is rejected. Invalid-label pre-open refusal is judged separately and passes. |
| F364-2 real child-origin bridge outcomes | PASS for all **16** real child rows, including query failure: original ingest, real private-VHD make errors, real shipping discovery failure. All original report/process/exit and raw hashes were checked with the independent parser; actual selected messages match the independently authored matrix. |
| App-origin component cases | All **12** pass current assertions: actual production bridge actions, typed recheck/decline boundaries, no forged child reports. Real UAC decline/person gestures remain C2. |
| Stderr independence | Retained original reports are used for outcomes. Ingest/cards preserve exit/report while changing captured stderr; make preserves every non-stderr report line while rewording diagnostic records. Message selection stays unchanged through the production selector. |
| Engine/spec/import identity | Engine remains `d96b4245`; no format/spec change. Imported C1 tree `29e99cfe232f8fcd49b64b9b671d5a6a020571bb` matches published Verification main. Import commit5862afb7 predates correction code. |

Reviewed the actual orchestration, bridge adapter and corrected production paths;
producer-private expectations are not substituted for independent tests. The
transport wrappers bind real child/report bytes and use production completion.
The generic-make LABEL_INVALID row sets an otherwise UI-unreachable long label;
it proves the fallback mapping, not a user-reachable label-box escape. CI runs
the Make request with a test launcher on an administrative Windows Server runner;
it does not establish the Windows11 UAC prompt or a real reader/card response.

### G3-D1: verifier correction, not a new Product requirement

The original `g3.check` wrongly required nonempty copyable diagnostics for **every**
row. A rejected single/mixed drop starts no child, so it has no raw child stderr.
This review corrects only that blanket nonempty-text assertion for the two
zero-child rejected-drop notices. It still requires exact message, zero additions,
zero child calls and no retry; any actual diagnostic must remain copyable. Child
diagnostic rows retain the assertion. Negative controls reject a launched child,
noncopyable actual text, or a child diagnostic that loses copyability.

The untouched producer result fails the old assertion on exactly those two fields;
all **28 rows pass the corrected verifier** without changing a byte of raw evidence.
No assertion is edited in Software's imported package. Software's statement that
the rejected-drop notice is not a Problem screen is not used to waive APP-1:
native Show-details control/state presentation remains G4/C2, which is not closed
here. This correction does not demand fictional stderr or approve an unseen screen.

## Rebuilt candidate identity

Both workflow identity and byte identity were checked. Candidate40800037890,
make40800041060 and G3 40800044586 all completed SUCCESS on **the exact head**.
The captured PR check set is recorded in AUDIT.json. CI success does not override
the independently reproduced census failure.

| Item | SHA-256 |
|---|---|
| ZIP | `65f252dc2b505b9ab5ab6cfe1cf862042525e369dfdbedd30b34b58dd43186c6` |
| digital-tape.exe | `5c2bd1716881d78fadf0d2043534501a3ffb2bf530b1b8227bdab8d0c69bb887` |
| tapectl.exe | `0ade9f16f2e24931f1146266957b843b5bac9ab2cbcccb00b91653dc714d3ca5` |
| ingest.exe | `3895f3f356c91b8a9fe870c33694da64bf2765df308bef118d657c1be4bb9a20` |

All member bytes equal BUILD.json. PE resources still request no elevation;
default-invoker scope carries. No candidate executable was launched locally.
The revised method note accurately describes the tested query errors and actual
bridge cases, but its general fail-stop claim needs the census correction above.

## Publication/replay and next owner

The [retained correction inputs](https://github.com/mmsanders/digital-tape-verification/releases/tag/evidence-364-correction1-2026-10-28)
asset `verification364-correction1-inputs.zip` is 51,098,934 bytes, SHA-256
`5226855cc39a1713b6e999c0c78ed532329af259a45903697e4fb3ccff866041`.
It contains only original project CI artifacts, hosted regression and review JSON;
no user music or private workspace source. `fetch.py DEST` authenticates before
extraction; `audit.py DEST --out RESULT` replays the independent judges and checks
the raw bridge outcomes, candidate bytes and regression, without Product execution.

Software624 returns the next corrected exact head and CI/candidate identities;
Verification364 remains open to dispose it. **Do not integrate e36ea492 or run C2
with it.** No automatic lead activation, polling or extra method round.
