# Mac off-card A6 rehearsal — collection unavailable; physical stage HELD

Verification146, 14 October2026. Michael returned actual native off-card evidence
after the guarded176 handoff. This disposes only that Mac rehearsal, not a new
card campaign, Product implementation or full-WP14 acceptance. Required agreement/
charter/status blob pins remain unchanged; live146 retains native/physical holds.
Product426 has integrated exact72e4e7c695655e25013e7849104a878856edbfb5 via
mergec4eb211cfbf67722abd439b6d16414ccb6ec9040; correction428 is now closed.

## Authenticated observations

Original `a6-rh-mac.azesRa.zip`:65,223bytes,22members including one directory;
SHA256`cd7ec2507a6308bf572a15627ae68125e04c13a5974e5ba96830d89812b04c5a`.
Original bytes retained unmodified in the evidence directory. No Library read or
change to the upload. Source hashes computed independently match176:

| File | SHA256 |
|---|---|
| Actual126,536-byte shipping `tapectl` | e7550d8bedbb0c784fd528c387a87cca2bad8d1b411c39217d25377329bb0beb |
| Actual `a6check.py` | 227ceed2f1ca8817447c4103983c72b16a060b1d3323de22c805289b621bd1ef |
| Actual `a6-macos.d` | c9764f11f7894fbe57dc08b0fb6248e70ce244b2f6137a9ee59d057397af7be8 |

Before/after hash records are identical and match actual bytes. Native host is
arm64 macOS26.2/build25C56; SIPenabled; Python3.9.12. Free space record shows
32,956,176KiB (31.429GiB), above the6GiB handoff guard.

| Observation | Actual evidence | Scope |
|---|---|---|
| Image provision | Saved exit0, empty stdout/stderr | Provision reported success; no fresh card operation |
| Image size |4,296,015,872bytes in geometry.txt | Bounded4GiB+1MiB image; mirror interval[4,296,015,360,4,296,015,872) |
| Allocation | `du -k`:256KiB; apparent size above4GiB | Sparse allocation observed on this Mac, not assumed for another filesystem |
| Verify stdout | `OK` | Reported successful verification text; native tapectl exit not captured |
| Tracer | DTrace exit0; SIP feature-unavailability notice | Tracer wrapper completion, not native I/O/result proof |
| Trace | BEGIN target44532 and END only | Zero process/open/read/write/flush/exit observations |
| Checker | FAIL, exit1; three failures and two holds | Correctly rejects unusable collection |

The complete42-byte trace is:

```text
A6 trace tool=dtrace target=44532
A6 end

```

DTrace stderr contains only its79-byte SIP feature-unavailability notice. No
drop or explicit runtime-error message is observed, but zero observed calls
cannot be promoted to complete tracing merely because BEGIN/END and exit0 exist.
No traced process exit exists; saved `verify-pid.txt` is the DTrace target, and
cannot independently bind a shipping executable when all process/open records
are absent. Do not infer tapectl exit0 from DTrace's exit0 or stdoutOK.

## Independent disposition

Ran the authenticated returned checker against the original raw inputs on Linux
(hashing the Mach-O binary as data, not executing it). **FAIL exit1** exactly
reproduced the entire saved checker JSON, including input hashes. Reasons:

- no captured record belongs to PID44532;
- PID44532 never opened rehearsal.img successfully;
- no read touches the full mirror interval above4GiB;
- no DTrace open executable-name binding;
- no recorded/traced tapectl exit.

The last two remain explicit HELD reasons. This is a native collection/capability
limitation, **not evidence of image/card corruption or a Product verify defect**.
SIP is enabled and warned of unavailable features; the precise reason for absent
observations (probe availability, target attribution or another collection limit)
is not established by this bundle. Do not call it a proven SIP-only cause.

The176 scoped parser/method correction PASS remains accurate: it was not native
format/probe acceptance and its fail-closed path correctly rejects this return.
All earlier accepted Mac/Windows/C60/ten-pull/README observations retain scope.

**Rehearsal disposition: unusable native capture; Mac physical A6 HELD.** No
physical verify instructions or unchanged Mac retry. Keep SIP/security settings
unchanged, shipping binary unchanged and no injected fallback. Return the exact
native limitation to PM384 and Software for the appropriate scoped next owner;
428closure does not self-activate a fresh execution assignment. Existing146
owns the evidence disposition and stays open. PM can issue diagnostic/method
work under the existing boundaries; this report does not authorize it itself.

Windows off-card collection remains independently issued by176/386 and may
proceed using that existing handoff. It is not blocked by this Mac collection
failure, and no physical Windows/card stage is advanced. No new full load,
dump, pull, README or other card operation is requested. Separate169 remains
unfinished and can continue its authorized host-only independent authoring.

Evidence directory contains the exact zip, independent JSON/exit and portable
replay. Run `python3 replay.py` there. Replay success means reproducing the
correctly rejected native capture, not native/card acceptance. SHA256SUMS pins
all retained files. Raw bundle is below the1MiB tree limit.
