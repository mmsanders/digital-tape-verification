# Verification352 — Software612 source return, correction1 required

**SOURCE HELD; no Product integration or candidate compilation clearance.**
Michael manually resumed this stage. Product main/base
`a993ba79d32ebde232072485fd1c8b83a95690d5`, Verification main
`10bbe7ad16c2759dc95743b065a01dcba6fd473a`. Canonical four/live352 updated
2026-10-28T02:04:20Z and612 return6459489249 read; Started6459904333.
PR615 exact returned head **44300ea3b37617075fbff48334b3596bc58b789a**.
Import1945218e3e8aafb46bb5f98856962e183b72da7f precedes implementation;
`tests/windows_cards_receipts_r1` tree **c3b0d52cc6dc30b8ee6dfc17250bef914e8e9b27**
equals independent publicationa4f3138c. No imported assertions changed. Review is
within the already-published cards-1/P1–P6 scope, not uncovered implementation.

## What passes and what was actually replayed

Current-head PR615 CI:122SUCCESS,0pending/failures at review. Cards workflow
run40624193966/job122605094193 passed9/9 c612 cases with no UNEXECUTED cases;
artifact **12788467739/evidence612**,76142-byte transport, API digest
`sha256:8babc73c67839263e1ef02ff21e44a012c68171f51338a460dc3d931c99c94ee`.
Downloaded once via gh run download; payloads were NOT executed. RESULT.json pins
every extracted artifact file's hash and bytes for exact offline reproduction.
Raw originals remain in the scoped retained artifact/local copy, not copied into
this public finding tree. The API transport digest is reported as API metadata,
not falsely claimed measured from the extracted directory.

