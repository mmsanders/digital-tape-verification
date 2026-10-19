# Verification208 — correction-round2 return, 19 October 2026

Exact Software head `0918e7d02030868f4f8f21059c6a190cbe7a0f62`, PR469,
paired Software465. **Overall S2 PASS withheld.** The submitted denied/incomplete
listing corrections pass their bounded controls; a whole-device ENOENT exception
still treats missing stack metadata as known no-slaves. S3 remains unstarted,
with device-binding and boundary-query policy held on PM472. No Product merge.

Product main `7c6df21f62bd59fbc63226e35804dcac8ed05d2d`; issued input
`5d2e37dd4b08883e1b12ae33be72db4f83d860f4`. Four canonical onboarding docs,
live208/465/210/467 and PM472 read.208 updated2026-10-19T15:16:24Z.
No competing active208 claim. Previous PR215/main46c66e04 receipts carry.
Only one host source and the two workflow control additions differ from38ca666;
no engine, policy, imported tests or other-platform implementation changes.

## Returned evidence

Run39279708753 at the exact head succeeded on Linux, macOS and Windows Server.
INPUTS.json authenticates all three original ZIPs by exact bytes and SHA256.
replay.py checks only the new raw producer-control records, not the unchanged39-row
campaign/audio or the previous five-archive S3 investigation.

Linux native dm-mounted no-fault control still records loop0 n_mounted1 and its
p1 mounted1, while the original ef2712c producer in the same fixture reports0.
The new denied and partial-readdir compiled controls each report all10 disks
unprobed, with n_mounted−1; loop0 p1 mounted is−1. The denied control also makes
OS-use unknown. In the plain fixture the readdir fault is non-triggering because
there is no non-empty stack listing; this is a valid no-change neighbour, not a
second triggered fault. These are test-build provider controls on a hosted
fixture, not physical-reader failure observations. New test-binary SHA256s:

| Platform | SHA256 |
|---|---|
| Linux |51a08f64941a3f7fcaef23f242fc92f7f75c93f56cc1cf482985ea682ff06e01|
| macOS |76f212317373c0f097c62d66e656ea044b1a8fb4d15b6315155b4fd4f48b0266|
| Windows Server |97255be0a8f2c4df94766d34262c65f7f78c0e24b413312feb06d63bfc67d118|

Other-platform implementation/accepted evidence carries unchanged. The Mac protocol
provider row remains NON-CAUSAL. Software corrected the earlier Linux probe narrative
without a new run: O_RDWR upgrade succeeded; final-close auto-clear was not proved.
Full Product CI was107 success,9 in progress,2 queued at review checkpoint; none
failed. Green cards jobs do not complete that pending required-CI condition.

## Remaining concrete correction — final round3

resolve_use now correctly rejects EACCES/EIO opening slaves and errno failures
before or after the first readdir entry. But it exempts every opendir ENOENT without
positively establishing that the node is a partition/non-stacked leaf. It then
falls through parent_disk: a class-visible, whole dm node whose slaves metadata
lookup returns ENOENT can be recorded as its own disk, leaving g_mnt_unknown0.
Missing metadata is not a successfully empty listing and cannot establish where
an unresolved mounted stack is backed. Earlier access(F_OK) is not a successful
slaves query. This is the existing unknown-mount-facts requirement, not a new
native race guarantee or an S3 retained-device rule.

`reproduce.py` compiles the exact four covered functions with harmless OS-query
fixtures and real errno-style results, with Product DISC_FAULT disabled. No real
/sys, device, kernel race or engine execution is claimed. SOURCE-RESULT.json pins
source SHA256da371434f4ee2d49410c75f19dca242a5af1a354a6f4a98bc84638c98cd6995e
and generated fixture SHA2560507f5ac7e4f3334e13d45745a64062e8a43c579a09327ac7015fc14601aab5a.

| Fixture | mount_unknown | Recorded ownership | Disposition |
|---|---:|---|---|
| Complete dm slaves→loop0p1 |0|loop0|PASS neighbour|
| dm slaves EACCES |1|none|PASS correction|
| dm slaves EIO |1|none|PASS correction|
| readdir EIO before any entry |1|none|PASS correction|
| readdir EIO after one entry |1|loop0 (partial)|PASS unknown propagation|
| Whole dm node, slaves ENOENT |0|dm-0|Correction required|
| Successfully empty whole-node listing |0|dm-0|Valid complete-listing neighbour|
| Positively identified partition, slaves ENOENT |0|loop0|Valid partition neighbour|

Return one consolidated narrow correction establishing an allowed leaf positively
or propagating unknown on missing whole-stack metadata. Preserve successful empty
listings and real partition attribution. Return causal missing-whole-metadata,
known-partition and known-good/listing-error neighbours; carry current successful
native and other-platform controls. No new broad campaigns, production seam or
physical/human work. That is correction return3 of at most3. If still unresolved,
stop this correction slice and route the precise blocker to PM without PASS;
also stop after two successive same unresolved findings without new evidence.

## Reproduce and durable transport

From Verification root, with a checkout of exact0918e7d at candidate:

```sh
python3 -B findings/P2-208-R3-2026-10-19/replay.py --artifacts /tmp/208-r3 --out /tmp/208-r3/REPLAY.json --release https://github.com/mmsanders/digital-tape-verification/releases/download/evidence-208-r3-2026-10-19-0918e7d
python3 -B findings/P2-208-R3-2026-10-19/reproduce.py --product candidate --out /tmp/208-r3/source
cmp /tmp/208-r3/REPLAY.json findings/P2-208-R3-2026-10-19/REPLAY.json
cmp /tmp/208-r3/source/RESULT.json findings/P2-208-R3-2026-10-19/SOURCE-RESULT.json
```

Normal existing CI authenticates original ZIPs, reproduces exact-source fixtures
and retains originals/results/generated C in the hash-pinned evidence release.
No accepted package byte changes.208 stays OPEN for the last bounded correction;
210's separate fixed next plan is published by PR216, with actual extension pending.
Ready206/Michael447/A6, closed209, PM472 and all native/physical/security/base/
engine/format/port/atomicity/media/target-timing holds remain unchanged.
