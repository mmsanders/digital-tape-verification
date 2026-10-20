"""Independent authenticated replay of Software485 raw receipts; never runs a child."""
import argparse, hashlib, importlib.util, json, sys, urllib.request, zipfile
from pathlib import Path, PureWindowsPath

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
URL='https://github.com/mmsanders/Digital-Tape/releases/download/evidence-software485-2026-10-20/software485-exact-shipping-return.zip'
ARCHIVE_SHA='36c12a30ab735628b248395b9e492daee638db6bc1332a2f5c00be3c6f8e2118'
ARCHIVE_SIZE=5721822
BINARY='d923613badda95baeb387d5415d5212a5dedb7c5c7144b21874479babd178f5b'
SOURCE='d36663d1e4f05abaac699a6c14e0fa86724db9b4decdb8c96abe0c9d1f645821'
KIT='ffb0f78ac3980fa1bb130f0aff22d53ebb100ed3323a8e50ba62a6ee1819c865'

def sha(b): return hashlib.sha256(b).hexdigest()
def blob(b): return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def check_inventory(data, inventory):
 assert set(data)==set(inventory), 'complete inventory'
 for n,f in inventory.items():
  assert len(data[n])==f['bytes'] and sha(data[n])==f['sha256'], 'raw identity: '+n