Independent `audit.py` ran the untouched Verification352 oracle directly against
all14 original envelopes and independent bindings. **7complete/7incomplete**, all
matched their declared expectations (Software's narrative8/6 count is incorrect).
Six retained child observations were independently crosschecked: both poll_once
runs, last production-poller run, refusal, malformed, timeout; PID/creation time/
argv/cwd/no-console and each retained raw-role hash matched. No new component or
native run was required. Source/test inspection confirms production constructor
and poll_once→discover→run_cards→command/run wiring, no receipt sink in note().
The successful-path original evidence is useful and is not discarded by findings.

Offline negative control on the real positive: exit=None with complete=True is
rejected by the frozen oracle; the same MODEL marked incomplete is retainable.
This is not a claim that an actual OS wait failure happened in the returned run.
The following are source error-path findings, not allegations about its originals.

## F352-1 [P1] Retain capture/wait failures before claiming a complete session

At `host/app/src/discovery.rs:249`, an error from try_wait followed by a failed
wait becomes Some(None); the wrapper labels it wait, `supervise` returns
Exited(None), and no actual successful reap/status is retained. At278–285 both
read_to_end results are discarded and failed reader joins become empty Vecs.
`cards_capture` then emits those buffers as complete originals, while the new
ledger never receives read/join errors.

At `host/app/src/diagnostics.rs:456`, only timed_out/cancelled automatically adds
a terminal flaw; Exited(None) does not. At491 the report/exit validation is skipped
when exit is None. With all three raw roles, publication and cleanup recorded,
gap() at564–565 can consequently allow complete=True without an observed exit.
The already-published independent oracle correctly rejects that complete receipt.
Separately, a stderr read error after a prefix (or a reader join failure) can have
valid stdout/report/exit, so the prefix/empty bytes can be labelled complete and
the footer can pass. This loses the exact error/partial-capture distinction PM611
and P5 explicitly required.

**Required correction:** retain actual wait outcome/error, stream read result and
reader join failure through Ran to the diagnostic ledger; distinguish an attempted
wait from observed terminal/reap. Missing/unknown terminal or capture makes evidence
incomplete, preserving truthful available originals/errors. Do not invent an exit,
original byte count or successful reap. Do not change Product judgment, its existing
timeout/shutdown/cleanup policy or child pins as a workaround. Add controlled
read-prefix+error, join failure and failed/unknown-wait cases at existing seams;
check actual incomplete receipts and unchanged Product result/schedule/cleanup.
No real S2/INGEST/app or native fault experiment is needed or authorized.

## F352-2 [P2] Record creation/removal facts, not inferred boolean explanations

`jobdir.rs:72–73` returns only `owned(dir) && remove_dir_all(dir).is_ok()`.
False therefore includes an ownership-guard refusal where remove_dir_all was NEVER
called. New `cards_cleanup` at502–508 nevertheless records attempted=True for
every Some(dir), then infers failed/missing using a later exists() call and invents
the explanation "remove_dir_all failed" or "already gone". The post-check cannot
recover the actual operation or its error; permission/metadata/race failure can
also make exists() false. The source correctly avoids deletion on a refused guard,
but the new receipt does not truthfully distinguish it.

Likewise `jobdir::create` at60 creates the directory, then marker/control/out
operations can fail. `Bridge::discover` at100–110 treats EVERY Err as job_dir=null
and cleanup not-created, even when a partial owned directory was created. Its
new diagnostic result can thus claim no creation although part of it happened.
The supplied job-create case fails earlier at the jobs root; it does not detect
this partial-creation path. No actual returned cleanup failure/guard refusal or
post-creation failure original is supplied, despite P2/P5's required controls.

**Required correction:** carry factual creation stage/known path and actual
cleanup attempt/result/error from the operation that owns them, preserving the
existing ownership checks and cleanup policy. Mark uncertain/partial operations
incomplete rather than recording unobserved not-created/remove-failed facts. Add
ordinary owned-fixture controls for guard-refused removal, actual removal failure
and create failure after directory creation; assert truthful receipts, retained
sentinels and unchanged policy. No ACL/admin/disk-full/system fault campaign.
If a small additive record is required, use the existing incomplete/missing path
to remain honest while returning its exact interface; do not weaken the frozen
oracle or silently relabel attempts. This is a covered factual-error correction,
not authorization to broaden cleanup behavior or build a new framework.

## Disclosed incidental changes and scope

* Existing Software-authored594 leaf/seq/fault-write +1 shifts target the same
  records after cards-contract atseq1, preserving sizes/outcomes. Accepted as
  mechanical adaptation to the additive session record; imported r2 unchanged.
* diagnostics594_check routes full originals through cards-1 then the documented
  legacy-only projection into untouched r2. Self-header binding there is only for
  those INGEST-only fixture envelopes; it is not independent actual cards identity.
* `ingest_job::now` visibility and the emit Result plumbing are within scope.
  The emit result is retained without changing View selection/dispatch behavior.
* OFF supplied case proves zero sink calls/files; it does not prove zero added
  receipt-only work: discovery::run currently gathers env/time/process-start even
  OFF. Keep that distinction explicit and gate receipt-only observations where
  practical. Do not call this a full timing/OS absence measurement.
* Publication-attempt is before emit, state_ref is a source/callback reference,
  not visible UI proof. Existing accepted child pins, S2 source, engine/format and
  INGEST behavior remain outside this correction's functional scope.

One consolidated **correction1** return within the issued max2 responses. Software
owns the narrow correction and original controlled evidence, then manual independent
review. No integration or candidate compilation until express source clearance;
candidate allowance remains0/2 attempts and0/1 upload. No protection bypass or
selfacceptance.352 stays OPEN for its already-issued source/candidate stages.
353 remains closed at the SplitIo layout blocker; no replay or new task there.
Both listeners PAUSED.7/12 and native/session/A6/INGEST/fullAPP/G2/old STOPs carry.

## Replay

Fetch artifact12788467739 from run40624193966 into a private evidence directory:
`gh run download 40624193966 --repo mmsanders/Digital-Tape -n evidence612 -D <owned-dir>`.
Then run this file's audit.py with `--evidence <owned-dir> --out <new-result.json>`.
It invokes only the independent Python oracle on retained bytes, never Product
payloads. `--self-check` checks publication/result integrity only and is labelled
as such; it does not replace the actual offline14-envelope replay recorded above.
