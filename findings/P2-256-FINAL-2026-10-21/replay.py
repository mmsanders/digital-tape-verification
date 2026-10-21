"""Authenticate changed preparation source/receipts as data; NEVER import the kit."""
import argparse,ast,hashlib,io,json,urllib.request,zipfile
from pathlib import Path
HEAD='26f99c20c34827bc4b6744683682b59d40968e04'
URL='https://raw.githubusercontent.com/mmsanders/Digital-Tape/'+HEAD+'/docs/REVIEW/software515/correction1/software515-correction1-final.zip'
def sha(b):return hashlib.sha256(b).hexdigest()
def gitblob(b):return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def query_ok(r,s):
 i=r['identity'];n=r['native']
 return (r['status']=='complete' and i['operation']=='absence-query' and i['nonce']==s['nonce'] and i['session_instance']==s['session_instance'] and i['source_sha256']==s['payload_source_sha256'] and i['image_sha256']==s['probe_image_sha256'] and n['name']=='DTVerify235_'+s['nonce'] and n['buffer_wchars']==4096 and n['returned']==0 and n['immediate_error']==2 and s['session_start_qpc']<=r['before']['qpc']<=r['after']['qpc']<s['capture_start_qpc'] and i['qpc_frequency']==s['qpc_frequency'] and i['qpc_frequency']>0)