def replay(path):
 raw=path.read_bytes(); assert len(raw)==ARCHIVE_SIZE and sha(raw)==ARCHIVE_SHA, 'original archive identity'
 with zipfile.ZipFile(path) as z:
  assert len(z.namelist())==len(set(z.namelist())), 'duplicate member'
  assert sum(i.file_size for i in z.infolist())<64*1024*1024, 'bounded archive'
  data={n:z.read(n) for n in z.namelist()}
 inv=json.loads(data['INVENTORY.json']); check_inventory({n:b for n,b in data.items() if n!='INVENTORY.json'},inv)
 authority=json.loads((HERE/'AUTHORITY.json').read_text())
 imported=json.loads(data['IMPORT.json']); assert imported['method_commit']=='6c0c4835be336b28313cad0f06f6ab1509d99489'
 assert imported['judge_commit']=='4a1a09a0e618bba4685312da8721275e9b2ce9c3' and imported['judge_tree']=='e8f4a02ef8b831cd31fbe26807d59e08ac2d46b8'
 expected={f['path']:f['sha'] for f in authority['method']}
 expected.update({'tests/wp16_shipping_exhaustion_r1/'+f['path']:f['sha'] for f in authority['judge']['tree']})
 assert set(f['path'] for f in imported['files'])==set(expected)
 producer={f['filename']:f['sha'] for f in authority['producer_files']}
 first_import={f['path']:f['sha'] for f in authority['import_method']+authority['import_judge']}
 assert authority['head_commit']['parents']==['c75653be55fe15be80e6d0be551a67d402b3ea6a']
 for f in imported['files']:
  n='method/'+f['path']; b=data[n]
  assert len(b)==f['bytes'] and sha(b)==f['sha256'] and blob(b)==expected[f['path']], 'verbatim independent import'
  assert producer['docs/REVIEW/software485/'+n]==blob(b), 'returned Product import identity'
  assert first_import['docs/REVIEW/software485/'+n]==blob(b), 'prior import commit identity'
 assert blob(data['SOURCE-ARGUMENT.md'])==producer['docs/REVIEW/software485/SOURCE-ARGUMENT.md']
 # Producer JSON metadata was committed with LF after Windows CRLF writing.
 # Authenticate original raw bytes above; normalize ONLY this index's newlines
 # to compare its Git publication. No child stream/output/source is normalized.
 assert blob(data['SOURCE-INDEX.json'].replace(b'\r\n',b'\n'))==producer['docs/REVIEW/software485/SOURCE-INDEX.json']
 index=json.loads(data['SOURCE-INDEX.json']); assert index['candidate']=='b9f430c8c9b33532abf07eea0ed2653310639f2d'
 tree=authority['s1tree']; assert tree['sha']==index['ingest_tree']=='835078995d4e9cc2424f9ea8d6f11304b45f783f' and not tree['truncated']
 actual={'host/ingest/'+f['path']:f for f in tree['tree'] if f['type']=='blob'}
 selected={n for n in actual if n.startswith('host/ingest/src/') or n.startswith('host/ingest/vendor/') or n in ['host/ingest/Cargo.toml','host/ingest/Cargo.lock','host/ingest/rust-toolchain.toml']}
 indexed={f['path']:f for f in index['files']}
 assert set(indexed)==selected|{'docs/WP16-INGEST-CONTRACT.md'}
 for n in selected: assert actual[n]['sha']==indexed[n]['blob'] and actual[n]['size']==indexed[n]['bytes'], 'source Git identity'
 assert sha(data['inputs/ingest.exe'])==BINARY and sha(data['inputs/ordinary.wav'])==SOURCE
 assert sha(data['inputs/approved-kit.zip'])==KIT
 import io
 with zipfile.ZipFile(io.BytesIO(data['inputs/approved-kit.zip'])) as kit:
  assert kit.namelist().count('ingest.exe')==1 and sha(kit.read('ingest.exe'))==BINARY
 prefix='candidate-result/'
 files=json.loads(data[prefix+'FILES.json'])
 check_inventory({n[len(prefix):]:b for n,b in data.items() if n.startswith(prefix) and n!=prefix+'FILES.json'},files)
 assert sha(data[prefix+'f0/ordinary.wav'])==SOURCE
 assert data[prefix+'output/foreign']==b'FOREIGN SENTINEL - DO NOT MODIFY\n'
 bind=json.loads(data[prefix+'BINDING.json']); assert bind['identity']['binary_sha256']==BINARY and bind['identity']['source_sha256']==SOURCE and bind['identity']['kit_sha256']==KIT
 assert bind['identity']['kit_member']=='ingest.exe'
 for n,h in bind['identity']['dependencies'].items(): assert sha(data['method/tests/wp16_shipping_exhaustion_r1/'+n])==h
 assert bind['adapter_sha256']==sha(data['method/findings/P2-232-METHOD-2026-10-20/external.py'])
 judge_path=ROOT/'tests/wp16_shipping_exhaustion_r1/runner.py'
 assert judge_path.read_bytes()==data['method/tests/wp16_shipping_exhaustion_r1/runner.py']
 spec=importlib.util.spec_from_file_location('judge232',judge_path); judge=importlib.util.module_from_spec(spec); spec.loader.exec_module(judge)
 result=json.loads(data[prefix+'RESULT.json']); rows=result['rows']
 assert result['binary_sha256']==BINARY and result['source_sha256']==SOURCE and result['platform']=='win32' and result['mode']=='candidate'
 assert [r['limit_mib'] for r in rows]==[None,3,4,6,8,12,64]
 positive=rows[0]['pair']; summary=[]
 binary_arg=rows[0]['load']['argv'][0]; case_args=rows[0]['case']['argv']
 assert PureWindowsPath(binary_arg).name=='ingest.exe'
 assert case_args[0]==binary_arg and case_args[1]=='--out' and case_args[3:5]==['--length','60'] and PureWindowsPath(case_args[2]).name=='DEST' and PureWindowsPath(case_args[5]).name=='f0'
 expected_files={'BINDING.json','RESULT.json','f0/ordinary.wav','output/foreign'}
 for i,row in enumerate(rows):
  for kind in ['load','case']:
   r=row[kind]; assert r['limit_mib']==row['limit_mib'] and r['method']=='Windows Job PROCESS_MEMORY, suspended assignment'
   assert r['exit_hex']==f"0x{r['exit']:08X}" and not r['timed_out']
   assert r['argv']==([binary_arg,'--version'] if kind=='load' else case_args)
   for stream in ['stdout','stderr']:
    n=f'row-{i}/{kind}.{stream}'; b=data[prefix+n]; expected_files.add(n)
    assert sha(b)==r[stream+'_sha256'] and b.decode()==r[stream], 'actual child raw stream'
  pair=None
  if row['case']['exit']==0:
   pair={n:sha(data[prefix+f'row-{i}/published-DEST/'+n]) for n in ['audio.wav','manifest.json']}
   expected_files.update(f'row-{i}/published-DEST/'+n for n in pair)
  assert row['pair']==pair and row['dest_exists']==(pair is not None)
  violations=judge.judge(row,positive); assert not violations and row['violations']==violations
  summary.append(dict(limit_mib=row['limit_mib'],load_exit=row['load']['exit'],case_exit=row['case']['exit'],pair=pair,violations=violations))
 assert set(files)==expected_files, 'no retained unexpected stage/output files'
 assert rows[0]['case']['exit']==0 and positive and sum(r['case']['exit']==1 for r in rows)==3
 baseline=json.loads(data['BASELINE-ACCESS.json']); assert baseline['actual_baseline_executed'] is False
 execution=json.loads(data['EXECUTION.json']); assert execution['exit']==0 and execution['producer_import_commit']=='c75653b'
 assert execution['cpu_upper_bound_seconds']<7200 and execution['logical_processors']==16
 return dict(archive_sha256=ARCHIVE_SHA,archive_bytes=len(raw),archive_members=len(data),inventory_files=len(inv),verbatim_import_files=len(imported['files']),source_index_files=len(indexed),raw_result_files=len(files),binary_sha256=BINARY,source_sha256=SOURCE,kit_sha256=KIT,host=bind['host'],rows=summary,successful_pair=positive,judgment='PASS for this exact executable/recorded Windows11 Client/input/seven caps',fresh_original_red='UNAVAILABLE; prior published RED carried only',internal='global UNPROVED; source-conditional arguments only',joined_peak='global UNPROVED; no actual new ID witness',source_argument_sha256=sha(data['SOURCE-ARGUMENT.md']),new_executable_runs=0)

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--archive',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--fetch',action='store_true');a=p.parse_args()
 if a.fetch:
  a.archive.parent.mkdir(parents=True,exist_ok=True)
  with urllib.request.urlopen(URL,timeout=60) as q: a.archive.write_bytes(q.read(ARCHIVE_SIZE+1))
 output=replay(a.archive)
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(output,indent=2)+'\n')
 print(json.dumps(output,indent=2))
