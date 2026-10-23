param(
  [Parameter(Mandatory=$true)][string]$ArtifactDir,
  [Parameter(Mandatory=$true)][string]$WorkDir,
  [Parameter(Mandatory=$true)][string]$Python,
  [Parameter(Mandatory=$true)][ValidateSet('approved-exec-command-require-escalated')][string]$ToolContext
)
$ErrorActionPreference='Stop'
. (Join-Path $PSScriptRoot 'window_gate.ps1')
function Ordinary-Path([string]$Path,[bool]$Directory) {
  $full=[IO.Path]::GetFullPath($Path)
  if ($full.StartsWith('\\') -or $full.Substring(2).Contains(':')) { throw 'Nonordinary path' }
  $item=Get-Item -LiteralPath $full
  if ($item.PSIsContainer -ne $Directory) { throw 'Wrong file/directory type' }
  $cursor=$item
  while ($null -ne $cursor) {
    if (($cursor.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'Reparse component' }
    if ($cursor.PSIsContainer) { $cursor=$cursor.Parent } else { $cursor=$cursor.Directory }
  }
  return $full
}
$artifact=Ordinary-Path $ArtifactDir $true
$pythonPath=Ordinary-Path $Python $false
$work=[IO.Path]::GetFullPath($WorkDir)
if (Test-Path -LiteralPath $work) { throw 'Fresh WorkDir required; preserve originals' }
[void](Ordinary-Path ([IO.Path]::GetDirectoryName($work)) $true)
if ($work.StartsWith('\\') -or $work.Substring(2).Contains(':')) { throw 'Nonordinary output' }
[void][IO.Directory]::CreateDirectory($work)
$pins=@{
 'digital-tape.exe'='05bc85626bfeaaa904f9ec52b2208f18e584d5808916a5e561be762eebac02dc';
 'ingest.exe'='3895f3f356c91b8a9fe870c33694da64bf2765df308bef118d657c1be4bb9a20';
 'tapectl.exe'='82798af2899e9364b9c9bfaa2021daf6cc51ccd0c6562598d50e0a86944bb7a9'
}
$facts=[ordered]@{case='A0-r2';source='45695aa0edb8a757db5074d17c39eda12bcda888';
 start_utc=[DateTime]::UtcNow.ToString('o');parent_pid=$PID;cwd=$artifact;argv=@();pins=$pins;
 tool_route=$ToolContext;samples=@();native_window_ready=$false;page_readiness='UNEXECUTED / no actual page observer';
 ui_interaction='UNEXECUTED';selected_webview2_runtime='UNAVAILABLE: module/child evidence not yet observed';
 close_posted=$false;graceful_exit=$false;forced_owned_cleanup=$false;capture_complete=$false;verdict='STOP'}
function Save-Facts { $facts | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath (Join-Path $work 'launch.private.json') -Encoding utf8 }
$p=$null;$started=$false;$outFile=$null;$errFile=$null;$outTask=$null;$errTask=$null;$clock=$null
try {
  Save-Facts
  $contextFile=Join-Path $work 'context.private.json'
  & $pythonPath -B (Join-Path $PSScriptRoot 'context.py') --route $ToolContext --output $contextFile
  if ($LASTEXITCODE -ne 0) { throw 'Ordinary context admission failed; no Product invocation' }
  $facts.context=Get-Content -LiteralPath $contextFile -Raw | ConvertFrom-Json
  $principal=[Security.Principal.WindowsPrincipal]::new([Security.Principal.WindowsIdentity]::GetCurrent())
  $facts.recorder_effective_admin=$principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
  if ($facts.recorder_effective_admin -or $facts.context.token_elevated -or $facts.context.effective_admin -or $facts.context.parent_pid -ne $PID) { throw 'Non-admin bound recorder context required' }
  if ([IO.DriveInfo]::new([IO.Path]::GetPathRoot($work)).AvailableFreeSpace -lt 256MB) { throw 'Insufficient ordinary log/fixture headroom' }
  foreach ($name in $pins.Keys) {
    $file=Ordinary-Path (Join-Path $artifact $name) $false
    if ((Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash.ToLowerInvariant() -ne $pins[$name]) { throw "Bundle mismatch: $name" }
  }
  $buildPath=Ordinary-Path (Join-Path $artifact 'BUILD.json') $false
  $build=Get-Content -LiteralPath $buildPath -Raw | ConvertFrom-Json
  if ($build.source_head -ne $facts.source -or $build.s1_source -ne '35b23cacae886d9b3693b7104f581d8646ea5667' -or $build.child_version -ne '0.1.1 INGEST-1 arithmetic-profile INGEST1-AP4') { throw 'BUILD mismatch' }
  $facts.build_sha256=(Get-FileHash -LiteralPath $buildPath).Hash.ToLowerInvariant()
  Add-Type -Path (Join-Path $PSScriptRoot 'WindowNative.cs')
  $info=[Diagnostics.ProcessStartInfo]::new()
  $info.FileName=Join-Path $artifact 'digital-tape.exe';$info.WorkingDirectory=$artifact
  $info.UseShellExecute=$false;$info.CreateNoWindow=$false
  $info.RedirectStandardOutput=$true;$info.RedirectStandardError=$true
  $outFile=[IO.File]::Open((Join-Path $work 'stdout.bin'),[IO.FileMode]::CreateNew)
  $errFile=[IO.File]::Open((Join-Path $work 'stderr.bin'),[IO.FileMode]::CreateNew)
  $p=[Diagnostics.Process]::new();$p.StartInfo=$info
  $clock=[Diagnostics.Stopwatch]::StartNew()
  [void]$p.Start();$started=$true;$facts.pid=$p.Id;$facts.process_start_ticks=$p.StartTime.ToUniversalTime().Ticks
  $facts.launch_utc=[DateTime]::UtcNow.ToString('o')
  $outTask=$p.StandardOutput.BaseStream.CopyToAsync($outFile);$errTask=$p.StandardError.BaseStream.CopyToAsync($errFile)
  Save-Facts
  $seq=0;$ready=$null
  while ($clock.ElapsedMilliseconds -le 20000) {
    $p.Refresh();if ($p.HasExited) { break }
    $observed=@([App283Native]::Snapshot([uint32]$p.Id))
    $candidates=@($observed | Where-Object { $_.title -ceq 'Digital Tape' -and $_.visible -and $_.top_level -and $_.owner_handle -eq 0 })
    $sample=@{seq=$seq;elapsed_ms=$clock.ElapsedMilliseconds;utc=[DateTime]::UtcNow.ToString('o');pid=$p.Id;
      start_ticks=$facts.process_start_ticks;handle=0;title='';visible=$false;responding=$false;top_level=$false;owner_handle=0;ambiguous=($candidates.Count -gt 1);observed_owned_windows=$observed}
    if ($candidates.Count -eq 1) {
      $candidate=$candidates[0]
      foreach ($key in @('pid','handle','title','visible','responding','top_level','owner_handle')) { $sample[$key]=$candidate.$key }
    }
    $facts.samples+=@($sample);Save-Facts
    $ready=Get-ReadyWindow $facts.samples $p.Id $facts.process_start_ticks
    if ($null -ne $ready) { break }
    $seq++;Start-Sleep -Milliseconds 500
  }
  if ($null -ne $ready -and !$p.HasExited) {
    try {
      # Own app modules only. Loader identity is not selected browser runtime proof.
      $facts.own_webview_modules=@($p.Modules | Where-Object { $_.ModuleName -match 'WebView' } | ForEach-Object {
        @{name=$_.ModuleName;path=$_.FileName;version=$_.FileVersionInfo.FileVersion;sha256=(Get-FileHash -LiteralPath $_.FileName).Hash.ToLowerInvariant()}
      })
    } catch { $facts.module_observation_error=$_.Exception.Message }
    # Revalidate the exact owned handle immediately before a normal OS WM_CLOSE.
    $fresh=@([App283Native]::Snapshot([uint32]$p.Id) | Where-Object { $_.handle -eq $ready.handle })
    $facts.preclose_owned_windows=$fresh
    if ($fresh.Count -eq 1 -and $fresh[0].title -ceq 'Digital Tape' -and $fresh[0].visible -and $fresh[0].responding -and $fresh[0].top_level -and $fresh[0].owner_handle -eq 0 -and $clock.ElapsedMilliseconds -le 20000) {
      $facts.native_window_ready=$true;$facts.ready_elapsed_ms=$ready.elapsed_ms
      $facts.close_requested_utc=[DateTime]::UtcNow.ToString('o')
      $facts.close_elapsed_ms=$clock.ElapsedMilliseconds
      $facts.close_posted=[App283Native]::Close($ready.handle,[uint32]$p.Id)
      if ($facts.close_posted) { $facts.graceful_exit=$p.WaitForExit(10000) }
    }
  }
  if (!$p.HasExited) { $facts.forced_owned_cleanup=$true;$p.Kill();[void]$p.WaitForExit(5000) }
  if ($p.HasExited) { $facts.exit=$p.ExitCode }
  $facts.capture_complete=[Threading.Tasks.Task]::WaitAll([Threading.Tasks.Task[]]@($outTask,$errTask),5000)
  if (Test-NormalQuit $facts) { $facts.verdict='NATIVE WINDOW READINESS AND NORMAL QUIT observed; page/UI unexecuted' }
} catch { $facts.error=$_.Exception.ToString() }
finally {
  if ($started -and !$p.HasExited) {
    $facts.forced_owned_cleanup=$true
    try { $p.Kill();[void]$p.WaitForExit(5000) } catch { $facts.cleanup_error=$_.Exception.Message }
  }
  if ($null -ne $outTask -and $null -ne $errTask) {
    try { $facts.capture_complete=[Threading.Tasks.Task]::WaitAll([Threading.Tasks.Task[]]@($outTask,$errTask),5000) } catch { $facts.capture_error=$_.Exception.Message }
  }
  if ($null -ne $outFile) { $outFile.Dispose() };if ($null -ne $errFile) { $errFile.Dispose() }
  if ($facts.forced_owned_cleanup) { $facts.verdict='STOP / owned cleanup is not normal quit' }
  if (!(Test-NormalQuit $facts) -and $facts.verdict -like 'NATIVE WINDOW*') { $facts.verdict='STOP / incomplete final receipt' }
  $facts.end_utc=[DateTime]::UtcNow.ToString('o')
  foreach ($name in @('stdout.bin','stderr.bin')) {
    $f=Join-Path $work $name
    if (Test-Path -LiteralPath $f) { $facts[$name+'_sha256']=(Get-FileHash -LiteralPath $f).Hash.ToLowerInvariant() }
  }
  Save-Facts
}
$facts | ConvertTo-Json -Depth 12
if (!(Test-NormalQuit $facts)) { exit 1 }
