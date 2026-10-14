# Off-card collection only. No PhysicalDrive, load, pulls or physical stage.
param([Parameter(Mandatory=$true)][string]$TapeCtl)
$ErrorActionPreference = 'Stop'
$binary = (Resolve-Path -LiteralPath $TapeCtl).Path
$origin = $PWD.Path
$os = Get-CimInstance Win32_OperatingSystem
if ($os.ProductType -ne 1 -or $os.Caption -notmatch 'Windows 11' -or $env:PROCESSOR_ARCHITECTURE -ne 'AMD64') { throw 'STOP: use native x64 PowerShell on Windows 11' }
$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) { throw 'STOP: Administrator PowerShell required' }
$python = $null
$pythonCommand = Get-Command python -ErrorAction SilentlyContinue
if ($pythonCommand -and $pythonCommand.Source -notmatch '\\WindowsApps\\') { $python = $pythonCommand.Source }
$checker = Join-Path $PSScriptRoot 'a6check.py'
if ((Get-FileHash -LiteralPath $binary -Algorithm SHA256).Hash.ToLowerInvariant() -ne '82798af2899e9364b9c9bfaa2021daf6cc51ccd0c6562598d50e0a86944bb7a9') { throw 'STOP: shipping binary hash mismatch' }
if ((Get-FileHash -LiteralPath $checker -Algorithm SHA256).Hash.ToLowerInvariant() -ne '227ceed2f1ca8817447c4103983c72b16a060b1d3323de22c805289b621bd1ef') { throw 'STOP: checker hash mismatch' }
if ($origin -notmatch '^[A-Za-z]:\\') { throw 'STOP: use a local disk folder' }
$letter = $origin.Substring(0,1)
$drive = Get-PSDrive -Name $letter
if ($drive.Free -lt 6GB) { throw 'STOP: need 6 GiB free in the current folder' }
$disks = @(Get-Partition -DriveLetter $letter | Get-Disk)
if ($disks.Count -ne 1) { throw 'STOP: cannot identify the rehearsal filesystem disk' }
$diskNumber = $disks[0].Number
$run = Join-Path $origin ('a6-rh-win-' + [Guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $run -ErrorAction Stop | Out-Null
$started = $false
function Invoke-CaptureStep([string]$Step,[string]$Exe,[string[]]$Arguments) {
  $process = Start-Process -FilePath $Exe -ArgumentList $Arguments -WorkingDirectory $run -NoNewWindow -Wait -PassThru -RedirectStandardOutput (Join-Path $run ($Step+'-out.txt')) -RedirectStandardError (Join-Path $run ($Step+'-err.txt'))
  $process.Refresh()
  if ($null -eq $process.ExitCode) { throw ('STOP: unknown exit for '+$Step) }
  $process.ExitCode | Out-File -Encoding ascii (Join-Path $run ($Step+'-exit.txt'))
  if ($Step -in @('wpr-start','wpr-stop','tracerpt')) { ($Step+' '+$process.ExitCode) | Out-File -Append -Encoding ascii (Join-Path $run 'tracer-exits.txt') }
  return $process
}
Push-Location $run
try {
  Copy-Item -LiteralPath $binary -Destination '.\tapectl.exe'
  Copy-Item -LiteralPath $checker -Destination '.\a6check.py'
  if ((Get-FileHash .\tapectl.exe -Algorithm SHA256).Hash.ToLowerInvariant() -ne '82798af2899e9364b9c9bfaa2021daf6cc51ccd0c6562598d50e0a86944bb7a9') { throw 'STOP: copied binary hash mismatch' }
  if ((Get-FileHash .\a6check.py -Algorithm SHA256).Hash.ToLowerInvariant() -ne '227ceed2f1ca8817447c4103983c72b16a060b1d3323de22c805289b621bd1ef') { throw 'STOP: copied checker hash mismatch' }
  $os | Format-List Caption,Version,BuildNumber,OSArchitecture | Out-File versions.txt
  (Get-Item "$env:SystemRoot\System32\wpr.exe", "$env:SystemRoot\System32\tracerpt.exe").VersionInfo | Format-List | Out-File -Append versions.txt
  $drive | Format-List | Out-File space.txt
  $disks[0] | Format-List Number,FriendlyName,BusType,Size,LogicalSectorSize,PhysicalSectorSize | Out-File filesystem-disk.txt
  Get-FileHash .\tapectl.exe,.\a6check.py -Algorithm SHA256 | Format-List | Out-File -Width 4096 hashes-before.txt
  $profiles = Invoke-CaptureStep 'wpr-profiles' "$env:SystemRoot\System32\wpr.exe" @('-profiles')
  if ($profiles.ExitCode -ne 0) { throw 'STOP: WPR profile listing failed' }
  $provision = Invoke-CaptureStep 'provision' (Join-Path $run 'tapectl.exe') @('provision','rehearsal.img','--label','A6-REHEARSAL','--uuid','00112233445566778899aabbccddeeff','--epoch','1760000000','--image-bytes','4296015872')
  if ($provision.ExitCode -ne 0) { throw 'STOP: image provision failed' }
  $size = (Get-Item -LiteralPath '.\rehearsal.img').Length
  $size | Out-File -Encoding ascii geometry.txt
  if ($size -ne 4296015872) { throw 'STOP: unexpected image size' }
  $allocation = Invoke-CaptureStep 'allocation' "$env:SystemRoot\System32\fsutil.exe" @('sparse','queryflag','rehearsal.img')
  # queryflag may report not-sparse: the 6GiB preflight budget covers the full image.
  $start = Invoke-CaptureStep 'wpr-start' "$env:SystemRoot\System32\wpr.exe" @('-start','FileIO','-start','DiskIO','-filemode')
  if ($start.ExitCode -ne 0) { throw 'STOP: tracer refused; no cancellation/security-policy workaround' }
  $started = $true
  try {
    $verify = Invoke-CaptureStep 'verify' (Join-Path $run 'tapectl.exe') @('verify','rehearsal.img')
    ('pid '+$verify.Id+' exit '+$verify.ExitCode) | Out-File -Encoding ascii verify-pid.txt
  } finally {
    if ($started) {
      $started = $false
      $stop = Invoke-CaptureStep 'wpr-stop' "$env:SystemRoot\System32\wpr.exe" @('-stop','verify.etl')
      if ($stop.ExitCode -ne 0) { throw 'STOP: WPR stop failed; retain all output' }
    }
  }
  if ($verify.ExitCode -ne 0) { throw 'STOP: verify failed' }
  $export = Invoke-CaptureStep 'tracerpt' "$env:SystemRoot\System32\tracerpt.exe" @('verify.etl','-o','verify.xml','-of','XML','-y')
  if ($export.ExitCode -ne 0) { throw 'STOP: tracer export failed' }
  Get-FileHash .\tapectl.exe,.\a6check.py -Algorithm SHA256 | Format-List | Out-File -Width 4096 hashes-after.txt
  if (Compare-Object (Get-Content hashes-before.txt) (Get-Content hashes-after.txt)) { throw 'STOP: source changed during collection' }
  if ($python) {
    $pythonVersion = Invoke-CaptureStep 'python-version' $python @('--version')
    if ($pythonVersion.ExitCode -ne 0) { throw 'STOP: local Python unavailable; send raw evidence' }
    & $python .\a6check.py --format etw-xml --trace verify.xml --pid $verify.Id --capacity 4296015872 --geometry geometry.txt --target rehearsal.img --disk $diskNumber --exe tapectl.exe --sha256 82798af2899e9364b9c9bfaa2021daf6cc51ccd0c6562598d50e0a86944bb7a9 --stdout verify-out.txt --diagnostics wpr-stop-err.txt --diagnostics wpr-stop-out.txt --diagnostics tracerpt-err.txt --diagnostics tracerpt-out.txt --tracer-log tracer-exits.txt --exit-code $verify.ExitCode 1> checker.json 2> checker-err.txt
    $result = $LASTEXITCODE
    $result | Out-File -Encoding ascii checker-exit.txt
    if ($result -ne 0) { throw 'STOP: checker is not PASS; send evidence without changing the recipe' }
  } else {
    'Local checker not run: no existing Python executable. Send raw evidence for independent review.' | Out-File checker-not-run.txt
  }
} catch {
  $_ | Out-String | Out-File -Encoding utf8 stop.txt
  Write-Host ('STOP: '+$_.Exception.Message)
} finally {
  Pop-Location
  $files = @(Get-ChildItem -LiteralPath $run -File | Where-Object Name -ne 'rehearsal.img' | ForEach-Object FullName)
  try { Compress-Archive -LiteralPath $files -DestinationPath ($run+'.zip') -ErrorAction Stop; Write-Host ('Evidence: '+$run+'.zip') }
  catch { Write-Host ('Zip failed; keep and send the logs in '+$run) }
  Write-Host 'STOP here and send evidence to Verification. No card stage is authorized by this script.'
  Write-Host ('Disposable image retained at '+(Join-Path $run 'rehearsal.img'))
}
