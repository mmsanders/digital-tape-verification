"""Offline original archive and source-flow checks. NEVER import/execute kit."""
import argparse,ast,hashlib,importlib.util,io,json,ntpath,pathlib,urllib.request,zipfile
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
SHA=lambda b:hashlib.sha256(b).hexdigest()
BLOB=lambda b:hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
HEAD='6eeaa84996aad392ed3323ddc8db752e7951bdae'
URL='https://raw.githubusercontent.com/mmsanders/Digital-Tape/'+HEAD+'/'
def fetch(url):
 with urllib.request.urlopen(url,timeout=45) as f:return f.read()
def main():
 p=argparse.ArgumentParser();p.add_argument('--archive',type=pathlib.Path);p.add_argument('--offline',type=pathlib.Path);p.add_argument('--out',type=pathlib.Path,required=True);a=p.parse_args()
 pins=json.loads((HERE/'INPUTS.json').read_text(encoding='utf-8'));blobs={x['path']:x['blob'] for x in pins['changed_files']}
 b=a.archive.read_bytes() if a.archive else fetch(URL+'docs/REVIEW/software515/software515-preparation-return.zip')
 assert len(b)==134295 and SHA(b)==pins['archive_sha256'] and BLOB(b)==pins['archive_blob']
 with zipfile.ZipFile(io.BytesIO(b)) as z:
  names=z.namelist();assert len(names)==42 and len(set(names))==42
  assert all(not n.startswith('/') and '..' not in pathlib.PurePosixPath(n).parts and '\\' not in n and ':' not in n for n in names)
  f={n:z.read(n) for n in names}
 j=lambda n:json.loads(f[n]);inv=j('FILES.json');assert set(inv)==set(f)-{'FILES.json'}
 for n,v in inv.items():assert len(f[n])==v['bytes'] and SHA(f[n])==v['sha256']
 source={}
 for n in ['probe.py','prepare.py','NOT_AUTHORIZED_TO_RUN.txt']:
  raw=(a.offline/'256-return'/n).read_bytes() if a.offline else fetch(URL+'host/observer-kit/'+n)
  assert BLOB(raw)==blobs['host/observer-kit/'+n];source[n]=raw
 assert source['probe.py']==f['probe.py']
 assert source['NOT_AUTHORIZED_TO_RUN.txt'].decode().splitlines()==f['NOT_AUTHORIZED_TO_RUN.txt'].decode().splitlines()
 launch=j('LAUNCH.json');dry=j('DRY-RUN.json');raw_dry=j('dry-stdout.bin');assert dry==raw_dry and f['dry-stderr.bin']==b''
 assert launch['source']==pins['tested_payload'] and launch['exit']==0
 assert launch['duration_ns']==launch['end_ns']-launch['start_ns']==532000000 and launch['parent_cpu_ns']==31250000
 assert dry['pid']==launch['pid']==24672 and dry['parent_pid']==launch['parent_pid']==15376 and dry['nonce']==launch['argv'][-1]
 assert ntpath.normcase(ntpath.normpath(launch['argv'][0]))==ntpath.normcase(ntpath.normpath(dry['image'])) and ntpath.basename(dry['image'])=='probe-235.exe'
 assert dry['image_sha256']==launch['image_sha256']==SHA(f['probe-235.exe'])=='b07b03b9ba866a341a3c13ee69710fbc8d43d4ce2523dee13f6df5c25378d15b'
 assert len(f['probe-235.exe'])==107304 and f['probe-235.exe'][:2]==b'MZ'
 assert dry['source_sha256']==SHA(f['probe.py']) and dry['pointer_bits']==64 and not dry['ctypes_imported']
 assert dry['native_target_calls']==dry['token_probes']==dry['capture_launches']==0
 assert '--dry-run' in launch['argv'] and '--future-execute' not in launch['argv']
 post=j('POSTPROCESS.json');assert post['child_attempts']==1 and not post['original_raw_overwritten'] and not post['native_future_entry_executed']
 method=ROOT/'tests/observer_kit_readiness_r1';mb={x['name']:(method/x['name']).read_bytes() for x in pins['import_files']};assert len(mb)==5
 for x in pins['import_files']:assert len(mb[x['name']])==x['size'] and BLOB(mb[x['name']])==x['sha']
 tree=b''.join(b'100644 '+n.encode()+b'\0'+bytes.fromhex(BLOB(mb[n])) for n in sorted(mb));assert hashlib.sha1(b'tree '+str(len(tree)).encode()+b'\0'+tree).hexdigest()==pins['method_tree']
 s=importlib.util.spec_from_file_location('independent256',method/'oracle.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 assert m.check(j('SYNTHETIC.json'))=='SYNTHETIC_READINESS_CONTROLS_ONLY'
 controls=j('CONTROLS.json');assert len(controls['rejected'])==28
 for i,c in enumerate(controls['rejected']):
  assert c['rejected'] is True and c['recipe']==f'negative-{i:02d}.json'
  try:m.check(j(c['recipe']))
  except AssertionError:pass
  else:raise AssertionError('retained synthetic mutation admitted')
 # Static inspection only. This AST is NEVER compiled or executed.
 text=source['probe.py'].decode();tree_ast=ast.parse(text)
 top_imports=[n for n in tree_ast.body if isinstance(n,(ast.Import,ast.ImportFrom))]
 assert all('ctypes' not in ast.unparse(n) for n in top_imports)
 future=next(n for n in tree_ast.body if isinstance(n,ast.FunctionDef) and n.name=='future_native_payload')
 calls=[n for n in ast.walk(future) if isinstance(n,ast.Call)]
 assert sum(ast.unparse(n.func)=='kernel.QueryDosDeviceW' for n in calls)==1
 assert not any(ast.unparse(n.func) in ('print','emit','write') for n in calls)
 trial=next(n for n in future.body if isinstance(n,ast.Try) and any('after = clocks()' in ast.unparse(x) for x in n.body))
 assert not trial.handlers and trial.finalbody
 plan=source['NOT_AUTHORIZED_TO_RUN.txt'].decode()
 capture=plan.index('/BackingFile');child=plan.index('--case-request "$Session\\absent-dos-zero.json"')
 assert capture<child and '--future-execute' in plan
 assert plan.count('--future-execute')==6
 original=(ROOT/'tests/wp16_observer_visibility_r1/README.md').read_text(encoding='utf-8')
 assert 'Before capture, QueryDosDeviceW' in original.replace('\n',' ')
 result=dict(candidate=HEAD,archive_sha256=pins['archive_sha256'],original_members=42,inventory_entries=41,ordinary_dry_run_processes=1,actual_native_cases=0,token_reprobes=0,capture_launches=0,actual_image='probe-235.exe',image_sha256=dry['image_sha256'],synthetic_mutations_rejected=28,corrected_offline_path_comparison=True,original_raw_preserved=True,readiness='HELD_CORRECTION1_OF2',findings=['E1 exact-name absence query is inside last future child after capture starts; carried236 requires before capture','E2 post-CreateFile clock failure closes handle but unwinds before emitting native return/error/absence facts'],scope='source/offline preparation only; no native or helper execution by Verification')
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n');print(json.dumps(result,sort_keys=True))
if __name__=='__main__':main()
