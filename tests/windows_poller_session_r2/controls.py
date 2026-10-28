"""Preparation identity checks only; executable helper controls run in Windows CI."""
import ast,hashlib,json
import prepare as p
data,r=p.prepared('a'*40,held=True)
qualified,q=p.prepared('a'*40)
assert not q['held'] and r['held']
assert qualified['Start-Session.ps1']==data['Start-Session.ps1'].replace(b"throw 'Verification361 HELD: control variant; NO launch admission'\n",b'')
assert b'throw \'Verification361 HELD:' not in qualified['Start-Session.ps1']
for n in ['WindowNative.cs','window_gate.ps1']:
    assert data[n]==(p.TESTS/'windows_app_start_r2'/n).read_bytes().replace(b'\r\n',b'\n')
s=data['Start-Session.ps1'].decode()
assert "Verification361 HELD:" in s
assert s.index('$facts.parent_identity=')<s.index('$facts.close_posted=[App283Native]::Close')
assert s.count('WaitAll(')==1 and s.count('$p.Kill()')==1
assert '$decision=Get-CloseDecision' in s and 'Get-WaitBudget' in s
assert s.index('Test-ManualConsent')<s.index('[void]$p.Start()')
assert 'Set-ExecutionPolicy' not in s and '-ExecutionPolicy' not in r['command']
assert 'method361' in r['command']
ast.parse(data['context.py'],feature_version=(3,10))
print(json.dumps(dict(scope='361 preparation only; no PowerShell/native/Product execution',command=r['command'],command_sha256=r['command_sha256'],method_sha256=r['method_sha256'],unchanged_native_helpers=True),indent=2))
