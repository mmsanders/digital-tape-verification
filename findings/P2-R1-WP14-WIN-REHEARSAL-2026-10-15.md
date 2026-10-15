# Windows 11 off-card rehearsal — native export unsupported; physical A6 HELD

Verification #146, 15 October 2026. **Reader disconnected is fine.** The issued
#176 rehearsal targets only a new local `rehearsal.img`; neither card nor reader
is required. No physical stage follows this return. This is an actual native
evidence disposition, not a repeat of completed C60/load/dump/pull/README work.

Inputs: Product main `c6ff868086e3333bb7568e60d3a2f4ec60fd3344`, Verification main
`fe8f3bdf16c83ef8564d073e900bb1b98cf125a4`, live #146 updated
`2026-10-15T16:03:31Z` plus latest ADR-181 routing. Required AGENTS/CLAUDE/STATUS/
Verification charter re-read at that Product pin. Product's accepted #176 method
head `72e4e7c695655e25013e7849104a878856edbfb5` was integrated via `c4eb211`.
No Product implementation/private tests inspected; individual lead, no subworkers.

## Authenticated actual observations

Original ZIP `a6-rh-win-a00d8c054a0d41ccb1e026d735f97dbc.zip`:
98,602,972 bytes, 34 members, SHA256
`9b23466b502f386bc3c12ac8a6674710d0caf9491358c2c654bb5717d7cbd755`.
All members were read/hash-checked, including the 278,921,216-byte ETL and the
1,770,780,200-byte XML. The original attachment remains unchanged.

| Observation | Actual record | Boundary |
|---|---|---|
| Platform | Windows 11 Home x64, version10.0.26200/build26200 | Named desktop target, not Server/Windows10 substitution |
| Shipping exe | 435,533 bytes; SHA256 `82798af2899e9364b9c9bfaa2021daf6cc51ccd0c6562598d50e0a86944bb7a9` | Exact #176 release; hashed as data, never executed here |
| Checker | SHA256 `227ceed2f1ca8817447c4103983c72b16a060b1d3323de22c805289b621bd1ef` | Exact #176 bytes; before/after hash records match |
| Image | 4,296,015,872 bytes (4GiB+1MiB), on disk0 local NVMe, logical512/physical4096 | Image capacity differs from backing-disk capacity; no physical-card target |
| Allocation | fsutil marks file sparse, exit0 | Sparse attribute observed; actual allocated-byte count/free-byte value not present in the saved formatted reports |
| Provision | exit0, empty stdout/stderr | Fresh disposable image only |
| Verify | PID4596, exit0, stdout exactly `OK`, empty stderr | Successful tool result, not proof of native call coverage |
| WPR/export | start0, stop0, tracerpt0 | Export stdout warns some events do not match schema |
| Local checker | Explicitly not run: no existing Python executable | Allowed by issued handoff; not a missing user step |

ETL SHA256 `8241f5560b5d5e367d1d9b6e954ef34d26db630824bad72d7e23874a033872cc`;
XML SHA256 `e50da0d54c0ab406e49431ff23f189ce28475670358e19dc4978232899f834d8`.
Windows exports several side reports as UTF-16; they were decoded accordingly,
not mistaken for corrupt text. The script's free-space guard preceded execution,
but `space.txt` contains no numeric Free value, so no measured free-byte claim
is made. Keep the original ZIP/run folder/ETL; no unchanged recapture requested.

## Whole-export audit and concrete native incompatibility

Independently streamed **all 1,232,801 events**, without a full XML DOM. All have
timestamps, with zero adjacent ordering inversions. The actual EventTrace header
has `EventsLost=0` and `BuffersLost=0`. These are good recording facts; they do
not repair absent decoded fields or prove usable process/result attribution.

**WIN-A6-001 — event-class location differs.** Classic kernel records place
`9e814aad-3204-11d2-9a82-006008a86939` in `System/Provider/@Guid`. Their event
class is instead `ExtendedTracingInfo/EventGuid`, e.g. Header `68fdd900…`,
Process `3d6fa8d0…`, Thread `3d6fa8d1…`, FileIo `90cbdc39…`. The unchanged helper
dispatches on Provider Guid. None of its five recognized class GUIDs occurs as
a Provider Guid anywhere in this export. It therefore recognizes no class,
including the real zero-loss header and the real process-start record for
`tapectl.exe` / `verify rehearsal.img`. This is unsupported native export shape,
not evidence that the process/header never existed.

