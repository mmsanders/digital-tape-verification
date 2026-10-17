"""Independent campaign-coordinate / fresh-image audit. No Product imports.

Use with the thirteen authenticated, separately unpacked artifact directories.
The original packet is optional and supports carrying forward unchanged full
image-hash computations without rehashing the load campaign's 32 MiB images.
"""
import argparse,collections,json
from pathlib import Path
import replay as R

def boundary(hist,nblocks):
    # Coordinates are operation-relative; setup callbacks stay in persistence
    # replay, but must not shift operation unit/call/barrier ordinals.
    hist=[e for e in hist if e.get('phase')=='op']
    units=[e for e in hist if e['t']=='W'];U=len(units)
    cuts=set(range(min(8,U)+1))|set(range(max(0,U-8),U+1))
    for k in range(U.bit_length()):cuts.update((2**k-1,2**k,2**k+1))
    for k in range(1024,U+1,1024):cuts.update((k-1,k,k+1))
    calls=collections.defaultdict(list);meta=set()
    for i,e in enumerate(units):
        calls[e['call']].append(i)
        if e['lba']<2048 or e['lba']==nblocks-1:meta.add(e['call'])
    for c in meta:
        for x in (min(calls[c]),max(calls[c])+1):cuts.update((x-1,x,x+1))
    n=0;bars=0
    for e in hist:
        if e['t']=='W':n+=1
        elif e['t']=='F':cuts.update((n-1,n,n+1));bars+=1
    cuts=sorted(x for x in cuts if 0<=x<=U)
    errors=set(meta)
    for x in cuts:
        for i in (x-1,x):
            if 0<=i<U:errors.add(units[i]['call'])
    order=list(calls)
    return {'op_units':U,'cut_units':cuts,'error_write_calls':sorted(order.index(c) for c in errors),'barriers':bars}

def signature(r):
    return R.canon({k:r[k] for k in ('binding','scenario','base','coordinate','initial_sha256','epoch','projections','remount_key')})+r['trace']['trace_sha256'].encode()

