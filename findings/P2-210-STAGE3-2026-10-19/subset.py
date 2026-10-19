"""New fixed-lane subset replay, raw snapshot binding and unchanged199 predicates.
Imports only independent Verification models. No Product execution/import.
Run each family separately because historical packages use bare module names.
"""
import argparse, collections, copy, hashlib, importlib.util, json, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def load(path,name):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
R=load(ROOT/'findings/P2-WP10-SUBSET-R2-2026-10-17/replay.py','independent_replay')
O=load(ROOT/'findings/P2-SUBSET-ROWS-2026-10-17/rows.py','rows')
sys.modules['rows']=O
PLAN=json.loads((ROOT/'tests/wp10_subset_extension_r1/PLAN.json').read_text())
def device(raw,hist):
 d=R.M.Device({i:raw[i*512:(i+1)*512]for i in range(len(raw)//512)});i=0
 while i<len(hist):
  e=hist[i]
  if e['t']=='W':
   call=[e]
   while i+1<len(hist)and hist[i+1]['t']=='W'and hist[i+1]['call']==e['call']:i+=1;call.append(hist[i])
   assert [x['id']for x in call]==list(range(d.next_id,d.next_id+len(call)))
   assert [x['lba']for x in call]==list(range(e['lba'],e['lba']+len(call)))
   assert len({x['ack']for x in call})==1
   data=b''.join(bytes.fromhex(x['hex'])for x in call);assert len(data)==512*len(call)
   if e['ack']:d.write(e['lba'],data)
   else:d.write(e['lba'],data,acknowledged=False,visible=[])
  elif e['t']=='F':d.flush(successful=e['ok'])
  else:assert e['t']=='CUT'and i==len(hist)-1
  i+=1
 return d
def durable(raw,d):
 b=bytearray(raw)
 for l,v in d.durable.items():b[l*512:(l+1)*512]=v
 return bytes(b)

def run(root,lane,out):
 family='dup'if lane=='lane3'else'respool';sys.path.insert(0,str(ROOT/'tests'/O.FAMILIES[family]))
 import fixture
 if lane=='lane3':
  sys.path.insert(0,str(ROOT/'tests/wp10_residue_d10'))
  RP=load(ROOT/'tests/wp10_residue_d10/plan.py','residue_plan')
 else:CP=load(ROOT/'findings/P2-SUBSET-ROWS-2026-10-17/respool_copy.py','copy_predicates')
 orders=load(ROOT/'tests/wp10_subset_extension_r1/orders.py','fixed_orders')
 part=root/'stage3'/lane;runs=R.lines(part/'runs.jsonl')
 meta={r['snapshot_sha256']:r['snapshot']for r in R.lines(part/'snapshots.jsonl')}
 for h,s in meta.items():assert R.sha(R.canon(s))==h
 obs={(r['projection_sha256'],r['remount_key']):r for r in R.lines(part/'remounts.jsonl')}
 extras=collections.defaultdict(list)
 for e in R.lines(part/'EXTRA-ORDERS.jsonl'):extras[e['label']].append(e)
 results=[];cache={};controls={};snapshot_bound=set();seen_coordinates=set();positive=cuts=unexecuted=0
 for r in runs:
  raw,_=R.initial(str(part/'initial'/(r['initial_sha256']+'.img.gz')));hist=R.trace(part,r['trace'])
  label=r['label'];coord=r['coordinate'];worker=r['worker']
  if lane=='lane3':
   op,shape,suffix=label.split('/',2);assert op in PLAN['atomic_residue']['operations']and shape in PLAN['atomic_residue']['shapes']
   img=RP.blank(shape)if shape in RP.BLANK_VARIANTS else RP.base(*(RP.EXHAUSTION_SHAPES.get(shape)or RP.RESIDUE_SHAPES[shape]))
   expected=bytearray((RP.M.MIRROR+1)*512)
   for k,l in RP.M.TRACKED.items():expected[l*512:(l+1)*512]=img[k]
   assert raw==bytes(expected),'crafted initial differs from independent builder'
   if suffix=='complete':assert not worker['cut_fired']and worker['operation_result']=='TAPE_OK';positive+=1;key=(op,shape,'complete')
   else:
    want=json.loads(suffix);assert want in PLAN['atomic_residue']['coordinates'];key=(op,shape,R.canon(want).decode())
    assert worker['cut_fired']and worker['operation_result']=='TAPE_ERR_IO';cuts+=1
   scenario=(op,shape)
  else:
   scenario=tuple(r['scenario']);assert list(scenario)in PLAN['long_copy']['scenarios'];want=json.loads(label.split('/',2)[2])
   assert want in PLAN['long_copy']['coordinates'];key=(*scenario,R.canon(want).decode())
   assert r['base']=='fixture'
   if worker['cut_fired']:assert worker['operation_result']=='TAPE_ERR_IO';cuts+=1
   else:
    assert scenario==('no_lower_run','pass1')and worker['operation_result']=='TAPE_OK'
    assert sum(e['t']=='W'and e.get('phase')=='op'for e in hist)==worker['op_units']==3
    assert all(e['t']!='CUT'for e in hist);unexecuted+=1
   CP.check(raw,hist,scenario[0])
   if 'wrong-copy-byte'not in controls:
    bad=copy.deepcopy(hist);w=next(e for e in bad if e['t']=='W'and 2048<=e['lba']<len(raw)//512-1);w['hex']=('00'if w['hex'][:2]!='00'else'01')+w['hex'][2:]
    try:CP.check(raw,bad,scenario[0])
    except AssertionError:controls['wrong-copy-byte']='detected on actual returned trace'
    else:raise AssertionError('wrong copy byte undetected')
  if lane=='lane4' or not label.endswith('/complete'):
   assert all(str(coord[k])==str(v)for k,v in want.items()),'label/actual coordinate mismatch'
   assert all(str(v)=='-'for k,v in coord.items()if k not in want),'extra unplanned fault'
  else:assert all(str(v)=='-'for v in coord.values())
  assert key not in seen_coordinates;seen_coordinates.add(key)
  if worker['cut_fired']:
   cut=hist[-1];assert cut['t']=='CUT'
   if coord['cut_op_unit']!='-':assert cut['op_unit']==int(coord['cut_op_unit'])==worker['op_units']
   else:assert cut['op_flush']==int(coord['cut_op_barrier_entry'])
  d=device(raw,hist);ev=[dict(id=e.id,call=e.call,lba=e.lba,ack=e.acknowledged,sha256=R.sha(e.data))for e in d.events]
  assert len(ev)==r['epoch']['length']and d.flush_results==r['epoch']['barrier_results']
  assert R.sha(R.canon(ev))==r['epoch']['events_sha256']and ev==r['epoch']['events']
  repeated=len(ev)-len({e['lba']for e in ev});assert repeated==r['epoch']['repeated_lba_events']==0
  base=durable(raw,d);dh=R.sha(base);assert dh==r['epoch']['durable_sha256']
  plans=list(R.M.exhaustive(d.events))if len(ev)<=8 else[p for seed in PLAN['persistence']['large_seeds']for p in R.M.sampled(d.events,seed)]
  assert len(plans)==len(r['projections'])and r['projections_inline']
  for p,q in zip(plans,r['projections']):assert all(q[k]==v for k,v in p.items())
  targets=list(orders.targeted([dict(id=e.id,lba=e.lba)for e in d.events]))if len(ev)>8 else[]
  ex=extras.pop(label,[]);assert len(ex)==len(targets)
  for p,q in zip(targets,ex):assert q['scenario']==list(scenario)and all(q[k]==v for k,v in p.items())
  states=collections.Counter();byid={e.id:e for e in d.events}
  for p,q in list(zip(plans,r['projections']))+list(zip(targets,ex)):
   final={byid[i].lba:byid[i].data for i in p['landing_order']}
   ck=(dh,tuple((l,R.sha(b))for l,b in sorted(final.items())))
   if ck not in cache:
    b=bytearray(base)
    for l,v in final.items():b[l*512:(l+1)*512]=v
    h=R.sha(b);o=obs[h,r['remount_key']];s=O.snap(meta,o['image_snapshot'])
    derived=O.raw_snapshot(bytes(b),s);assert derived==s,'actual compact snapshot does not bind restored raw bytes'
    cache[ck]=h;snapshot_bound.add(h)
   h=cache[ck];assert h==q['image_sha256'];o=obs[h,r['remount_key']];s=O.snap(meta,o['image_snapshot']);pre=O.raw_snapshot(raw,s)
   if lane=='lane3':
    value=O.dup_check(s,o,pre,scenario,hist)
    if label.endswith('/complete'):assert value.get('identity')=='fresh'
    if 'wrong-identity'not in controls and value.get('identity')=='fresh':
     bad=copy.deepcopy(o);bad['actual_selected_uuid']='00'*16
     try:O.dup_check(s,bad,pre,scenario,hist)
     except AssertionError:controls['wrong-identity']='detected on actual returned complete neighbour'
     else:raise AssertionError('wrong identity undetected')
   else:value=O.respool_check(s,o,pre,scenario,hist)
   states[R.canon(value).decode()]+=1
  results.append(dict(label=label,contexts=len(plans)+len(targets),epoch=len(ev),cut=bool(worker['cut_fired']),states=dict(states)))
 assert not extras
 if lane=='lane3':assert len(runs)==120 and positive==24 and cuts==96
 else:assert len(runs)==18 and cuts==12 and unexecuted==6
 result=dict(lane=lane,runs=len(runs),complete_neighbours=positive,executed_cuts=cuts,unexecuted=unexecuted,
             contexts=sum(r['contexts']for r in results),raw_bound_images=len(snapshot_bound),repeated_lba_events=0,
             controls=controls,rows=results,scope='new fixed rows only; operation-specific predicates; finite large epochs, no repeated-LBA coverage')
 out.write_text(json.dumps(result,indent=2)+'\n');print({k:v for k,v in result.items()if k!='rows'})

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--lane',choices=['lane3','lane4'],required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();run(a.root,a.lane,a.out)
