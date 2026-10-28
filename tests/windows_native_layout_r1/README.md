# Verification353 — finite native layout matrix and BLOCKED return

PM611 / Software613; manually selected by Michael. Product input
`a993ba79d32ebde232072485fd1c8b83a95690d5`, Verification input
`ed34966c909edb5c9e3aaa4bb753e84f6343152f`; canonical four/charter/live issues
read. App352 Stage A was published first. No new613 implementation was inspected.
Raw decoding is expressly in scope; no new permission/declaration was requested.

**Full route1 kit BLOCKED: required SplitIo32 actual version/export/length is not
qualified in the finite authorized evidence.** The Microsoft SplitIo_Info page
describes ParentIrp/ChildIrp, but supplies no event-version table. Neither the
independently retained real185 five-event XML nor the subsequent51-record compact
excerpt contains a SplitIo record. They cannot prove its actual exported version
or payload length. A synthetic parent/child pair cannot fill that gap. Do not
learn the version on a first workload trial, invent a lineage edge, treat missing
SplitIo as absent I/O, or build a full passing kit from this partial matrix.
Other unqualified tuples below also remain STOP. One consolidated bounded return;
no third speculative interface or provider search. PM decides any future schema-only
observation, which is NOT issued by this publication.

## Immutable finite evidence and what it actually shows

`PROVENANCE.json` pins the exact inputs and records the small inventories.
`native185.xml` is byte-identical to the original independently retained
Verification185 excerpt and Product's copy,6959 bytes,
SHA256 `28a02766f56222e5b699c5d00b79b7319600822f37de46f4d118c38e29636dcb`.
Original Verification path:
`findings/P2-R1-WP14-WIN-REHEARSAL-2026-10-15-evidence/native-excerpt.xml`.
Product path: `tools/wp14-capture/fixtures/verification-185/native-excerpt.xml`.
Original actual build26200, kernel-session XML export: Header v2, FileIo OpEnd v3,
raw Read67 v3 length48, named Create64 v3, raw Thread Start v3 length74.
All five are identity-extracted; this intentionally partial reference decoder
handles four and refuses Create. This does NOT overturn the old checker's accepted
five-record decoding; it simply states the smaller implemented reference surface.

Only the already-public29582-byte `P2-A6-PHYSICAL-2026-10-19/NATIVE-EXCERPT.json`
was inventoried (51 records; SHA256
`f3a3e5624cfe97948bd670a5c5fd11a782f26211b63b726891c0dd416e186bb5`).
It corroborates Thread Start/End v3 length74, Read/Write v3 length48 and named
OpEnd v3. It has named Process Start/End v4 and Defunct v5, FileIo Name v2 and
Create v3, DiskIo Write11 v3. No raw Process/DiskIo/SplitIo/OpEnd payload lengths
are exposed there. The normalized JSON's missing Provider is NOT invented back
into an original XML event. No whole trace, old checker, physical device, OS
query, capture, app or workload was executed. The original949k/1.23m-event
results and their holds are unchanged, not replayed here.

## Closed support matrix

All supported decoder rows require the exact tracerpt Event namespace
`http://schemas.microsoft.com/win/2004/08/events/event`, System Version/Opcode,
an actual trace header PointerSize8, and the class identity rules below. The
reference export shape is the already-qualified26200 retained shape; this is no
promise about unobserved builds, exporters, parent class versions or payload tails.

| Class / GUID suffix | Tuple / export | Evidence classification and disposition |
|---|---|---|
| EventTrace_Header /68fdd900… | opcode0 v2, named | Native185 header. Require BufferSize, PointerSize, EventsLost, BuffersLost, BuffersWritten, LogFileMode, StartTime, EndTime, ProviderVersion as bounded unsigned values; timesu64, othersu32. PointerSize exactly8 from this header. Decode loss counters, never erase them; any full method still must STOP loss/lifecycle. No raw header support. |
| FileIo /90cbdc39… |67/68 v3 x64, raw15005, lengths44/48 only | Canonical §2.3 already qualified this exact layout, independently retained Read48; later compact/raw-key controls corroborate Write48. Fixed44 base and common67/68 semantics carried. Synthetic44 variant tests interpretation only. Decode offsets below; TTID equals header ThreadID. No named ReadWrite or version2 inference from parent FileIo EventVersion. |
| Thread /3d6fa8d1… |1–4 v3 x64, raw15005, lengths72/74 only | Canonical §2.3 plus native185 Start74; later retained Start/End74 corroborate.72 fixed base and3/4 rundown are carried documented shapes, not newly observed runtime rows.74 permits only the witnessed empty UTF16 name0000; no variable-name extension. |
| FileIo OpEnd |76 v3 x64, named exactly IrpPtr/ExtraInfo/NtStatus | Actual185 + later compact and primary semantic support. IrpPtr/ExtraInfo u64 pointers; NtStatusu32; nonzero valid IrpPtr. No raw20/24-byte guess, no fabricated successful result. Decoder returns fields only; sole-pending request/IRP ambiguity/lifetime rules remain in the unchanged judgment. |
| FileIo Create/Name/Cleanup/Close/Flush/other requests | actual named Create64v3 and Name32/35/36v2 are inventoried; other tuples not proved here | Partial oracle deliberately refuses them. They are not ignored or projected into ReadWrite. Primary-document semantics and prior accepted judgment carry, but no raw offsets/lengths are extrapolated. Full method must retain all request/lifetime/ambiguity accounting, including classes69–75/77. |
| Process /3d6fa8d0… | retained named Start1/End2v4, Defunct39v5; no raw length | Observed field sets in PROVENANCE, primary semantic expectations only for full lifetime contract; not added to this partial decoder. No substitution of header PID for payload ProcessId, no first-observed version pin. Missing/unqualified required lifecycle is STOP. |
| DiskIo /3d6fa8d4… | retained named Write11v3; no raw length; Init12/13/15 and Flush14 absent from finite excerpts | Primary describes TypeGroup1 Read/Write fields/units; recorded Write set is inventoried. No raw Process-style or FileIo-style extrapolation. Required unqualified Init/Flush tuple/export is STOP; no header issuer fallback, nearest-time or fitted offset join. |
| SplitIo /d837ca92… |32 VolMgr, actual version/export/length absent | **Required missing layout — BLOCKED.** Primary-only ParentIrp/ChildIrp semantics cannot qualify an observed version or binary length. No invented links or runtime learning. |
| Anything else | unknown class/opcode/version/pointer/export/length | STOP_LAYOUT_UNSUPPORTED regardless of apparent issuer, never silently drop a potentially relevant record. |

