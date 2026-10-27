# Verification344 — field obligations and causal controls

Design only; all proposed controls UNEXECUTED. These are observations that a future
independently reviewed method must demonstrate, not invented fields added to old data.
The16 old checker controls and21 supplement controls stay unchanged; no new harness.

| Obligation | Actual native fields / binding | Existing authenticated status / missing fact |
|---|---|---|
| Executable and lifetime | Hash-pinned executable + witnessed launch; native Process Start/End image/command/PID and thread lifetimes, with reuse accounted | Prior baseline carries. [Process schema](https://learn.microsoft.com/en-us/windows/win32/etw/process-typegroup1) supplies image/command/process identity, not executable SHA256. Post-exit records never become live-PID I/O. |
| Returned final sector | FileIo Read Offset/IoSize/IrpPtr/FileObject/FileKey/TTID, sole pending request; same valid OpEnd IrpPtr/NtStatus/ExtraInfo | Old two full successful512byte returns above4GiB carry; IoSize alone is requested bytes. [OpEnd](https://learn.microsoft.com/en-us/windows/win32/etw/fileio-opend) supplies actual returned count/status. New collection would need its own exact results. |
| Upper/lower lineage (route1) | Every required SplitIo ParentIrp/ChildIrp edge with provider/version/pointer-width/native record identity, bounded request lifecycles; DiskIo leaf Irp | Old upper pointers differ from lower; no positive chain established. A shared FileKey/name/size is not lineage. SplitIo documents VolMgr splits only, not arbitrary cache-generated causality. |
| Coordinate and disk (route1) | Same live file identity and measured VCN/LCN extent run, cluster size, heap-base sector offset/sector size, contemporaneous volume disk extents, DiskIo DiskNumber/ByteOffset/TransferSize | Two lower writes explicitly disk0 not1; old file/disk delta3261169664 lacks historical translation. No modern extent query repairs that. |
| Operation coverage (route2) | Declared enabled native schema/path domain, initiation-completion accounting, explicit disk identity for every reaching write/flush, pending drain; no observer gaps | Zero observed selected-disk writes/no loss carry, universal write coverage does not. Init alone lacks disk; completion events alone omit unresolved pending operations. |
| No loss | Existing header counters + capture start/stop/decoder success; future raw session [EventsLost/LogBuffersLost/RealTimeBuffersLost](https://learn.microsoft.com/en-us/windows/win32/api/evntrace/ns-evntrace-event_trace_properties) where applicable | Old no-loss carries. Zero loss is necessary, not proof disabled/uncovered event types were observed. Unknown schema/counter/window is non-PASS. |
| Complete disposition | Full immutable original records + independent proof for EACH of the four disputed records; no filtering to convenient process/stream | Old four-record FAIL and supplementHELD/zero exclusions remain. No stream on selected disk can be excused as an unrelated filename. |

| Proposed causal case | Required discrimination / meaningful stop |
|---|---|
| Positive paper model | One valid live upper request, explicit native lineage, known matching extent/range and one distinct-disk leaf; native successful final512byte read and complete no-write accounting. This is a proof model, not actual acceptance. |
| Wrong disk / same-card other stream | Leaf DiskNumber=selected, or other stream located there: FAIL; filename differs cannot rescue it. |
| Mismatched / reused request | Wrong parent/child, missing/zero key, new request before old life resolves, PID/thread reuse: no exclusion; preserve ambiguity until every outstanding request resolves. |
| Ambiguous counterpart | Two same-key/size candidates, overlapping child ranges, extra/unmapped descendant: HELD; no nearest-time selection. Old69/25 candidates remain nonunique. |
| Unknown coordinates | Drop heap base, historical extent, cluster size or disk extent; change one offset/sector unit; sparse/compressed/layered layout not proved: HELD, even when a fitted constant delta exists. |
| Historical drift | Present-day file/volume map differs or lacks lifetime-stability evidence: cannot justify old exclusion. No new query treated as old fact. |
| Short / failed read | ExtraInfo511, unsuccessful NtStatus, missing OpEnd, gap or offset at/below2^32-1: no complete final-sector proof. IoSize512/verifyOK do not rescue it. |
| Lost / uncovered event | Positive loss counter, unknown schema, recorder starts late/stops with pending I/O, missing required initiation/disk mapping: non-PASS. Disabled event classes cannot be certified by zero loss. |
| Post-exit attribution | Move selected Read/Write past Thread/Process End: retain old failure; do not extend lifetime by proximity. Explicit lower other-disk fact may only prove its own disk, not the upper request. |
| Completion-only false absence | Omit the completion of a write initiation: route2 must HOLD; no lower write event is not evidence it never reached selected disk. |
| Off-card versus qualification | Successful owned-file method control proves only that declared schema/matching path. It never supplies real-card identity, geometry or native acceptance for the retained/future card run. |

No proposed control was run; examples provide detecting obligations before any
future implementation. PM must separately issue a concrete feasible method; no
capture/operator/privilege or physical-device instruction is granted by this table.
