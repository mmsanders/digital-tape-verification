# Corrected Mac physical C60 pull method — P2V-006

**READY for the bounded witness on the previously authenticated arm64/macOS26+ machine and positively identified owned card.** This supersedes the original REAL-CARD.md pull setup/reset/order, preserving the original bytes. Read with [Mac assessment](P2-R1-WP14-MAC-2026-10-12.md) and [authenticated release](P2-R1-WP14-RELEASE-2026-10-09.md). Uses unchanged shipping binary/Product5e2df5a; no rebuild, test facts or engine change.

Preserve the existing successful Mac run folder and card first. **Do Windows10 readback of that Mac-created card before erasing it**, using the original Windows read-only verify/dump/README instructions. Fresh Windows3600s provision/load/reinsert is still required; preserve readback before that destructive step. This order change saves the useful existing cartridge and does not replace any criterion. Windows can return independently while pulls remain pending.

## Preconditions and explicit reset

Use the exact reviewed Product checkout root, verified `./tapectl`, canonical C60.wav and `tests/golden/src/quiet.wav`. Mac raw access needs sudo. Known binary hash `e7550d8bedbb0c784fd528c387a87cca2bad8d1b411c39217d25377329bb0beb`; C60 `c7369c6fdcb476fcc7f6a9d68aaab276f68a4d316ffb595faabb736e6046495d`; quiet `d97a9735a2beb3defc09808b8f33a760c88e1b171eddb988082b8e0a5ad7692c`.

Resolve card/reader identity gaps in the assessment. Remove other external disks. Inspect inserted/removed disk enumeration; identify the physical card rather than trusting the previous number. Replace N below only after doing that. **Fresh provision erases the selected card for EVERY trial.** Do not run a reset while a failed/unclassified trial awaits review. No bulk ten-trial script is supplied.

```sh
diskutil list external physical
DISK=/dev/diskN
CARD=/dev/rdiskN
T=01
D=pull-corrected-$T
mkdir "$D"
diskutil list external physical > "$D/disks-before.txt"
diskutil info "$DISK" > "$D/card-before.txt"
uname -m > "$D/arch.txt"
sw_vers > "$D/os.txt"
shasum -a 256 ./tapectl C60.wav tests/golden/src/quiet.wav > "$D/inputs.txt"
sudo -v
```

Do not reuse an existing trial folder or overwrite the original pull-01 evidence. Require expected hashes and card identity first. Close Finder windows. If a foreign mounted volume causes refusal, retain it and unmount only the identified card, then retry that step; never bypass the binary safety policy. The exact raw path repeated by `--erase` is the destructive confirmation.

```sh
sudo /usr/bin/time -p ./tapectl provision "$CARD" --label PULL-C90 --length-s 5400 --erase "$CARD" > "$D/provision.txt" 2> "$D/provision-time.txt"
echo $? > "$D/provision-exit.txt"
```

Inspect provision exit/output before the next command; require exit0 and retain UUID/epoch. The90-minute allocation is1817 chunks; baseline plus full C60 needs1214. **The source remains the same full60-minute C60**, not a90-minute waveform.

```sh
sudo ./tapectl load "$CARD" tests/golden/src/quiet.wav > "$D/baseline-load.txt" 2>&1
echo $? > "$D/baseline-load-exit.txt"
```

Require baseline exit0 before continuing. Capture the established nonempty old state:

```sh
sudo ./tapectl verify "$CARD" > "$D/before-verify.txt" 2>&1
echo $? > "$D/before-verify-exit.txt"
sudo ./tapectl dump "$CARD" --side A -o "$D/before-A.wav" > "$D/before-A.txt" 2>&1
echo $? > "$D/before-A-exit.txt"
sudo ./tapectl dump "$CARD" --side B -o "$D/before-B.wav" > "$D/before-B.txt" 2>&1
echo $? > "$D/before-B-exit.txt"
cmp tests/golden/src/quiet.wav "$D/before-A.wav"
echo $? > "$D/before-A-cmp-exit.txt"
cmp tests/golden/src/quiet.wav "$D/before-B.wav"
echo $? > "$D/before-B-cmp-exit.txt"
shasum -a 256 "$D/before-A.wav" "$D/before-B.wav" > "$D/before-hashes.txt"
wc -c "$D/before-A.wav" "$D/before-B.wav" > "$D/before-sizes.txt"
```

Require verify0/OK, dump0/0 and cmp0/0. Both old WAVs are793844 bytes /198450 frames with the quiet hash. STOP on failure; do not attempt a pull on an unestablished baseline.

## One witnessed interruption

Run this in the foreground from the same repository root:

```sh
sudo -v
date -u +%Y-%m-%dT%H:%M:%SZ > "$D/load-start-utc.txt"
sudo /usr/bin/time -p ./tapectl load "$CARD" C60.wav > "$D/load.txt" 2> "$D/load-time.txt"
echo $? > "$D/load-exit.txt"
```

While the load is **actually still running**, physically remove the card at the chosen elapsed time; record stopwatch elapsed, wall time, visible progress if any and the physical act in `$D/pull-note.txt`. Do not use Ctrl-C or a process kill as the physical pull. Let the command return and capture its exit/error/time. If it completed before removal, the trial is not a mid-load pull; retain that fact and repeat the numbered trial from fresh provision in a new folder.