def main():
 p=argparse.ArgumentParser();p.add_argument('--archive',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args();raw=a.archive.read_bytes() if a.archive else urllib.request.urlopen(URL).read()
 assert len(raw)==286003 and sha(raw)=='3656c4495c5ffe15aeb22962e7d8f0936cffc6e5c090a09a24e38ef912667b00' and gitblob(raw)=='c1e3d43a79f2139b50315a2b9600dda201177d70'
 z=zipfile.ZipFile(io.BytesIO(raw));ns=z.namelist();assert len(ns)==len(set(ns))==9
 assert all(not n.startswith('/') and '..' not in Path(n).parts and '\\' not in n for n in ns)
 f={n:z.read(n) for n in ns};j=lambda n:json.loads(f[n]);inv=j('PACKAGE-FILES.json');assert set(inv)==set(f)-{'PACKAGE-FILES.json'}
 for n,v in inv.items():assert len(f[n])==v['bytes'] and sha(f[n])==v['sha256']
 assert len(f['original/software515-preparation-return.zip'])==134295 and sha(f['original/software515-preparation-return.zip'])=='85a6f19ddb3be91374bb00e700e5786d450edf7911d9c869360cfa3ea8629ede'
 assert sha(f['prior/software515-correction1-pre-canonicalization.zip'])=='987533e621528af5aa4a153afb29bf670bf03e22e882a03645a2ffea3b4d6c79'
 assert gitblob(f['source/probe.py'])=='b2878c32643b0141e214fe377010562fdf4aad04'
 assert gitblob(f['source/correction_controls.py'])=='f8ea6865b2dc0b8c19a0d59d6acd4b709b969d58'
 assert gitblob(f['source/NOT_AUTHORIZED_TO_RUN.txt'])=='916ee12e0cc7243dd286ec1aed1ffd0e4aed02ba'
 correction=j('CORRECTION.json');controls=j('final-controls/CONTROLS.json');ci=j('final-controls/FILES.json')['CONTROLS.json'];assert len(f['final-controls/CONTROLS.json'])==ci['bytes'] and sha(f['final-controls/CONTROLS.json'])==ci['sha256']
 assert controls['source_sha256']==sha(f['source/probe.py'])==correction['final_sources']['source/probe.py']
 assert controls['control_source_sha256']==sha(f['source/correction_controls.py'])
 for k in ('native_calls','query_calls','token_probes','capture_launches','child_launches'):assert controls[k]==0
 assert controls['ctypes_imported'] is False
 rows=controls['retention_controls'];assert len(rows)==6
 for row in rows:
  assert row['synthetic'] is True and row['counts']['operation']==1 and row['counts']['close']==int(row['valid'])
  events=row['events'];first=events[0];assert first['kind']=='native-original' and first['native']==row['result']['native'] and first['identity']['synthetic'] is True
  assert first['native']['valid_owned_handle']==row['valid']
  assert events[-1]['kind']=='completion' and events[-1]['status']==row['result']['status']
  expected='incomplete' if row['clock_failure'] or row['close_failure'] else 'complete';assert row['result']['status']==expected
  if row['clock_failure']:assert any(e['kind']=='incomplete-clock' for e in events)
  if row['close_failure']=='raise':assert any(e['kind']=='incomplete-close' for e in events)
  if row['close_failure']=='return':assert any(e['kind']=='close-original' and e['fact']['success'] is False for e in events)
 assert query_ok(controls['query_positive'],controls['query_session'])
 mutants=controls['rehashed_query_rejections'];assert len(mutants)==10
 for m in mutants:assert m['synthetic'] is True and m['rejected'] is True and not query_ok(m['rehashed_receipt'],controls['query_session'])
 # Static AST inspection only. No compile/import/exec, FFI or child launch.
 source=f['source/probe.py'].decode();tree=ast.parse(source);funcs={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
 retain=ast.get_source_segment(source,funcs['retain_call']);assert retain.index('native=operation()')<retain.index("sink(dict(kind='native-original'")<retain.index("result['after']=clocks()")<retain.index('finally:')
 assert retain.count("close(native['handle_raw'])")==1 and "if native.get('valid_owned_handle') is True:" in retain
 future=ast.get_source_segment(source,funcs['future_native_payload']);assert future.count('kernel.QueryDosDeviceW(name,buffer,4096)')==1
 assert 'if query_only:' in future and future.index('if not query_only:')<future.index('validate_query_receipt(')
 assert future.index('error=ctypes.get_last_error() if count==0 else None')>future.index('kernel.QueryDosDeviceW(name,buffer,4096)')
 assert future.index('error=ctypes.get_last_error() if raw==invalid else None')>future.index('handle=kernel.CreateFileW(')
 assert "with Path(facts_path).open('x'" in future and 'result=retain_call(operation,clocks,close,sink,identity)' in future
 # FFI import is lexically confined to the dormant native function.
 for n in tree.body:
  if isinstance(n,(ast.Import,ast.ImportFrom)):assert not any(x.name=='ctypes' for x in n.names)
 plan=f['source/NOT_AUTHORIZED_TO_RUN.txt'].decode();commands=[x for x in plan.splitlines() if x.startswith('& ')]
 query=[x for x in commands if '--future-query ' in x];cases=[x for x in commands if '--future-execute ' in x];assert len(query)==1 and len(cases)==6
 assert plan.index(query[0])<plan.index('& "$Observer" /AcceptEula')<plan.index(cases[0])
 assert all('--query-receipt "$Session\\absence-query.json"' in x for x in cases)
 assert 'NOT AUTHORIZED TO RUN' in plan and 'already-available authorized Administrator' in plan and 'fresh explicit user/scope authorization' in plan
 result=dict(verdict='READY-FOR-SEPARATE-AUTHORIZATION: conditional preparation kit only',candidate=HEAD,package_bytes=286003,closed_members=9,source_sha256=sha(f['source/probe.py']),original_package_preserved=True,original_image_receipt_scope='417652fb only; corrected source STATIC/SYNTHETIC ONLY',synthetic_retention_paths=6,rehashed_query_rejections=10,future_queries_before_capture=1,future_target_cases=6,independent_native_calls=0,independent_kit_imports=0,actual_native_cases='6 UNEXECUTED/UNQUALIFIED',authority='No collection, native absence, observer capability, integration or human task. Existing235/491 privilege stop absolute; future actual runner/session/filesystem/time ownership needs separate exact scope and already-authorized Administrator context.')
 a.out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result))
if __name__=='__main__':main()
