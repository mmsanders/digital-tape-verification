"""Only new parameterization/attribution controls; no Product/token/Win32 call."""
import ast,copy,json
from pathlib import Path
import prepare as p
def main():
    data,receipt=p.prepared('a'*40)
    assert data['WindowNative.cs']==(p.OLD/'WindowNative.cs').read_bytes().replace(b'\r\n',b'\n')
    assert data['window_gate.ps1']==(p.OLD/'window_gate.ps1').read_bytes().replace(b'\r\n',b'\n')
    s=data['Start-Session.ps1'].decode();c=data['context.py'].decode()
    assert "throw 'Verification359 HELD:" in s.splitlines()[1]
    assert s.index("throw 'Verification359 HELD:") < s.index('$ArtifactDir=')
    assert p.manifest()['admission'].startswith('HELD:')
    for text in ["$info.Arguments='--diagnostic-receipts'","$facts.parent_identity=",'Read-LiveSession','WaitForExit(10000)','Test-ManualConsent','Retain-Session','S-1-16-8192']:
        assert text in s,text
    assert s.index('$facts.parent_identity=')<s.index('$facts.close_posted=[App283Native]::Close')
    assert s.index('Test-ManualConsent')<s.index('[void]$p.Start()')
    assert 'Set-ExecutionPolicy' not in s and '-ExecutionPolicy' not in receipt['command'] and 'runas' not in s.lower()
    assert 'manual human resumption record separate' in c and 'no per-command prompt claimed' in c
    assert 'caller attests tool approved this exact invocation' not in c
    ast.parse(c,feature_version=(3,10))
    assert '--diagnostic-receipts' not in receipt['command'] # it is the app argv, not a launcher argument
    m=p.manifest();assert m['attempt_limit']==1 and m['terminal_polls']==2 and m['after_ready_ms']==15000 and m['normal_close_ms']==10000
    print(json.dumps(dict(scope='new preparation identity/argv/consent deltas ONLY',inherited_native_bytes='unchanged',native_calls=0,product_executions=0,command=receipt['command'],command_sha256=receipt['command_sha256']),indent=2))
if __name__=='__main__':main()
