"""Trace-level re-spool live-set/copy-before-index proof, not a model replay.

The full durability projection/hash replay is carried from191/195. This adds
independent operation conditions on actual raw write payloads and successful
barriers. It uses no Product code and does not materialize projected images.
"""
import argparse,collections,copy,json,struct,sys
from pathlib import Path
import rows as R
sys.path.insert(0,str(R.ROOT/'tests/respool_full_draft8'))
import fixture
B=fixture.BASE
PATTERNS=[fixture.pattern_block(10,i) for i in range(2048)]

def compact(meta,n):
    return dict(block_count=n,primary_hex=meta[0].hex(),mirror_hex=meta[n-1].hex(),slot_prefix_hex=[(meta[l]+meta[l+1]).hex() for l in (8,136,264,392)])

def check(raw,hist,kind):
    n=len(raw)//512;lb=(0,n-1,8,9,136,137,264,265,392,393)
    meta={l:raw[l*512:(l+1)*512] for l in lb};current=fixture.from_compact(compact(meta,n));sb=B.select_sb(current);H=struct.unpack_from('<I',sb,56)[0]
    aa=B.live_slot(current,0);bb=B.live_slot(current,1);assert aa is not None and bb is not None
    livea=B.entry_chunks(B.parse_entries(current.slots[aa]));liveb=B.entry_chunks(B.parse_entries(current.slots[bb]));initial_a=current.slots[:2]
    good=set();pending=set();copied=0;commits=0;dirty=False
    if kind=='v3_003':
        for c in (10,12):
            for i,p in enumerate(PATTERNS):
                l=2048+c*1024+i
                if raw[l*512:(l+1)*512]==p:good.add(l)
        # The actual restored base itself must have the original logical timeline.
        es=B.parse_entries(current.slots[bb]);assert es in [[(10,0,262144)],[(12,0,262144)]]
        start=2048+es[0][0]*1024;assert all(start+i in good for i in range(2048))
    else:
        # Only the logical40-byte payload is normative for the decline copy.
        l=2048+10*1024
        if raw[l*512:l*512+40]==fixture.pattern_bytes(31,40):good.add(l)
    for e in hist:
        if e['t']=='W':
            l=e['lba'];p=bytes.fromhex(e['hex'])
            if 2048<=l<n-1:
                c=(l-2048)//1024;assert c>=H and c not in livea|liveb,('copy overlaps protected/live set',l,H,sorted(liveb))
                if kind=='v3_003':
                    assert c in (10,11,12,13);base=10 if c<12 else 12;offset=l-(2048+base*1024);assert p==PATTERNS[offset],'copied PCM byte mismatch'
                else:assert c==10 and p[:40]==fixture.pattern_bytes(31,40),'decline logical copy'
                if e['ack']:pending.add(l)
                copied+=1
            elif l in meta:
                if l in (265,393) and e.get('phase')=='op':
                    first,start,frames=struct.unpack_from('<III',p)
                    assert start==0 and frames>0
                    base=2048+first*1024;count=(frames+127)//128
                    assert all(base+i in good for i in range(count)),'index entry attempted before complete durable copy'
                if e['ack']:meta[l]=p;dirty=True
        elif e['t']=='F' and e['ok']:
            good.update(pending);pending.clear()
            if dirty:
                now=fixture.from_compact(compact(meta,n));assert now.slots[:2]==initial_a
                assert B.select_sb(now)==sb
                j=B.live_slot(now,1);assert j is not None
                if now.slots[j]!=current.slots[bb]:
                    es=B.parse_entries(now.slots[j]);assert len(es)==1
                    first,start,frames=es[0];assert start==0
                    # Every newly selected logical data block was already durable
                    # (or independently correct in the actual restored base).
                    count=(frames+127)//128;base=2048+first*1024
                    assert all(base+i in good for i in range(count)),'index published before complete durable copy'
                    commits+=1
                current=now;bb=j;liveb=B.entry_chunks(B.parse_entries(now.slots[j]));dirty=False
    return {'copy_units_checked':copied,'new_index_commits_checked':commits}

def run(root,out):
    result={'scope':'actual trace payload/live-range/durable-before-index predicates, prior model replay carried','traces':0,'copy_units':0,'index_commits':0,'failures':[],'controls':{}};seen=set();control=None
    for part in sorted(root.glob('wp10-subset-*/respool-*/part-*')):
      for r in R.lines(part/'runs.jsonl'):
        if 'trace' not in r:continue
        key=(r['initial_sha256'],r['trace']['trace_sha256'])
        if key in seen:continue
        seen.add(key);raw=R.initial(str(part/'initial'/(r['initial_sha256']+'.img.gz')));h=R.trace(part,r)
        try:
            x=check(raw,h,r['scenario'][0]);result['traces']+=1;result['copy_units']+=x['copy_units_checked'];result['index_commits']+=x['new_index_commits_checked']
            if control is None and x['copy_units_checked']>0:control=(raw,h,r['scenario'][0])
        except Exception as e:result['failures'].append({'part':str(part.relative_to(root)),'scenario':r['scenario'],'base':r['base'],'trace':key[1],'error':str(e)})
    if control:
        raw,h,k=control
        for name in ('wrong-copy-byte','below-H-copy','missing-copy-barrier'):
            bad=copy.deepcopy(h);e=next(e for e in bad if e['t']=='W' and 2048<=e['lba']<len(raw)//512-1)
            if name=='wrong-copy-byte':e['hex']=('00' if e['hex'][:2]!='00' else '01')+e['hex'][2:]
            elif name=='below-H-copy':e['lba']=2048
            else:
                copied=False
                for i,x in enumerate(bad):
                    if x['t']=='W' and 2048<=x['lba']<len(raw)//512-1:copied=True
                    if copied and x['t']=='F' and x['ok']:del bad[i];break
            try:check(raw,bad,k)
            except Exception as e:result['controls'][name]='REJECTED: '+str(e)
            else:result['controls'][name]='UNDETECTED'
    out.write_text(json.dumps(result,indent=2)+'\n');print({k:v for k,v in result.items() if k!='failures'},'errors',len(result['failures']))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args();run(a.root,a.out)
