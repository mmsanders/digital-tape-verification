param([Parameter(Mandatory=$true)][string]$PreparedDir)
$ErrorActionPreference='Stop'
. (Join-Path $PSScriptRoot 'session_gate.ps1')
. (Join-Path $PSScriptRoot 'session_io.ps1')
$script:positive=0;$script:negative=0
function Pass([bool]$Condition,[string]$Name) { if (!$Condition) { throw "Positive failed: $Name" };$script:positive++ }
function Reject([scriptblock]$Action,[string]$Name) { try { & $Action } catch { $script:negative++;return };throw "Negative survived: $Name" }
# Parse generated launch/context text, but NEVER source or invoke the launcher.
$text=Get-Content -LiteralPath (Join-Path $PreparedDir 'Start-Session.ps1') -Raw
$tokens=$null;$errors=$null
[void][Management.Automation.Language.Parser]::ParseInput($text,[ref]$tokens,[ref]$errors)
Pass ($errors.Count -eq 0) 'generated PowerShell AST'
$tree=[Management.Automation.Language.Parser]::ParseInput($text,[ref]$tokens,[ref]$errors)
$ordinary=$tree.Find({param($n)$n -is [Management.Automation.Language.FunctionDefinitionAst] -and $n.Name -eq 'Ordinary-Path'},$true)
. ([scriptblock]::Create($ordinary.Extent.Text))
$m=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'METHOD.json') -Raw | ConvertFrom-Json
$sid='11111111111111111111111111111111';$app=Join-Path $m.artifact 'digital-tape.exe';$exe=Join-Path $m.artifact 'tapectl.exe'
function Rows {
  $r=@(@{kind='session';data=@{app_pid=42;app_path=$app;app_sha256=$m.app_sha256;app_os_start_ns=100;source_commit=$m.source}},@{kind='cards-contract';data=@{cards_schema=1}})
  foreach ($n in 1,2) {
    $r+=@(@{kind='cards-admit';data=@{run_id="cards-$n";ticket=$n}},@{kind='cards-launch';data=@{run_id="cards-$n";ticket=$n;pid=50+$n;exe=$exe;pin_sha256=$m.tapectl_sha256;exe_sha256_observed=$m.tapectl_sha256;pin_version_label=$m.tapectl_label;argv=@($exe,'cards','--report','SYNTHETIC','--report-nonce',('a'*32))}},@{kind='cards-terminal';data=@{run_id="cards-$n";ticket=$n;pid=50+$n;end='exited';wait_kind='wait'}})
  }
  for ($i=0;$i -lt $r.Count;$i++) { $r[$i].schema=1;$r[$i].session=$sid;$r[$i].seq=$i }
  return $r
}
function Count($R) { Get-TerminalCount $R $sid 42 $app $m.app_sha256 100 }
Pass ((Count (Rows)) -eq 2) 'two unique bound first-party terminals'
$r=Rows;Pass ((Count $r[0..4]) -eq 1) 'one terminal is not two'
foreach ($key in 'app_pid','app_path','app_sha256','app_os_start_ns','source_commit') {
  $r=Rows;$r[0].data[$key]='wrong';Reject { Count $r } "header $key"
}
$r=Rows;$r[2].session='other';Reject { Count $r } 'foreign session'
$r=Rows;$r[4].data.pid=777;Reject { Count $r } 'wrong child PID'
$r=Rows;$r[4].data.ticket=77;Reject { Count $r } 'wrong ticket'
$r=Rows;$r[3].data.exe='C:\wrong.exe';Reject { Count $r } 'unexpected child path'
$r=Rows;$r[3].data.pin_sha256='0'*64;Reject { Count $r } 'wrong S2 pin'
$r=Rows;$r[7].data.run_id='cards-1';Reject { Count $r } 'duplicate terminal cannot advance count'
$r=Rows;$r[7].seq=99;Reject { Count $r } 'sequence gap'
$r=Rows;$r[7].kind='child';Reject { Count $r } 'unexpected INGEST/non-cards activity'
$r=Rows;$r[7].data.end='imagined';Reject { Count $r } 'unsupported terminal'
$consent=@{human='Michael';route=$m.route;permission_mode='auto';per_command_prompt=$false;command_sha256='c'*64;method_publication='a'*40;method_sha256='b'*64;human_message_ref='SYNTHETIC human reference, not actual consent';human_message_text='SYNTHETIC resume exact pending method';manual_resumption_utc='2026-10-28T17:01:00Z';publication_utc='2026-10-28T17:00:00Z'}
Pass (Test-ManualConsent $consent ('c'*64) ('a'*40) ('b'*64)) 'manual resumption in unchanged auto mode'
foreach ($key in 'human','route','permission_mode','command_sha256','method_publication','method_sha256','human_message_ref') {
  $x=$consent.Clone();$x[$key]='';Pass (!(Test-ManualConsent $x ('c'*64) ('a'*40) ('b'*64))) "missing $key fails closed"
}
$x=$consent.Clone();$x.per_command_prompt=$true;Pass (!(Test-ManualConsent $x ('c'*64) ('a'*40) ('b'*64))) 'no fictional per-command prompt'
$x=$consent.Clone();$x.manual_resumption_utc='2026-10-28T16:59:00Z';Pass (!(Test-ManualConsent $x ('c'*64) ('a'*40) ('b'*64))) 'resumption must follow publication'
$facts=@{native_window_ready=$true;ready_elapsed_ms=1500;close_posted=$true;close_elapsed_ms=6500;graceful_exit=$true;forced_owned_cleanup=$false;exit=0;capture_complete=$true;pid=42;process_start_ticks=123;parent_identity=@{pid=42;start_ticks=123;image_sha256=$m.app_sha256}}
Pass (Test-SessionBounds $facts) 'new close/parent attribution bound'
foreach ($kv in @(@('close_elapsed_ms',16501),@('ready_elapsed_ms',20001),@('forced_owned_cleanup',$true),@('exit',1),@('capture_complete',$false))) {
  $x=$facts.Clone();$x[$kv[0]]=$kv[1];Pass (!(Test-SessionBounds $x)) "bad bound $($kv[0])"
}
# NEW owned-file method tests only: synthetic records, no app, token or native calls.
$root=Join-Path ([IO.Path]::GetTempPath()) ('v359-control-'+[Guid]::NewGuid().ToString('N'))
[void](New-Item -ItemType Directory -Path $root)
$control=Join-Path $root 'control';$dir=Join-Path $control ('diag-'+$sid)
[void](New-Item -ItemType Directory -Path (Join-Path $dir 'blobs') -Force)
[IO.File]::WriteAllText((Join-Path $dir '.digital-tape-diagnostic-session'),('{"schema":1,"session":"'+$sid+'"}'),[Text.UTF8Encoding]::new($false))
$json=((Rows | ForEach-Object { $_|ConvertTo-Json -Depth 8 -Compress }) -join "`n")+"`n"
[IO.File]::WriteAllText((Join-Path $dir 'records.jsonl'),$json+'{"partial":',[Text.UTF8Encoding]::new($false))
$got=Read-LiveSession $control 42 $app $m.app_sha256 100
Pass ($got.terminal_count -eq 2 -and $got.partial_tail) 'partial last line never counted'
$out=Join-Path $root 'retained';$kept=@(Retain-Session $control $out)
Pass ($kept.Count -eq 2 -and [IO.File]::ReadAllText((Join-Path $out 'records.jsonl')) -ceq ($json+'{"partial":')) 'raw partial original copied intact'
Reject { Retain-Session $control $out } 'retention never overwrites'
[IO.File]::WriteAllBytes((Join-Path $dir 'records.jsonl'),[byte[]]@(255,10))
Reject { Read-LiveSession $control 42 $app $m.app_sha256 100 } 'invalid complete UTF8 rejected'
# Keep these tiny synthetic fixtures as test outputs; no recursive cleanup/deletion command.
@{scope='new method controls ONLY';positive=$script:positive;negative=$script:negative;product_executions=0;native_api_calls=0;synthetic_fixture=$root}|ConvertTo-Json
