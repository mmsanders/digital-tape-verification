"""361 fresh verifier method; generation never executes PowerShell/native/Product."""
import argparse,ast,hashlib,importlib.util,json,os,re
from pathlib import Path
HERE=Path(__file__).resolve().parent
TESTS=Path(os.environ.get('VERIFICATION_TESTS',HERE.parent))
spec=importlib.util.spec_from_file_location('held359',TESTS/'windows_poller_session_r1'/'prepare.py')
legacy=importlib.util.module_from_spec(spec);spec.loader.exec_module(legacy)

def prepared(publication,held=False):
    assert re.fullmatch('[0-9a-f]{40}',publication)
    original=legacy.HERE;legacy.HERE=HERE
    try:data,receipt=legacy.prepared(publication)
    finally:legacy.HERE=original
    s=data['Start-Session.ps1'].decode()
    # The qualified new output differs from its tested HELD twin only by this guard.
    guard="throw 'Verification359 HELD: new PowerShell controls did not execute; this authoring publication grants NO launch admission'\n"
    assert s.count(guard)==1
    s=s.replace(guard,"throw 'Verification361 HELD: control variant; NO launch admission'\n" if held else '')
    command=receipt['command'].replace('method359','method361')
    command_sha=hashlib.sha256(command.encode()).hexdigest()
    s=s.replace(receipt['command_sha256'],command_sha)
    s=s.replace('terminal_polls_observed=0;', 'terminal_polls_observed=0;declared_jobs=@();normal_close_wait_ms=0;normal_close_elapsed_ms=0;cleanup_elapsed_ms=0;final_elapsed_ms=0;')
    s=s.replace("$facts.terminal_polls_observed=$signal.terminal_count", "$facts.terminal_polls_observed=$signal.terminal_count;$facts.declared_jobs=$signal.declared_jobs")
    s=s.replace("if ($signal.stopped) { $facts.close_reason='receipt-incomplete';break }\n        if ($signal.terminal_count -ge 2) { $facts.close_reason='two-first-party-terminals';break }", "$decision=Get-CloseDecision $facts.ready_elapsed_ms $clock.ElapsedMilliseconds $signal.terminal_count $signal.stopped\n        if ($decision -cne 'continue') { $facts.close_reason=$decision;break }")
    s=s.replace('14750','14000') # one-second scheduling margin; actual15s assertion remains mandatory
    s=s.replace('Start-Sleep -Milliseconds 100;$p.Refresh()', 'Start-Sleep -Milliseconds (Get-WaitBudget $clock.ElapsedMilliseconds ($facts.ready_elapsed_ms+14000) 100);$p.Refresh()')
    s=s.replace("if ($facts.close_posted) { $facts.graceful_exit=$p.WaitForExit(10000) }", """if ($facts.close_posted) {
        $facts.normal_close_wait_ms=Get-WaitBudget $clock.ElapsedMilliseconds 60000 10000
        $facts.graceful_exit=$p.WaitForExit($facts.normal_close_wait_ms)
        $facts.normal_close_elapsed_ms=$clock.ElapsedMilliseconds-$facts.close_elapsed_ms
      }""")
    a=s.index('  if (!$p.HasExited) { $facts.forced_owned_cleanup=');b=s.index('} catch { $facts.error=',a)
    s=s[:a]+s[b:]
    a=s.index('  if ($started -and !$p.HasExited) {');b=s.index('  if ($null -ne $outFile)',a)
    s=s[:a]+'''  $cleanupStart=$null;$finalDeadline=60000
  if ($started -and !$p.HasExited) {
    $facts.forced_owned_cleanup=$true;$cleanupStart=$clock.ElapsedMilliseconds
    $finalDeadline=[Math]::Min(70000,$cleanupStart+10000)
    try { $p.Kill();[void]$p.WaitForExit((Get-WaitBudget $clock.ElapsedMilliseconds $finalDeadline 5000)) } catch { $facts.cleanup_error=$_.Exception.Message }
  }
  if ($started -and $p.HasExited) { $facts.exit=$p.ExitCode }
  if ($null -ne $outTask -and $null -ne $errTask) {
    try { $facts.capture_complete=[Threading.Tasks.Task]::WaitAll([Threading.Tasks.Task[]]@($outTask,$errTask),(Get-WaitBudget $clock.ElapsedMilliseconds $finalDeadline 5000)) } catch { $facts.capture_error=$_.Exception.Message }
  }
''' + s[b:]
    a=s.index("      $jobsPath=Join-Path $DataRoot 'jobs'");b=s.index("    }\n  } catch { $facts.retention_error=",a)
    s=s[:a]+'''      $post=Get-PostJobs (Join-Path $DataRoot 'jobs') $facts.declared_jobs
      $facts.post_jobs=$post.entries;$facts.post_jobs_status=$post.status;$facts.post_jobs_scope=$post.scope
''' + s[b:]
    s=s.replace("  $facts.end_utc=", """  if ($started) {
    $facts.final_elapsed_ms=$clock.ElapsedMilliseconds
    if ($null -ne $cleanupStart) { $facts.cleanup_elapsed_ms=$clock.ElapsedMilliseconds-$cleanupStart }
    if ($facts.final_elapsed_ms -gt $finalDeadline) { $facts.error='Final/cleanup deadline overrun; originals preserved; no retry' }
  }
  $facts.verdict='STOP / incomplete or unqualified result'
  if ((Test-NormalQuit $facts) -and (Test-SessionBounds $facts)) { $facts.verdict='PARENT NATIVE WINDOW/CLOSE component observed; first-party poller originals require independent offline disposition' }
  $facts.end_utc=""")
    data['Start-Session.ps1']=s.encode()
    receipt.update(command=command,command_sha256=command_sha,files={n:hashlib.sha256(b).hexdigest() for n,b in data.items()},held=held,scope='361 method generation only; StageA admission requires exact publication on MAIN plus later trusted manual Software resumption; no execution during generation')
    return data,receipt

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--publication',required=True);p.add_argument('--out',required=True,type=Path);p.add_argument('--held',action='store_true');a=p.parse_args()
    data,receipt=prepared(a.publication,held=a.held);assert not a.out.exists();a.out.mkdir()
    for n,b in data.items():(a.out/n).write_bytes(b)
    (a.out/'PREPARED.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt,indent=2))
