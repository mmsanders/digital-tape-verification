"""Verification325 source/archive/build audit. No producer, executable or build runs."""
import ast,copy,hashlib,importlib.util,io,json,struct,subprocess,sys,zipfile
from pathlib import Path
import argparse
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--data', type=Path, required=True)
parser.add_argument('--verification-git', type=Path, required=True)
parser.add_argument('--product-git', type=Path, required=True)
args=parser.parse_args()
p=args.data; v=args.verification_git; prod=args.product_git
head='3bd470aeb059668733c5d0f91ea6f71d16e594d8';source='1731f6ecef2d6cb72a228f2c88c297cf4b59553f'
def sha(b):return hashlib.sha256(b).hexdigest()
def git(root,*args):return subprocess.check_output(['git','-C',str(root),*args])
def obj(ref,path):return git(prod,'show',ref+':'+path)
def rev(s):return git(prod,'rev-parse',s).decode().strip()
def js(path):return json.loads(path.read_text(encoding='utf-8-sig'))
assert rev(source)==source and rev(head)==head
packages={'windows_discovery_candidate_r2':('4e65c51879cb4a305f3be2fef79e98f8045fb64c','7731e29a5f6081140f013a8eb622fbae491d7c2f'),'windows_discovery_candidate_r1':('c3925a405d992fa02deaf9694d439286eeb75197','38c20dea'),'windows_preview_r1':('25282007045b95577d7a8385c2825c2f6de1f74e','ca844497')}
imp=rev('d9b27ab9');assert rev(imp+'^')==source and rev('346c07cd^')==imp and rev(head+'^')==rev('346c07cd')
for name,(tree,pub) in packages.items():
    assert rev(imp+':tests/'+name)==rev(head+':tests/'+name)==tree
    pubfull=git(v,'rev-parse',pub).decode().strip();subprocess.run(['git','-C',str(v),'merge-base','--is-ancestor',pubfull,'fcad6b0cba06478a54294ea7298e7d3dc0da5819'],check=True)
    assert git(v,'rev-parse',pubfull+':tests/'+name).decode().strip()==tree
allowed={'.github/workflows/windows-candidate-585.yml','tools/app/package_candidate.py','tests/IMPORTS.json'}
paths=git(prod,'diff','--name-only',source,head).decode().splitlines();assert all(x in allowed or any(x.startswith('tests/'+n+'/') for n in packages) for x in paths)
assert set(git(prod,'diff','--name-only',imp,'346c07cd').decode().splitlines())=={'.github/workflows/windows-candidate-585.yml','tools/app/package_candidate.py'}
assert git(prod,'diff','--name-only','346c07cd',head).decode().splitlines()==['.github/workflows/windows-candidate-585.yml']
# Original564 builder is unchanged; old write() defaults remain the original archive name.
old=ast.parse(obj(source,'tools/app/package_candidate.py'));new=ast.parse(obj(head,'tools/app/package_candidate.py'))
def function(module,name):return next(n for n in module.body if isinstance(n,ast.FunctionDef) and n.name==name)
assert ast.dump(function(old,'build'),include_attributes=False)==ast.dump(function(new,'build'),include_attributes=False)
assert not git(prod,'diff','--name-only',source,head,'--','host/app','.github/workflows/windows-candidate.yml')
record=js(p/'evidence-container/RECORD.json');facts=js(p/'evidence-container/facts.json')
for key,path in [('source_tree',''),('host_app_tree','host/app'),('tools_app_tree','tools/app'),('engine_tree','engine')]:
    expected=rev(source+('^{tree}' if not path else ':'+path));assert facts[key]==record[key]==expected
assert facts['source_head']==record['source_head']==source and facts['packager_source']==head and facts['run_id']==40571246452
lock=obj(source,'host/app/Cargo.lock');assert lock==(p/'evidence-container/Cargo.lock').read_bytes()
assert sha(lock)==(p/'evidence-container/Cargo.lock.sha256').read_text(encoding='utf-8-sig').strip()
data=(p/'candidate-container/Digital-Tape-Windows11-x64-discovery-candidate.zip').read_bytes()
assert sha(data)=='3f144cf565e0e195763898a446938c88bace85d9f60dceeb04622efdd3fe6076'
with zipfile.ZipFile(io.BytesIO(data)) as z:
    files={n:z.read(n) for n in z.namelist()};build=json.loads(files['BUILD.json']);members={n:dict(bytes=len(b),sha256=sha(b)) for n,b in files.items()}
