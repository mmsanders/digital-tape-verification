# Verification #196: current Software return — CORRECTION / HELD

Activation: Michael's direct “Check the latest from software!”; live #196 updated
2026-10-17T15:17:51Z. Product main 35d4862892b276226d0851f89436b1dcf5560f37;
Verification input main 42f169f1b5448bc646a2b181ced51c14e385017c.
APP-1A authority: ADR-185 / PM449, issued normative PM450 at 86e2f4c (merged
05315e2d), unchanged on input main. Required onboarding four documents and live
assignment read. No engine implementation inspected; host parser/report review
follows independent test publication. No subworkers.

## Exact returned heads and disposition

| Return | Head | Disposition |
|---|---|---|
| #453 shipping exhaustion / visibility supplement | 23f5a18ca2e1d3e72a24e023347e96428c174ac9 | Windows shipping exhaustion CORRECTION; limitations remain |
| #454 S1 report, stacked on held #436 | ea445e1c8004c92484946d7408b296bb20bd1b6b | HELD: independent import and bounded process/parser evidence required; underlying #436 held |
| #455 S4 app shell | 8e7b39e648314c8940423ce9ed551f29812fe6da | CORRECTION: G1 static negative controls fail; independent import absent |

No overall exact-head PASS or Product merge clearance is issued. Software owns
Product fixes/integration; PM449 routes the next exact-head correction tranche.
This closes the current verification assignment at a concrete correction/blocker,
not at Product acceptance.

## V196-01: static gate ignores shipping code after a test module

Actual #455 tools/app1a/g1_static.py splits the entire Rust file at the first
`#[cfg(test)]` marker. Rust applies that attribute to the following item, not to
the remainder of the file. A function after the test module is shipping code.
The already-published static_controls.py appends functions to existing app files.
On actual host/app/src/jobdir.rs, the ordinary-file positive and baseline return0,
but Unix raw-read, Windows alias raw-read and partition-write negatives also
return0. Moving the same functions before the marker makes all three negatives
return nonzero. No device is opened: these are disposable source mutations.
This demonstrates a gate blind spot, not an observed raw-device access in the
unmodified app. Using lib.rs additionally rejects the ordinary-file positive by
module policy, so the causal comparison uses jobdir.rs, an allowed FS module.

Reproduction: `python3 -B reproduce.py --static-only /exact/head/host/app --out OUT`.
The unchanged published fail-fast runner is invoked first; a recording adapter
then captures every row without changing snippets or expected judgments.
`static-local.json` records the completed local run. CI repeats the actual gate.
Software must repair cfg scoping and return real positive/negative results; a
literal search over only a prefix cannot substantiate G1's static claim. The
before-marker ordinary-file positive is also rejected by the gate's root policy;
the after-marker positive succeeds because the entire suffix is skipped. Both
results are retained rather than presenting the ignored positive as analyzer coverage.

## V196-02: exact shipping Windows allocation abort

Independent retrieval of the GitHub job logs confirms Software's reported failure
in two hosted Windows Server executions: run39041650946/job117422193896 and
run39042030018/job117423290169. The logs are retained here with SHA256SUMS.
Both authenticate the original shipping ingest.exe as
0e1ef2cb4f283eb876f08019222da5d3ac744ec30d49f020a2e87323f31bcac1,
from kit artifact12067900169/run38948012087 (ZIP digest
32d6643c1cb782dcf6ac540f14b733be556a3b089b49fd53475076b9f5503eac).
At 6MiB Job process-memory limit, --version succeeds (0), while the actual case
returns3221226505 = 0xC0000409 with “memory allocation of 4196368 bytes failed”.
DEST/stage/sentinel cleanup is reported clean; 8MiB and unlimited positives
publish. 2/3/4MiB rows return1 with the tool's own OOM diagnostic and cleanup.
INGEST-1 requires resource exhaustion exit1 with no published output (§resource
policy); the clean abort still violates the exit requirement. CI's successful
supplement workflow means evidence collection succeeded, not contract PASS.
This review authenticates and interprets returned executions; it is not a new
local Windows execution. Software's source-allocation diagnosis is not asserted
as independently established by this log review. PM should issue a pinned host
fix, preserving #436's original identity rather than replacing its bytes silently.

Linux logs bind rebuilt bytes to the original shipping hash and show bounded
exit1 exhaustion. macOS setrlimit probes refuse the requested limits; unconstrained
success is not an exhaustion receipt. No native Windows11 or macOS exhaustion
coverage is invented.

