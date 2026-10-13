# Windows PowerShell physical C60 pulls — Michael #386

**READY on Michael's observed Windows11 machine, at his explicit13October request.** This replaces the Mac-specific execution instructions for the ten physical pulls; no duplicate ten-pull Mac campaign is requested. Windows10 platform acceptance remains a separate issued requirement pending PM disposition. This method works with Windows PowerShell5.1 or PowerShell7; it does not change Product/engine/binary/flushes or the WP10 outcome criteria. Use the same hash-verified shipping release and one positively identified owned PNY card.

Fresh5400-second allocation before **each** trial → quiet baseline → full C60 load → physical pull → read-only evidence. The earlier corrected capacity proof/image preflight remains applicable:1817 chunks hold2 baseline+1212 C60, with adopt-in-place promotion and lawful phase2 decline. The INPUT remains the full60-minute C60. Original immutable package/release bytes and successful3600s Mac/Windows records remain intact.

## 1. Prepare the folder and helpers once

Open **Administrator PowerShell**, use your existing `C:\Users\mrtro\claude\tapetest` folder (or the actual folder with the tested executable/C60). Close Explorer/Notepad windows on the card. Keep all evidence on the computer, not the card. Do not change system execution policy. Open [the helper definitions](P2-R1-WP14-WINDOWS-PULL-helpers.ps1), copy their whole contents, and paste them into this PowerShell session. They only define four functions; no device command runs until you explicitly invoke it.

```powershell
Set-Location C:\Users\mrtro\claude\tapetest
$Root = (Get-Location).Path
$Exe = (Resolve-Path .\tapectl.exe).Path
$C60 = (Resolve-Path .\C60.wav).Path
$ExpectedExe = '82798af2899e9364b9c9bfaa2021daf6cc51ccd0c6562598d50e0a86944bb7a9'
$ExpectedC60 = 'c7369c6fdcb476fcc7f6a9d68aaab276f68a4d316ffb595faabb736e6046495d'
$ExpectedQuiet = 'd97a9735a2beb3defc09808b8f33a760c88e1b171eddb988082b8e0a5ad7692c'
if ((Get-FileHash $Exe -Algorithm SHA256).Hash -ne $ExpectedExe) { throw 'Wrong executable; stop.' }
Assert-Wav -Path $C60 -Bytes 635040044 -Hash $ExpectedC60
```

If quiet.wav is not already in this folder, get the unchanged baseline at the exact reviewed Product source commit. No build/golden regeneration is needed:

```powershell
Invoke-WebRequest -UseBasicParsing -Uri 'https://raw.githubusercontent.com/mmsanders/Digital-Tape/5e2df5aaf23e9ed0e230c444a40650da9459ddb2/tests/golden/src/quiet.wav' -OutFile (Join-Path $Root 'quiet.wav')
$Quiet = (Resolve-Path .\quiet.wav).Path
Assert-Wav -Path $Quiet -Bytes 793844 -Hash $ExpectedQuiet
```

If you already have quiet.wav, skip only the download, set `$Quiet` and run its assertion. No truncated/silent substitute baseline. `Invoke-Tape` captures command/output/exit/start/end and stops its stopwatch **automatically as the native command returns**; no manually stopped timer. PowerShell's NativeCommandError wrapper around a flush-count stderr diagnostic is retained; the actual executable exit code decides command success.

## 2. Identify and erase only the selected card — repeat EVERY trial

First preserve existing successful run files/screenshots. Your Mac-created-card Windows readback is already reported; no need to recreate it for this procedure. Remove other external drives. Use insertion/removal, capacity/model and the physical card/reader photos to identify the disk. Do not use a drive letter as the raw target. Number can change on every reinsertion.

```powershell
Get-Disk | Format-List Number,FriendlyName,SerialNumber,Size,BusType,IsBoot,IsSystem
$DiskNumber = -1  # REPLACE -1 only after identifying your owned test card
$disk = Get-Disk -Number $DiskNumber -ErrorAction Stop
if ($disk.IsBoot -or $disk.IsSystem -or $disk.Size -gt 137438953472) { throw 'Unsafe disk selection; stop.' }
$Card = '\\.\PhysicalDrive' + $DiskNumber
$T = '01'  # next numbered trial, 01 through 10
$D = Join-Path $Root ('pull-win-' + $T)
if (Test-Path $D) { throw 'Existing trial folder; preserve it and use a new attempt folder.' }
New-Item -ItemType Directory -Path $D | Out-Null
Get-Disk | Format-List Number,FriendlyName,SerialNumber,Size,BusType,IsBoot,IsSystem | Out-File (Join-Path $D 'disks-before.txt')
$disk | Format-List * | Out-File (Join-Path $D 'card-before.txt')
Get-CimInstance Win32_OperatingSystem | Select-Object Caption,Version,BuildNumber,OSArchitecture | ConvertTo-Json | Set-Content (Join-Path $D 'os.json')
Save-WavRecords -Paths @($Exe,$C60,$Quiet) -Output (Join-Path $D 'inputs.json')
$confirmation = Read-Host ('Provision ERASES this card. Type exactly ' + $Card + ' to confirm')
if ($confirmation -cne $Card) { throw 'No matching destructive confirmation; stop.' }
```

