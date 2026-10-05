# P2-R1 / Verification #146 — contract preflight and paper review

Input Product main / #383 merge: `437283291c944d24a3d574dee0e3f44ba97e1896`.
Input Verification main: `6ace9bfc135f3b9b44eabd978ccf925870bc5d48`.
Issue updated `2026-10-05T20:36:07Z`. Single Verification context, no subworkers.
No WP-14 implementation was read. Michael explicitly restricted work to this repo;
this report is the delivery for Product #384, linked from Verification #146.

## E-1: recommend approval, with a narrower compatibility claim

**Confirmed:** FAT32 cannot conform at 16 MiB with 512-byte sectors: even before
metadata there are only 32,768 sectors, below the 65,525 data-cluster threshold.
A mislabeled FAT32 volume is not a conforming FAT16 volume either. PM's universal
statement that every OS reads it as FAT16 is stronger than needed; some reject it.

**Confirmed feasible:** 16 MiB FAT16, 2 KiB clusters, partition type 0x0E.
For example, one reserved sector, two 32-sector FATs and 512 root entries
(32 sectors) give floor((32768−1−64−32)/4) = **8167 data clusters**.
Each FAT needs (8167+2)×2 = 16,338 bytes, fitting its 16,384 bytes. This sits
comfortably inside FAT16's cluster interval. BPB bytes/sector=512, sectors/cluster=4,
hidden sectors=2048 and total sectors=32768 are mutually consistent.

The partition view remains at LBA 34816. All engine-visible metadata, offsets,
CRC rules and APIs stay unchanged. Firmware never reads partition 1. This changes
frozen §3 text and the host-owned partition-type byte, so Michael's approval is
still required; Verification does not issue the erratum.

Paper evidence supports FAT16 compatibility; it does **not** witness this produced
partition on Windows 10 or current macOS. The real-card A1 run must do that.
Apple documents FAT16 support; Microsoft's Windows 10 driver-test documentation
explicitly includes FAT16 volumes. Raw MBR type 0x0E is the contract's proposed
LBA FAT16 identifier; OS recognition of the actual produced card remains witnessed.

Sources (accessed 5 Oct 2026; no implementation expectations derived from them):

