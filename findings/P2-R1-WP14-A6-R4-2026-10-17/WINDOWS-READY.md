# One short Windows 11 physical A6 capture

Ready under Verification193 after exact Product441 method/rehearsal PASS at
`a50a211679b7893c7ac581d392784191519525d6`. This collects one read-only `verify`
of the existing card with the already accepted shipping binary. It does not
repeat the rehearsal, load, dumps, pulls or README checks. Physical A6 is still
unaccepted until the resulting native evidence is independently reviewed.

Use your existing Windows11 machine, the same owned PNY64GB card and reader,
and the same `tapectl.exe`. Close other applications and card Explorer windows.
Keep output on the computer with several GB free. Do not change execution policy,
security settings, the binary or card contents. The blocks below are reviewed
PowerShell instructions using the existing capture mechanism; they have not
been run on your physical machine by Verification.

Open **Administrator PowerShell** in your ordinary computer folder containing
`tapectl.exe`. Run each block in order. A stop/error means keep the output and
return it; do not improvise a retry or destructive card reset.

## 1. Check the binary and select the current disk

```powershell
$ErrorActionPreference = 'Stop'
$Root = (Get-Location).Path
$TapeCtl = (Resolve-Path .\tapectl.exe).Path
$ExpectedExe = '82798af2899e9364b9c9bfaa2021daf6cc51ccd0c6562598d50e0a86944bb7a9'
if ((Get-FileHash $TapeCtl -Algorithm SHA256).Hash -ne $ExpectedExe) { throw 'Wrong shipping binary; stop.' }
$os = Get-CimInstance Win32_OperatingSystem
if ($os.Caption -notmatch 'Windows 11' -or $os.OSArchitecture -notmatch '64') { throw 'This procedure is for Windows11x64.' }
Get-Disk | Format-List Number,FriendlyName,SerialNumber,BusType,Size,LogicalSectorSize,IsBoot,IsSystem
$DiskNumber = -1 # Replace ONLY after identifying the same owned card/reader; disk numbers can change.
$disk = Get-Disk -Number $DiskNumber -ErrorAction Stop
if ($disk.IsBoot -or $disk.IsSystem -or $disk.Size -ne 62537072640 -or $disk.LogicalSectorSize -ne 512) { throw 'Selection differs from the witnessed card geometry; stop and send the identification.' }
$Card = '\\.\PhysicalDrive' + $DiskNumber
$rootLetter = [IO.Path]::GetPathRoot($Root).Substring(0,1)
if ($rootLetter -notmatch '^[A-Za-z]$') { throw 'Use an ordinary computer drive folder, not a UNC path.' }
$folderDisks = @(Get-Partition -DriveLetter $rootLetter | Get-Disk)
if ($folderDisks.Number -contains $DiskNumber) { throw 'Output folder is on the card; stop and use the computer drive.' }
$RootDrive = Get-PSDrive -Name $rootLetter
if ($RootDrive.Free -lt 6442450944) { throw 'Need at least6GiB free on the computer output drive.' }
$D = Join-Path $Root ('a6-physical-win-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
if (Test-Path $D) { throw 'Existing evidence folder; preserve it.' }
New-Item -ItemType Directory -Path $D | Out-Null
$disk | Format-List Number,FriendlyName,SerialNumber,BusType,Size,LogicalSectorSize,PhysicalSectorSize,PartitionStyle,IsBoot,IsSystem | Out-File (Join-Path $D 'geometry.txt')
$os | Select-Object Caption,Version,BuildNumber,OSArchitecture | ConvertTo-Json | Set-Content (Join-Path $D 'os.json')
Get-Disk | Format-List * | Out-File (Join-Path $D 'all-disks-before.txt')
Copy-Item $TapeCtl (Join-Path $D 'tapectl.exe')
Get-FileHash $TapeCtl -Algorithm SHA256 | Format-List | Out-File (Join-Path $D 'binary-hash.txt')
$confirm = Read-Host ('Confirm the same owned card. Type exactly READONLY ' + $Card)
if ($confirm -cne ('READONLY ' + $Card)) { throw 'No matching confirmation; stop.' }
```

The byte capacity is the previously witnessed card's geometry, not a statement
that the USB reader exposes CID. Record card/reader identification or CID unavailable
in the note. If your working folder is on a UNC path or card volume, move to an
ordinary computer drive before starting. Do not assume the old disk number.

## 2. Collect one verify, retaining actual exit codes and tracer diagnostics

