# Called only after the original synthetic controls in this same test scope.
# Requirements authored before corrected helpers. Zero native/Product execution.
foreach ($row in @(@(0,10000,5000,5000),@(9000,10000,5000,1000),@(10000,10000,5000,0),@(10001,10000,5000,0))) {
  Pass ((Get-WaitBudget $row[0] $row[1] $row[2]) -eq $row[3]) 'single shared remaining deadline'
}
Reject { Get-WaitBudget -1 10000 5000 } 'negative time'
Pass ((Get-CloseDecision 1000 2000 1 $false) -ceq 'continue') 'one terminal continues'
Pass ((Get-CloseDecision 1000 2000 2 $false) -ceq 'two-terminals') 'two terminals close'
Pass ((Get-CloseDecision 1000 16000 0 $false) -ceq 'deadline') 'readiness plus15s closes'
Pass ((Get-CloseDecision 1000 2000 0 $true) -ceq 'incomplete') 'incomplete stops'
Reject { Get-CloseDecision 2000 1000 0 $false } 'retrograde time'
foreach ($property in 'error','capture_error','collection_error','retention_error','cleanup_error') {
  $x=$facts.Clone();$x[$property]='synthetic failure';Pass (!(Test-SessionBounds $x)) "failure $property never PASS"
}
$x=$facts.Clone();$x.parent_identity=$facts.parent_identity.Clone();$x.parent_identity.pid=0;Pass (!(Test-SessionBounds $x)) 'zero parent fails'
foreach ($pair in @(@('normal_close_wait_ms',10001),@('normal_close_elapsed_ms',10001),@('final_elapsed_ms',60001),@('cleanup_elapsed_ms',10001),@('post_jobs_status','unbound-leftover'),@('diagnostic_copy_complete',$false))) {
  $x=$facts.Clone();$x[$pair[0]]=$pair[1];Pass (!(Test-SessionBounds $x)) "final bound $($pair[0])"
}
foreach ($pair in @(@('image_path','C:\wrong.exe'),@('os_start_ns',0),@('start_ticks',0))) {
  $x=$facts.Clone();$x.parent_identity=$facts.parent_identity.Clone();$x.parent_identity[$pair[0]]=$pair[1];Pass (!(Test-SessionBounds $x)) "parent $($pair[0])"
}
$x=$facts.Clone();$x.argv=@($app);Pass (!(Test-SessionBounds $x)) 'missing diagnostic argv'
$x=$consent.Clone();$x.human_message_text='';Pass (!(Test-ManualConsent $x ('c'*64) ('a'*40) ('b'*64))) 'empty human text fails'
# Restore synthetic valid records after prior malformedUTF8 case.
[IO.File]::WriteAllText((Join-Path $dir 'records.jsonl'),$json,[Text.UTF8Encoding]::new($false))
[IO.File]::WriteAllText((Join-Path $dir '.digital-tape-diagnostic-session'),'{"schema":1,"session":"foreign"}',[Text.UTF8Encoding]::new($false))
Reject { Retain-Session $control (Join-Path $root 'foreign-retain') } 'foreign marker cannot be retained as owned'
[IO.File]::WriteAllText((Join-Path $dir '.digital-tape-diagnostic-session'),('{"schema":1,"session":"'+$sid+'"}'),[Text.UTF8Encoding]::new($false))
Reject { Read-LiveSession (Join-Path $root 'absent') 42 $app $m.app_sha256 100 } 'missing session'
[IO.File]::WriteAllText((Join-Path $dir 'records.jsonl'),"not-json`n",[Text.UTF8Encoding]::new($false))
Reject { Read-LiveSession $control 42 $app $m.app_sha256 100 } 'malformed complete line'
[IO.File]::WriteAllText((Join-Path $dir 'records.jsonl'),(('x'*65536)+"`n"),[Text.UTF8Encoding]::new($false))
Reject { Read-LiveSession $control 42 $app $m.app_sha256 100 } 'oversized complete line'
[IO.File]::WriteAllText((Join-Path $dir 'records.jsonl'),('x'*16777217),[Text.UTF8Encoding]::new($false))
Reject { Read-LiveSession $control 42 $app $m.app_sha256 100 } 'oversized complete log'
[IO.File]::WriteAllText((Join-Path $dir 'records.jsonl'),$json,[Text.UTF8Encoding]::new($false))
$jobs=Join-Path $root 'jobs';Pass ((Get-PostJobs $jobs @()).status -ceq 'absent') 'jobs absent recorded'
[void](New-Item -ItemType Directory -Path $jobs)
Pass ((Get-PostJobs $jobs @()).status -ceq 'empty') 'empty is not cleanup history'
$bound=Join-Path $jobs 'cards-1';[void](New-Item -ItemType Directory -Path $bound)
$post=Get-PostJobs $jobs @($bound);Pass ($post.status -ceq 'bound-leftover' -and $post.entries[0].receipt_bound) 'bound leftover is not removed'
$post=Get-PostJobs $jobs @();Pass ($post.status -ceq 'unbound-leftover' -and !$post.entries[0].receipt_bound) 'unknown leftover not inspected or erased'
Pass (Test-Path -LiteralPath $bound) 'post-job observation removes nothing'
