<#
Read-only checker for the published WP14 physical witness procedure.
It reads local saved evidence only. It never opens a disk, calls tapectl,
repairs a card, provisions a card, or writes a report.
Green clearance is limited to the preclassified exact quiet/quiet old state.
Mixed/new/staged/error outcomes need independent Verification review.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$TrialFolder,
    [ValidateSet('BeforeLoad','AfterPull')][string]$Stage = 'AfterPull'
)
$ErrorActionPreference = 'Stop'
$QuietHash = 'd97a9735a2beb3defc09808b8f33a760c88e1b171eddb988082b8e0a5ad7692c'
$C60Hash = 'c7369c6fdcb476fcc7f6a9d68aaab276f68a4d316ffb595faabb736e6046495d'
$ExeHash = '82798af2899e9364b9c9bfaa2021daf6cc51ccd0c6562598d50e0a86944bb7a9'
function Require([bool]$Condition, [string]$Reason) {
    if (-not $Condition) { throw $Reason }
}
function Read-Text([string]$Name) {
    $path = Join-Path $Folder $Name
    Require (Test-Path -LiteralPath $path -PathType Leaf) ('Missing ' + $Name)
    return [IO.File]::ReadAllText($path)
}
function Read-Json([string]$Name) { return (Read-Text $Name | ConvertFrom-Json) }
function Leaf([string]$Path) { return ($Path -split '[\\/]')[-1] }
function Get-RecordedDisk([string]$Name) {
    $text = Read-Text $Name
    Require ($text -match '(?m)^\s*Number\s*:\s*(\d+)\s*$') ('Missing disk number in ' + $Name)
    $number = [int]$Matches[1]
    Require ($text -match '(?m)^\s*IsBoot\s*:\s*False\s*$') ('Boot/unknown disk in ' + $Name)
    Require ($text -match '(?m)^\s*IsSystem\s*:\s*False\s*$') ('System/unknown disk in ' + $Name)
    Require ($text -match '(?m)^\s*Size\s*:\s*(\d+)\s*$') ('Missing disk size in ' + $Name)
    $size = [long]$Matches[1]
    Require ($size -gt 17825792 -and $size -le 137438953472 -and $size % 512 -eq 0) ('Unexpected disk geometry in ' + $Name)
    return @{number=$number; size=$size; target=('\\.\PhysicalDrive' + $number)}
}
function Get-Command([string]$Stem, [string[]]$Arguments, [int]$Exit) {
    $c = Read-Json ($Stem + '-command.json')
    Require ($null -ne $c.exit -and [int]$c.exit -eq $Exit) ($Stem + ': unexpected native exit')
    Require ((Read-Text ($Stem + '-exit.txt')).Trim() -eq [string]$Exit) ($Stem + ': exit records disagree')
    Require (@($c.args).Count -eq $Arguments.Count) ($Stem + ': wrong argument count')
    for ($i=0; $i -lt $Arguments.Count; $i++) {
        # Output/source filenames are checked independently from copied folder paths.
        if ($Arguments[$i].StartsWith('leaf:')) {
            Require ((Leaf ([string]$c.args[$i])) -ceq $Arguments[$i].Substring(5)) ($Stem + ': wrong filename')
        } else { Require ([string]$c.args[$i] -ceq $Arguments[$i]) ($Stem + ': wrong command/target/options') }
    }
    Require ($null -ne $c.seconds -and [double]$c.seconds -ge 0 -and -not [double]::IsNaN([double]$c.seconds) -and -not [double]::IsInfinity([double]$c.seconds)) ($Stem + ': invalid timing')
    $start = [DateTimeOffset]::Parse([string]$c.started_utc)
    $end = [DateTimeOffset]::Parse([string]$c.ended_utc)
    Require ($end -ge $start) ($Stem + ': reversed timestamps')
    return @{start=$start; end=$end; seconds=[double]$c.seconds}
}
function Check-Quiet([string]$Name) {
    $path = Join-Path $Folder $Name
    Require (Test-Path -LiteralPath $path -PathType Leaf) ('Missing actual WAV ' + $Name)
    Require ((Get-Item -LiteralPath $path).Length -eq 793844) ($Name + ': not exact quiet length; preserve card')
    Require ((Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash -eq $QuietHash) ($Name + ': not exact quiet audio; preserve card for review')
}
function Crc32([byte[]]$Data) {
    [uint32]$crc = 4294967295
    foreach ($b in $Data) {
        $crc = $crc -bxor [uint32]$b
        for ($i=0; $i -lt 8; $i++) {
            if ($crc -band 1) { $crc = ($crc -shr 1) -bxor [uint32]3988292384 }
            else { $crc = $crc -shr 1 }
        }
    }
    return ($crc -bxor [uint32]4294967295)
}
function Check-OldSuperblock([byte[]]$Bytes, [string]$Name) {
    Require ($Bytes.Length -eq 512) ($Name + ': wrong superblock size')
    Require ([BitConverter]::ToString($Bytes,0,8) -eq '54-41-50-45-46-53-00-01') ($Name + ': bad magic')
    Require ((Crc32 $Bytes[0..507]) -eq [BitConverter]::ToUInt32($Bytes,508)) ($Name + ': bad CRC; preserve card')
    Require ($Bytes[16] -eq 0 -and [BitConverter]::ToUInt32($Bytes,48) -eq 5400 -and [BitConverter]::ToUInt32($Bytes,52) -eq 1817) ($Name + ': unexpected state/capacity')
    Require ([BitConverter]::ToUInt32($Bytes,56) -eq 2 -and [BitConverter]::ToUInt32($Bytes,124) -eq 0) ($Name + ': mixed/staged state needs review')
    $uuid = ([BitConverter]::ToString($Bytes,20,16)).Replace('-','').ToLowerInvariant()
    Require ($uuid -eq $TrialUuid) ($Name + ': UUID differs from this provision')
    Require ([BitConverter]::ToUInt32($Bytes,84) -eq ($AfterDisk.size / 512 - 34816 - 1)) ($Name + ': mirror geometry mismatch')
}
try {
    $Folder = (Resolve-Path -LiteralPath $TrialFolder).Path
    Require (Test-Path -LiteralPath $Folder -PathType Container) 'Use an extracted trial folder, not the ZIP.'
    $BeforeDisk = Get-RecordedDisk 'card-before.txt'
    $inputs = @(Read-Json 'inputs.json')
    foreach ($expected in @(
        @{name='tapectl.exe'; bytes=435533; hash=$ExeHash},
        @{name='C60.wav'; bytes=635040044; hash=$C60Hash},
        @{name='quiet.wav'; bytes=793844; hash=$QuietHash}
    )) {
        $row = @($inputs | Where-Object { (Leaf ([string]$_.path)) -ceq $expected.name })
        Require ($row.Count -eq 1) ('Missing/ambiguous input record ' + $expected.name)
        Require ($row[0].sha256 -eq $expected.hash -and [long]$row[0].bytes -eq $expected.bytes) ('Wrong input identity ' + $expected.name)
    }
    $provision = Get-Command 'provision' @('provision',$BeforeDisk.target,'--label','PULL-C90','--length-s','5400','--erase',$BeforeDisk.target) 0
    $provisionText = Read-Text 'provision.txt'
    Require ($provisionText -match '(?m)^uuid ([0-9a-f]{32})\s*$') 'Missing provision UUID'
    $TrialUuid = $Matches[1]
    $baseline = Get-Command 'baseline-load' @('load',$BeforeDisk.target,'leaf:quiet.wav') 0
    $bv = Get-Command 'before-verify' @('verify',$BeforeDisk.target) 0
    Require ((Read-Text 'before-verify.txt').Trim() -ceq 'OK') 'Baseline verify has findings'
    $ba = Get-Command 'before-A' @('dump',$BeforeDisk.target,'--side','A','-o','leaf:before-A.wav') 0
    $bb = Get-Command 'before-B' @('dump',$BeforeDisk.target,'--side','B','-o','leaf:before-B.wav') 0
    Check-Quiet 'before-A.wav'; Check-Quiet 'before-B.wav'
    Require ($provision.end -le $baseline.start -and $baseline.end -le $bv.start -and $bv.end -le $ba.start -and $ba.end -le $bb.start) 'Setup timestamps out of order; review evidence'
    if ($Stage -eq 'BeforeLoad') {
        Require (-not (Test-Path -LiteralPath (Join-Path $Folder 'load-command.json'))) 'This folder already has a load attempt; do not reuse it for another pull.'
        Write-Host 'READY TO START C60 LOAD' -ForegroundColor Green
        Write-Host 'Fresh provision and exact quiet baseline checks passed. Run instruction set 3, then physically pull while loading.'
        exit 0
    }
    $load = Get-Command 'load' @('load',$BeforeDisk.target,'leaf:C60.wav') 1
    Require ((Read-Text 'load.txt') -match 'TAPE_ERR_IO') 'Load is not the recorded removed-device I/O outcome; review required'
    $AfterDisk = Get-RecordedDisk 'card-after.txt'
    Require ($AfterDisk.size -eq $BeforeDisk.size) 'Disk capacity changed; re-identification needs review'
    $av = Get-Command 'after-verify' @('verify',$AfterDisk.target) 0
    Require ((Read-Text 'after-verify.txt').Trim() -ceq 'OK') 'After verify has findings; preserve card'
    $aa = Get-Command 'after-A' @('dump',$AfterDisk.target,'--side','A','-o','leaf:after-A.wav') 0
    $ab = Get-Command 'after-B' @('dump',$AfterDisk.target,'--side','B','-o','leaf:after-B.wav') 0
    Check-Quiet 'after-A.wav'; Check-Quiet 'after-B.wav'
    Require ($bb.end -le $load.start -and $load.end -le $av.start -and $av.end -le $aa.start -and $aa.end -le $ab.start) 'Pull/recovery timestamps out of order'
    $notes = @(Get-ChildItem -LiteralPath $Folder -Filter 'pull-note*.txt' -File)
    Require ($notes.Count -eq 1) 'Need one pull-note*.txt recording actual time and physical action'
    $note = [IO.File]::ReadAllText($notes[0].FullName)
    Require ($note -match '(?i)load\s+not\s+returned') 'Note must confirm the load had not returned when removed'
    Require ($note -match '(?i)(removed|unplugged|pulled).*(adapter|reader|card|usb)') 'Add what you physically removed/unplugged to the pull note'
    Require ($note -match '(?i)(?:stopwatch\s*time|elapsed\s*(?:time)?)\s*:\s*~?\s*(\d+(?:\.\d+)?)') 'Record stopwatch time: seconds in pull note'
    $cut = [double]::Parse($Matches[1],[Globalization.CultureInfo]::InvariantCulture)
    Require ($cut -gt 0) 'Record a positive actual pull-time estimate'
    if ($cut -gt $load.seconds) {
        Write-Host 'NOTE: Hand stopwatch and command timer differ. Retain both readings; this does not by itself classify the physical cut.' -ForegroundColor Yellow
    }
    $metaPath = Join-Path $Folder 'p2-metadata.bin'
    if (Test-Path -LiteralPath $metaPath) {
        $meta = [IO.File]::ReadAllBytes($metaPath)
        Require ($meta.Length -eq 1048576) 'Metadata snapshot has wrong size'
        Check-OldSuperblock $meta[0..511] 'Primary snapshot'
    }
    $mirrorPath = Join-Path $Folder 'p2-mirror.bin'
    if (Test-Path -LiteralPath $mirrorPath) {
        Check-OldSuperblock ([IO.File]::ReadAllBytes($mirrorPath)) 'Mirror snapshot'
    } else {
        Write-Host 'NOTE: Mirror snapshot absent. Clean quiet/quiet clearance does not depend on it; retain any capture error.' -ForegroundColor Yellow
    }
    Write-Host 'SAFE TO START A FRESH NEXT TRIAL' -ForegroundColor Green
    Write-Host ('Permitted clean old state; actual pull note: {0}s. Keep this whole folder.' -f $cut)
    Write-Host 'Next: re-identify disk, new numbered folder, fresh 5400s provision, quiet baseline and prechecks. Use a different pull time.'
    Write-Host 'Do not erase merely because a different future outcome says OK; this checker clears quiet/quiet only. Final ten-trial acceptance remains Verification-owned.'
    exit 0
} catch {
    Write-Host 'STOP - SEND FOR REVIEW; KEEP THE CARD UNCHANGED' -ForegroundColor Red
    Write-Host $_.Exception.Message
    exit 2
}
