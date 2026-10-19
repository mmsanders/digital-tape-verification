"""Narrow raw/provider qualification. Reconstruct bytes, do not execute Product.
Old operation/model predicates stay unchanged; all samples retain exact bounds.
"""
import argparse,gzip,hashlib,importlib.util,json,re,subprocess,sys,urllib.request,zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
SOURCE='743f82939a8fc99e64b384db45430824b68482d1'
BIN='02bd7cb495f82edc75a4c9917633a4e838f3d09aac27f62de0c47fd7805ba271'
def sha(b):return hashlib.sha256(b).hexdigest()
def module(path,name):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def run(directory,out,release=None):
 directory.mkdir(parents=True,exist_ok=True);pins=json.loads((HERE/'INPUTS.json').read_text());archives={}
 for pin in pins:
  p=directory/(pin['name']+'.zip')
  if not p.exists():
   if release:
    with urllib.request.urlopen(release.rstrip('/')+'/'+p.name,timeout=60)as r,p.open('wb')as f:
     while b:=r.read(1024*1024):f.write(b)
   else:
    with p.open('wb')as f:subprocess.run(['gh','api',f"repos/mmsanders/Digital-Tape/actions/artifacts/{pin['id']}/zip"],stdout=f,check=True)
  assert p.stat().st_size==pin['bytes']and sha(p.read_bytes())==pin['sha256'];archives[pin['name']]=p
 root=directory/'returned';root.mkdir(exist_ok=True)
 with zipfile.ZipFile(archives['return'])as z:
  for i in z.infolist():assert not Path(i.filename).is_absolute()and'..'not in Path(i.filename).parts and(i.external_attr>>16)&0o170000!=0o120000
  z.extractall(root)
 sys.path.insert(0,str(ROOT/'tests/wp10_narrow_supplement_r1'))
 replay=module(ROOT/'tests/wp10_narrow_supplement_r1/replay.py','narrow_replay');judged=replay.run(root)
 assert len(judged['rows'])==14
 legacy=module(ROOT/'findings/P2-SUBSET-ROWS-2026-10-17/load_rows.py','original_load_state')
 bundle=json.loads((root/'BUNDLE.json').read_text())
 result={'source':SOURCE,'artifact_sha256':pins[0]['sha256'],'narrow_replay':judged,'source_runs':[], 'faults':[], 'commands':[]}
 # Authenticate the original four-shard selection without rerunning their models/campaigns.
 all_obs={};repair_contexts=0;repairs=set();initial=None;parts=[]
 for name in ['load0','load1','load2','load3']:
  seen={};nrepair=0
  with zipfile.ZipFile(archives[name])as z:
   for member in z.namelist():
    if '/initial/1d677f4c' in member:initial=gzip.decompress(z.read(member))
    if not member.endswith('remounts.jsonl'):continue
    for line in z.read(member).splitlines():
     d=json.loads(line);h=d['projection_sha256'];seen[h]=d;all_obs.setdefault(h,d)
     if any(e.get('needs_repair')for c in ['verify','dump_A','dump_B']for e in d[c]['engine']if e['kind']=='engine_info'):
      repairs.add(h);nrepair+=1
  repair_contexts+=nrepair;parts.append(dict(name=name,unique=len(seen),repair_contexts=nrepair))
 assert initial is not None and sha(initial)=='1d677f4c0e1fbeda0dd4d8c7cdb4211095f82342c4ca2b62fe7a51037bb83d8c'
 first={}
 for h,d in sorted(all_obs.items()):
  pair=legacy.check(d);first.setdefault(pair,h)
 selected={json.loads((root/r['record']).read_text())['projection_sha256']for r in bundle['command_rows']}
 assert repairs.issubset(selected) and len(repairs)==2 and repair_contexts==10
 result['selection']={'global_unique_images':len(all_obs),'parts':parts,'repair_contexts':repair_contexts,'repair_images':sorted(repairs),'global_first_by_state':first,'global_first_not_in_return':sorted(set(first.values())-selected),'scope':'five returned rows selected from load0; all four-shard distinct repair images are covered; global minimum empty/empty differs'}
 # The actual source callback traces and raw before/after images, not summary booleans alone.
 for shape,w in bundle['parts']['dup']['source_runs'].items():
  base=root/'dup/source'/shape;ev=[json.loads(l)for l in(base/'events.jsonl').read_text().splitlines()];src=[e for e in ev if e['device']=='source']
  assert w['source_write_callback_null']and w['operation_result']=='TAPE_OK'
  assert len(ev)==w['events_logged']<w['events_capacity']and len(src)==w['source_events']
  assert src and all(e['op']=='r'and e['rc']==0 for e in src)
  before=(base/'source-before.img').read_bytes();assert before==(base/'source-after.img').read_bytes()
  result['source_runs'].append(dict(shape=shape,events=len(src),raw_sha256=sha(before)))
 assert len({x['raw_sha256']for x in result['source_runs']})==1
 mutant=json.loads((root/'dup/source-mutant-control.json').read_text());assert mutant['source_write_callback_null']is False
 r0=bundle['duplicate_rows'][0];r=json.loads((root/r0['record']).read_text());sa,sb,da,db=[(root/r0[k]).read_bytes()for k in ['source_A_pcm','source_B_pcm','dest_A_pcm','dest_B_pcm']]
 r.update(source_raw_before='same',source_raw_after='same',source_A_sha256=sha(sa),source_B_sha256=sha(sb),source_label_hex='00'*32,destination_label_hex='00'*32,restored_sha256=r['selected_projection_sha256'])
 replay.oracle.duplicate(r,sa,sb,da,db);r['source_write_callback_null']=mutant['source_write_callback_null']
 try:replay.oracle.duplicate(r,sa,sb,da,db)
 except AssertionError:result['source_control']='actual non-NULL binding flag detected by independent predicate; no actual source writes claimed'
 else:raise AssertionError('non-NULL control undetected')
 # Independently derive every actual working image from success payloads; failed EBADF write lands nothing.
 for p in sorted((root/'load/faults').glob('*/record.json')):
  r=json.loads(p.read_text());seam=json.loads((p.parent/'seam-trace.json').read_text());assert seam['build']==SOURCE and seam['exit']==r['exit']and r['binary_sha256']==BIN
  work=bytearray(initial);w=f=0;events=[]
  for e in seam['events']:
   if e['kind']=='write':
    data=bytes.fromhex(e['data_hex']);assert len(data)==e['bytes']and e['offset']%512==0 and len(data)%512==0
    if e['ok']:work[e['offset']:e['offset']+len(data)]=data
    events.append(dict(t='W',ordinal=w,offset=e['offset'],bytes=e['bytes'],failed=not e['ok'],fault=e.get('fault')));w+=1
   elif e['kind']=='flush':
    events.append(dict(t='F',ordinal=f,os_call=e['os_call'],failed=not e['success'],os_error=e['os_error'],fault=e.get('fault')));f+=1
  assert events==r['load_events']and(w,f)==(r['op_calls'],r['op_barriers'])
  after=gzip.decompress((p.parent/'image-after.img.gz').read_bytes());assert bytes(work)==after and sha(after)==r['image_after_sha256']
  assert r['source_wav_sha256']==legacy.VOICE
  pair=legacy.check(r['post_failure_remount']);result['faults'].append(dict(name=p.parent.name,exit=r['exit'],calls=w,barriers=f,state=pair,image=sha(after)))
 assert len(result['faults'])==9
 # Per-command actual seam and output facts, including the two writable repair observations.
 for row in bundle['command_rows']:
  r=json.loads((root/row['record']).read_text());rec={'image':r['projection_sha256'],'commands':{}}
  for name,c in r['commands'].items():
   seam=json.loads((root/'load'/c['seam_trace']).read_text());assert seam['build']==SOURCE and seam['exit']==c['exit']and r['binary_sha256']==BIN
   ev=seam['events'];assert c['engine']==[e for e in ev if e['kind']in('engine_bind','engine_mount','engine_info')]
   paths=row['raw_inputs'][name];before=(root/paths['before']).read_bytes();after=(root/paths['after']).read_bytes();assert sha(before)==r['projection_sha256']
   writes=[e for e in ev if e['kind']=='write'];assert writes==c['write_events']
   if name=='verify':assert not writes and before==after and all(e['write_is_null']for e in ev if e['kind']=='engine_bind')
   else:
    wav=(root/'load/commands'/r['projection_sha256']/(name+'.wav')).read_bytes();assert sha(wav)==c['wav_sha256']==all_obs[r['projection_sha256']][name]['wav_sha256']
    if before!=after:
     # Fixed provisioned geometry, byte comparison only: mirror copied to primary, every other byte unchanged.
     primary=34816*512;expected=bytearray(before);expected[primary:primary+512]=before[-512:]
     assert bytes(expected)==after and len(writes)==1 and writes[0]['offset']==primary and writes[0]['bytes']==512
     assert any(e['kind']=='flush'and e['success']for e in ev)
   rec['commands'][name]={'exit':c['exit'],'writes':len(writes),'image_changed':before!=after}
  result['commands'].append(rec)
 status=json.loads((root/'load/COORDINATES.json').read_text())['status'];counts={k:sum(v==k for rows in status.values()for v in rows.values())for k in ['executed','unexecuted','proved-unavailable']}
 assert counts==dict(executed=7,unexecuted=397,**{'proved-unavailable':0});result['coordinates']=counts
 result['cpu']={'current_CI_measured':5.31,'earlier_CI_reported':7.71,'local_reported_estimate':31,'reported_total_approx':44.02,'cap':7200,'note':'local estimate is not an independently measured cumulative receipt'}
 out.write_text(json.dumps(result,indent=2)+'\n');print('PASS narrow replay, seven source traces/control, nine working images, five actual command/repair rows; four-shard repair inventory')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--artifacts',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--release');a=p.parse_args();run(a.artifacts,a.out,a.release)