Recheck the selection, then provision. The repeated raw path is also the binary's exact `--erase` confirmation. All tapectl safety refusals remain active. If a foreign mounted volume causes refusal, save it and unmount only the identified card with Windows disk tools before retrying that step. Never disable the guard, enable test facts or substitute a test binary.

```powershell
$code = Invoke-Tape -TapeArgs @('provision',$Card,'--label','PULL-C90','--length-s','5400','--erase',$Card) -Stem (Join-Path $D 'provision')
if ($code -ne 0) { throw 'Provision failed; inspect saved files before continuing.' }
$code = Invoke-Tape -TapeArgs @('load',$Card,$Quiet) -Stem (Join-Path $D 'baseline-load')
if ($code -ne 0) { throw 'Baseline failed; stop before a pull.' }
$code = Invoke-Tape -TapeArgs @('verify',$Card) -Stem (Join-Path $D 'before-verify')
if ($code -ne 0) { throw 'Baseline verification failed; preserve card.' }
$code = Invoke-Tape -TapeArgs @('dump',$Card,'--side','A','-o',(Join-Path $D 'before-A.wav')) -Stem (Join-Path $D 'before-A')
if ($code -ne 0) { throw 'Baseline A dump failed.' }
$code = Invoke-Tape -TapeArgs @('dump',$Card,'--side','B','-o',(Join-Path $D 'before-B.wav')) -Stem (Join-Path $D 'before-B')
if ($code -ne 0) { throw 'Baseline B dump failed.' }
Assert-Wav -Path (Join-Path $D 'before-A.wav') -Bytes 793844 -Hash $ExpectedQuiet
Assert-Wav -Path (Join-Path $D 'before-B.wav') -Bytes 793844 -Hash $ExpectedQuiet
Save-WavRecords -Paths @((Join-Path $D 'before-A.wav'),(Join-Path $D 'before-B.wav')) -Output (Join-Path $D 'before-wavs.json')
```

Require before-verify output `OK`; retain printed UUID/epoch in provision output. A baseline/setup failure is not one of the ten C60 pulls.

## 3. Start a full C60 load, then physically remove the card

Run this block together, not line-by-line with a manual timer pause. Keep the PowerShell window open:

```powershell
$code = Invoke-Tape -TapeArgs @('load',$Card,$C60) -Stem (Join-Path $D 'load')
Write-Host ('Load returned exit ' + $code + '; evidence and timing saved.')
```

While it is **still loading**, physically remove the SD card from the reader at your chosen stopwatch time. Use the same physical removal action each trial, record it explicitly, and leave the reader connected when possible. Do not use Ctrl-C, Safely Remove, Stop-Process or a process kill as the fault. Let the command finish reporting the missing-card failure; its exit and timing are saved automatically. Record actual pull elapsed/wall time and any visible progress in `$D\pull-note.txt`, including that the load had not returned when you removed it. The displayed Started timestamp supports this record; use a separate stopwatch for the physical act.

Ten distinct elapsed times spread across an observed load duration are required. The existing Windows timing2352.2852023s was manually stopped late and **is not an exact load duration**; do not use it as a precise schedule or assert the Windows run equalled Mac time. Start with an early pull, e.g.5s, then use the prior approximate duration and observations to choose progressively later distinct points. A starting plan based on Mac1619s is5,30,90,180,360,600,900,1200,1440,1560s; adjust to this machine's actual active load. If completion precedes the chosen pull, preserve the completion, do not count it, and repeat that numbered trial from fresh provision in a new folder. Ten early pulls at the same point do not satisfy spread. No extra full uninterrupted load just for timing is required.

## 4. Reinsert, re-identify and collect read-only results

