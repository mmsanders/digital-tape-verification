"""Independent V186-02 fill and bounded pre-index-commit operation review.
Imports only existing Verification publications, never Product code.
"""
import argparse,collections,copy,importlib.util,json,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'findings/P2-WP10-SUBSET-R2-2026-10-17'))
import replay as R
spec=importlib.util.spec_from_file_location('coordinate_audit',ROOT/'findings/P2-WP10-SUBSET-R2-2026-10-17/audit.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C)
sys.path.insert(0,str(ROOT/'tests/crash_core_draft8'))
import media
import fixture

def stage_property(s,o,baseline):
    fp=media.logical_fingerprint(s,requested_side=o['side'])
    assert fp['mount_result']==o['remount_result']=='TAPE_OK'
    assert (fp['sb_generation'],fp['promote_stage'],fp['a_high_water'])==(11,0,3)
    assert fp['a_entries']==fp['b_entries']==[(2,0,131072)]
    assert all(s['chunk_sha256'][str(c)]==baseline[str(c)] for c in (0,1,2))
    return fp

def device(part,r):
    raw,blocks=R.initial(str(part/'initial'/(r['initial_sha256']+'.img.gz')))
    d=R.M.Device(blocks);hist=R.trace(part,r['trace']);i=0
    while i<len(hist):
        e=hist[i]
        if e['t']=='W':
            call=[e]
            while i+1<len(hist) and hist[i+1]['t']=='W' and hist[i+1]['call']==e['call']:i+=1;call.append(hist[i])
            data=b''.join(bytes.fromhex(x['hex']) for x in call)
            d.write(e['lba'],data,acknowledged=e['ack'],**({} if e['ack'] else {'visible':[]}))
        elif e['t']=='F':d.flush(successful=e['ok'])
        i+=1
    return raw,d,hist

def review(root):
    members=set()
    for l in (root/'SHA256SUMS').read_text().splitlines():
        h,n=l.split(None,1);assert n!='./SHA256SUMS';assert R.sha((root/n).read_bytes())==h
        members.add(n.removeprefix('./'))
    assert members=={str(p.relative_to(root)) for p in root.rglob('*') if p.is_file() and p.name!='SHA256SUMS'}
    old=json.loads((ROOT/'findings/P2-WP10-SUBSET-R2-2026-10-17/audit-result.json').read_text())
    old_bases={(b['binding'],tuple(b['scenario']),b['index']):b['base'][11:] for b in old['second_bases']}
    parts={};new=[];bases=[];complete={};snapshots=0;predictions=0;image_contexts=set();controls={}
    for part in sorted(root.glob('*/part-*')):
        rows=R.lines(part/'runs.jsonl')
        selected=[r for r in rows if r.get('label') in ('cut_unit','error_write','second_cut')]
        if selected:
            # A view changes only the row selection; every referenced raw member
            # is the authenticated original. No observations/assertions change.
            with tempfile.TemporaryDirectory() as td:
                view=Path(td)
                for p in part.iterdir():
                    if p.name!='runs.jsonl':(view/p.name).symlink_to(p.resolve())
                (view/'runs.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in selected))
                result=R.replay(view);assert not result['errors'],result
                parts[str(part.relative_to(root))]=result
        snaps={r['snapshot_sha256']:r['snapshot'] for r in R.lines(part/'snapshots.jsonl')}
        obs={(r['projection_sha256'],r['remount_key']):r for r in R.lines(part/'remounts.jsonl')}
        for r in rows:
            if r.get('label')=='second_complete':
                t=r['second_cut_of'];k=(r['binding'],tuple(r['scenario']),t['second_base_index'])
                assert r['initial_sha256']==old_bases[k]==t['first_image_sha256']
                bases.append({'binding':r['binding'],'scenario':r['scenario'],'index':t['second_base_index'],'initial_sha256':r['initial_sha256']})
            if r.get('label') not in ('second_complete','cut_unit','error_write','second_cut'):continue
            raw,d,hist=device(part,r)
            if r.get('label')=='second_complete':
                bp=C.boundary(hist,len(raw)//512)
                complete[(r['binding'],tuple(r['scenario']),r['initial_sha256'])]=bp
                continue
            assert r['requested_fault']['fired'] is True
            if r['label']=='error_write':assert r['coordinate']['error_op_call']==1019 and r['worker']['error_fired']
            else:assert r['coordinate']['cut_op_unit']==1020 and r['worker']['cut_fired']
            # Initial failed setup write is retained in the actual full trace.
            assert sum(e['t']=='W' and e.get('phase')=='setup' for e in hist)==1
            assert any(e['t']=='W' and e.get('phase')=='setup' and not e['ack'] for e in hist)
            new.append({'scenario':r['scenario'],'label':r['label'],'coordinate':r['coordinate'],'epoch':r['epoch']['length'],'projections':len(r['projections']),'fault':r['requested_fault']})
            baseline={str(c):R.sha(raw[(2048+1024*c)*512:(2048+1024*(c+1))*512]) for c in range(5)}
            plans=[p for s in (1,183,3647685189) for p in R.M.sampled(d.events,s)]
            assert len(plans)==len(r['projections'])==201
            for p,q in zip(plans,r['projections']):
                k=(str(part),q['image_sha256'],r['remount_key'])
                if k in image_contexts:continue
                image_contexts.add(k);o=obs[(q['image_sha256'],r['remount_key'])]
                sr=o['image_snapshot'];s=dict(snaps[sr['metadata_snapshot_sha256']]);s.update({k:v for k,v in sr.items() if k!='metadata_snapshot_sha256'})
                image=d.crash_image(p['landing_order']);get=lambda l,n=1:b''.join(image.get(i,bytes(512)) for i in range(l,l+n))
                assert bytes.fromhex(s['primary_hex'])==get(0) and bytes.fromhex(s['mirror_hex'])==get(len(raw)//512-1)
                for name,lba in {'A0':8,'A1':136,'B0':264,'B1':392}.items():assert bytes.fromhex(s['slots'][name])==get(lba,2)
                for c,h in s['chunk_sha256'].items():assert h==R.sha(get(2048+1024*int(c),1024))
                snapshots+=1
                fp=stage_property(s,o,baseline)
                # Published stage fixture: A and B reference chunk2. At these
                # cuts the copy is not committed; protected A0..2 and the live
                # B timeline remain intact. Scratch chunk3 may change.
                if not controls:
                    controls['honest_observation']='PASS'
                    bad=copy.deepcopy(s);bad['primary_hex']=bad['mirror_hex']=fixture.stage_current_superblock().hex()
                    try:stage_property(bad,o,baseline)
                    except AssertionError:controls['CRC_valid_stage1_rollback']='REJECTED'
                    else:raise AssertionError('late-cut stage rollback was not detected')
                    bad=copy.deepcopy(s);payload=bytearray(get(2048+2*1024,1024));payload[0]^=1;bad['chunk_sha256']['2']=R.sha(payload)
                    try:stage_property(bad,o,baseline)
                    except AssertionError:controls['actual_one_bit_live_chunk_corruption']='REJECTED'
                    else:raise AssertionError('live timeline corruption was not detected')
                predictions+=1
    assert len(new)==12 and len(bases)==14
    assert collections.Counter(r['label'] for r in new)=={'cut_unit':4,'error_write':4,'second_cut':4}
    summary=json.loads((root/'core-respool-fill/summary-000.json').read_text())
    for name,bp in summary['bounded_plans'].items():
        assert bp['op_units']==bp['op_calls']==1028 and bp['barriers']==5
        assert bp['setup_units']==(0 if name.endswith('/-') else 1)
        assert bp['cut_units']==list(range(10))+[15,16,17,31,32,33,63,64,65,127,128,129,255,256,257,511,512,513]+list(range(1020,1029))
        delta=bp['v186_02_fill']
        if not name.endswith('/-'):
            assert delta=={'added_cut_units':[1020],'added_error_write_calls':[1019],'removed_cut_units':[1029],'removed_error_write_calls':[1028]}
        else:assert all(not v for v in delta.values())
    for b in bases:
        if b['index']!=0:continue
        family='core-respool-fill' if b['binding']=='crash_core' else 'respool-v3-fill'
        declared=json.loads((root/family/'summary-000.json').read_text())['bounded_plans']['/'.join(b['scenario'])]
        bp=complete[(b['binding'],tuple(b['scenario']),b['initial_sha256'])]
        assert all(declared[k]==v for k,v in bp.items())
    return {'fill_runs':new,'full_projection_replay':parts,'second_bases_match_prior':bases,'raw_snapshots_bound':snapshots,'precommit_stage_clear_and_live_A_B_predictions':predictions,'causal_controls':controls,'errors':[],'scope':'Twelve missing coordinates only,201 plans each; partial-copy pre-index-commit stage-cleared mount/live timeline property. Not all operation rows or full any-subset acceptance.'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args();r=review(a.root);a.out.write_text(json.dumps(r,indent=2)+'\n');print('fill',len(r['fill_runs']),'projections',sum(x['projections'] for x in r['fill_runs']),'snapshots',r['raw_snapshots_bound'])
