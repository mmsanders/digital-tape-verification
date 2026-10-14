# Off-card A6 rehearsal — native collection only

This package is for Verification146's next native-format review. It creates a
new disposable **4GiB+1MiB image**, provisions it and traces one verify. It has
no physical device argument, load, dump, pull or card stage. **Do not put the
card in the reader for this rehearsal.** Keep the existing accepted card intact.

Unzip `offcard-rehearsal.zip` in an ordinary local disk folder with at least
6GiB free. Keep `a6check.py`, `a6-macos.d` and both scripts together. Use the
same unchanged shipping release binary already used for the accepted round trip;
scripts enforce its exact hash. Do not rebuild or use tapectl-test. No new
software/security-policy workaround is required: a missing tool, blocked script
or inaccessible tracer is a stop and a concrete limitation to return.

Mac: native arm64, macOS26+. In Terminal, from the unpacked folder:

```sh
sh ./rehearse-macos.sh /absolute/path/to/your/tapectl
```

Replace only the binary path; quote it if it contains spaces. DTrace may prompt
for the administrator password. The script reads SIP status; it does not change
it. Do not disable SIP or use an injected tracer. A probe refusal, drop, error or
non-PASS stops the run. The exact DTrace program has not yet been run on a Mac.

Windows11x64: open native x64 **Administrator PowerShell**, change to the unpacked
folder, then run (replace only the existing shipping-binary path):

```powershell
.\rehearse-windows.ps1 -TapeCtl 'C:\absolute\path\to\tapectl.exe'
```

An existing working Python3 is used for an optional local checker. If it is
unavailable, the scripts still collect native raw evidence and record that the
local checker did not run; send those logs for independent review. No install,
execution-policy change or tracer cancellation workaround is part of this
handoff. WPR only stops the session this script successfully started; a failed
start does not cancel another recording. Actual WPR profile/export field
availability remains unvalidated until this rehearsal returns.

Both scripts hash the binary/helpers, save versions/free space, exact image
size and allocation observations, provision/verify stdout/stderr/exits/PID,
tracer diagnostics/exits and checker result or explicit not-run reason. Windows retains **raw ETL plus XML**.
The output zip excludes only `rehearsal.img`, which remains locally. This avoids
uploading a 4.3GB image. Keep the original run folder too. Once its evidence is
retained, you may delete only that new folder's disposable `rehearsal.img` to
recover space; do not delete card files or unrelated folders.

**Always stop after one rehearsal per platform, even if checker says PASS.**
Send the printed evidence zip(s) to Verification146; if a preflight stops before
creating a run folder, send the exact error. Checker PASS is a diagnostic
observation, not native/physical acceptance. If zip creation fails, retain the
raw log folder and report that failure. No automatic retry or physical verify
follows. Verification independently reviews completeness/native shapes and
results before issuing separate short read-only physical commands.

Script validation here is source review and POSIX shell syntax only. Windows
PowerShell/macOS DTrace have not executed in this Linux environment; the purpose
of this bounded rehearsal is to collect those actual observations honestly.