def audit(root,prior=None):
    out={'checksums':{},'load':{'records':0,'commands':0,'errors':[],'mutations':[]},'coordinates':[],'second_bases':[]}
    heavy=collections.defaultdict(list);newload=[];small=[]
    for bundle in sorted(p for p in root.glob('wp10-subset-*') if p.is_dir()):
        names=set()
        for l in (bundle/'SHA256SUMS').read_text().splitlines():
            h,n=l.split(None,1);assert n!='./SHA256SUMS';assert R.sha((bundle/n).read_bytes())==h,n;names.add(n.removeprefix('./'))
        actual={str(p.relative_to(bundle)) for p in bundle.rglob('*') if p.is_file() and p.name!='SHA256SUMS'}
        assert names==actual
        out['checksums'][bundle.name]=len(names)
        for p in sorted(bundle.glob('*/part-*/runs.jsonl')):
            rows=R.lines(p)
            if 'heavy' in bundle.name:
                for r in rows:
                    if r.get('plan')=='sampled':
                        assert [(q['seed'],q['draw']) for q in r['projections']]==[(s,d) for s in (1,183,3647685189) for d in range(67)]
                    heavy[(r['binding'],tuple(r['scenario']),r.get('base','fixture'))].append((p.parent,r))
            elif 'load' in bundle.name:newload+=rows
            else:small+=rows
        if 'load' not in bundle.name:continue
        for p in bundle.glob('load/part-*/remounts.jsonl'):
            for r in R.lines(p):
                out['load']['records']+=1;want=r['projection_sha256'];mut=[]
                assert r['format']=='WP10-SUBSET-REMOUNT-2' and r['fresh_image_per_command']
                for c in ('verify','dump_A','dump_B'):
                    x=r[c];out['load']['commands']+=1
                    assert x['image_sha256_before']==want
                    assert x['image_mutated']==(x['image_sha256_after']!=want)
                    assert len(x['seam_trace_sha256'])==64
                    assert all(k in x for k in ('engine','seam_writes','seam_flushes','exit','stdout','stderr'))
                    if x['image_mutated']:mut.append(c)
                assert mut==r['mutated_by']
                if mut:out['load']['mutations'].append({'part':str(p.relative_to(root)),'image':want,'commands':mut,'after':{c:r[c]['image_sha256_after'] for c in mut}})
    for key,rows in sorted(heavy.items()):
        binding,scenario,base=key
        comp=[(p,r) for p,r in rows if r.get('label') in ('complete','second_complete')]
        assert len(comp)==1,(key,len(comp))
        p,r=comp[0];hist=R.trace(p,r['trace']);raw,_=R.initial(str(p/'initial'/(r['initial_sha256']+'.img.gz')))
        bp=boundary(hist,len(raw)//512)
        labels=collections.defaultdict(set)
        bad=[]
        for pp,rr in rows:
            if 'coordinate' not in rr:continue
            for name,v in rr['coordinate'].items():
                if v!='-':labels[name].add(v)
            # U itself is the permitted end boundary, even if no subsequent
            # callback exists on which the worker can emit a CUT marker.
            if rr.get('label') in ('cut_unit','second_cut') and not rr['worker'].get('cut_fired') and rr['coordinate']['cut_op_unit']!=bp['op_units']:bad.append({'label':rr['label'],'coordinate':rr['coordinate'],'worker_op_units':rr['worker']['op_units']})
        second=base!='fixture'
        item={'binding':binding,'scenario':scenario,'base':base,'actual_operation_units':bp['op_units'],'actual_setup_units':sum(e['t']=='W' and e.get('phase')!='op' for e in hist),'expected_unit_cuts':bp['cut_units'],'observed_unit_cuts':sorted(labels['cut_op_unit']),'missing_unit_cuts':sorted(set(bp['cut_units'])-labels['cut_op_unit']),'extra_unit_cuts':sorted(labels['cut_op_unit']-set(bp['cut_units'])),'unfired_cuts':bad}
        if not second:
            item.update(expected_write_errors=bp['error_write_calls'],missing_write_errors=sorted(set(bp['error_write_calls'])-labels['error_op_call']),extra_write_errors=sorted(labels['error_op_call']-set(bp['error_write_calls'])),missing_barrier_entries=sorted(set(range(bp['barriers']))-labels['cut_op_barrier_entry']),missing_barrier_errors=sorted(set(range(bp['barriers']))-labels['error_op_barrier']))
        out['coordinates'].append(item)
        if second:
            t=r['second_cut_of'];first=heavy[(binding,scenario,'fixture')]
            matches=[rr for pp,rr in first if rr.get('coordinate',{}).get('cut_op_unit')==t['first_cut_op_unit'] and any(q['image_sha256']==t['first_image_sha256'] and q.get('mask')==t['first_mask'] and q.get('landing_order')==t['first_landing_order'] for q in rr.get('projections',[]))]
            assert matches and t['first_image_sha256']==r['initial_sha256']
            source=matches[0]
            ids=[e['id'] for e in source['epoch']['events']]
            selected=set(t['first_landing_order'])
            later=bool(selected) and any(i not in selected and i<max(selected) for i in ids)
            assert later==t['later_only']
            out['second_bases'].append({'binding':binding,'scenario':scenario,'base':base,'index':t['second_base_index'],'selection':t['base_selection'],'first_cut':t['first_cut_op_unit'],'first_mask':t['first_mask'],'first_landing_order':t['first_landing_order'],'matched_first_cut_records':len(matches)})
    basegroups=collections.defaultdict(list)
    for b in out['second_bases']:basegroups[(b['binding'],tuple(b['scenario']))].append(b)
    for k,bs in basegroups.items():
        assert len(bs)==2 and {b['index'] for b in bs}=={0,1} and len({b['base'] for b in bs})==2,k
        firstrows=[r for _,r in heavy[(*k,'fixture')] if r.get('label')=='first_cut_for_second']
        seen={};first=None;later=None;nxt=None
        for r in sorted(firstrows,key=lambda r:r['coordinate']['cut_op_unit']):
            ids=[e['id'] for e in r['epoch'].get('events',[])]
            for q in r['projections']:
                h=q['image_sha256']
                if h in seen:continue
                seen[h]=True;sel=set(q.get('landing_order',[]))
                lo=bool(sel) and any(i not in sel and i<max(sel) for i in ids)
                if first is None:first=h
                elif lo and later is None:later=h
                elif nxt is None:nxt=h
        assert {b['index']:b['base'][11:] for b in bs}=={0:first,1:later or nxt},k
    out['load'].update(runs=sum('trace' in r for r in newload),projections=sum(len(r.get('projections',[])) for r in newload),unreachable=sum('not_reachable' in r for r in newload))
    if prior:
        old=[r for p in prior.glob('load/part-*/runs.jsonl') for r in R.lines(p) if 'trace' in r]
        before=collections.Counter(signature(r) for r in old);after=collections.Counter(signature(r) for r in newload if 'trace' in r)
        out['load']['prior_math_identity']={'old_runs':len(old),'new_runs':sum(after.values()),'missing':sum((before-after).values()),'added':sum((after-before).values()),'unique_old':len(before),'unique_new':len(after),'rule':'exact coordinate/input/epoch/trace-hash/plan/projection equality; multiplicities may differ across sharding search tasks'}
        out['small_math_identity']={}
        for family in ('core','promote','dup','respool-decline'):
            old=[r for p in (prior/family).glob('part-*/runs.jsonl') for r in R.lines(p)]
            before=collections.Counter(signature(r) for r in old);after=collections.Counter(signature(r) for r in small if r['binding']==old[0]['binding'])
            out['small_math_identity'][family]={'old_runs':len(old),'new_runs':sum(after.values()),'missing':sum((before-after).values()),'added':sum((after-before).values())}
    return out

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--prior',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    out=audit(a.root,a.prior);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print('checksums',len(out['checksums']),'load',out['load']['records'],'coordinates',len(out['coordinates']))
