"""New32 actual host faults and one global neighbour; old receipts carry by pins."""
import argparse,copy,gzip,hashlib,importlib.util,json,sys,zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def load(p,n):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
sys.path.insert(0,str(ROOT/'tests/wp10_narrow_supplement_r1'));import oracle
sys.path.insert(0,str(ROOT/'findings/P2-SUBSET-ROWS-2026-10-17'));import load_rows as L
S=load(HERE/'subset.py','subset_tools')
HEAD='55552ad4fe57e99827ab8eb016044d0486017877'
BIN='a8ef69077d933406f25100f81add6f66b25ee90606fc0157de63c7b59244f833'
def sha(b):return hashlib.sha256(b).hexdigest()
def run(root,inputs,out):
 b=json.loads((root/'BUNDLE.json').read_text());plan=S.PLAN
 for n,h in b['files'].items():
  p=(root/n).resolve();assert p.is_relative_to(root.resolve())and p.is_file()and sha(p.read_bytes())==h
 assert len(b['files'])==290
 with zipfile.ZipFile(inputs/'old-return.zip')as z:
  old=json.loads(z.read('BUNDLE.json'))['files'];same=sum(b['files'].get(n)==h for n,h in old.items())
  assert same==80 and set(old).issubset(b['files'])
  # All old raw source/PCM/command inputs carry by exact bytes. gzip headers may differ.
  for n,h in old.items():
   if n.endswith('.img.gz'):assert gzip.decompress(z.read(n))==gzip.decompress((root/n).read_bytes())
  carry=dict(old_files=136,byte_identical=80,changed=56,
             note='workflow DID rerun Tiers1/2; original743f829 acceptance carries, no fresh campaign reacceptance inferred')
 with zipfile.ZipFile(inputs/'load1.zip')as z:
  part='load/part-001-02';rr=[json.loads(l)for l in z.read(part+'/runs.jsonl').splitlines()]
  original={json.loads(l)['projection_sha256']:json.loads(l)for l in z.read(part+'/remounts.jsonl').splitlines()}
  want=plan['global_empty_command'];assert want==json.loads((ROOT/'findings/P2-210-RETURN-2026-10-19/REVIEW.json').read_text())['selection']['global_first_by_state']['empty/empty']
  candidates=[(r,q)for r in rr for q in r.get('projections',[])if q['image_sha256']==want]
  assert candidates and want in original,'the retained remount row DOES exist'
  r,q=candidates[0];initial=gzip.decompress(z.read(part+'/initial/'+r['initial_sha256']+'.img.gz'));assert sha(initial)==r['initial_sha256']
  ref=r['trace'];key=ref.get('reference_trace_sha256',ref['trace_sha256']);raw=z.read(part+'/traces/'+key+'.jsonl.gz');raw=gzip.decompress(raw);assert sha(raw)==key
  hist=[json.loads(l)for l in raw.splitlines()]
  if ref['stored']!='whole':
   hist=hist[:ref['prefix_records']];n=ref['unacknowledged_cut_call_units']
   if n:
    for e in hist[-n:]:e['ack']=False
   hist.append(ref['cut_record'])
   assert sha(b''.join(json.dumps(e,sort_keys=True).encode()+b'\n'for e in hist))==ref['trace_sha256']
  d=S.device(initial,hist);image=S.durable(initial,d);image=bytearray(image)
  events={e.id:e for e in d.events}
  for i in q['landing_order']:e=events[i];image[e.lba*512:(e.lba+1)*512]=e.data
  assert sha(image)==want
  row=b['command_rows'][-1];record=json.loads((root/row['record']).read_text());assert record['projection_sha256']==want and record['binary_sha256']==BIN
  assert json.loads((root/row['original_observation']).read_text())==original[want]
  assert L.check(original[want])=='empty/empty'
  for name,c in record['commands'].items():
   paths=row['raw_inputs'][name];before=(root/paths['before']).read_bytes();after=(root/paths['after']).read_bytes();assert before==after==bytes(image)
   seam=json.loads((root/'stage3'/c['seam_trace']).read_text());assert seam['build']==HEAD and seam['exit']==c['exit']==0
   assert c['engine']==[e for e in seam['events']if e['kind']in('engine_bind','engine_mount','engine_info')]
   assert not[e for e in seam['events']if e['kind']=='write']and c['write_events']==[]
   if name=='verify':assert all(e['write_is_null']for e in c['engine']if e['kind']=='engine_bind')and c['stdout']=='OK\n'
   else:assert sha((root/'stage3/commands'/want/(name+'.wav')).read_bytes())==c['wav_sha256']==L.EMPTY
   c['input_before_sha256']=c['input_after_sha256']=want
  record['carried_state_judge_pass']=True;oracle.command_detail(record)
  bad=copy.deepcopy(original[want]);bad['dump_A']['wav_sha256']=L.VOICE
  try:L.check(bad)
  except AssertionError:control='actual-row impossible new/empty pair detected'
  else:raise AssertionError('impossible pair undetected')
 # Only the new32 plus their actual complete route control are assessed.
 rows=[];seen=set()
 for row in b['fault_rows']:
  if not row['record'].startswith('stage3/'):continue
  p=root/row['record'];r=json.loads(p.read_text());oracle.host_fault(r)
  coord=(r['requested']['kind'],r['requested']['ordinal']);assert coord not in seen;seen.add(coord)
  rows.append((p,r))
 assert seen=={(c['kind'],c['ordinal'])for c in plan['load_faults']}
 controlpath=root/'stage3/faults/none/record.json';rows.append((controlpath,json.loads(controlpath.read_text())))
 faults=[]
 for p,r in rows:
  assert r['binary_sha256']==BIN and r['source_wav_sha256']==L.VOICE
  assert r['actual_input_sha256']==r['pristine_input_sha256']==sha(initial)
  seam=json.loads((p.parent/'seam-trace.json').read_text());assert seam['build']==HEAD and seam['exit']==r['exit']
  work=bytearray(initial);events=[];w=f=0
  for e in seam['events']:
   if e['kind']=='write':
    data=bytes.fromhex(e['data_hex']);assert len(data)==e['bytes']and e['offset']%512==len(data)%512==0
    if e['ok']:work[e['offset']:e['offset']+len(data)]=data
    events.append(dict(t='W',ordinal=w,offset=e['offset'],bytes=e['bytes'],failed=not e['ok'],fault=e.get('fault')));w+=1
   elif e['kind']=='flush':events.append(dict(t='F',ordinal=f,os_call=e['os_call'],failed=not e['success'],os_error=e['os_error'],fault=e.get('fault')));f+=1
  assert events==r['load_events']and(w,f)==(r['op_calls'],r['op_barriers'])
  failed=[e for e in events if e['failed']]
  if p.parent.name=='none':assert not failed and r['exit']==0
  else:
   assert len(failed)==1
   assert (failed[0]['t'],failed[0]['ordinal'])==('W'if r['requested']['kind']=='write'else'F',r['requested']['ordinal'])
  assert bytes(work)==gzip.decompress((p.parent/'image-after.img.gz').read_bytes())and sha(work)==r['image_after_sha256']
  pair=L.check(r['post_failure_remount']);faults.append(dict(name=p.parent.name,calls=w,barriers=f,state=pair))
 assert len(faults)==33
 assert faults[-1]['calls']==353 and faults[-1]['barriers']==52 and faults[-1]['state']=='new/new'
 result=dict(carry=carry,global_command=dict(image=want,state='empty/empty',fresh_commands=3,original_row='retained and exactly matched; no placeholder',control=control),
             new_faults=32,faults=faults,remaining=dict(executed=39,unexecuted=365,proved_unavailable=0),
             scope='actual working effects, not physical persistence; old14 accepted narrow rows carried')
 out.write_text(json.dumps(result,indent=2)+'\n');print({k:v for k,v in result.items()if k!='faults'})
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--inputs',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();run(a.root,a.inputs,a.out)
