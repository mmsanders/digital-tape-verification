# C1 Stage 2 — findings on Software624 exact head; C2 not cleared

Verification364, 28 October 2026 PDT. Stage1 is published at merge
`48489cf9a53f390de4ded216dc1f293c15e830ee`. Software's
[Ready for Verification return](https://github.com/mmsanders/Digital-Tape/issues/624#issuecomment-6480248520)
is for **`8c142d3b9d382d5d48fd648ec53a11b0d59a805c`**, Product PR626.
Same-issue Stage2 is authorized by Michael's scope update. No Product implementation
edit, native app launch, physical card, kernel tracing or new receipt session.

**FINDINGS. This exact head is not cleared for integration or Michael's C2 run.**
WP-14/WP-16 Stage1 acceptance stands. WP-15 G1/G3/G4/G5 close only after C2; G2 is
separate. Correct and return the next exact head in Software624; Verification364
disposes that correction in this same issue. No separate method/admission round.

## What passed, and what it proves

- Downloaded the actual make/candidate artifacts from runs40761455133/40761454767,
  authenticated both workflow head SHAs as the returned exact head, and re-ran the
  **unchanged `tests/wp15_cards_make_r1/runner.py`** over every retained file.
  **31 Linux + 10 Windows Server rows PASS**, equal to the producer's judgments.
  This includes actual private loop/dm/VHD I/O, equivalence, refusal, report parents,
  removal/reinsert/swap fixtures and fail-stop behavior within the reported scope.
- The non-NULL verify-binding mutant is rejected by that same immutable judge.
  This is a mutated observation bundle, not a new execution of a defective Product.
- Reviewed the adapter journal conversion and covered host open/bind/I/O/fail-stop
  paths. The observer records actual compiled-test call sites; policy facts are
  injected, device I/O is real. Hardcoded session1 is bounded to the observed single
  authorized open; the oracle separately rejects another open. Probe/query handles
  are outside this trace, which is disclosed. ADR-195 requires no new kernel observer.
- Independent production-bridge tests pass on this head in the C1 CI job: actual
  file/mixed drop admission, worker completion on spawn failure, Make decline/spawn
  failure, and all eight pre/post-confirm recheck mismatches. Recheck/launcher inputs
  are typed component boundaries. No real UAC/gesture/device acceptance is inferred.
- Actual Software G1 static gate and independent source mutations were requalified:
  baseline and ordinary file pass; all three raw-device source mutants fail.
  Inspected production ordinary ingest/cards spawn versus make-only runas. PE
  resources request no elevation. Default invoker is recorded honestly, not as
  fictitious explicit manifest nodes. #361's Medium parent carries under ADR-195.
- Engine is unchanged `d96b4245e04d74078f8938744b1394c3018516f7`; no spec delta.
  Imported S3 tree `81b627b7149458c0037dda5e69eac337f40fb8bd` is exactly the verifier
  tree. Candidate byte identity is confirmed below. Product's returned PR checks
  were 129 SUCCESS; green checks do not override the findings.

The five-point [make method note](https://github.com/mmsanders/Digital-Tape/blob/8c142d3b9d382d5d48fd648ec53a11b0d59a805c/docs/REVIEW/software-c1/MAKE-METHOD.md)
is coherent on provision's accepted safety/open, one retained handle, NULL-write
verify, OS-reported removal classification, report parent binding and test scope.
The path-query/open race and invisible swaps are disclosed limits expressly
retained by ADR-195; they are not new holds. The note's assertion that no query is
made and hence HOST_QUERY_FAILED cannot occur is incorrect for initial required
queries, as F364-1 explains. Typed launcher tests are not the real UAC prompt;
that observation belongs in C2. No new native tracing requirement is added.

## Findings and required correction evidence

### F364-1 — required-query OS errors collapse into policy refusals

APP-1A §7 remains normative under ADR-195: a failure of a required initial safety
query must stop with exit1 / `HOST_QUERY_FAILED`, `subject:null`, `phase:safety`,
`op:media_query` and the OS error. Known unsafe policy facts retain exit3. No new
post-authorization polling/query cadence is required.

The exact head explicitly says make never emits HOST_QUERY_FAILED
([tapectl.c:1041](https://github.com/mmsanders/Digital-Tape/blob/8c142d3b9d382d5d48fd648ec53a11b0d59a805c/host/tapectl.c#L1041)).
It calls `target_safety_why` and reports any nonzero result as a refusal
([tapectl.c:1208](https://github.com/mmsanders/Digital-Tape/blob/8c142d3b9d382d5d48fd648ec53a11b0d59a805c/host/tapectl.c#L1208)).
Windows `probe_device` actually calls required DeviceIoControl/system/pagefile/
volume queries. Failed queries leave refusing facts and return0; for example
`IOCTL_DISK_GET_LENGTH_INFO` failure becomes `UINT64_MAX`, hence a size refusal,
and a system-volume query failure leaves `holds_os=1`. `target_safety_why` has no
separate query-error outcome. The authorized open also performs a required
geometry query in `hport_os_open`; its failure is collapsed into device-open exit2.
Fail-stop disk safety is preserved, but these are not the specified error outcomes.

**Correction:** distinguish required-query OS failure from known policy refusal in
make's host path, preserving existing standalone provision semantics and safety.
Use the already-published `wp15_boundary_query_r1` expectations plus current ADR-195
rules: a real failed required OS query with a known-policy-refusal neighbor, exact
report/exit/OS-error binding and no subsequent work. A narrowly compiled test-only
fault paired with shipping-source evidence is sufficient; no physical/native
session or new observer is requested. Check the resulting real failure through
the production app completion path and its card-interrupted sentence.

### F364-2 — actual child outcomes are not yet connected to G3 bridge evidence

The new Make tests in Software's return are typed component inputs. The S3 bundles
are real tool outcomes, but do not run the app completion/message path. Neither
fact establishes the end-to-end child-origin mapping required by APP-1 §7. Existing
parser fixtures and producer-private tests cannot supply that missing linkage.

**Correction evidence:** run the Stage1 `c1_closeout_r1/g3.py` child-origin matrix
through the production completion path using actual tool exits/report originals
on CI images/loop/VHDs. Reuse existing real S1 outcomes where already published;
bind them to their actual source/version/nonce/exit and independently authored
message expectations. Capture outputs/raw refs and adapter/bridge refs. Include
capacity, removal/device I/O, verify findings, truncated music, safety refusal,
generic make and required-query failures. Preserve the original report when
passing it to the parser; do not manufacture a report for an expected message.
Changing captured stderr wording with the same exit/report must not change the
message. App-origin typed tests already pass; they do not need a new native run.

This is the contract's existing G3 requirement, not a request for every imaginable
failure, a new admission round or a global coverage theorem. If a particular case
is contractually guarded/unreachable, identify it specifically for disposition.

### F364-3 — finish the lawful own-p1 positive after verifier routing correction

Software correctly reported the old judge's F1/F2: the success path rejected a
lawful own-p1 unmount, and an invalid label cannot be a retained-session case.
Stage1 added `c1_closeout_r1/make_supplement.py` beside the immutable old package.
Stage2 strengthens its control to require **successful** own-p1 unmount before
authorization and reject failed/foreign unmount or any early write.

**Correction evidence:** return the real lawful exact-own-p1 unmount + one-session
success row, judged by the supplement and ordinary equivalence checks. Existing
failed-unmount and byte-invalid-layout refusals carry. Route invalid-label exit2
to `input_refusal`, not `session`; retain its original process/report/trace and
unchanged-target evidence. No assertion edit in an imported old package is allowed.

The old M1 parser omission of HOST_QUERY_FAILED is already addressed by the separate
published `wp15_boundary_query_r1` extension; use it. S2 fixtures holding no audio
and hence disabled Make do not test Make-era readiness. Existing `shell_oracle`
readiness predicates and Stage1's real-ready bridge setup are the current boundary.

## Exact candidate identity

| Item | Independently measured SHA-256 |
|---|---|
| ZIP | `20221d65592334baaf5c51b4ab958cc1d6c4e59b70e5caddea1cae10fc97db77` |
| digital-tape.exe | `869ba8c48b676a6422fbe49ca6c21efd05a65f9e13a72fbfb729ba11797cfd5a` |
| tapectl.exe | `5186a1e05e0df753512baadf102be9d19fa8b315336c1286dfbb7cc82d85e24a` |
| ingest.exe | `3895f3f356c91b8a9fe870c33694da64bf2765df308bef118d657c1be4bb9a20` |

ZIP/member bytes equal Software's declaration, BUILD head matches the returned
head, app contains the two compiled child hash pins, tapectl contains the declared
head version and no TAPECTL_TEST_FACTS/PAUSE strings. Build identity and code
review carry source binding; hashes alone are not a reproducible-build proof.
Candidate workflow40761454767 and make workflow40761455133 both completed SUCCESS
on the exact head. No candidate executable was run by this audit.

## Durable replay and next owner

Original downloaded files, candidate ZIP/build evidence and A6 result are retained
in [evidence-364-c1-2026-10-28](https://github.com/mmsanders/digital-tape-verification/releases/tag/evidence-364-c1-2026-10-28),
asset `verification364-c1-inputs.zip`, 50,714,663 bytes, SHA-256
`c6b1130387ef9f111242b896ee048c6e36af326fefe32e5e74250a4110563263`.
`fetch.py DEST` verifies that hash before extraction; `audit.py DEST --out RESULT`
replays the immutable S3 judge, negative control and byte checks without executing
Product. CI runs this same replay and the independent boundary-query controls.
AUDIT.json records all row results, original artifact digests and declared limits.
The native Windows Server observations stay supplemental to C2's Windows 11/card.

**Next owner: Software624, same branch/correction task.** Return corrected exact
head, CI/raw bridge and own-p1 outcomes, revised method note, and candidate hashes
if the build changes. Verification364 remains open to dispose that head in this
same issue. Michael resumes the leads manually; no lead wakeup, automatic polling
or extra task is started. Michael should not run C2 with this head.