```powershell
function Invoke-A6Native {
    param([string]$NativeTool,[string[]]$NativeArgs,[string]$Stem)
    $savedPreference = $ErrorActionPreference
    try {
        # Windows PowerShell5.1 can wrap native stderr as an ErrorRecord.
        # Retain it without converting diagnostic text into a launch failure.
        $ErrorActionPreference = 'Continue'
        $LASTEXITCODE = $null
        & $NativeTool @NativeArgs 1> ($Stem + '-out.txt') 2> ($Stem + '-err.txt')
        $nativeCode = $LASTEXITCODE
    } finally { $ErrorActionPreference = $savedPreference }
    if ($null -eq $nativeCode) { throw ('No actual native exit code from ' + $NativeTool) }
    return $nativeCode
}
Get-Command wpr.exe,tracerpt.exe | Format-List Source,Version | Out-File (Join-Path $D 'tracer-tools.txt')
(Get-Item "$env:SystemRoot\System32\wpr.exe","$env:SystemRoot\System32\tracerpt.exe").VersionInfo | Format-List | Out-File (Join-Path $D 'tracer-versions.txt')
$profilesCode = Invoke-A6Native -NativeTool wpr.exe -NativeArgs @('-profiles') -Stem (Join-Path $D 'profiles')
if ($profilesCode -ne 0) { throw 'WPR profiles unavailable; keep diagnostics and stop.' }
$now = Get-Disk -Number $DiskNumber
if ($now.Size -ne $disk.Size -or $now.SerialNumber -ne $disk.SerialNumber -or $now.FriendlyName -ne $disk.FriendlyName -or $now.IsBoot -or $now.IsSystem) { throw 'Disk identification changed; stop.' }
$startCode = Invoke-A6Native -NativeTool wpr.exe -NativeArgs @('-start','FileIO','-start','DiskIO','-filemode') -Stem (Join-Path $D 'wpr-start')
('wpr-start ' + $startCode) | Set-Content -Encoding ascii (Join-Path $D 'tracer-exits.txt')
if ($startCode -ne 0) { throw 'WPR did not start (possibly an existing trace). Do not cancel another trace; return diagnostics.' }
$process = $null
try {
    ('verify ' + $Card) | Set-Content (Join-Path $D 'command.txt')
    (Get-Date).ToUniversalTime().ToString('o') | Set-Content (Join-Path $D 'start-utc.txt')
    $process = Start-Process -FilePath $TapeCtl -ArgumentList @('verify',$Card) -NoNewWindow -Wait -PassThru -RedirectStandardOutput (Join-Path $D 'verify-out.txt') -RedirectStandardError (Join-Path $D 'verify-err.txt')
    $process.Id | Set-Content -Encoding ascii (Join-Path $D 'verify-pid.txt')
    $process.ExitCode | Set-Content -Encoding ascii (Join-Path $D 'verify-exit.txt')
    (Get-Date).ToUniversalTime().ToString('o') | Set-Content (Join-Path $D 'end-utc.txt')
} finally {
    $stopCode = Invoke-A6Native -NativeTool wpr.exe -NativeArgs @('-stop',(Join-Path $D 'verify.etl')) -Stem (Join-Path $D 'wpr-stop')
    ('wpr-stop ' + $stopCode) | Add-Content -Encoding ascii (Join-Path $D 'tracer-exits.txt')
}
$exportCode = Invoke-A6Native -NativeTool tracerpt.exe -NativeArgs @((Join-Path $D 'verify.etl'),'-o',(Join-Path $D 'verify.xml'),'-of','XML','-y') -Stem (Join-Path $D 'tracerpt')
('tracerpt ' + $exportCode) | Add-Content -Encoding ascii (Join-Path $D 'tracer-exits.txt')
Get-Disk -Number $DiskNumber | Format-List * | Out-File (Join-Path $D 'card-after.txt')
Get-FileHash $TapeCtl -Algorithm SHA256 | Format-List | Out-File (Join-Path $D 'binary-hash-after.txt')
@('Same owned card and reader: FILL IN identification.','CID: FILL IN actual value or unavailable through USB reader.','Physical actions: card remained inserted; one verify only.','Any messages or deviations: FILL IN.') | Set-Content (Join-Path $D 'return-note.txt')
Write-Host ('Evidence folder: ' + $D)
Write-Host ('Verify exit: ' + $process.ExitCode + '; WPR stop: ' + $stopCode + '; export: ' + $exportCode)
```

Keep every output even on a nonzero exit, lost-event report, missing field or
access refusal. The collector never substitutes a zero for a missing exit code.
If PowerShell stops during collection, preserve the folder and report exactly
where it stopped. Do not run another card command.

## 3. Hash and return the packet

Edit `return-note.txt` with the actual identification/observations, then:

```powershell
Get-ChildItem $D -File | Get-FileHash -Algorithm SHA256 | Select-Object Path,Hash | ConvertTo-Json | Set-Content (Join-Path $D 'file-hashes.json')
$Packet = $D + '.zip'
Compress-Archive -Path (Join-Path $D '*') -DestinationPath $Packet -CompressionLevel Optimal
Get-FileHash $Packet -Algorithm SHA256 | Format-List
Write-Host $Packet
```

Attach that packet to Michael447 (or return it in this chat). Preserve the folder
and ZIP. If the ZIP is too large or compression fails, return the message and
printed folder path; do not delete ETL/XML or split away native records.

Verification will hash/check the collection using the exact reviewed checker:
Product441 commit `a50a211679b7893c7ac581d392784191519525d6`,
`tools/wp14-capture/a6check.py`, SHA256
`7cbba051629d56bffd85e715fe34cb909421aa6b105a52c883f383aed10b8d89`.
Its flags are format etw-xml; captured PID/actual exit; target PhysicalDriveN;
same disk number; actual geometry/capacity; shipped binary/hash above; captured
stdout; tracer-exits; ALL six start/stop/export diagnostic files. The last-sector
read must establish the full512 bytes at capacity minus512 with native returned
length/status, loss completeness and correct identity. Missing native coverage
stays HELD. Raw-disk writes remain failures, even to an unrelated named stream.

This read-only capture establishes no write-command A6 behavior, card atomicity,
Mac A6, media qualification, target throughput or full-package acceptance.
