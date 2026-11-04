# V388 exact Software kit review — HOLD

Assignment: [Verification388](https://github.com/mmsanders/digital-tape-verification/issues/388), Product PM657 / ADR205 at aa3b87f9eab583fada697c82cb9fe3226fef80d6. Required current Product entry documents and scoped authority authenticated in AUTH.json.

Reviewed Software652 / PR654 exact **d62e0de07c81dc5abe1c8ffbf378bd077a2a7eab**. Engine tree d96b4245e04d74078f8938744b1394c3018516f7 remains unchanged. The sole firmware-changing implementation commit follows both unchanged test imports: be1_binding_r1 tree b094d319e184bd6c410d93604e9ec784c60ba490 at586abc12652a5bd64901e68a017e3f35bed3eb6c; be1_if3_r1 tree b8b7ce9f02e6aa551cdd526a91dfe21c2c70e7ae at0591f474f493d13eb19617b81ba5331c4a5ac72e. Source provenance, branch scope and canonical file hashes are retained in AUTH.json.

## Findings

**SW652-R1 / P2 — continuous received data bypasses wall-time expiry.** Capture.read checks the deadline only following an empty read; its nonempty path writes and immediately returns. Under the published fake port/clock, a 0.03-second digest capture succeeds at 0.91 seconds. Digest, info and timed interrupt modes all reproduce. Enforce expiry on every path including completion, while retaining all bytes actually received. This is a simulated timeout invariant, not measured target latency.

**SW652-R2 / P2 — bundle confinement is lexical only.** safe_path and check_files accept linked/quiet.serial even when its directory resolves outside BUNDLE. A task-owned Windows junction to synthetic saved bytes is accepted by the unguarded checker (exit0, overall NOT_RUN, F1 CONSISTENT). The independent guard detects and denies the outside read (exit97). Reject resolved escapes before opening the file; guard denial is not Product confinement. Linux regression uses a symlink; Windows uses a junction. No private data or device was accessed.

**SW652-R3 / P2 — malformed field types escape validation.** An observation with criterion=[] causes FIELDS.get to raise TypeError; superseded_by=[] similarly raises from ids.get after schema validation. Both runs terminate without the required INVALID report. Validate types before dictionary lookup and return report/exit2. TYPE-PROBES and the new two regression cases retain both failures.

These are review-discovered combinations, not a claim that the old implementation followed these new expectations. Import tests/be1_review_r1 unchanged before implementing their fixes. Default strict mode must pass all eight cases on the corrected head. Historical mode pins this original checker/helper hash pair and succeeds only when exactly six failures and two positives reproduce; its green result is explicitly HOLD, never clearance.

## Execution and scope

Canonical-source Windows execution: existing checker109/109, capture4/4, IF3 checker53/53, IF3 capture47/47 pass. All32 existing harness controls pass. New eight-case package reproduces six failures and two positives, with six detecting predicate controls. Small result summaries are retained beside this report. The publication workflow repeats these covered suites and controls on Ubuntu24 against the exact Product head; its run identity is supplied in the publication return. Raw generated bundles/streams are not committed. Frozen reference bytes were hash-authenticated, never regenerated. Old packages and dispositions are immutable.

Covered checker, capture helper and bench packet were reviewed. Packet commands agree with the seven frozen reference recipes and retain failed attempts, real provenance requirements, F3 pending/F4 deferred, USB-only preparation and target safety boundaries. Passing synthetic observations establish artifact consistency only. The three findings prevent off-target kit clearance; no firmware, target, acoustic, media or physical-method acceptance follows.

Product PR654 CI:113 success,2 cancelled,1 skipped,2 failed. Both macOS jobs were runnerless with zero steps before cancellation; regression failed30/31 and qualification failed13/15, with a dependent package census skipped. This is a separate CI blocker, not evidence of a kit logic failure. ADR205 routes normal-aggregate deferred-macOS correction to Software658; mandatory selected Windows/Linux, goldens/integrity and uncertain/missing/failure/cancel handling must remain fail-closed. No policy waiver or Product workflow edit is made here.

## Publication and dependency return

Hardware review PR387 is now published unchanged at merge45033381d64759fc43d0466d29e0e08198c81a65, source d474aec3bd35b094ff69bf818c2bbd1d935f5686, tests/rig_review_r1 tree a640b1c1f340efa0a7288efa164489a3b648e3ab, CI41876912450 SUCCESS. Hardware651 received those unchanged fix-import pins. Its original18852b5 stays HOLD for HW651-R1/R2.

The final named-input check found no Software658 return comments and no corrected Hardware651 head (latest return is our publication pin). Therefore the CI-policy and corrected-Hardware reviews have no supplied candidate. Publish ready work, return findings to Software652 and stop at that dependency under388. No automatic polling, new campaign, purchase, energising or Product merge is authorized by this disposition. Fabrication/charging remain CLOSED; DRAFT11 is not issued.