Physically reinsert. Confirm the same card, then update DiskNumber/Card if changed. **No load/provision/reset-b/promote/respool before collection.**

```powershell
Get-Disk | Format-List Number,FriendlyName,SerialNumber,Size,BusType,IsBoot,IsSystem
# Recheck and update $DiskNumber if needed; then:
$disk = Get-Disk -Number $DiskNumber -ErrorAction Stop
if ($disk.IsBoot -or $disk.IsSystem) { throw 'Wrong disk after reinsert.' }
$Card = '\\.\PhysicalDrive' + $DiskNumber
$disk | Format-List * | Out-File (Join-Path $D 'card-after.txt')
$code = Invoke-Tape -TapeArgs @('verify',$Card) -Stem (Join-Path $D 'after-verify')
$code = Invoke-Tape -TapeArgs @('dump',$Card,'--side','A','-o',(Join-Path $D 'after-A.wav')) -Stem (Join-Path $D 'after-A')
$code = Invoke-Tape -TapeArgs @('dump',$Card,'--side','B','-o',(Join-Path $D 'after-B.wav')) -Stem (Join-Path $D 'after-B')
Save-WavRecords -Paths @((Join-Path $D 'after-A.wav'),(Join-Path $D 'after-B.wav')) -Output (Join-Path $D 'after-wavs.json')
```

Each command has its own exit file. Missing/partial output is recorded, not silently treated as silence. Save raw metadata before reset for mixed/new/staged/error outcomes, using read-only helpers and the **newly reported disk size**:

```powershell
$CardBytes = [long]$disk.Size
if ($CardBytes % 512 -ne 0 -or $CardBytes -le 17825792) { throw 'Unexpected device geometry; stop.' }
try {
    Save-ReadOnlyRange -Source $Card -Offset 17825792 -Count 1048576 -Output (Join-Path $D 'p2-metadata.bin')
    Save-ReadOnlyRange -Source $Card -Offset ($CardBytes - 512) -Count 512 -Output (Join-Path $D 'p2-mirror.bin')
    Save-WavRecords -Paths @((Join-Path $D 'p2-metadata.bin'),(Join-Path $D 'p2-mirror.bin')) -Output (Join-Path $D 'metadata.json')
} catch {
    $_ | Out-File (Join-Path $D 'metadata-error.txt')
    throw 'Metadata capture failed; preserve card for Verification, no repair/reset.'
}
```

This reads the first2048 partition2 sectors and the mirror at capacity minus512. No FileAccess.Write is opened on the card. If administrative access/OS sharing refuses the read, retain the refusal and return the existing evidence/card; do not bypass it. These independent raw reads **do not establish A6 native access by shipped tapectl**. Do not mistake the metadata helper for tapectl instrumentation.

## 5. Decide whether another trial may start

Same original WP10 predicates: overwrite B at0 → commit → promote; tapefs §§8/8.1/9.1/9.3.4. Old quiet=793844 bytes/hash above; new C60=635040044 bytes/hash above.

| Captured state | Action |
|---|---|
| Both A/B exact quiet, dump exits0/0 and verify0/OK | Permitted old state before B commit, including inactive-slot fallback. Keep the complete folder; this clean pattern is preclassified and you may start next numbered trial from fresh5400s provision |
| A quiet / B C60 | Permitted mixed post-record/early-promote candidate; retain metadata and return for independent stage mapping before reset |
| Both C60 | Completed or promote intermediate/declined candidate; retain actual mid-load proof and metadata; return for mapping before reset |
| Any NEEDS_REPAIR/degraded/mount/read error or other audio/length | Preserve folder and card unchanged for Verification; no automatic PASS or corruption verdict from the exit alone |

Do not approve just because verify saysOK. No prefixes, zero-padding, added tails or missing final frame are accepted. Do not reset an unclassified card. Every new/reset-eligible trial starts with fresh provision+baseline; reloading quiet onto the previous full state repeats the original defect. Keep all ten actual pull records and Verification mappings on #146/#386. Manual pulls neither exhaust WP10 nor qualify card atomicity.

After ten accepted/mapped pulls, prepare the post-pull successful state with fresh3600s provision and **one** C60 load (using Invoke-Tape for automatic timing), then Safely Remove, physical reinsert/re-identify, verify/dump both sides/hash/size/Explorer README. This final state check follows the pulls; do not repeat the already successful earlier run merely to resubmit its existing evidence. Windows10 selection, physical >4GiB capture, media/hardware/target<30s/write/async/phase holds remain separate.
