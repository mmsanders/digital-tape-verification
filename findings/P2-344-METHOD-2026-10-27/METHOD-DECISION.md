# Verification344 — native A6 closure-method decision

27 October2026. **Neither assessed route is substantiated by the published retained
facts. Do not issue A6 PASS or repeat the old scan.** The concrete missing evidence
is an independently captured request-lineage AND historical coordinate bridge for
the two upper writes, or qualified complete selected-disk write coverage that makes
their unresolved attribution immaterial. These are alternative sufficient proofs,
not facts supplied by the existing filenames, event proximity or constant delta.

Recommend one finite next scope for PM to consider: **route1 off-card feasibility
only**, with the exact bridge fields and stop below. Do not pursue route2 as an
unbounded provider search. No execution, capture, physical work or human task is
issued here; PM owns any next scope. This design decision completes344, not WP14.

## Authority, fixed inputs and criterion

Michael selected both open issues; [344](https://github.com/mmsanders/digital-tape-verification/issues/344)
updated2026-10-27T20:31:54Z, Started6453222259. Product main/spec context
`6af3daa86328d234ccb97f508d0fea702a5fbd3d`, Verification input
`494f8336f05d7b5ec9d4b8d6bf75151c8d214789`; canonical four and own charter read.
[WP14 A6](https://github.com/mmsanders/Digital-Tape/blob/6af3daa86328d234ccb97f508d0fea702a5fbd3d/docs/PACKAGES/WP-14.md)
requires all commands on large real media beyond4GiB; existing accepted CLI/source/
witness facts carry. This decision concerns the remaining native verify evidence,
not substituting one512byte read for the whole criterion. Read-only/NULL-write and
64bit offsets remain in WP14-CLI-CONTRACT §§4.1/6; Windows-only ADR191 applies.

The [223 ledger](https://github.com/mmsanders/digital-tape-verification/blob/d88040bb12f4c54c165e39d94eeef74771c18fa1/findings/P2-223-METHOD-2026-10-20/README.md)
and RESULT.json are the retained-evidence input. Old checker **FAIL**, supplement
**HELD**, zero exclusions remain. Two native successful complete final512byte reads
above4GiB, verifyOK, zero observed selected-disk writes and no loss carry. Four
post-exit records remain undisposed. Selected lower writes explicitly disk0, target1;
upper/lower request IDs differ. Same-key/size choices are69 and25; observed offset
delta3261169664 is not measured extent translation. No selected pointer pair was
found together by the earlier bounded scan; that is not universal impossibility.
No full trace, private raw data, checker or former control was rerun for344.

## Route1 — explicit native lineage plus historical extent translation

For EACH unresolved upper FileIo write, bind valid FileKey/open FileObject lifetime
and upper IrpPtr to the actual lower DiskIo Irp via a captured, unambiguous native
parent/child chain (or identical request where actually present). Microsoft documents
[SplitIo_Info ParentIrp/ChildIrp](https://learn.microsoft.com/en-us/windows/win32/etw/splitio-info)
for volume-manager splitting. This makes a concrete candidate edge, not a guarantee
that every cache/driver-generated request uses it or that this trace contains it.
Do not substitute FileKey for request identity or infer undocumented edges.
The [SplitIo provider description](https://learn.microsoft.com/en-us/windows/win32/etw/splitio)
specifically discusses mirroring-related splits and an explicit SPLIT_IO enable
flag. Neither page promises arbitrary cached-file lineage on this ordinary stack.

The leaf must carry explicit non-target DiskNumber and compatible byte ranges.
[DiskIo_TypeGroup1](https://learn.microsoft.com/en-us/windows/win32/etw/diskio-typegroup1)
uses physical-disk ByteOffset, whereas [FileIo_ReadWrite](https://learn.microsoft.com/en-us/windows/win32/etw/fileio-readwrite)
uses file Offset and a requested IoSize. Equality requires independently established
coordinate translation, not matching numbers. For a positively identified simple,
non-sparse/non-compressed file on a single basic volume, sufficient historical facts
include that open file's extent run, cluster/sector sizes, cluster-heap base and
volume-to-disk extent, valid throughout the operation (including no relocation).

[Retrieval pointers](https://learn.microsoft.com/en-us/windows/win32/api/winioctl/ni-winioctl-fsctl_get_retrieval_pointers)
and [VCN/LCN runs](https://learn.microsoft.com/en-us/windows/win32/api/winioctl/ns-winioctl-retrieval_pointers_buffer)
describe file allocation; [retrieval base](https://learn.microsoft.com/en-us/windows/win32/api/winioctl/ni-winioctl-fsctl_get_retrieval_pointer_base)
is a volume-relative SECTOR offset. [Volume extents](https://learn.microsoft.com/en-us/windows/win32/api/winioctl/ni-winioctl-ioctl_volume_get_volume_disk_extents)
and [DISK_EXTENT](https://learn.microsoft.com/en-us/windows/win32/api/winioctl/ns-winioctl-disk_extent)
identify physical disk and its byte extent. A current query cannot prove an old mapping.
These documented APIs identify needed facts; **no query is authorized or executed**.

Paper rule for that restricted simple mapping: for file offset f in a measured run
beginning VCN v / LCN l, with cluster bytes c, sector bytes s, heap-base sectors b,
and volume disk-start byte a, physical offset is a+b*s+l*c+(f-v*c). Require the
ENTIRE returned/request interval inside measured extents; split across runs when
necessary. Example using invented paper facts a=1048576,b=0,c=4096,v=0,l=100,
f=16384 gives1474560, not16384. This is arithmetic illustration, not old-card evidence.
Unknown base, sparse LCN=-1, layered/spanned mapping or relocation stops this rule;
do not extrapolate it to an unsupported storage layout.

Why sufficient IF all facts exist: explicit lineage proves the lower operation is
the upper request's descendant; measured coordinates and complete range accounting
prevent a same-size bystander match; explicit different disk proves exclusion under
[§2.5](https://github.com/mmsanders/Digital-Tape/blob/6af3daa86328d234ccb97f508d0fea702a5fbd3d/docs/WP14-NATIVE-CAPTURE.md).
All descendants/reuse/lifetimes/conflicts must be accounted, not one convenient leaf.
Remaining post-exit disk records require their own direct disk evidence; never assign
them back to dead threads. Existing native read results remain a separate obligation.

**Availability:** no such bridge is established in223. Historical file/volume/base/
mapping-stability facts were not established by that evidence ledger. A transitive
SplitIo chain is NOT certified absent by the bounded pair scan, but no positive
chain is published either. Neither an invented decoder nor another full scan is a
licensed solution. Minimum old-evidence rescue would be authenticated contemporaneous
bridge/extent records already retained and identified by a concrete provenance pointer;
none is provided. Present-day mapping and new off-card success cannot repair history.

## Route2 — independent complete selected-disk operation coverage

Alternative sufficient argument: a qualified native observer proves EVERY write
or flush reaching the selected physical disk during the entire relevant window,
irrespective of process/file/stream, and proves none occurred. Together with native
successful final-sector reads and process/binary binding, this could remove reliance
on an ambiguous upper-to-lower write pairing. Stronger device coverage cannot excuse
a write to another stream on that SAME disk. It cannot restore post-exit PID attribution.

This coverage is NOT established merely by zero DiskIo writes and no event loss.
Microsoft says [DiskIo events are emitted at completion](https://learn.microsoft.com/en-us/windows/win32/etw/diskio);
[ReadInit/WriteInit/FlushInit](https://learn.microsoft.com/en-us/windows/win32/etw/diskio-typegroup2)
identify Irp/issuing thread but do not themselves carry a DiskNumber. An incomplete
or unmatched initiation remains unknown, not other-disk. Retained loss=0 means no
reported lost enabled events, not that a provider covers every relevant I/O path.
No independent coverage/control argument exists in the published ledger for this
stronger claim. App logs, read-only intent, polling and verifyOK are insufficient.

**Feasibility/stop:** a future method would first need independently detecting
off-card controls for every claimed path, failed/short/pending completions, filters,
same-disk other streams and post-exit delayed I/O, plus a finite coverage domain.
If coverage cannot be bounded/documented, STOP; do not add providers/drivers or
declare a generic no-write proof. That is materially broader than route1 and is
not the recommended next scope. No installed/qualified observer for it is asserted.

## Finite next decision and shortest possible new evidence

PM may separately issue ONE route1 feasibility control on an owned ordinary file,
with an already permitted native ETW recorder, declared OS/version/schema and
prepublished controls from FIELD-CONTROL-TABLE.md. Goal: does the intended stack
actually emit valid lineage edges AND independently measured matching coordinates?
Its declared profile must cover the explicit SplitIo class rather than assume the
old FileIO/DiskIO recipe did. If the intended non-mirrored stack emits no required
edge, that is the finite route1 failure, not permission to add providers or drivers.
One documented method, one bounded result; missing edges, unknown mapping, loss,
nonunique match or unavailable permission ends it. No provider-switch/install/
privilege workaround, VHD, sparse allocation or card involvement. The historical
WPR recipe required an administrator; this non-admin design activation grants no
such access, and future feasibility must expressly resolve recorder/operator consent.

Only after a successful independent off-card method disposition could PM decide on
new real-card evidence. If historical bridges truly cannot be supplied, the shortest
candidate collection is ONE unchanged independently pinned CLI read-only verify
on an already provisioned identified card, capture beginning before process start
and ending after pending I/O/teardown settles, with contemporaneous identity and
coordinate facts. No provision/load/dump/pull/format/write campaign, card changes,
new binary or repeated successful witnesses. It still needs explicit future scope,
qualified recorder/permission, safe operator method and independent preflight;
no command or human request is issued here. Any target write/loss/unknown linkage
stops without an alternate retry. A new result would be new evidence, never a rewrite
of the old FAIL/HELD. Off-card success alone does not qualify a physical card.

Actual344 work: published-ledger/document research and paper reasoning only.
Primary Microsoft sources accessed27October2026. Paper controls are proposed,
unexecuted; no framework/checker/oracle or Product code changes. No native absence
claim, A6/rung advance or reinterpretation of accepted criteria. WP14 remains3/4;
original physical/native/own-HOST/S3/fullAPP/G2 holds and STOPs remain.
