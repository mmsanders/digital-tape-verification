"""359 exact618 adaptation of existing283/316 launcher. PREPARATION ONLY; no native calls."""
import argparse,ast,hashlib,json,os,re
from pathlib import Path
HERE=Path(__file__).resolve().parent
TESTS=Path(os.environ.get('VERIFICATION_TESTS',HERE.parent))
OLD=TESTS/'windows_app_start_r2'
PINS={'Start-App.ps1':'b23d54869fd2fd58e1a422a64b6c70da397c49e632cf1cf7a389b143aff242e4','window_gate.ps1':'a8af2eb0ba2106cdcc2387e4ee1d5bead177b5bf89443937233e9c777901b9f3','context.py':'a0e7f153e77e52f196c829d4ddb290dd129efdec777b9ff582a6bb3f3e6e6bf3','WindowNative.cs':'868c11c40d776792a184dba00dc7f2a6b9a286db286cdff2981d2077956988dc'}
ROUTE='manual-software-resumption-existing-auto-mode'
def sha(b):return hashlib.sha256(b).hexdigest()
def once(s,a,b):assert s.count(a)==1,a;return s.replace(a,b,1)
def manifest():return json.loads((HERE/'METHOD.json').read_text())
def prepared(publication):
    assert re.fullmatch('[0-9a-f]{40}',publication)
    m=manifest();base={n:(OLD/n).read_bytes().replace(b'\r\n',b'\n') for n in PINS}
    assert all(sha(base[n])==h for n,h in PINS.items())
    s=base['Start-App.ps1'].decode();start=s.index("$ErrorActionPreference='Stop'")
    command=r'powershell.exe -NoProfile -File "C:\Users\mrtro\DigitalTape-618-kit\method359\Start-Session.ps1" -Consent "C:\Users\mrtro\DigitalTape-618-kit\consent618.json"'
    method_sha=sha((HERE/'METHOD.json').read_bytes().replace(b'\r\n',b'\n'))
    header="param([Parameter(Mandatory=$true)][string]$Consent)\nthrow 'Verification359 HELD: new PowerShell controls did not execute; this authoring publication grants NO launch admission'\n"+f"$ArtifactDir='{m['artifact']}';$WorkDir='{m['work']}';$Python='{m['python']}';$ToolContext='{ROUTE}'\n$DataRoot='{m['data']}';$publication='{publication}';$methodSha='{method_sha}';$commandSha='{sha(command.encode())}'\n"
    s=header+s[start:]
    s=once(s,". (Join-Path $PSScriptRoot 'window_gate.ps1')",". (Join-Path $PSScriptRoot 'window_gate.ps1')\n. (Join-Path $PSScriptRoot 'session_gate.ps1')\n. (Join-Path $PSScriptRoot 'session_io.ps1')")
    s=once(s,"$pythonPath=Ordinary-Path $Python $false","$pythonPath=Ordinary-Path $Python $false\nif ((Get-FileHash -LiteralPath $pythonPath -Algorithm SHA256).Hash.ToLowerInvariant() -cne '"+m['python_sha256']+"') { throw 'Existing Python pin mismatch' }")
    s=once(s,'[void][IO.Directory]::CreateDirectory($work)','[void](New-Item -ItemType Directory -Path $work -ErrorAction Stop)')
    for old,new in [('05bc85626bfeaaa904f9ec52b2208f18e584d5808916a5e561be762eebac02dc',m['app_sha256']),('82798af2899e9364b9c9bfaa2021daf6cc51ccd0c6562598d50e0a86944bb7a9',m['tapectl_sha256']),('45695aa0edb8a757db5074d17c39eda12bcda888',m['source'])]:s=once(s,old,new)
    s=once(s,"case='A0-r2'",f"case='native618-one-session';method_publication='{publication}';method_sha256='{method_sha}';consent_route='{ROUTE}';terminal_polls_observed=0;live_samples=@();diagnostic_copy_complete=$false;collection_error=$null;parent_identity=$null")
    needle="  $contextFile=Join-Path $work 'context.private.json'"
    pre=r'''  $consentPath=Ordinary-Path $Consent $false
  if ($consentPath -ine 'C:\Users\mrtro\DigitalTape-618-kit\consent618.json') { throw 'Wrong consent file' }
  $consentRecord=Get-Content -LiteralPath $consentPath -Raw | ConvertFrom-Json
  if (!(Test-ManualConsent $consentRecord $commandSha $publication $methodSha)) { throw 'Missing exact-method manual resumption; no launch' }
  $facts.consent=$consentRecord;$facts.consent_sha256=(Get-FileHash -LiteralPath $consentPath -Algorithm SHA256).Hash.ToLowerInvariant()
  $facts.per_command_prompt=$false;$facts.permission_mode='auto';$facts.policy_changed=$false
  $prepared=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'PREPARED.json') -Raw | ConvertFrom-Json
  if ($prepared.publication -cne $publication -or $prepared.method_sha256 -cne $methodSha -or $prepared.command_sha256 -cne $commandSha) { throw 'Prepared method mismatch' }
  if (@($prepared.files.PSObject.Properties).Count -ne 7) { throw 'Incomplete prepared helper set' }
  foreach ($property in $prepared.files.PSObject.Properties) {
    if ($property.Name -notin @('Start-Session.ps1','context.py','window_gate.ps1','WindowNative.cs','METHOD.json','session_gate.ps1','session_io.ps1')) { throw 'Unknown prepared file' }
    $preparedFile=Ordinary-Path (Join-Path $PSScriptRoot $property.Name) $false
    if ((Get-FileHash -LiteralPath $preparedFile -Algorithm SHA256).Hash.ToLowerInvariant() -cne $property.Value) { throw 'Prepared helper changed' }
  }
  [void](Ordinary-Path $DataRoot $true)
  if (Test-Path -LiteralPath (Join-Path $DataRoot 'control')) { throw 'Declared fresh control root is no longer absent; preserve it and STOP' }
  if (Test-Path -LiteralPath (Join-Path $DataRoot 'jobs')) {
    [void](Ordinary-Path (Join-Path $DataRoot 'jobs') $true)
    if (@(Get-ChildItem -LiteralPath (Join-Path $DataRoot 'jobs') -Force).Count -ne 0) { throw 'Existing jobs; no cleanup or overwrite' }
  }
  if (@(Get-Process -Name digital-tape,tapectl,ingest -ErrorAction SilentlyContinue).Count -ne 0) { throw 'Conflicting process; no launch' }
'''
    s=once(s,needle,pre+'\n'+needle)
    s=once(s,'  $principal=',"  $groups=(& whoami /groups /fo csv /nh | Out-String)\n  if ($LASTEXITCODE -ne 0 -or $groups -notmatch 'S-1-16-8192') { throw 'Current Medium integrity not established' }\n  $facts.integrity_groups=$groups\n  $principal=")
    s=once(s,"  Add-Type -Path",f"  if ($facts.build_sha256 -cne '{m['build_sha256']}') {{ throw 'Specific BUILD hash mismatch' }}\n  Add-Type -Path")
    s=once(s,'$info.UseShellExecute=$false;',"$info.Arguments='--diagnostic-receipts';$facts.requested_argv=@($info.FileName,'--diagnostic-receipts');$facts.argv=$facts.requested_argv\n  $info.UseShellExecute=$false;")
    a=s.index('    try {\n      # Own app modules');b=s.index('    # Revalidate the exact owned handle',a)
    s=s[:a]+r'''    $facts.native_window_ready=$true;$facts.ready_elapsed_ms=$ready.elapsed_ms
    $p.Refresh()
    $image=Ordinary-Path $p.MainModule.FileName $false
    $facts.parent_identity=@{pid=$p.Id;image_path=$image;image_sha256=(Get-FileHash -LiteralPath $image -Algorithm SHA256).Hash.ToLowerInvariant();start_ticks=$p.StartTime.ToUniversalTime().Ticks;observed_utc=[DateTime]::UtcNow.ToString('o')}
    $facts.parent_identity.os_start_ns=([decimal]$facts.parent_identity.start_ticks-[decimal]621355968000000000)*100
    if ($image -ine $info.FileName -or $facts.parent_identity.image_sha256 -cne $pins['digital-tape.exe'] -or $facts.parent_identity.start_ticks -ne $facts.process_start_ticks) { throw 'Running parent identity mismatch' }
    Save-Facts
    while (!$p.HasExited -and $clock.ElapsedMilliseconds -lt $facts.ready_elapsed_ms+14750 -and $clock.ElapsedMilliseconds -lt 59000) {
      try {
        $signal=Read-LiveSession (Join-Path $DataRoot 'control') $p.Id $image $pins['digital-tape.exe'] $facts.parent_identity.os_start_ns
        $facts.terminal_polls_observed=$signal.terminal_count
        $facts.live_samples+=@(@{elapsed_ms=$clock.ElapsedMilliseconds;session=$signal.session;terminal_count=$signal.terminal_count;partial_tail=$signal.partial_tail;complete_lines=$signal.complete_lines;scope='FIRST-PARTY stop trigger only'})
        if ($signal.stopped) { $facts.close_reason='receipt-incomplete';break }
        if ($signal.terminal_count -ge 2) { $facts.close_reason='two-first-party-terminals';break }
      } catch { $facts.collection_error=$_.Exception.Message;$facts.close_reason='collection-blocker';break }
      Start-Sleep -Milliseconds 100;$p.Refresh()
    }
    if (!$facts.close_reason) { $facts.close_reason='readiness-plus15s-bound' }
    if ($p.HasExited -or $p.StartTime.ToUniversalTime().Ticks -ne $facts.process_start_ticks) { throw 'Parent exited/reused before controlled close' }
''' + s[b:]
    s=once(s,'-and $clock.ElapsedMilliseconds -le 20000) {','-and $clock.ElapsedMilliseconds -le 60000) {')
    s=once(s,"$facts.close_elapsed_ms=$clock.ElapsedMilliseconds","$facts.close_elapsed_ms=$clock.ElapsedMilliseconds\n      if ($facts.close_elapsed_ms-$facts.ready_elapsed_ms -gt 15000) { $facts.collection_error='Close observation bound overrun' }")
    s=once(s,"  if (Test-NormalQuit $facts) { $facts.verdict='NATIVE WINDOW READINESS AND NORMAL QUIT observed; page/UI unexecuted' }","  if ((Test-NormalQuit $facts) -and (Test-SessionBounds $facts)) { $facts.verdict='PARENT NATIVE WINDOW/CLOSE component observed; FIRST-PARTY poller records require offline review' }")
    s=once(s,"  $facts.end_utc=",r'''  try {
    if ($started) {
      $facts.diagnostic_manifest=@(Retain-Session (Join-Path $DataRoot 'control') (Join-Path $work 'diagnostic'))
      $facts.diagnostic_copy_complete=$true
      $jobsPath=Join-Path $DataRoot 'jobs'
      if (Test-Path -LiteralPath $jobsPath) {
        [void](Ordinary-Path $jobsPath $true)
        $facts.post_jobs=@(Get-ChildItem -LiteralPath $jobsPath -Force | ForEach-Object { @{name=$_.Name;directory=$_.PSIsContainer;reparse=(($_.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)} })
        $facts.post_jobs_status='observed; listing is not cleanup-history proof'
      } else { $facts.post_jobs_status='absent' }
    }
  } catch { $facts.retention_error=$_.Exception.Message }
  $facts.end_utc=''' )
    s=once(s,"if (!(Test-NormalQuit $facts)) { exit 1 }","if (!(Test-NormalQuit $facts) -or !(Test-SessionBounds $facts) -or !$facts.diagnostic_copy_complete -or $facts.collection_error -or $facts.retention_error) { exit 1 }")
    c=base['context.py'].decode().replace('approved-exec-command-require-escalated',ROUTE)
    c=once(c,"sandbox_mode='require_escalated (caller approval record required)'","sandbox_mode='existing Claude auto mode; unchanged; manual human resumption record separate'")
    c=once(c,"approval='caller attests tool approved this exact invocation; script cannot independently verify tool decision'","approval='no per-command prompt claimed; independent audit must verify referenced human manual resumption'")
    c=once(c,'python=sys.version,','python=sys.version,python_executable=sys.executable,')
    ast.parse(c,feature_version=(3,10))
    data={'Start-Session.ps1':s.encode(),'context.py':c.encode(),'window_gate.ps1':base['window_gate.ps1'],'WindowNative.cs':base['WindowNative.cs']}
    for n in ['METHOD.json','session_gate.ps1','session_io.ps1']:data[n]=(HERE/n).read_bytes().replace(b'\r\n',b'\n')
    return data,dict(publication=publication,method_sha256=method_sha,command=command,command_sha256=sha(command.encode()),files={n:sha(b) for n,b in data.items()},scope='PREPARATION; one later manually resumed session only; no launch during generation')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--publication',required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    data,receipt=prepared(a.publication);assert not a.out.exists();a.out.mkdir()
    for n,b in data.items():(a.out/n).write_bytes(b)
    (a.out/'PREPARED.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt,indent=2))
