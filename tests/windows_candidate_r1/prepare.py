"""307 source/pin receipt preparation only. NEVER launch a Product or native API."""
import argparse, copy, hashlib, json, re
from pathlib import Path

HERE=Path(__file__).resolve().parent
OLD=HERE.parent/'windows_app_start_r2'
APP='05bc85626bfeaaa904f9ec52b2208f18e584d5808916a5e561be762eebac02dc'
SOURCE='45695aa0edb8a757db5074d17c39eda12bcda888'
INGEST='3895f3f356c91b8a9fe870c33694da64bf2765df308bef118d657c1be4bb9a20'
TAPECTL='82798af2899e9364b9c9bfaa2021daf6cc51ccd0c6562598d50e0a86944bb7a9'
PINS={'Start-App.ps1':'b23d54869fd2fd58e1a422a64b6c70da397c49e632cf1cf7a389b143aff242e4','window_gate.ps1':'a8af2eb0ba2106cdcc2387e4ee1d5bead177b5bf89443937233e9c777901b9f3','context.py':'a0e7f153e77e52f196c829d4ddb290dd129efdec777b9ff582a6bb3f3e6e6bf3','WindowNative.cs':'868c11c40d776792a184dba00dc7f2a6b9a286db286cdff2981d2077956988dc'}

def manifest(m):
    for k in ['source_head','source_tree','frontend_disposition','bridge_disposition']:
        assert re.fullmatch('[0-9a-f]{40}',m[k])
    for k in ['app_sha256','build_sha256','archive_sha256']:
        assert re.fullmatch('[0-9a-f]{64}',m[k])
    assert m['source_head']!=SOURCE and m['app_sha256']!=APP,'old app promotion forbidden'
    assert m['ingest_sha256']==INGEST and m['tapectl_sha256']==TAPECTL
    assert m['s1_source']=='35b23cacae886d9b3693b7104f581d8646ea5667'
    assert m['child_version']=='0.1.1 INGEST-1 arithmetic-profile INGEST1-AP4'
    assert type(m['ci_run']) is int and m['ci_run']>0
    assert m['platform']=='Windows11 x64' and m['attempt_limit']==1
    assert m['scope']=='startup/native-window/normal-quit ONLY'
    assert m['disabled']==['discovery','make','elevation','raw-device','shipping-test-switch']
    assert m['startup_bounds_ms']==20000 and m['quit_bounds_ms']==10000
    assert m['actual_ui']=='UNEXECUTED' and m['selected_runtime']=='UNAVAILABLE unless bound from actual own process facts'

def once(s,a,b):
    assert s.count(a)==1,'unexpected original recorder bytes: '+a
    return s.replace(a,b,1)

def prepare(m,pin):
    manifest(m);assert re.fullmatch('[0-9a-f]{64}',pin)
    data={}
    for name,sha in PINS.items():
        b=(OLD/name).read_bytes().replace(b'\r\n',b'\n');assert hashlib.sha256(b).hexdigest()==sha
        data[name]=b
    s=data['Start-App.ps1'].decode()
    s=once(s,APP,m['app_sha256']);s=once(s,SOURCE,m['source_head'])
    s=once(s,"case='A0-r2'","case='A0-new-candidate-307';method_manifest_sha256='"+pin+"'")
    needle='$facts.build_sha256=(Get-FileHash -LiteralPath $buildPath).Hash.ToLowerInvariant()'
    s=once(s,needle,needle+"\n  if ($facts.build_sha256 -cne '"+m['build_sha256']+"') { throw 'Specific BUILD pin mismatch' }")
    s=once(s,'$p=[Diagnostics.Process]::new();$p.StartInfo=$info',"$facts.requested_argv=@($info.FileName);$facts.argv=@($info.FileName);Save-Facts\n  $p=[Diagnostics.Process]::new();$p.StartInfo=$info")
    s=once(s,'$facts.launch_utc=[DateTime]::UtcNow.ToString(\'o\')',"$facts.argv=@($p.StartInfo.FileName)\n  $facts.launch_utc=[DateTime]::UtcNow.ToString('o')")
    data['Start-App.ps1']=s.encode()
    return data

def fixture():
    return dict(source_head='a'*40,source_tree='b'*40,frontend_disposition='c'*40,bridge_disposition='d'*40,app_sha256='e'*64,build_sha256='f'*64,archive_sha256='1'*64,
                ingest_sha256=INGEST,tapectl_sha256=TAPECTL,s1_source='35b23cacae886d9b3693b7104f581d8646ea5667',child_version='0.1.1 INGEST-1 arithmetic-profile INGEST1-AP4',
                ci_run=1,platform='Windows11 x64',attempt_limit=1,scope='startup/native-window/normal-quit ONLY',disabled=['discovery','make','elevation','raw-device','shipping-test-switch'],
                startup_bounds_ms=20000,quit_bounds_ms=10000,actual_ui='UNEXECUTED',selected_runtime='UNAVAILABLE unless bound from actual own process facts')

def controls():
    m=fixture();d=prepare(m,'2'*64)
    assert d['window_gate.ps1']==(OLD/'window_gate.ps1').read_bytes().replace(b'\r\n',b'\n')
    assert d['WindowNative.cs']==(OLD/'WindowNative.cs').read_bytes().replace(b'\r\n',b'\n')
    assert b'$facts.requested_argv=@($info.FileName)' in d['Start-App.ps1']
    assert b'$facts.argv=@($p.StartInfo.FileName)' in d['Start-App.ps1']
    for k,v in [('source_head',SOURCE),('app_sha256',APP),('ingest_sha256','0'*64),('attempt_limit',2),('disabled',[]),('startup_bounds_ms',30000),('quit_bounds_ms',20000),('actual_ui','PASS')]:
        bad=copy.deepcopy(m);bad[k]=v
        try:manifest(bad)
        except AssertionError:continue
        raise AssertionError('candidate causal control survived: '+k)
    print('PASS exact new-candidate/pin/argv/scope preparation controls; ZERO Product/Win32 execution')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--manifest',type=Path);p.add_argument('--expected-manifest-sha256');p.add_argument('--out',type=Path);a=p.parse_args()
    if not a.manifest:controls()
    else:
        b=a.manifest.read_bytes();pin=hashlib.sha256(b).hexdigest();assert pin==a.expected_manifest_sha256
        data=prepare(json.loads(b.decode('utf-8-sig')),pin)
        assert a.out and not a.out.exists();a.out.mkdir(parents=False)
        for name,content in data.items():(a.out/name).write_bytes(content)
        (a.out/'PREPARED.json').write_text(json.dumps(dict(manifest_sha256=pin,files={n:hashlib.sha256(b).hexdigest() for n,b in data.items()},runtime_admission='requires independent307 exact GitHub comment; preparation is NOT launch authority'),indent=2)+'\n')
