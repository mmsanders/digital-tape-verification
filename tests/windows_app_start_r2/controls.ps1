$ErrorActionPreference='Stop'
. (Join-Path $PSScriptRoot 'window_gate.ps1')
function Sample([int]$Seq,[long]$Ms) {
  return @{seq=$Seq;elapsed_ms=$Ms;pid=123;start_ticks=567;handle=99;title='Digital Tape';top_level=$true;owner_handle=0;visible=$true;responding=$true;ambiguous=$false}
}
$good=@((Sample 0 4000),(Sample 1 4500),(Sample 2 5000))
if ($null -eq (Get-ReadyWindow $good 123 567)) { throw 'Positive ready control failed' }
$mutations=@(
  @{key='title';value=''},@{key='title';value='Other'},@{key='pid';value=124},
  @{key='start_ticks';value=568},@{key='top_level';value=$false},@{key='owner_handle';value=10},
  @{key='visible';value=$false},@{key='responding';value=$false},@{key='ambiguous';value=$true},
  @{key='elapsed_ms';value=4000},@{key='elapsed_ms';value=20001},@{key='seq';value=0},@{key='handle';value=100})
foreach ($m in $mutations) {
  $rows=@($good | ForEach-Object { $_.Clone() });$rows[2][$m.key]=$m.value
  if ($null -ne (Get-ReadyWindow $rows 123 567)) { throw "Detecting control survived: $($m.key)" }
}
if ($null -ne (Get-ReadyWindow @((Sample 0 180)) 123 567)) { throw 'Premature first handle survived' }
$stale=@($good)+@{seq=3;elapsed_ms=5500;pid=123;start_ticks=567;handle=0}
if ($null -ne (Get-ReadyWindow $stale 123 567)) { throw 'Earlier ready samples survived latest unready fact' }
$quit=@{native_window_ready=$true;close_posted=$true;graceful_exit=$true;forced_owned_cleanup=$false;exit=0;capture_complete=$true}
if (!(Test-NormalQuit $quit)) { throw 'Positive quit control failed' }
foreach ($m in @(@{key='forced_owned_cleanup';value=$true},@{key='native_window_ready';value=$false},@{key='exit';value=-1},@{key='graceful_exit';value=$false})) {
  $bad=$quit.Clone();$bad[$m.key]=$m.value
  if (Test-NormalQuit $bad) { throw 'False normal quit survived' }
}
Add-Type -Path (Join-Path $PSScriptRoot 'WindowNative.cs')
'PASS shared recorder gate: readiness/order/identity/staleness/cleanup causal controls; C# compiled; ZERO Win32 API or Product execution'