## Independent import, parser binding, and process scope

The tests were already published before these implementations: corrected package
on Verification/main 42f169f1b5448bc646a2b181ced51c14e385017c, package Git tree
eb94f18ba4e47f7c7bc7e842d640d3542cfeaba6; publication PR199 CI39043765226 green.
Neither returned app candidate imports that tree. Software's “not published”
statement is incorrect; its reported repository-access problem is addressed by
an authenticated two-part Product452 comment handoff:
https://github.com/mmsanders/Digital-Tape/issues/452#issuecomment-6242095833 and
https://github.com/mmsanders/Digital-Tape/issues/452#issuecomment-6242096086.
Concatenated base64 decodes to a gzip git archive with SHA256
446e0cd961626646e35830e957f58d85db169e5e6e2977065adf9d3afdbf6c0d.
Import the exact directory verbatim; adapters stay outside it. Do not derive new
expectations from Software's private tests or failure-site map.

`reproduce.py` fetches the two exact public Product heads, binds a minimal Rust
adapter directly to actual report.rs/messages.rs, and runs the ingest subset of
the published 627-case corpus. Other-tool cases remain outside this S1/S4 slice;
S2/S3 are unbuilt, not silently treated as app PASS. Adapter tests actual validity
and exact rendered message; exit0 published-pair validation lies outside this
parser/message unit binding and is not inferred from it. Parser source hashes,
all input bytes, expected judgments and actual results go to parser.json.
Actual CI39074757652 at publication head106afd3 measured281 ingest parser cases:
6 validity mismatches, including rejection of valid JOINED_PEAK boundary-array
subject and acceptance of duplicate keys, insignificant whitespace, out-of-range
folder ordinal, path traversal component, and a decomposed non-NFC name. The last
three also select named unusable-file messages instead of generic fallback
(3 rendered-message mismatches). These are actual report.rs/messages.rs bindings,
not an oracle-only synthetic run. Software must correct validation and preserve
valid reports; the remaining346 corpus cases are tapectl scope and not counted.

The same CI exposed a Verification harness error: ingest_process.py compared raw
stdout using different DEST arguments, whose success summaries correctly include
the path. That assertion is withdrawn as a Product finding. This publication
corrects only the invocation mechanics: use the same DEST for both runs, move each
published pair to its retained result directory, and preserve exact stdout/stderr
and pair-byte equality assertions. No expected outcome is relaxed. The original
eb94f18b handoff must therefore be followed by this published single-file correction;
the final handoff comment identifies the corrected package tree. The independent
normative parser inputs and expectations are unchanged.

CI also builds #454's shipping configuration, authenticates the frozen Stage1
source pack, and runs the unchanged independent ingest_process.py smoke using
ordinary.wav SHA256 d36663d1e4f05abaac699a6c14e0fa86724db9b4decdb8c96abe0c9d1f645821.
Results preserve actual argv, stdout/stderr hashes, file/output facts and assertion
failures. This is a rebuild of the exact source head, not a claim its bytes equal
Software's release artifacts. Full ADAPTER late-write faults, all closed-ID actual
reachability, no-flag full campaign and native app events remain unaccepted.

The existing normal Verification workflow runs the bounded reproduction on this
publication PR and retains verification196-exact-head-results for90days. Its
green result asserts that finding reproduction completed, not that Product passed.
The PR's final evidence comment identifies the exact CI run, artifact ID/digest
and measured totals. No new Product gate or test-oracle change is introduced.

## Remaining scope and ownership

Software reports Windows Procmon/WPR FileIO miss zero-access and failed attempts;
Handle ETW improves successful zero-access coverage but still misses the failed
not-found/access-denied controls. The committed visibility logs support retaining
that explicit limitation. Absence under these methods cannot establish absence
of all attempted opens; this is not a universal impossibility claim.

APP's native G1 runtime, elevation/decline, ordinary macOS and Windows11,
Making/Done and full G3/G4/G5, discovery S2 / make S3 and physical G2/A6 remain
held or unbuilt as previously scoped. No rerun of accepted independent audio math,
no weakening of Mac security, and no new physical-device request. #436 remains
HELD. Product PM449 owns routing; Software owns exact test import, gate/parser
corrections, and pinned exhaustion fix return. A fresh Verification issue should
identify the next concrete head and actual evidence at return.
