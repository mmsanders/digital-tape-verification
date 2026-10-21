"""Retained failure evidence only: no native process, model or fault invocation."""
import argparse,gzip,hashlib,importlib.util,io,json,urllib.request,zipfile
from pathlib import Path
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--archive',type=Path);p.add_argument('--root',type=Path,default=Path('.'));p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 raw=a.archive.read_bytes() if a.archive else urllib.request.urlopen('https://github.com/mmsanders/Digital-Tape/releases/download/evidence-software514-2026-10-21/software514-positive-stop-return.zip').read()
 assert len(raw)==1014923 and sha(raw)=='78fed87f002b8c76fbaf05481087454245c7320ffffa6d3adf4089fefb5654e8'
 z=zipfile.ZipFile(io.BytesIO(raw));ns=z.namelist();assert len(ns)==len(set(ns))==134
 assert all(not n.startswith('/') and '..' not in Path(n).parts and '\\' not in n for n in ns)
 f={n:z.read(n) for n in ns};j=lambda n:json.loads(f[n]);inv=j('RETENTION-FILES.json');assert set(inv)==set(f)-{'RETENTION-FILES.json'}
 for n,v in inv.items():assert len(f[n])==v['bytes'] and sha(f[n])==v['sha256']
 b=f['RETENTION-FILES.json'];assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()=='e832a585622b966735408367725f3808ff8dd12d'
 sp=importlib.util.spec_from_file_location('independent252',a.root/'tests/evidence_recorder_r1/oracle.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 commands=[]
 for i in range(5):
  idx=f'{i:05d}';name='command-'+idx;prefix='raw/recorder/cases/'+name+'/';case={n[len(prefix):]:b for n,b in f.items() if n.startswith(prefix)};req=j('raw/recorder-request-'+idx+'.json')
  assert m.check_complete(case,req)=='COMPLETE_EVIDENCE';assert req['source_commit']=='78a2b27c076f0055aaef2c437a5a99a8c7cd2c70'
  payload=j('raw/request-'+idx+'.json');assert json.loads(case['input.bin'])==payload
  pre='raw/commands/'+idx+'/native/';inventory=j(pre+'MANIFEST.json');assert set(inventory)=={n[len(pre):] for n in f if n.startswith(pre)}-{'MANIFEST.json'}
  for n,v in inventory.items():assert len(f[pre+n])==v['bytes'] and sha(f[pre+n])==v['sha256']
  launch=j(pre+'LAUNCH.json');ex=j(pre+'EXIT.json');process=j('raw/commands/'+idx+'/PROCESS.json');commands.append(process['argv'][1])
  assert ex['code']==process['exit']==0 and not ex['timeout'];assert launch['argv']==payload['argv']==process['proxy_argv']
  assert launch['source']==payload['source']=='55552ad4fe57e99827ab8eb016044d0486017877'
 assert commands==['provision','load','verify','dump','dump']
 assert {n.split('/')[2] for n in f if n.startswith('raw/faults/')}=={'none'}
 plan=json.loads((a.root/'tests/fault_cost_r2/PLAN.json').read_bytes());assert sha(gzip.decompress(f['raw/initial.img.gz']))==plan['initial_sha256'];assert sha(f['raw/source.wav'])==plan['source_wav_sha256'];assert sha(f['raw/original-baseline.jsonl'])==plan['original_complete_trace_sha256']
 pos=j('raw/POSITIVE.json');assert (pos['complete_events'],pos['writes'],pos['barriers'])==(405,353,52)
 rec=j('raw/faults/none/record.json');assert rec['fault_fired'] is None and not rec['failed_events'] and rec['exit']==0
 seam=j('raw/faults/none/seam-trace.json');events=[x for x in seam['events'] if x['kind'] in ('write','flush')];assert len(events)==405
 assert sum(x['kind']=='write' for x in events)==353 and sum(x['kind']=='flush' for x in events)==52
 assert all(x.get('ok',x.get('success')) for x in events)
 assert sha(gzip.decompress(f['raw/faults/none/image-after.img.gz']))==rec['image_after_sha256']
 gates=[j('raw/gates/'+f'{i:05d}.json') for i in range(6)];last=gates[-1]
 assert last['workspace_allocated_bytes']==181616640>144*1024**2 and last['active_row'] is None
 assert last['cpu_including_build_reserve']==601.584185 and all(g['active_row'] is None for g in gates)
 build=j('build-receipts/BUILD-GATE.json');assert build['actual_cpu_seconds']==4.48 and build['actual_allocated_bytes']==10215424
 assert b'AssertionError: build/positive workspace exceeded128+16MiB' in f['build-receipts/driver-stderr.txt']
 driver=Path(__file__).with_name('tested-driver.py.txt').read_bytes();assert hashlib.sha1(b'blob '+str(len(driver)).encode()+b'\0'+driver).hexdigest()=='c7060add342e72a866bded25bcdba9b1d889d9ad'
 text=driver.decode();assert text.index("_,pos=L.run_fault")<text.index("assert allocated(a.out.parent)<=144*1024**2")<text.index("for row in plan['rows']:",text.index("_,pos=L.run_fault"))
 result=dict(verdict='FINAL SCOPED STOP: phase storage overrun / late gate; zero new fault credit',closed_retention_members=134,complete_recorder_calls=5,positive_shape_events=405,new_fault_coordinates=0,accepted_original=41,pending_original=363,unexecuted=[['write',64],['write',346],['write',351],['barrier',50]],last_precommand_allocated_bytes=181616640,combined_phase_reservation=150994944,overrun_bytes=30621696,transport='Hash/Git-bound Software retention envelope; original Actions outer ZIP not independently downloaded',remaining='Final total CPU/allocation and producer final ledger/ZIP absent. Source-only fix unexecuted. No retry or integration; PM owns fresh costed scope.')
 a.out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result))
if __name__=='__main__':main()
