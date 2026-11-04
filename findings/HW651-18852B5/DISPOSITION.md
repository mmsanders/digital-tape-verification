# Hardware651 exact-head review — HOLD

Reviewed on Michael's direct instruction "review work from hardware"; return uses
existing651. Candidate18852b5080419585d0f7300d996af959014bc47a, Product main51d0f8f,
Verification input84c95d0e. No Product files or prior package bytes were changed.

**HOLD for two reproduced code findings and unresolved Product CI.** The published
27/71/229-case suites all pass independently on this head. Those results establish
their bounded coverage, not overall clearance. New review regressions expose six
failed cases across the two findings; one valid-setup positive still passes.

## HW651-R1 [P2] — unqualified setup still earns proof and cut credit

In media_atomicity.py, judge's manifest handling records a missing/bad/repointed/
wrong-card manifest as a problem and leaves mf=None. _validate_r2 at line497 then
returns True without a manifest. At lines710–723 judge still counts qualifying rows
and calls completion_proven for OLD. A valid row trace cannot authenticate the
run's missing or failed setup.

Reproducer: a manifest with controls.E0.result='fail', otherwise coherent synthetic
records and1,000 good row traces plus a late OLD row. load_manifest correctly reports
the failed prerequisite, but judge reports qualifying=1000 and
completed_write_reverted=[1001]. The same occurs with no manifest, changed exact
manifest bytes and a manifest belonging to another card. The final verdict is FAIL
already; **this is erroneous proof/count reporting, not a false PASS**.

ADR204/WP05 forbids completion proof from unqualified/incomplete evidence, and the
corrected schema requires authenticated matching plan4 setup before a rig-r2 row
earns credit. Gate qualification/rollback proof on that authentication, keep the
setup/run-integrity problems and preserve raw observations. Do not attribute a
rollback to the card when its method prerequisites failed. A valid authenticated
OLD completion must still be detected; blanket suppression is not a fix.

## HW651-R2 [P2] — invalid manifests escape the problems-return API

Schema5.1 promises load_manifest never raises on bad input. Two independently
reproduced inputs violate that contract:
- host_script.path containing a NUL raises ValueError from path resolution/read
  (ref at line217; only OSError is caught).
- a500-digit integer in an A threshold raises OverflowError in math.isfinite
  (_num at line182), rather than returning an out-of-window/input problem.

Both are validly serialized JSON test inputs that the loader must refuse through
its documented problems list. Validate unsafe paths and numeric conversions, or
convert expected validation exceptions into problems. No new limits need be invented.
Windows observations are retained; CI reproduces the exact candidate on Linux.

## CI and authenticated coverage

Product PR646 exact head has53 successful,15 skipped, one cancelled macOS job and
one failed regression aggregate. Run41872559629, aggregate job126732546248 records
`FAIL abandoned selected wp14-macos` and `regression: FAIL (30/31 ran)`.
The cancelled macOS job's raw log was unavailable. This does not establish a rig
code failure in that job, and it is not green required CI. No broad rerun or gate
relaxation was performed. Resolve/reroute it with the integration owner.

All three imported trees match their independent publications and precede their
corresponding implementation commits:1ca703a4 at9f611c4 beforedc38a4d,
ccf9bd21 at7832f52 before577d177,0d38fbe2 atfa6417b before18852b5. The declared
already-existing row extras get no retrospective tests-first waiver. Diff against
main stays under hardware/. Authority hashes and exact identities are in INPUTS.json.

Canonical Git judge blob03382e6ec422a06048514122db0c2b4557ae46ba, LF file SHA256
4d199e54673e12dafc5ecf026f5d9fbaf4022bd9d310b9e6e8ee97f49e34a21e was exported
for independent runs. Hardware's CRLF working-file hash is a different file identity;
that difference is not a source-tampering finding.

New tests/rig_review_r1 preserves prior tests unchanged. Its strict mode rejects
this head; historical mode authenticates the old blob and exactly six failures.
Green historical CI reproduces the HOLD, never clears it. These new regressions
are authored during review; import them unchanged before corresponding fixes.

Next owner Hardware651: correct the two findings, preserve evidence, import the new
regressions before fixes and return an exact head with CI status. Product merge stays
with Software/PM routing. No physical method/campaign, calibration, media, SPI-to-SD4,
safety, purchase, fabrication/charging or batching clearance. All records are synthetic.
