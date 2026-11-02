"""Offline independent replay of #374 raw publication; no Product imports/execution."""
import argparse,gzip,hashlib,json,sys
from pathlib import Path
from crash import ROOT,load,replay_faults
from wp17 import compare,pcm
def sha(b):return hashlib.sha256(b).hexdigest()
def review(first,second):
    fault=replay_faults(first/'faults')
    host=json.loads((second/'host/HOST.json').read_text());assert len(host['goldens'])==10
    for row in host['goldens']:
        ref=ROOT/'tests/golden/ref'/(row['name']+'.wav');actual=second/'host'/(row['name']+'.wav')
        assert ref.read_bytes()==actual.read_bytes() and sha(actual.read_bytes())==row['wav_sha256']
        raw=pcm(actual);assert sha(raw)==row['pcm_sha256']and len(raw)==row['frames']*4
        compare(pcm(ref),raw)
    assert sum(r['rate_scope']=='1x'for r in host['goldens'])==7
    S=load(ROOT/'findings/P2-210-STAGE3-2026-10-19/subset.py','subset374_review')
    sys.path.insert(0,str(ROOT/'tests/respool_full_draft8'))
    CP=load(ROOT/'findings/P2-SUBSET-ROWS-2026-10-17/respool_copy.py','copy374_review')
    part=second/'long/lane4';rp=S.R.replay(part);assert rp['runs']==6 and not rp['errors']
    meta={r['snapshot_sha256']:r['snapshot']for r in S.R.lines(part/'snapshots.jsonl')}
    obs={(r['projection_sha256'],r['remount_key']):r for r in S.R.lines(part/'remounts.jsonl')}
    seen=[]
    for row in S.R.lines(part/'runs.jsonl'):
        initial,_=S.R.initial(str(part/'initial'/(row['initial_sha256']+'.img.gz')));hist=S.R.trace(part,row['trace'])
        unit=int(row['coordinate']['cut_op_unit']);seen.append(unit)
        assert row['scenario']==['no_lower_run','pass1']and unit in (63,64,65,127,128,129)
        assert sum(e['t']=='W'and e.get('phase')=='op'for e in hist)==row['worker']['op_units']==3<unit
        assert not row['worker']['cut_fired']and row['worker']['operation_result']=='TAPE_OK'and all(e['t']!='CUT'for e in hist)
        CP.check(initial,hist,'no_lower_run')
        d=S.device(initial,hist);assert len(d.events)==0
        raw=S.durable(initial,d);h=sha(raw);o=obs[h,row['remount_key']]
        snapshot=S.O.snap(meta,o['image_snapshot']);assert S.O.raw_snapshot(raw,snapshot)==snapshot
        pre=S.O.raw_snapshot(initial,snapshot);S.O.respool_check(snapshot,o,pre,('no_lower_run','pass1'),hist)
    assert sorted(seen)==[63,64,65,127,128,129]
    return dict(faults=fault,long_requests=6,long_cuts=0,long_proved_unavailable=6,long_raw_replay=rp,
                host_goldens=10,normal_rate=7,scrub_vectors=3,engine_tree=host['engine_tree'],
                exclusions=['target PCM','target stack','target timing','physical behavior','exhaustive large epochs','media qualification','batching authorization'])
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('first',type=Path);p.add_argument('second',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    r=review(a.first.resolve(),a.second.resolve());a.out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
