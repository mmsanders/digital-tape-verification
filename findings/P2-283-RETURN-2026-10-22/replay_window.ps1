param([Parameter(Mandatory=$true)][string]$Receipt)
$ErrorActionPreference='Stop'
. (Join-Path $PSScriptRoot '../../tests/windows_app_start_r2/window_gate.ps1')
$r=Get-Content -LiteralPath $Receipt -Raw | ConvertFrom-Json -AsHashtable
$ready=Get-ReadyWindow $r.samples $r.pid $r.process_start_ticks
if ($null -eq $ready -or !(Test-NormalQuit $r)) { throw 'Actual window receipt does not meet published gate' }
'PASS actual retained window/quit receipt through unchanged shared gate; ZERO Product/native API execution'