## Exact raw offsets and units

Little endian; offsets in bytes. PointerSize comes from the recorded header, not
OS x64, process bitness, or the MOF's nominal uint32 spelling for Pointer fields.
FileIo v3: Offset@0 u64 (file-relative bytes), IrpPtr@8 u64, FileObject@16 u64,
FileKey@24 u64, TTID@32 u32, IoSize@36 u32 (requested bytes), IoFlags@40 u32.
44-byte base; optional witnessed4-byte tail@44 is reported uninterpreted, never
read as another field. Any other length STOP. FileKey is stream identity, not
interchangeable with a live FileObject. Offset/IoSize are requested range, not
native returned bytes; OpEnd result joining still applies.

Thread v3: ProcessId@0u32, TThreadId@4u32; StackBase@8, StackLimit@16,
UserStackBase@24, UserStackLimit@32, Affinity@40, Win32StartAddr@48,
TebBase@56 (all u64); SubProcessTag@64u32; BasePriority@68, PagePriority@69,
IoPriority@70, ThreadFlags@71 (u8).72-byte base;74 only if bytes72:74=0000.
The Thread payload describes the SUBJECT thread. In actual185 the header
ThreadID=27364 while payload TThreadId=25552: this is legitimate creator/current
context. Do NOT transplant FileIo's TTID/header crosscheck onto Thread lifecycle
records. Conversely, FileIo's required TTID/header mismatch always STOPs.

## Class, number and export guards

Kernel-session Provider9e814aad… is NOT a class identity conflict with the
authoritative ExtendedTracingInfo/EventGuid. A Provider naming another known
class than EventGuid IS a conflict. A required kernel-session EventGuid missing
or duplicated/malformed is STOP. A standalone known class Provider may name itself;
this is a synthetic consistency control, not a newly qualified original export.
No added provider/control API or provider hunt. Unsupported namespaces, duplicate
fields, mixed raw/named exports, unknown processing-error code, malformed/odd hex,
missing/truncated/unrecognized tail, numeric sign/fraction/overflow or invalid
identity are STOP. No zero filling, header PID lifetime fallback or ignoring an
unknown required record just because it looks unrelated.

The pure reference oracle checks interpretation, not raw authenticity or absence.
Its header-context argument must come from the authenticated matching header;
passing an invented Python dict is not trace provenance. It has no A6 PASS verdict,
OS access, API bridge, profile launcher or workload implementation.

## Primary references checked during authoring

* [FileIo_ReadWrite](https://learn.microsoft.com/en-us/windows/win32/etw/fileio-readwrite): read/write field semantics. Its generic MOF ordering includes TTID before FileObject and must NOT be silently treated as the independently qualified v3 raw order. Exact v3 order/length authority here is the existing canonical §2.3 plus pinned actual bytes, not a parent EventVersion assumption.
* [Thread_TypeGroup1](https://learn.microsoft.com/en-us/windows/win32/etw/thread-typegroup1): subject process/thread, fixed fields, pointer qualifiers, start/end/rundown semantics.
* [FileIo_OpEnd](https://learn.microsoft.com/en-us/windows/win32/etw/fileio-opend): completion identity, ExtraInfo and NtStatus semantics; no raw version extrapolation.
* [EventTrace_Header](https://learn.microsoft.com/en-us/windows/win32/etw/eventtrace-header): recorded pointer width/loss/timing fields.
* [Process_TypeGroup1](https://learn.microsoft.com/en-us/windows/win32/etw/process-typegroup1) and [DiskIo_TypeGroup1](https://learn.microsoft.com/en-us/windows/win32/etw/diskio-typegroup1): lifecycle and disk-coordinate/byte-count/issuer semantics. They do not convert the retained named projections into qualified raw layouts for all versions.
* [SplitIo_Info](https://learn.microsoft.com/en-us/windows/win32/etw/splitio-info): parent/child IRPs and opcode32; no actual captured version/length supplied by this documentation or the finite retained inputs.

## Return boundary

Run `python -B tests/windows_native_layout_r1/controls.py` for new independent
small-shape controls only. Actual185 bytes are hash-checked, new synthetic variants
are labelled; neither is a fresh Windows observation.350's5positive/47negative
models and original16/21 controls carry unchanged and are not rerun for a base
move. Existing a6check.py/oracle/old results remain unchanged.

Full Software613 kit implementation is NOT cleared. Deliver this useful bounded
matrix/reference oracle; return the named layout blocker directly to613/PM611 and
close353 as the issued bounded BLOCKED disposition. No new full kit, correction
loop, human task, capture or schema-only trial is authorized. Settled C1 ordinary
versus admin-recorder separation, C3 preallocate before baseline, C5 alignment/
access0 rights and C2 fail-closed layout constraints carry. Equal extents do not
prove absence of layering.7/12, originals/STOPs and native/session/A6/INGEST/
fullAPP/G2 holds remain. No source/native integration clearance is implied.
