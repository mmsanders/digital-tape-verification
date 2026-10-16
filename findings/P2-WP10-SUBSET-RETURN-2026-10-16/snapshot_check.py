"""Corroborate pre-remount raw snapshots against independently projected bytes.
Core/promote raw mount/PCM predicates are reused; no ordinal durability oracle.
"""
import argparse,json,sys,hashlib
from pathlib import Path
import replay as R
M=R.M
B=512
SLOTS={'A0':8,'A1':136,'B0':264,'B1':392}
def run(root,family):
 if family in ('core','promote','dup'):
  sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tests'/({'core':'crash_core_draft8','promote':'promote_draft8','dup':'format_dup_identity_draft8'}[family])))
  import media
 errors=[];checked=0;mounts=0;audio=0
 for part in sorted((root/family).glob('part-*')):
  snaps={r['snapshot_sha256']:r['snapshot'] for r in R.lines(part/'snapshots.jsonl')}
  obs={(r['projection_sha256'],r['remount_key']):r for r in R.lines(part/'remounts.jsonl')};done=set()
  for r in R.lines(part/'runs.jsonl'):
   if 'trace' not in r:continue
   raw,blocks=R.initial(str(part/'initial'/(r['initial_sha256']+'.img.gz')));d=M.Device(blocks);hist=R.trace(part,r['trace']);i=0
   while i<len(hist):
    e=hist[i]
    if e['t']=='W':
     call=[e]
     while i+1<len(hist) and hist[i+1]['t']=='W' and hist[i+1]['call']==e['call']:i+=1;call.append(hist[i])
     b=b''.join(bytes.fromhex(x['hex']) for x in call)
     if e['ack']:d.write(e['lba'],b)
     else:d.write(e['lba'],b,acknowledged=False,visible=[])
    elif e['t']=='F':d.flush(successful=e['ok'])
    i+=1
   plans=list(M.exhaustive(d.events)) if len(d.events)<=8 else [p for s in (1,183,3647685189) for p in M.sampled(d.events,s)]
   for p,q in zip(plans,r['projections']):
    key=(q['image_sha256'],r['remount_key'])
    if key in done:continue
    done.add(key)
    o=obs[key]
    if 'image_snapshot' not in o:continue
    sr=o['image_snapshot'];s=dict(snaps[sr['metadata_snapshot_sha256']]);s.update({k:v for k,v in sr.items() if k!='metadata_snapshot_sha256'})
    img=d.crash_image(p['landing_order']);get=lambda l,n=1:b''.join(img.get(i,bytes(B)) for i in range(l,l+n))
    try:
     assert bytes.fromhex(s['primary_hex'])==get(0)
     assert bytes.fromhex(s['mirror_hex'])==get(len(raw)//B-1)
     if family=='core':
      for name,lba in SLOTS.items():assert bytes.fromhex(s['slots'][name])==get(lba,2)
      for c,h in s['chunk_sha256'].items():assert R.sha(get(2048+1024*int(c),1024))==h
      predicted=media.inspect_snapshot(s,requested_side=o['side'])['mount_result'];assert o['remount_result']==predicted;mounts+=1
     elif family=='promote':
      for name,lba in SLOTS.items():
       assert bytes.fromhex(s[name.lower()+'_header_hex'])==get(lba)
       assert bytes.fromhex(s[name.lower()+'_entries_hex'])==get(lba+1)
      for c,b in s['chunk0_hex'].items():assert bytes.fromhex(b)==get(2048+1024*int(c))
      for side in ('A','B'):
       pred=media.inspect_snapshot(s,side)['mount_result'];assert o['actual_mount_'+side]==pred;mounts+=1
       if pred=='TAPE_OK':assert media.render_sha256(s,side)==o['actual_audio_'+side+'_sha256'];audio+=1
     elif family=='dup':
      assert bytes.fromhex(s['a0_head_hex'])==get(8,len(s['a0_head_hex'])//1024)
      assert bytes.fromhex(s['b0_head_hex'])==get(264,len(s['b0_head_hex'])//1024)
      pred=media.inspect_snapshot(s);actual=o['actual_remount_result']
      assert actual==pred['mount_result'] or pred['mount_result']=='TAPE_ERR_BAD_MAGIC' and actual=='TAPE_ERR_CRC'
      if actual=='TAPE_OK':assert o['actual_selected_uuid']==pred['selected_uuid']
      mounts+=1
     else:
      for (name,lba),b in zip(SLOTS.items(),s['slot_prefix_hex']):assert bytes.fromhex(b)==get(lba,2)
     checked+=1
    except Exception as e:errors.append({'part':part.name,'image':key[0],'scenario':r['scenario'],'type':type(e).__name__,'error':str(e)})
 return {'family':family,'raw_snapshots_checked':checked,'independent_mount_predictions':mounts,'independent_PCM_hash_predictions':audio,'errors':errors,'scope':'snapshot binding and core/promote raw-state parser/PCM only; not all operation crash-table outcomes'}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('family');p.add_argument('--out',type=Path,required=True);a=p.parse_args();r=run(a.root,a.family);a.out.write_text(json.dumps(r,indent=2)+'\n');print({k:v for k,v in r.items() if k!='errors'},'errors',len(r['errors']))
