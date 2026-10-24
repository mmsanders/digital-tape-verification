$ErrorActionPreference='Stop'
. (Join-Path $PSScriptRoot '../windows_app_start_r2/window_gate.ps1')
$temp=Join-Path ([IO.Path]::GetTempPath()) ('synthetic307-'+[Guid]::NewGuid().ToString('N'))
[void][IO.Directory]::CreateDirectory($temp)
$manifest=Join-Path $temp 'manifest.json';$receipt=Join-Path $temp 'receipt.json'
try {
  $m=@{source_head=('a'*40);build_sha256=('f'*64);app_sha256=('e'*64);ingest_sha256=('1'*64);tapectl_sha256=('2'*64)}
  $m | ConvertTo-Json | Set-Content -LiteralPath $manifest -Encoding utf8
  $pin=(Get-FileHash -LiteralPath $manifest).Hash.ToLowerInvariant()
  $samples=@(4000,4500,5000) | ForEach-Object { @{seq=($_-4000)/500;elapsed_ms=$_;pid=123;start_ticks=567;handle=99;title='Digital Tape';top_level=$true;owner_handle=0;visible=$true;responding=$true;ambiguous=$false} }
  $good=@{method_manifest_sha256=$pin;source=$m.source_head;build_sha256=$m.build_sha256;pins=@{'digital-tape.exe'=$m.app_sha256;'ingest.exe'=$m.ingest_sha256;'tapectl.exe'=$m.tapectl_sha256};
    cwd='C:\bundle';argv=@('C:\bundle\digital-tape.exe');requested_argv=@('C:\bundle\digital-tape.exe');pid=123;process_start_ticks=567;parent_pid=456;
    context=@{token_elevated=$false;effective_admin=$false;parent_pid=456;tool_route='approved-exec-command-require-escalated'};recorder_effective_admin=$false;
    samples=$samples;native_window_ready=$true;close_posted=$true;graceful_exit=$true;forced_owned_cleanup=$false;exit=0;capture_complete=$true;
    close_elapsed_ms=5100;ready_elapsed_ms=5000;preclose_owned_windows=@($samples[-1]);page_readiness='UNEXECUTED / no actual page observer';ui_interaction='UNEXECUTED'}
  $good | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $receipt -Encoding utf8
  & (Join-Path $PSScriptRoot 'judge.ps1') -Receipt $receipt -Manifest $manifest | Out-Null
  $mutations=@(@{key='source';value=('b'*40)},@{key='argv';value=@()},@{key='requested_argv';value=@('C:\other.exe')},@{key='pid';value=0},
    @{key='method_manifest_sha256';value=('0'*64)},@{key='recorder_effective_admin';value=$true},@{key='forced_owned_cleanup';value=$true},
    @{key='close_elapsed_ms';value=20001},@{key='page_readiness';value='PASS'},@{key='preclose_owned_windows';value=@()})
  foreach ($mutation in $mutations) {
    $bad=$good.Clone();$bad[$mutation.key]=$mutation.value
    $bad | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $receipt -Encoding utf8
    $refused=$false
    try { & (Join-Path $PSScriptRoot 'judge.ps1') -Receipt $receipt -Manifest $manifest | Out-Null } catch { $refused=$true }
    if (!$refused) { throw "Candidate receipt causal control survived: $($mutation.key)" }
  }
  'PASS synthetic307 manifest/argv/identity/context/claim/quit controls; ZERO Product/Win32 calls'
} finally {
  foreach ($p in @($manifest,$receipt)) { if (Test-Path -LiteralPath $p) { Remove-Item -LiteralPath $p } }
  [IO.Directory]::Delete($temp,$false)
}