**WIN-A6-002 — necessary event payloads were not decoded.** `tracerpt` explicitly
warns about schema mismatch and suggests a less-restricted export. The actual
XML contains `ProcessingErrorData/ErrorCode=15005` and raw `EventPayload`, with
no decoded `EventData` fields, for:

| Event class/opcode | Whole-capture count | Schema-error count |
|---|---:|---:|
| FileIo Read67 | 41,684 | 41,684 |
| FileIo Write68 | 8,769 | 8,769 |
| Thread Start1 | 399 | 399 |
| Thread End2 | 1,186 | 1,186 |
| Thread DCStart3 | 6,377 | 6,377 |
| Thread DCEnd4 | 5,610 | 5,610 |

FileIo OpEnd76 does have decoded `IrpPtr`, `NtStatus`, `ExtraInfo` records
(132,859 globally), but its corresponding requests/lifetimes cannot be bound
from those undecoded fields. Merely changing the GUID selector cannot establish
read offsets, lengths, objects, request/completion identity, logical issuer or
no-target-write coverage. `System/Execution/ProcessID` is not a replacement for
the issued thread/request lifetime method. Some target-image Create records
are emitted in system-process context; do not attribute them by convenience.
No missing integer/status is filled with zero, and no result is inferred from OK.

## Unchanged checker reproduction

The returned checker reads an entire XML string/DOM; this large actual export
was instead supplied to its **unchanged parser and judge** through a streaming
root iterator. Every Event and child value is preserved, in original order;
only XML delivery is changed. The input SHA was computed while streaming. No
Windows binary executed and no Product parser correction was implemented.
Result: **FAIL**, two failures and two holds, saved in `independent-checker.json`:

- no recognized captured record for PID4596;
- no recognized read covering `[4296015360,4296015872)`;
- helper cannot recognize the EventTrace header;
- helper cannot recognize the process start.

The third/fourth are parser limitations, not contradictory native facts. Helper
target-call counts of zero are **unrecognized observations**, never a proof of
zero native reads/writes. Actual greater-than4GiB returned-byte coverage and
physical A6 are **HELD**. This is no Product verify defect or image corruption
finding; the scoped conditional #176 method PASS remains historical and bounded.

Five exact original Event byte ranges are retained as a 6,959-byte XML excerpt:
indices1/123047/123053/123379/123924 (header, decoded OpEnd, undecoded Read,
target-path Create, undecoded Thread Start). It demonstrates both incompatibilities
without publishing unrelated machine-wide payloads. It is explicitly an excerpt,
not a complete capture or substitute for the original. Default replay checks the
committed audit facts and unchanged-parser rejection on this excerpt; optional
`replay.py --archive ORIGINAL.zip` reproduces the full-capture checker result.

## Next owner / retention / holds

**PM #384 owns routing a Windows native export/parser correction.** Software
should use these exact native shapes, preserve all #176 fail-closed controls,
and demonstrate decoded version-correct request/lifetime/result records and
bounded-memory handling before another user run. Re-export/analysis of retained
ETL may help; `-lr` is an exporter suggestion, not an independently qualified
fix. No new tracer, shipping-binary rebuild/injection, security-policy change,
physical verify or unchanged rehearsal is authorized by this report. Closed
Software428 is not silently reactivated. Software438's Mac-only route remains
separate and unchanged.

Original raw ZIP is >1MiB and is **not committed to the Git tree**. It remains in
the supplied persistent attachment; `original-archive.json` records its hash and
location, and `original-members.json` pins every member. Current GitHub connector
has no release-asset upload operation, so repo release retention/fetch of the full
raw archive is explicitly pending. This report and the exact scoped excerpt are
publishable now; no durable GitHub full-raw replay availability is claimed. Keep
the user's original unchanged, rather than splitting raw payloads into Git files.

Return directly to #146/#384/#386. Keep #146 open for native/physical A6. Accepted
software, final Windows success/A9/README and ten-pull results stay unchanged;
WP14 full package remains held. No fresh user physical action is requested.