Use ten distinct actual elapsed times spread across the measured load duration. Based on the observed1619.06s run, a starting schedule is5,30,90,180,360,600,900,1200,1440,1560 seconds. These are scheduling suggestions, not guaranteed device boundaries. Adjust later targets to actual duration and completion; a near-end pull still must occur during active load. Do not invent exact write/flush cuts from a stopwatch. A successful completion on the90-minute label may be substantially quicker or slower than the prior run; no redundant uninterrupted half-hour calibration is required before trying an early pull.

## Reinsert and preserve read-only observations

Physically reinsert; re-identify disk number against the same card. Update DISK/CARD if changed. **Do not load, provision, reset-b, promote or respool before collecting evidence.**

```sh
diskutil list external physical > "$D/disks-after.txt"
diskutil info "$DISK" > "$D/card-after.txt"
sudo ./tapectl verify "$CARD" > "$D/after-verify.txt" 2>&1
echo $? > "$D/after-verify-exit.txt"
sudo ./tapectl dump "$CARD" --side A -o "$D/after-A.wav" > "$D/after-A.txt" 2>&1
echo $? > "$D/after-A-exit.txt"
sudo ./tapectl dump "$CARD" --side B -o "$D/after-B.wav" > "$D/after-B.txt" 2>&1
echo $? > "$D/after-B-exit.txt"
```

Hash and size only the outputs actually produced, including partial outputs from a failed dump; retain each dump's exit/error. Do not replace missing outputs with zeros. For example, when both files exist:

```sh
shasum -a 256 "$D/after-A.wav" "$D/after-B.wav" > "$D/after-hashes.txt"
wc -c "$D/after-A.wav" "$D/after-B.wav" > "$D/after-sizes.txt"
```

Also preserve a small read-only media snapshot for independent WP10 mapping when any finding or mixed/staged outcome appears. Set CARD_BYTES to the exact newly reported disk size, divisible by512; the previous card reported62537072640. These dd commands read the card and write files on the Mac; they do not repair it. The mirror offset must use the newly confirmed size, not an assumed64GB value.

```sh
CARD_BYTES=62537072640
sudo dd if="$CARD" of="$D/p2-metadata.bin" bs=512 skip=34816 count=2048 2> "$D/p2-metadata-dd.txt"
echo $? > "$D/p2-metadata-dd-exit.txt"
sudo dd if="$CARD" of="$D/p2-mirror.bin" bs=512 skip=$((CARD_BYTES / 512 - 1)) count=1 2> "$D/p2-mirror-dd.txt"
echo $? > "$D/p2-mirror-dd-exit.txt"
shasum -a 256 "$D/p2-metadata.bin" "$D/p2-mirror.bin" > "$D/metadata-hashes.txt"
```

Metadata is2048 partition2 sectors (1MiB) plus its mirrored512-byte superblock. These independent dd reads **do not discharge A6's shipped-tapectl native >4GiB capture**.

## Permitted outcomes and reset decision

WP11 load = overwrite B from0 → commit → promote; normative sources are tapefs §§8/8.1/9.1/9.3.4, WP10 and the issued WP11/WP14 contracts. Here old=quiet793844 bytes; new=C60 635040044 bytes. No prefixes, blended audio, extra tail or zero-padding tolerance is introduced.

| Captured state | Interpretation / next step |
|---|---|
| A=exact quiet, B=exact quiet; dump exits0/0, verify0/OK | Permitted old state before B commit (including torn inactive B slot with valid old fallback). Preserve the complete trial evidence; this clean old-state pattern is preclassified by Verification and may reset for the next numbered trial |
| A=exact quiet, B=exact C60 | Permitted post-record/pre-promote or early-promote mixed state. Preserve metadata and return for independent boundary/stage mapping **before reset** |
| A=exact C60, B=exact C60 | Completed or permitted promote intermediate/declined state. Both identical audio alone does not locate the stage. Preserve metadata and actual mid-load proof; return for mapping **before reset** |
| NEEDS_REPAIR / degraded / mount/read error / any other hash or length | No automatic PASS/FAIL from exit code alone. Preserve outputs+metadata and the card unchanged; Verification compares exact recovery predicates before another write. Unclassified corruption stays held |

This table does not waive a mountability or audio invariant; raw media failures require assessment, not a relaxed oracle. Ten manual timings do not exhaust WP10 boundaries or qualify atomicity.

For every accepted/reset-eligible trial, start the NEXT numbered trial from fresh5400s provision plus baseline; never merely reload quiet onto the prior trial's full allocation. Record one row per trial with card/reader/OS/binary identity, UUID/epoch, old/new hashes, actual pull time, load exit, verify findings, A/B exits/sizes/hashes and Verification's outcome mapping. Interrupted provisioning/baseline setup is not one of the ten C60 pulls.

After ten recorded/mapped pulls, prepare a final successful C60 by **fresh provision first** (original3600s label for the standard roundtrip), load once, eject/reinsert and verify/dump exact bytes as the original method requires. Do not attempt quiet→C60 on3600s. Retain original Mac success separately; no need to repeat it solely to prove the already-observed success. Any final load is only for the post-pull final state/platform handoff.

Physical Windows10 fresh provisioning/durable roundtrip, exact card/reader provenance, any absent OS screenshot, physical >4GiB capture and full WP14 acceptance remain pending. This overlay supplies a capacity-feasible method; it makes no physical pull result or media qualification claim.
