"""Read-only offered candidate archive/CI evidence audit; no executable extraction."""
import argparse,hashlib,io,json,struct,subprocess,sys,zipfile
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--workspace',type=Path,required=True);ap.add_argument('--product',type=Path,required=True);ap.add_argument('--verifier',type=Path,required=True);a=ap.parse_args()
root=a.workspace;product=a.product
sys.path.insert(0,str(a.verifier/'tests/windows_candidate_r1'))
import prepare,claude
sha=lambda b:hashlib.sha256(b).hexdigest()
git=lambda *a:subprocess.check_output(['git','-C',str(product),*a])
base=root/'review564/docs/REVIEW/software564'
mbytes=(base/'MANIFEST.json').read_bytes();m=json.loads(mbytes)
assert sha(mbytes)=='d28082644506472050220fa7080ec59df726114b10050552dcf9a8e797c96c8e'
prepare.manifest(m)
outer=(root/'candidate564-artifact.zip').read_bytes()
assert sha(outer)=='a19c47d7d474414cfb0c8cf992fd6e984bf9ff160c5e38efdd7e09a45b12aa94'
with zipfile.ZipFile(io.BytesIO(outer)) as z:
    assert z.namelist()==['Digital-Tape-Windows11-x64-candidate.zip']
    archive=z.read(z.namelist()[0])
assert sha(archive)==m['archive_sha256'] and len(archive)==2438637
inventory={}
with zipfile.ZipFile(io.BytesIO(archive)) as z:
    assert z.namelist()==['BUILD.json','README.txt','digital-tape.exe','ingest.exe','tapectl.exe']
    for name in z.namelist():
        b=z.read(name);info=z.getinfo(name)
        assert info.date_time==(2026,10,24,0,0,0) and info.external_attr>>16==0o100644
        inventory[name]=dict(bytes=len(b),sha256=sha(b))
        if name.endswith('.exe'):
            assert b[:2]==b'MZ';pos=struct.unpack_from('<I',b,0x3c)[0]
            assert b[pos:pos+4]==b'PE\0\0' and struct.unpack_from('<H',b,pos+4)[0]==0x8664
        else: assert b==(base/name).read_bytes()
    build=json.loads(z.read('BUILD.json'))
    guide=z.read('README.txt').decode()
for name,key in [('digital-tape.exe','app_sha256'),('ingest.exe','ingest_sha256'),('tapectl.exe','tapectl_sha256'),('BUILD.json','build_sha256')]:
    assert inventory[name]['sha256']==m[key]
for key in ['source_head','source_tree','frontend_disposition','bridge_disposition']:
    assert build[key]==m[key]
assert git('rev-parse',m['source_head']+'^{tree}').decode().strip()==m['source_tree']
for path,want in [('host/app','4e282664107e2635b72dec8801b76e06660fb892'),('tools/app','cb842620ba709429ebfa284f1407b2c59a5d7c8a')]:
    assert git('rev-parse',m['source_head']+':'+path).decode().strip()==want
assert git('diff','--name-only','4611a0803017da5a79deaa35ae95e7b3692c64fe',m['source_head'])==b''
assert build['run_id']==40141860952 and build['run_attempt']==1
assert build['frontend_disposition']==build['bridge_disposition']=='fad2eac7b5aa375a788c8e3ce0a3f7c83374be6f'
evidence=(root/'candidate564-build-evidence.zip').read_bytes()
assert sha(evidence)=='ecdadecf851a49760b9a9c0f2076b5d497d865af9891d87abe6d830f97c0249d'
with zipfile.ZipFile(io.BytesIO(evidence)) as z:
    for name in ['facts.json','INVENTORY.json']: assert z.read(name)==(base/name).read_bytes()
    assert b'Finished `release`' in z.read('app-build.stderr.txt')
    assert z.read('app-build.stdout.txt')==b''
    for line in z.read('host-app-tree.txt').decode('utf-8-sig').splitlines():
        mode,kind,blob,path=line.split();assert kind=='blob'
        assert git('rev-parse',m['source_head']+':'+path).decode().strip()==blob
data=claude.prepared(m,sha(mbytes))
result=dict(source=m['source_head'],source_tree=m['source_tree'],manifest_sha256=sha(mbytes),archive_sha256=sha(archive),artifact_sha256=sha(outer),members=inventory,
            prepared_files={n:sha(b) for n,b in data.items()},python=claude.PYTHON,python_sha256=claude.PYTHON_SHA,tool_route=claude.ROUTE,
            build_and_archive='PASS exact offered run only; no reproducible compilation claim',runtime='UNEXECUTED; admission and exact granted tool decision remain separate',product_execution=False)
(root/'RESULT564.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS exact candidate source/CI artifact/archive/BUILD/member/PE/manifest and Claude method binding; ZERO Product execution')