assert len(files)==5 and set(files)=={'digital-tape.exe','ingest.exe','tapectl.exe','BUILD.json','README.txt'}
assert build['run_id']==40571246452 and build['packager_source']==head
inventory=js(p/'candidate-container/INVENTORY.json');assert inventory['archive']['sha256']==sha(data) and inventory['archive']['bytes']==len(data)
assert {x['name']:{'bytes':x['bytes'],'sha256':x['sha256']} for x in inventory['members']}==members
assert (p/'candidate-container/MANUAL-TEST-SHEET.txt').read_text()==record['manual_sheet']
assert files['BUILD.json']==(p/'evidence-container/BUILD.json').read_bytes() and files['README.txt']==(p/'evidence-container/README.txt').read_bytes()
assert sha(files['ingest.exe'])=='3895f3f356c91b8a9fe870c33694da64bf2765df308bef118d657c1be4bb9a20'
assert sha(files['tapectl.exe'])=='44ef26869ba2d01a8a183660a2c7a050d0e7e9ff37c40b727131512739ea6ded'
ib=(p/'ingest-transport.zip').read_bytes();tb=(p/'tapectl-transport.zip').read_bytes()
assert sha(ib)=='a19c47d7d474414cfb0c8cf992fd6e984bf9ff160c5e38efdd7e09a45b12aa94' and sha(tb)=='83fa0d72d76948615613c388187a114d9fd03107b85d7842f37ead558f0f3b9b'
with zipfile.ZipFile(io.BytesIO(ib)) as z:nested=z.read('Digital-Tape-Windows11-x64-candidate.zip')
assert sha(nested)=='a4b11f750fb7e3d9fd77a0e6dc1009683496ef6881791c1947a03970310b190b'
with zipfile.ZipFile(io.BytesIO(nested)) as z:assert z.read('ingest.exe')==files['ingest.exe']
with zipfile.ZipFile(io.BytesIO(tb)) as z:assert z.read('tapectl.exe')==files['tapectl.exe']
pins=js(p/'evidence-container/compile-env.json');assert pins==record['compile_env']==build['compile_pins']
for value in pins.values():assert value.encode('ascii') in files['digital-tape.exe']
app=files['digital-tape.exe'];assert app[:2]==b'MZ';pe=struct.unpack_from('<I',app,0x3c)[0];assert app[pe:pe+4]==b'PE\0\0'
assert struct.unpack_from('<H',app,pe+4)[0]==0x8664 and struct.unpack_from('<H',app,pe+24)[0]==0x20b and struct.unpack_from('<H',app,pe+24+68)[0]==2
assert struct.unpack_from('<II',app,pe+24+112+4*8)==(0,0) # no embedded certificate; not runtime readiness
# Measured independent registry: restrict claims to retained direct checks of the exact INGEST.
registry=dict(authority='Verification325 measured archive-byte registry; no native/build-count-exception acceptance',components={
 'digital-tape.exe':dict(**members['digital-tape.exe'],source=source,publication='fcad6b0cba06478a54294ea7298e7d3dc0da5819',scope='covered integrated source; new binary BUILD/ARCHIVE bytes only'),
 'ingest.exe':dict(**members['ingest.exe'],source='35b23cacae886d9b3693b7104f581d8646ea5667',publication='81033e2a20b4fed377fdbbb82963693b10c9b79b',scope='exact retained DIRECT P0/P1 only'),
 'tapectl.exe':dict(**members['tapectl.exe'],source='f9306c2c5a42ebd039edd67b0b7cef6a7d434b2b',publication='fdffea5759c2cf48b37a6960c5ed36d09ab91b98',scope='accepted S2 source/child identity only; no new poller execution')},allowed_claims=['direct ingest positive','direct ingest empty-folder refusal'],required_exclusions=['actual UI','app-driven child','fullAPP','fullINGEST','CLI A6','native session','shipping Make','G2'])
oracle=p/'oracle'
for name,fn in [('windows_discovery_candidate_r2','contract.py'),('windows_discovery_candidate_r1','contract.py'),('windows_preview_r1','archive.py')]:
    d=oracle/name;d.mkdir(parents=True,exist_ok=True);(d/fn).write_bytes(git(v,'show','fcad6b0cba06478a54294ea7298e7d3dc0da5819:tests/'+name+'/'+fn))
spec=importlib.util.spec_from_file_location('r2',oracle/'windows_discovery_candidate_r2/contract.py');r2=importlib.util.module_from_spec(spec);spec.loader.exec_module(r2)
positive=r2.check(data,registry,record)
bad=copy.deepcopy(registry);bad['components']['tapectl.exe']['sha256']='82798af2899e9364b9c9bfaa2021daf6cc51ccd0c6562598d50e0a86944bb7a9'
try:r2.check(data,bad,record)
except AssertionError as e:assert str(e)=='tapectl.exe'
else:raise AssertionError('mismatch control survived')
checked=copy.deepcopy(record);checked['final_build_count']=2
assert r2.prior.check(data,registry,checked)
try:r2.check(data,registry,checked)
except AssertionError:pass
else:raise AssertionError('actual repeat build not caught')
failed=js(p/'failed-evidence-container/INVENTORY.json');assert failed['members'][2]['name']=='digital-tape.exe'
assert failed['members'][2]['sha256']!=members['digital-tape.exe']['sha256']
out=dict(source=source,head=head,import_commit=imp,source_trees={k:record[k] for k in ['source_tree','host_app_tree','tools_app_tree','engine_tree']},package_trees={n:t[0] for n,t in packages.items()},members=members,archive_sha256=sha(data),archive_bytes=len(data),lock_sha256=sha(lock),compiled_pins=pins,transports=dict(ingest=sha(ib),tapectl=sha(tb)),producer_record_sha256=sha((p/'evidence-container/RECORD.json').read_bytes()),measured_judgments=dict(r1='PASS archive/source/pin/readiness metadata',r2_producer_count1='PASS mechanically, does not authenticate the count',pin_mismatch='REJECT tapectl.exe',actual_compilations=2,uploaded_candidate_artifacts=1,r2_truthful_count2='REJECT final_build_count==1 as intended'),process_disclosure=dict(first_run=40570284830,first_app_sha256=failed['members'][2]['sha256'],final_run=40571246452,workflow_only_fix='explicit exit0 after checking expected negative',new_build_requested=False),overall='HELD: one-final-build scope exceeded; PM disposition required; normal pending CI retained; no rebuild requested')
for name,value in [('AUDIT.json',out),('REGISTRY.json',registry),('CHECKED_RECORD.json',checked)]: (p/name).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
print(json.dumps(out,indent=2))
