param([Parameter(Mandatory=$true)][string]$Receipt,[Parameter(Mandatory=$true)][string]$Manifest)
$ErrorActionPreference='Stop'
. (Join-Path $PSScriptRoot '../windows_app_start_r2/window_gate.ps1')
$r=Get-Content -LiteralPath $Receipt -Raw | ConvertFrom-Json
$m=Get-Content -LiteralPath $Manifest -Raw | ConvertFrom-Json
$pin=(Get-FileHash -LiteralPath $Manifest -Algorithm SHA256).Hash.ToLowerInvariant()
if ($r.method_manifest_sha256 -cne $pin -or $r.source -cne $m.source_head -or $r.build_sha256 -cne $m.build_sha256) { throw 'Source/manifest/BUILD identity mismatch' }
if ($r.pins.'digital-tape.exe' -cne $m.app_sha256 -or $r.pins.'ingest.exe' -cne $m.ingest_sha256 -or $r.pins.'tapectl.exe' -cne $m.tapectl_sha256) { throw 'Binary pins mismatch' }
$app=Join-Path $r.cwd 'digital-tape.exe'
if ($r.pid -le 0 -or $r.process_start_ticks -le 0 -or @($r.argv).Count -ne 1 -or @($r.requested_argv).Count -ne 1 -or $r.argv[0] -cne $app -or $r.requested_argv[0] -cne $app) { throw 'Requested/used argv/PID mismatch' }
if ($r.context.token_elevated -ne $false -or $r.context.effective_admin -ne $false -or $r.recorder_effective_admin -ne $false -or $r.context.parent_pid -ne $r.parent_pid) { throw 'Ordinary bound token required' }
if ($r.context.tool_route -cne 'approved-exec-command-require-escalated') { throw 'Wrong tool route' }
$ready=Get-ReadyWindow @($r.samples) $r.pid $r.process_start_ticks
if ($null -eq $ready -or !(Test-NormalQuit $r) -or $r.close_elapsed_ms -gt 20000 -or $r.ready_elapsed_ms -gt 20000) { throw 'Original ready/normal-quit predicate failed' }
$fresh=@($r.preclose_owned_windows)
if ($fresh.Count -ne 1 -or $fresh[0].handle -ne $ready.handle -or $fresh[0].pid -ne $r.pid -or $fresh[0].title -cne 'Digital Tape' -or !$fresh[0].visible -or !$fresh[0].responding -or !$fresh[0].top_level -or $fresh[0].owner_handle -ne 0) { throw 'Preclose identity not retained' }
if ($r.page_readiness -notlike 'UNEXECUTED*' -or $r.ui_interaction -cne 'UNEXECUTED') { throw 'Unsupported UI claim' }
'ONLY exact new-binary native-window readiness/normal quit; page/input/G1/G2 UNEXECUTED'
