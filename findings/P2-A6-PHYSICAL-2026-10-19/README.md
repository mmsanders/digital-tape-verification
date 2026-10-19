# Physical Windows A6 return: native read proof present; overall gate held

Michael directly returned the authorized one-verify continuation on19 October2026.
PM473 (updated20:49:54Z) lifted the collector pause for the exact instructions
published by PR220. Input Verification main4073bbc6c8f8e909f1410c69a214e86676f5fcac;
collector instructions SHA2560077ff5c14a47db5d08bc964702bbc84fa712dbee91b6055000ece032efe30fd.
This is a new physical return, not a reopening/repetition of the off-card rehearsal
or collector219. The reply listener remains paused. No Software notification.

## Observations authenticated

Original attachment `a6-physical-win-20261019-142004.zip`:92,802,476bytes,
SHA2560246c24a96b1de22bad15086aa925def9d2b43bb6ecd13c146a305f914df0bcb,
matching Michael's attached screenshot. All29 listed member hashes pass. Original
ZIP and full ETL/XML remain in Michael's attached packet; no full-machine trace or
unrelated host data is republished here. NATIVE-EXCERPT.json selects original
records with their original indices; it is not a substitute complete capture.

Windows11 Home10.0.26200 x64; Windows PowerShell5.1.26100.9444. Target was
PhysicalDrive1,62,537,072,640bytes,512-byte sectors; before/after geometry agrees.
Michael confirms the same card/reader, retained insertion and one verify; CID is
unavailable through the USB reader. Shipping tapectl hash is exactly
82798af2899e9364b9c9bfaa2021daf6cc51ccd0c6562598d50e0a86944bb7a9.
PID30236 returned actual exit0 and stdout `OK`; stderr empty. Start/end receipts
21:20:22.5713985Z–21:21:09.9965346Z span47.4251361s including collector bookkeeping.
WPR start/stop and tracerpt actual exits are0. The collector scope correction worked.

The unchanged accepted checker from Product441/a50a211679b7893c7ac581d392784191519525d6,
SHA2567cbba051629d56bffd85e715fe34cb909421aa6b105a52c883f383aed10b8d89,
streamed all948,634 XML records locally. Existing16 Verification controls passed.
CHECKER-RESULT.json is its actual unmodified result, including one FAIL reason.
No Windows executable or physical command was run by Verification.

Two native FileIo reads at62,537,072,128 each requested512bytes and their unique
OpEnd records report NtStatus0 and ExtraInfo512. They cover the complete final
sector above4GiB. The accompanying DiskIo requests provide corroboration but are
not used as returned-length proof. Header EventsLost/BuffersLost are both0;
the observed schema warning is qualified by the accepted raw-payload decoders.
No required class remains undecoded. The checker observes77,556 target read
records (FileIo plus DiskIo observations), zero target writes and zero target
flushes. This is not77,556 independent high-level calls. Open access mode is not
observable in the ETW Create record, so it is not inferred.

## Precise remaining stop

Overall physical A6 is **HELD**, not PASS. The exact accepted checker returns
**FAIL solely for four records after the observed process/thread lifetime**:
480422,480439,480466,480483. It explicitly does not attribute them to PID30236.
Its identity classifier calls all four unrelated and names the system-volume
`\Device\HarddiskVolume3\$LogFile`; there is no unresolved write target. During
the raw audit, records480422/480466 decode as4096/8192-byte FileIo writes with
FileKey0xffffa18609084d30. Records480439/480483 are their DiskIo counterparts on
**DiskNumber0**, with that same key. The card is **DiskNumber1**. These concrete
other-disk facts are the basis of the recommendation below. During
the observed process lifetime its five other-stream writes are likewise identified
as system-volume LogFile/Mft or the host stdout file, not the card.

The current checker exempts positively unrelated post-exit FileIo writes only
for IMAGE targets. The physical target retains the stricter whole-disk rule.
This return therefore does not waive those four records, turn the gate green,
or imply corruption of the card. Full read proof and overall gate disposition
are separate findings. The exact record/payload evidence and continued negative
controls are preserved for PM's bounded method decision.

Recommendation: PM schedule a focused disposition of these retained four records
and whether the physical rule needs a distinct-other-disk exclusion. Any changed
method needs its own issued scope and causal controls; do not relax a test to fit
this return. The saved ETL/XML and bytes already contain the evidence needed for
that review. **No physical retry, reset, reformat, load, pull, replacement binary,
trace cancellation or security change is requested.** Software remains undisturbed.
PM owns the current Michael473 brief; Mac/full-package/physical media qualification,
write-command A6 and other held acceptance remain unchanged.

## Reproduce

Use Michael's exact attached ZIP and Product441 checker at the pin above.
`replay.py --packet ORIGINAL.zip --checker PRODUCT/tools/wp14-capture/a6check.py
--work NEW_EMPTY_DIRECTORY` authenticates the ZIP/member receipts and compares the
full actual checker result. `extract.py verify.xml --out NATIVE-EXCERPT.json`
reselects the original native records. `validate.py` checks the committed compact
native facts and preserves the non-PASS stop. CI runs that compact validation and
the existing16 controls; full private-capture execution was local and is explicitly
not claimed as CI execution. Publication itself grants no physical retry or PASS.
