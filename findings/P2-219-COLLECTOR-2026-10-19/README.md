# Verification219: physical A6 collector stop

Input Verification main c5e28b80a0e505a295fa71daaef7a6d2c6f411c6;
Product main d09e5ba772729cb9b3d1c9b38b9052c4cbf77c6e (ADR189). Assignment219 updated
2026-10-19T20:38:41Z; PM475 routes Verification only. Software is not contacted.
Original document at b9f08bf655cd9a20f2122b5a962f3bf05315f996 has SHA256
73cf18e5a31b2d1e3958a04459ff764dfbd42872b23ac776fdefe204e78232b7.

The original function assigns a local `$LASTEXITCODE = $null`, invokes a native
application, then reads that same local variable. Native execution updates the
global automatic variable, which the local null shadows. A successful process can
therefore be followed by the observed missing-exit stop. The corrected function
explicitly clears and reads `$global:LASTEXITCODE`; a missing actual exit still
throws, and a real nonzero exit remains nonzero. Native stderr and the caller's
error preference retain their prior handling. No success value is fabricated.

`controls.ps1` extracts the exact old and new functions from their documents,
checks that their executable difference is only those two scope qualifiers, and
uses harmless cmd.exe children with actual exits0/7 plus stdout/stderr. It also
tests a returning PowerShell function without any native exit (stale zero seeded),
a nonexistent executable and a redirection failure. Optional WPR invocation is
`-profiles` only. CI runs Windows PowerShell5.1 and PowerShell7 on Windows Server;
it does not start/stop a trace, elevate, touch a card or run tapectl. Raw results
and stdout/stderr are retained by the scoped workflow.

Actual CI39321782153/job118297380197 passed on Windows Server2022 with
Windows PowerShell5.1.20348.5622 and PowerShell7.6.6. Both reproduced the original
missing-exit error after true native exits0 and7; both corrected versions returned
the actual0/7 with stdout/stderr, rejected missing exits and invocation failures,
restored caller error preferences, and returned actual0 for WPR profiles only.
This confirms a collector defect that accounts for the screenshot; it does not
prove that Michael's WPR invocation itself succeeded. Initial control iterations
corrected an overly specific expected invocation-error message and a test-only
Get-Command array conversion; the collector correction remained the same two
scope qualifiers. First green raw receipts are retained in release
`evidence-219-1073160cee10361c2d22f804943b678162c84174`, native-controls.zip
SHA256 e5fdd3dbce091e782c0d467cfcb7fbeb849a1f881b2beab636da0b8a98f74b21.
That first Windows release also contains CRLF checkout copies of the scripts;
use the subsequent exact-LF publication linked from the issue219 final return
for corrected instructions. The workflow now preserves and authenticates exact
instruction bytes before its controls and final immutable release.

Corrected WINDOWS-READY.md SHA256:
0077ff5c14a47db5d08bc964702bbc84fa712dbee91b6055000ece032efe30fd.
The immutable `evidence-219-<author-head>` release carries native-controls.zip,
WINDOWS-READY.md, controls.ps1 and SHA256SUMS. The issue219 return binds the final
green CI and merged main commit. These are process-control observations only.

Michael's screenshot establishes a stop at profiles before the visible block's
trace start and card verify. It does not establish WPR's actual exit or explain
any other card command. The scope defect is reproduced on both tested shells, but
his profiles-out.txt, profiles-err.txt and PowerShell version are unavailable.
No further physical run is needed to diagnose this defect. Those existing two
files and version are the smallest optional facts to distinguish an additional
WPR profile/capability failure on his machine.

The corrected WINDOWS-READY.md is a candidate collector, explicitly PAUSED until
PM475 updates Michael473 and authorizes continuation. It adds a PowerShell-version
receipt and changes the return destination to473. All disk/binary/geometry/free-
space/confirmation checks and the single read-only verify/trace evidence gates
carry unchanged. Shipping tapectl SHA256 remains
82798af2899e9364b9c9bfaa2021daf6cc51ccd0c6562598d50e0a86944bb7a9.
Preserve the existing folder. No retry, reset, format, pull, trace cancellation,
policy change or replacement binary is authorized. Corrected206 INGEST is separate.

Stop after this bounded collector disposition. PM owns physical continuation;
Windows11 physical/native evidence and overall A6 acceptance remain held.
