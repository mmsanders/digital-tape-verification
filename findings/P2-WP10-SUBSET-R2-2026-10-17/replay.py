"""Independent raw subset-packet replay. Imports only Verification's model.
No Product adapter is imported, no operation acceptance is inferred from hashes.
"""
import argparse,collections,gzip,hashlib,json,sys
from pathlib import Path
from functools import lru_cache
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tests/wp10_subset_r1'))
import model as M

def sha(b):return hashlib.sha256(b).hexdigest()
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
IMAGE_CACHE={}
def lines(p):return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
@lru_cache(64)
def initial(p):
 b=gzip.decompress(Path(p).read_bytes());assert sha(b)==Path(p).name[:-7]
 return b,{i:b[i*512:(i+1)*512] for i in range(len(b)//512)}
@lru_cache(64)
def trace_bytes(p):return gzip.decompress(Path(p).read_bytes())
def trace(part,ref):
 if ref['stored']=='whole':raw=trace_bytes(str(part/'traces'/(ref['trace_sha256']+'.jsonl.gz')))
 else:
  raw=trace_bytes(str(part/'traces'/(ref['reference_trace_sha256']+'.jsonl.gz')))
  assert sha(raw)==ref['reference_trace_sha256']
  rows=[json.loads(l) for l in raw.splitlines()][:ref['prefix_records']]
  c=ref['cut_record'].get('call');n=ref['unacknowledged_cut_call_units']
  if n:
   for r in rows[-n:]:assert r['t']=='W' and r['call']==c;r['ack']=False
  rows.append(ref['cut_record']);raw=b''.join(json.dumps(r,sort_keys=True).encode()+b'\n' for r in rows)
 assert sha(raw)==ref['trace_sha256'];return [json.loads(l) for l in raw.splitlines()]
def replay(part):
 snaps={r['snapshot_sha256']:r['snapshot'] for r in lines(part/'snapshots.jsonl')}
 for h,s in snaps.items():assert sha(canon(s))==h
 remounts={(r['projection_sha256'],r['remount_key']):r for r in lines(part/'remounts.jsonl')}
 runs=proj=0;missing=collections.Counter();errors=[];epochs=collections.Counter();cache=IMAGE_CACHE;not_reachable=0;second=0
 for r in lines(part/'runs.jsonl'):
  if 'trace' not in r:not_reachable+=1;continue
  runs+=1;second+=('second_cut_of' in r)
  try:
   raw,blocks=initial(str(part/'initial'/(r['initial_sha256']+'.img.gz')));d=M.Device(blocks)
   hist=trace(part,r['trace']);i=0
   while i<len(hist):
    e=hist[i]
    if e['t']=='W':
     call=[e]
     while i+1<len(hist) and hist[i+1]['t']=='W' and hist[i+1]['call']==e['call']:i+=1;call.append(hist[i])
     assert [x['id'] for x in call]==list(range(d.next_id,d.next_id+len(call)))
     assert [x['lba'] for x in call]==list(range(e['lba'],e['lba']+len(call)))
     assert len({x['ack'] for x in call})==1
     data=b''.join(bytes.fromhex(x['hex']) for x in call)
     assert len(data)==512*len(call)
     if e['ack']:d.write(e['lba'],data)
     else:d.write(e['lba'],data,acknowledged=False,visible=[])
    elif e['t']=='F':d.flush(successful=e['ok'])
    else:assert e['t']=='CUT' and i==len(hist)-1
    i+=1
   assert len(d.events)==r['epoch']['length'];epochs[len(d.events)]+=1
   assert d.flush_results==r['epoch']['barrier_results']
   ev=[{'id':e.id,'call':e.call,'lba':e.lba,'ack':e.acknowledged,'sha256':sha(e.data)} for e in d.events]
   assert sha(canon(ev))==r['epoch']['events_sha256']
   if 'events' in r['epoch']:assert ev==r['epoch']['events']
   buf=bytearray(raw)
   for lba,b in d.durable.items():buf[lba*512:(lba+1)*512]=b
   durable=bytes(buf);dh=sha(durable);assert dh==r['epoch']['durable_sha256']
   plans=list(M.exhaustive(d.events)) if len(d.events)<=8 else [p for s in (1,183,3647685189) for p in M.sampled(d.events,s)]
   assert r['plan']==('exhaustive' if len(d.events)<=8 else 'sampled') and len(plans)==len(r['projections'])
   by_id={e.id:e for e in d.events}
   for p,q in zip(plans,r['projections']):
    proj+=1
    if r['projections_inline']:assert all(q[k]==v for k,v in p.items())
    else:
     assert sha(p['mask'].encode())==q['mask_sha256'] and sha(canon(p['landing_order']))==q['landing_order_sha256']
     assert all(q[k]==v for k,v in p.items() if k not in ('mask','landing_order'))
    final={by_id[id].lba:by_id[id].data for id in p['landing_order']}
    ck=(dh,tuple((k,sha(v)) for k,v in sorted(final.items())))
    if ck not in cache:
     bb=bytearray(durable)
     for lba,b in final.items():bb[lba*512:(lba+1)*512]=b
     cache[ck]=sha(bb)
    h=cache[ck];assert h==q['image_sha256']
    assert (h,r['remount_key']) in remounts
   if r['base'].startswith('projection:'):assert r['base'][11:]==r['initial_sha256']
  except Exception as e:errors.append({'scenario':r.get('scenario'),'coordinate':r.get('coordinate'),'error':str(e),'type':type(e).__name__})
 return {'runs':runs,'projections':proj,'remount_records':len(remounts),'epoch_histogram':dict(epochs),'second_cut_runs':second,'not_reachable':not_reachable,'errors':errors}
def links(root):
 index=set();rows=[]
 for path in root.rglob('runs.jsonl'):
  for r in lines(path):
   if 'trace' not in r:continue
   rows.append(r)
   if r['base']=='fixture' and r['coordinate']['cut_op_unit']!='-':
    for q in r['projections']:
     if 'landing_order' in q:index.add((r['binding'],tuple(r['scenario']),r['coordinate']['cut_op_unit'],q['image_sha256'],q['mask'],tuple(q['landing_order'])))
 errors=[];n=0
 for r in rows:
  if 'second_cut_of' not in r:continue
  n+=1;c=r['second_cut_of'];k=(r['binding'],tuple(r['scenario']),c['first_cut_op_unit'],c['first_image_sha256'],c['first_mask'],tuple(c['first_landing_order']))
  if c['first_image_sha256']!=r['initial_sha256'] or k not in index:errors.append({'binding':r['binding'],'scenario':r['scenario'],'first':c})
 return {'second_cut_runs':n,'errors':errors,'scope':'first-cut coordinate/scenario/selected-mask/order/image matches each authenticated second initial image; not a RAM-state claim'}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--out',type=Path,required=True);p.add_argument('--links-only',action='store_true');p.add_argument('--exclude-load',action='store_true');a=p.parse_args()
 if a.links_only:a.out.write_text(json.dumps(links(a.root),indent=2)+'\n');raise SystemExit
 out={}
 bundles=[a.root] if (a.root/'SHA256SUMS').exists() else sorted(x for x in a.root.glob('wp10-subset-*') if x.is_dir())
 for bundle in bundles:
  if a.exclude_load and 'load' in bundle.name:continue
  for line in (bundle/'SHA256SUMS').read_text().splitlines():
   h,name=line.split(None,1)
   assert name.strip()!='./SHA256SUMS', 'checksum index must exclude itself'
   assert sha((bundle/name.strip().lstrip('*')).read_bytes())==h,name
  for part in sorted(bundle.glob('*/part-*')):
   if not (part/'runs.jsonl').exists():continue
   r=replay(part);out[str(part.relative_to(a.root))]=r;print(str(part),r['runs'],r['projections'],'errors',len(r['errors']),flush=True)
   a.out.write_text(json.dumps(out,indent=2)+'\n')
 a.out.write_text(json.dumps(out,indent=2)+'\n')
 raise SystemExit(1 if any(r['errors'] for r in out.values()) else 0)
