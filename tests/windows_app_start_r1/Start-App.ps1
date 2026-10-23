param(
  [Parameter(Mandatory=$true)][string]$ArtifactDir,
  [Parameter(Mandatory=$true)][string]$WorkDir
)
# One ordinary actual GUI launch, bounded window metadata observation and normal close.
# Read README source/safety eligibility first. This does NOT exercise UI controls.
$ErrorActionPreference = 'Stop'
function Ordinary-Path([string]$Path, [bool]$Directory) {
  $full=[IO.Path]::GetFullPath($Path)
  if ($full.StartsWith('\\') -or $full.Substring(2).Contains(':')) { throw 'Device/UNC/ADS path refused' }
  $item=Get-Item -LiteralPath $full
  if ($item.PSIsContainer -ne $Directory) { throw 'Wrong ordinary file/directory type' }
  $cursor=$item
  while ($null -ne $cursor) {
    if (($cursor.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'Reparse component refused' }
    if ($cursor.PSIsContainer) { $cursor=$cursor.Parent } else { $cursor=$cursor.Directory }
  }
  return $full
}
$artifact=Ordinary-Path $ArtifactDir $true
$work=[IO.Path]::GetFullPath($WorkDir)
if (Test-Path -LiteralPath $work) { throw 'Fresh owned WorkDir required; preserve previous run' }
[void](Ordinary-Path ([IO.Path]::GetDirectoryName($work)) $true)
if ($work.StartsWith('\\') -or $work.Substring(2).Contains(':')) { throw 'Nonordinary output refused' }
[void][IO.Directory]::CreateDirectory($work)
$pins=@{
 'digital-tape.exe'='05bc85626bfeaaa904f9ec52b2208f18e584d5808916a5e561be762eebac02dc';
 'ingest.exe'='3895f3f356c91b8a9fe870c33694da64bf2765df308bef118d657c1be4bb9a20';
 'tapectl.exe'='82798af2899e9364b9c9bfaa2021daf6cc51ccd0c6562598d50e0a86944bb7a9'
}
$facts=[ordered]@{case='A0-actual-launch-window-facts-normal-close';start_utc=[DateTime]::UtcNow.ToString('o');
 source='45695aa0edb8a757db5074d17c39eda12bcda888';parent_pid=$PID;argv=@();cwd=$artifact;
 platform=[Runtime.InteropServices.RuntimeInformation]::OSDescription;architecture=[Runtime.InteropServices.RuntimeInformation]::OSArchitecture.ToString();
 shell=$PSVersionTable.PSVersion.ToString();pins=$pins;window_samples=@();ui_interaction='UNEXECUTED';visual_observation='UNEXECUTED';
 physical_make='DISABLED / NOT EXECUTED';verdict='INCOMPLETE'}
$receipt=Join-Path $work 'launch.private.json'
function Save-Facts { $facts | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $receipt -Encoding utf8 }
$p=$null;$started=$false;$outFile=$null;$errFile=$null;$outTask=$null;$errTask=$null
try {
  foreach ($name in $pins.Keys) {
    $file=Ordinary-Path (Join-Path $artifact $name) $false
    if ((Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash.ToLowerInvariant() -ne $pins[$name]) { throw "Bundle identity mismatch: $name" }
  }
  $build=Get-Content -LiteralPath (Join-Path $artifact 'BUILD.json') -Raw | ConvertFrom-Json
  if ($build.source_head -ne $facts.source -or $build.s1_source -ne '35b23cacae886d9b3693b7104f581d8646ea5667') { throw 'BUILD source identity mismatch' }
  $facts.build_sha256=(Get-FileHash -LiteralPath (Join-Path $artifact 'BUILD.json')).Hash.ToLowerInvariant()
  Save-Facts
  $info=[Diagnostics.ProcessStartInfo]::new()
  $info.FileName=Join-Path $artifact 'digital-tape.exe';$info.WorkingDirectory=$artifact
  $info.UseShellExecute=$false;$info.CreateNoWindow=$false
  $info.RedirectStandardOutput=$true;$info.RedirectStandardError=$true
  $outFile=[IO.File]::Open((Join-Path $work 'stdout.bin'),[IO.FileMode]::CreateNew)
  $errFile=[IO.File]::Open((Join-Path $work 'stderr.bin'),[IO.FileMode]::CreateNew)
  $p=[Diagnostics.Process]::new();$p.StartInfo=$info
  [void]$p.Start();$started=$true;$facts.pid=$p.Id;$facts.launch_utc=[DateTime]::UtcNow.ToString('o');Save-Facts
  $outTask=$p.StandardOutput.BaseStream.CopyToAsync($outFile)
  $errTask=$p.StandardError.BaseStream.CopyToAsync($errFile)
  for ($n=0;$n -lt 40;$n++) {
    $p.Refresh();if ($p.HasExited) { break }
    $facts.window_samples+=@{utc=[DateTime]::UtcNow.ToString('o');main_window_handle=$p.MainWindowHandle.ToInt64();main_window_title=$p.MainWindowTitle;responding=$p.Responding}
    if ($p.MainWindowHandle -ne [IntPtr]::Zero -and $p.Responding) { break }
    Start-Sleep -Milliseconds 500
  }
  $facts.window_fact=(@($facts.window_samples | Where-Object { $_.main_window_handle -ne 0 -and $_.responding }).Count -gt 0)
  if (!$p.HasExited) {
    $facts.close_requested_utc=[DateTime]::UtcNow.ToString('o')
    $facts.close_main_window_return=$p.CloseMainWindow()
    $facts.graceful_exit=$p.WaitForExit(10000)
    if (!$facts.graceful_exit) { $facts.forced_owned_cleanup=$true;$p.Kill();[void]$p.WaitForExit(5000) }
  } else { $facts.graceful_exit=$false }
  if ($p.HasExited) { $facts.exit=$p.ExitCode }
  $facts.capture_complete=[Threading.Tasks.Task]::WaitAll([Threading.Tasks.Task[]]@($outTask,$errTask),5000)
  if ($facts.window_fact -and $facts.graceful_exit -and $facts.exit -eq 0 -and $facts.capture_complete) {
    $facts.verdict='WINDOW-METADATA-AND-QUIT observed; UI/Empty state NOT proved'
  } else { $facts.verdict='STOP / incomplete startup-window-normal-quit'; }
} catch { $facts.error=$_.Exception.ToString();$facts.verdict='STOP' }
finally {
  if ($started -and !$p.HasExited) { $facts.forced_owned_cleanup=$true;$p.Kill();[void]$p.WaitForExit(5000) }
  if ($null -ne $outFile) { $outFile.Dispose() };if ($null -ne $errFile) { $errFile.Dispose() }
  $facts.end_utc=[DateTime]::UtcNow.ToString('o')
  foreach ($name in @('stdout.bin','stderr.bin')) {
    $f=Join-Path $work $name
    if (Test-Path -LiteralPath $f) { $facts[$name+'_sha256']=(Get-FileHash -LiteralPath $f).Hash.ToLowerInvariant() }
  }
  Save-Facts
}
$facts | ConvertTo-Json -Depth 8