- [Microsoft FAT Specification, §3.5, pp. 14–15](https://www.scs.stanford.edu/~zyedidia/docs/_other/fat.pdf), Microsoft-authored specification hosted by Stanford.
- [Microsoft Installable File System Filter Test](https://learn.microsoft.com/en-us/windows-hardware/test/hlk/testref/14b230f3-7eee-437e-ab2f-375b200de6f3), Windows 10 test applicability and FAT16 volumes.
- [Apple File System Programming Guide, supported formats](https://developer.apple.com/library/archive/documentation/FileManagement/Conceptual/FileSystemProgrammingGuide/FileSystemDetails/FileSystemDetails.html), FAT16/FAT32 support.

## R3 contract findings

### P2V-001 — blocking: damaged-layout findings unreachable

§2 recognition requires signature, the exact first two partition entries and zero
last entries. `verify` §4.1 requires findings for wrong types, other layout
mismatches and a partition extending past actual capacity. These are precisely
conditions excluded by recognition. A regular file is then classified as bare
TAPEFS; a device is refused as `NOT_PROVISIONED`, exit 2. Neither reaches the
required exit-1 finding. Truncating one sector also changes the required entry-2
sector count and therefore fails recognition.

Reproduction: `python3 tests/wp14_r1/selftest.py` independently constructs an exact
MBR, flips each type, status/CHS/start, unused-entry and signature byte, and shortens
the actual capacity one sector. Each validation defect fails exact recognition.
These are contradiction witnesses, **not accepted expected CLI results**.

Recommendation for PM: a separate recognizer for a *candidate* whole-card layout
on `verify`, followed by exact validation; keep mutation/provision recognition
strict. Explicitly state damaged-device `verify` precedence versus
`NOT_PROVISIONED`, and what malformed images route to the MBR validator without
misclassifying bare TAPEFS. Verification must not choose this product behavior.

### P2V-002 — blocking for loop runs: loop paths excluded

§2 accepts only `/dev/sdX` and `/dev/mmcblkN` on Linux and refuses anything else;
the assignment expressly requires Linux loop devices. `/dev/loopN` is consequently
`REFUSE_NOT_WHOLE_DEVICE` even with removable/SD facts. Recommendation: PM defines
a TAPECTL_TEST-only loop route, its identity binding and facts-file interface.
The shipped binary must retain production naming restrictions.

Local access also has no loop device: `losetup -f` returned
`cannot find an unused loop device: No such file or directory`.
No device was created or written. Linux CI must supply this environment.

### P2V-003 — clarify before timestamp/tail assertions

FAT timestamps are said to come from any u32 epoch, but FAT's year range begins
at 1980, its time resolution is 2 s, and UTC/local interpretation is not specified.
Epoch 1 (used by WP-11) has no representable FAT date. A conforming build needs a
declared rejection/clamp rule, rounding and timezone policy. The unaffected runner
uses representable epoch 315532800; it does not invent the other cases.

The issue invokes a "WP-11 tail rule" that the issued WP-11 contract does not
state. Exact render emits the final frame at 1×; WAV output is canonical. The
runner compares exact bytes/length and allows no invented padding or last-frame
loss. PM should cite the intended rule before a different tolerance is accepted.

### P2V-004 — clarify interrupted provision outcome at final identity

§3 says an interrupted provision leaves a card treated as not provisioned.
After the MBR write, before its flush, §8.1 permits that MBR to have persisted.
The preceding successful barriers already made both partitions durable, so this
is a completed cartridge. An interrupt before the initial MBR invalidation may
also leave the old card intact. Specify old identity before invalidation,
unprovisioned after durable invalidation/before new identity, and completed new
identity if the final MBR landed. Do not make a correct write-through port fail.

### A3/A4/A5 binding dependency, not an invented API

The contract allows a facts seam but specifies no symbol, input schema or invocation.
NULL binding is not established by a file hash alone, nor is durable OS flush
established by successfully reading cached bytes. `oracle.py` provides an independent
normalized trace checker; a Software-owned mechanical adapter must supply observed
probe/policy/write-open/write/OS-flush/binding facts and authenticate its capture.
A synthetic trace is only an oracle self-test. Real no-op-flush and non-NULL-port
negative controls must still be run on the bound candidate on all configurations.

## Preflight geometry and settled regressions

DRAFT-10 bytes are copied exactly under `tests/wp14_r1/spec/` with manifest hashes.
C-60 needs 1212 chunks and minimum **1,243,137 partition-2 blocks**, including its
mirror. Whole-card minimum is 1,277,953 sectors; a one-block-short image must
fail geometry before truncating/writing an existing file. A full 64 GB image is
valid, with its mirror beyond 4 GiB; no enormous audio timeline is needed to reach
that mirror. Size ceiling equality (128 GiB) passes; one byte above refuses.

R3 settled-regression checks: geometry uses ceiling and a reserved mirror;
reverse frame zero uses the already-published golden; callbacks retain count and
64-bit byte extents; a real mount/service path is required for candidate round
trips; this package does not impose an exact implementation call count or the
same conforming write trace. Budget 1 belongs to accepted engine suites and is
not a new WP-14 CLI knob. Existing engine suites stay byte-identical and run at A8.

## Q-P2-1(a): existing modes are insufficient

**No.** Flush-required persists none of an unflushed epoch; write-through persists
all acknowledged writes. Even including every write-through prefix cut does not
cover a later block persisted while an earlier block is lost. For two distinct
blocks initially `(a,b)`, writes `(A,B)` admit `(a,B)` under any-subset persistence.
The existing modes/prefixes produce `(a,b)`, `(A,b)` or `(A,B)`, never `(a,B)`.
The executable self-test enumerates all four masks and demonstrates this gap.

A third mode must retain the write-event log since each last successful flush,
with LBA, count, bytes, order and acknowledgement/error status. It must permit
background persistence of any subset before/within the next flush, not only a
prefix or all-or-none state. Split multi-block calls at the 512-byte atomic unit.
On successful flush, persist the whole preceding logical epoch in its final
per-LBA state. On failure/cut, remount only durable bytes; no RAM/cache reuse.

For repeated writes to the same LBA, retain versions, not just a dirty bitmap.
The port must declare any per-LBA ordering guarantee; absent one, conservatively
enumerate possible persistence orders of selected versions, with last landed
version winning before the barrier. A successful barrier restores the final
logical write value. Cross-LBA order is unconstrained. Erroring writes/flushes
have unknown durability; retain their permitted effects too. Torn writes remain
the separate negative-control model for the standing atomic-block assumption.

Exhaustively enumerate small epochs and use recorded deterministic masks/seeds
for large ones, reporting bounds rather than calling sampling exhaustive. Run
all accepted operation/recovery scenarios through their original state oracles,
including two interruptions and repeated-LBA updates, and controls for dropped
barriers/identity-before-data. Event traces with legal different grouping must
not be rejected just for differing from one expected trace.

This is a model-coverage gap, not evidence of an engine defect or a rewrite of
the previous bounded WP-10 dispositions. No batching acceptance follows. PM owns
Q-P2-1(b), and must route qualification of the enlarged state space before relying
on that space for firmware batching.

## Return boundary

Paper reviews and reproducible preflight are complete. Unaffected image runner,
geometry/policy/MBR/FAT/trace oracles and coverage inventory are published as a
**partial package**, with controls and actual self-test evidence. Full Stage 1
publication is blocked by P2V-001/002 and missing observation bindings. No Product
binary, Linux loop, Windows, macOS or physical-card case was executed here.
Stage 2 has not started. Issue #146 remains open per its two-stage instructions;
PM owns contract clarification, Software owns mechanical evidence binding,
Michael owns E-1 and the physical witness. No product/safety hold is removed.
