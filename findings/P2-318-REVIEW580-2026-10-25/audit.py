"""Independent read-only PR580 review. Never runs the offered child or native UI."""
import argparse, hashlib, importlib.util, json, subprocess
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--repo',type=Path,required=True)
p.add_argument('--artifacts',type=Path,required=True,help='child.zip, evidence.zip and expanded child/, evidence/')
a=p.parse_args();ROOT=a.artifacts.resolve();REPO=a.repo.resolve()
HEAD='18f424f66bbd0ad9c9f74c930d524627a3a6cf82'
BASE='1cf5577099ecc4445e8465bfb9addb1d780008eb'
def git(*args): return subprocess.check_output(['git',*args],cwd=REPO)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert git('rev-parse','origin/main').decode().strip()==BASE
assert git('rev-parse',HEAD+':tests/windows_discovery_r1').decode().strip()=='ec9cda078291e24230302b732fe40d97b412a184'
for commit in ['96717de5e6085d6a9dfc13ef197e227244df3280','8b7bca75c656eca2664e20f9cbba9e4e694d37ef',HEAD]:
    assert subprocess.run(['git','merge-base','--is-ancestor',commit,HEAD],cwd=REPO).returncode==0
paths=['host/app/src/bridge.rs','host/app/src/state.rs','host/app/frontend/screen.mjs','host/app/tests/discovery_component.rs','tests/windows_discovery_r1/contract.py','tests/wp15_app1a_r1/oracle.py']
for p in paths:
    target=ROOT/'source'/p;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(git('show',HEAD+':'+p))
spec=importlib.util.spec_from_file_location('contract',ROOT/'source/tests/windows_discovery_r1/contract.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
r=json.loads((ROOT/'evidence/discovery.json').read_bytes())
raw=json.loads((ROOT/'evidence/discovery.raw.json').read_bytes())
build=json.loads((ROOT/'evidence/child-build.json').read_bytes())
assert sha(ROOT/'child.zip')=='532a2b481a18ae52f0c2d8c439375805028ecc65995173e44c58f0f8e01ed710'
assert sha(ROOT/'evidence.zip')=='0ce7a42c20d3feca255869bcdf0edca87c9235e15446c897d53f3e31542557fa'
assert sha(ROOT/'child/tapectl.exe')==build['sha256']=='3cd678cbae5da79a1da99e6bfb2fb91d7ab711568e2557d133e245b4aa8b8ee9'
assert build['source']==HEAD and build['version']=='tapectl-wp15-s2+'+HEAD[:12]
assert build['bytes']==(ROOT/'child/tapectl.exe').stat().st_size==493712
assert build['engine_tree']==git('rev-parse',HEAD+':engine').decode().strip()==c.ENGINE
for path,x in build['crosswalk']['blobs'].items():assert x['current']==git('rev-parse',HEAD+':'+path).decode().strip()
c.controls();qualified=c.qualify(r,HEAD)
assert len(raw['rows'])==len(c.CASES)==23
for case,actual in zip(c.CASES,raw['rows']):
    assert case['id']==actual['id']
    ran=actual['ran']
    assert ran['exit']==case['exit'] and bytes(ran['stdout']).decode()==case['stdout']
    assert (bytes(ran['report']).decode() if ran['report'] is not None else '')==case['report']
    assert actual['request']['nonce']==c.NONCE and actual['request']['version']==c.VERSION
    assert actual['view']['card_line']==r['rows'][case['id']]['line']
    assert actual['view']['make_enabled'] is False
assert len(set(x['nonce'] for x in raw['requests']))==3
problem=[x for x in raw['rows'] if x['id'] in ['zero-unprobed','enum-unavailable']]
assert all(x['view']['view']=='empty' and not x['view']['details_available'] and x['details'] for x in problem)
inventory={str(p.relative_to(ROOT)).replace('\\','/'):{'bytes':p.stat().st_size,'sha256':sha(p)} for d in ['evidence','child'] for p in sorted((ROOT/d).rglob('*')) if p.is_file()}
result=dict(candidate=HEAD,base=BASE,import_tree='ec9cda078291e24230302b732fe40d97b412a184',qualifier=qualified,controlled_rows=23,
    details_unreachable=[dict(id=x['id'],view=x['view'],details=x['details']) for x in problem],
    shutdown_trace=raw['traces']['shutdown'],inventory=inventory,
    evidence_class='Independent source/raw/hash and production test-DOM review only; no child/native/UI/device execution',
    disposition='CORRECTION 1 REQUIRED: discovery details access and shutdown/start registration race; no merge/live clearance')
(ROOT/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k not in ['inventory','details_unreachable']},indent=2))
