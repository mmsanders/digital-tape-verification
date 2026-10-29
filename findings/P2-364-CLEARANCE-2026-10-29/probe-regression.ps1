$ErrorActionPreference='Stop'
$base=$env:RUNNER_TEMP
$retained=Join-Path $base 'verifier364-final'
New-Item -ItemType Directory $retained | Out-Null
foreach($which in 'old','new') {
    Copy-Item "$env:GITHUB_WORKSPACE/probe-$which.exe" "$env:GITHUB_WORKSPACE/probe.exe"
    $env:RUNNER_TEMP=Join-Path $retained $which
    New-Item -ItemType Directory $env:RUNNER_TEMP | Out-Null
    try { & ./tests/c1_volume_query_r1/run.ps1; $outcome='r1 runner completed (criterion failed)' }
    catch { $outcome="r1 reproduction runner threw: $_" }
    $path=Join-Path $env:RUNNER_TEMP 'verifier364-volume-query/RESULT.json'
    $r=Get-Content -LiteralPath $path -Raw | ConvertFrom-Json
    if($r.baseline_mounts -lt 1 -or $r.failed_calls -lt 1 -or $r.typed_error_code -ne 21) {throw 'control was not established'}
    $expected=$which -eq 'new'
    if($r.required_query_fail_stop_pass -ne $expected) {throw "$which criterion outcome mismatch"}
    "$which : $outcome" | Set-Content (Join-Path $env:RUNNER_TEMP 'RUNNER.txt')
    Get-Content -LiteralPath $path
}
$env:RUNNER_TEMP=$base
