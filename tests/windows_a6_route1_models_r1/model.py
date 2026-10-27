"""348 independent SYNTHETIC proof-model predicates. Not a native decoder/admission tool."""
import copy

MIB = 1048576
KEYWORDS = {'ProcessThread', 'FileIO', 'FileIOInit', 'DiskIO', 'DiskIOInit', 'SplitIO'}

def need(value, reason):
    if not value:
        raise ValueError(reason)

def integer(value, minimum=0):
    return type(value) is int and value >= minimum

def mapped(mapping, offset, count):
    """Restricted simple-volume interval translation; all units explicit in model."""
    need(integer(offset) and integer(count, 1), 'UNMAPPED')
    a, b, s, c = (mapping[k] for k in ('disk_start', 'base_sectors', 'sector', 'cluster'))
    need(all(integer(x) for x in (a,b)) and integer(s,1) and integer(c,1) and c%s==0, 'UNMAPPED')
    cursor = offset
    result = []
    previous = -1
    for v, end, lcn in mapping['runs']:
        need(all(integer(x) for x in (v,end,lcn)) and end>v and v>=previous, 'LAYOUT_UNSUPPORTED')
        previous = end
        lo, hi = max(offset,v*c), min(offset+count,end*c)
        if hi<=lo:
            continue
        need(lo==cursor, 'UNMAPPED')
        start = a+b*s+lcn*c+(lo-v*c)
        result.append((mapping['disk'],start,start+hi-lo))
        cursor = hi
    need(cursor==offset+count, 'UNMAPPED')
    return sorted(result)

def judge(m):
    """Returns MODEL_CONTROL_PASS only. Inputs cannot establish native authenticity."""
    need(m['scope']=='SYNTHETIC_ONLY', 'NOT_NATIVE_DECODER')
    token=m['token']
    need(token=={'integrity':'Medium','elevated':False,'origin':'ordinary-terminal'}, 'PERMISSION_UNAVAILABLE')
    profile=m['profile']
    need(set(profile['keywords'])==KEYWORDS and len(profile['keywords'])==len(KEYWORDS)
         and profile['collectors']==1 and profile['providers']==1 and profile['stacks']==[], 'PROFILE_UNSUPPORTED')
    need(integer(profile['buffer_kib'],1) and integer(profile['buffers'],1), 'PROFILE_UNSUPPORTED')
    need(m['unknown_schema']==[] and m['pointer_header']==8, 'SCHEMA_UNKNOWN')
    f=m['file']
    need(f['length']==2*MIB and integer(f['allocation']) and f['allocation']>=f['length']
         and f['length']<=16*MIB and f['prepared_before_baseline'], 'ALLOCATION_BASELINE')
    need(not any(f[k] for k in ('sparse','compressed','reparse')) and f['fresh_output'], 'FIXTURE_UNSAFE')
    need(f['id_before'] and f['id_before']==f['id_after'] and f['cleanup_id']==f['id_before'], 'FILE_IDENTITY')
    before,after=m['before'],m['after']
    need(before==after, 'MAPPING_DRIFT')
    need(before['kind']=='basic-single-extent' and before['extent_count']==1
         and integer(before['disk']), 'LAYOUT_UNSUPPORTED')
    need(integer(f['alignment'],1) and integer(f['buffer_address'],1)
         and f['alignment']%before['sector']==0 and f['buffer_address']%f['alignment']==0, 'ALIGNMENT')
    mapped(before,0,f['length'])
    w=m['window']
    need(all(integer(v) for v in w.values()), 'LIFECYCLE')
    need(w['events_lost']==w['buffers_lost']==0, 'LOSS')
    need(w['start']<w['process_start']<w['process_end']<w['drained']<=w['stop']
         and w['stop']-w['start']<=60000, 'WINDOW')
    claimed=set(); used_edges=set(); file_ranges=[]
    requests=m['requests']; leaves=m['leaves']; edges=m['edges']
    need(len(requests)==4, 'WORKLOAD_FAILED')
    for i,q in enumerate(requests):
        need(integer(q['irp'],1) and integer(q['file_key'],1), 'IDENTITY')
        need(all(integer(q[k]) for k in ('start','end','offset','requested','returned','status')), 'COMPLETION')
        need(w['process_start']<=q['start']<q['end']<=w['process_end'], 'LIFECYCLE')
        for other in requests[:i]:
            need(q['irp']!=other['irp'] or q['start']>=other['end'] or other['start']>=q['end'], 'REUSED_REQUEST')
        need(q['requested']==512*1024 and q['returned']==q['requested'] and q['status']==0, 'COMPLETION')
        need(q['offset']%before['sector']==0 and q['requested']%before['sector']==0, 'ALIGNMENT')
        expected=mapped(before,q['offset'],q['requested']); file_ranges.append((q['offset'],q['offset']+q['requested']))
        available=[(j,e) for j,e in enumerate(edges) if q['start']<=e['time']<=q['end']]
        reachable={q['irp']}; birth={q['irp']:q['start']}; expanded=True; local=set()
        while expanded:
            expanded=False
            for j,e in available:
                if j in local or e['parent'] not in reachable:
                    continue
                need(integer(e['child'],1) and e['child'] not in reachable, 'AMBIGUOUS')
                need(e['time']>=birth[e['parent']], 'LIFECYCLE')
                birth[e['child']]=e['time']
                reachable.add(e['child']);local.add(j);expanded=True
        internal={edges[j]['parent'] for j in local}
        terminal=reachable-internal
        selected=[(j,d) for j,d in enumerate(leaves) if d['irp'] in terminal and q['start']<=d['time']<=q['end']]
        need(selected and {d['irp'] for _,d in selected}==terminal, 'NO_LINEAGE')
        need(len(selected)==len(terminal), 'AMBIGUOUS')
        actual=[]
        for j,d in selected:
            need(j not in claimed and d['file_key']==q['file_key'], 'IDENTITY')
            need(d['time']>=birth[d['irp']], 'LIFECYCLE')
            need(integer(d['bytes'],1), 'COMPLETION')
            actual.append((d['disk'],d['offset'],d['offset']+d['bytes']));claimed.add(j)
        # Adjacent leaf partitions may merge; overlap, gap, wrong disk or coordinate cannot.
        actual.sort(); merged=[]
        for interval in actual:
            if merged and merged[-1][0]==interval[0] and merged[-1][2]==interval[1]:
                merged[-1]=(interval[0],merged[-1][1],interval[2])
            else:
                merged.append(interval)
        need(merged==expected, 'UNMAPPED')
        used_edges.update(local)
    need(claimed==set(range(len(leaves))) and used_edges==set(range(len(edges))), 'UNMATCHED')
    need(sorted(file_ranges)==[(i*512*1024,(i+1)*512*1024) for i in range(4)], 'WORKLOAD_FAILED')
    read=m['read']
    need(all(integer(read[k]) for k in ('offset','requested','returned','status','start','end')), 'COMPLETION')
    need(read['offset']==f['length']-4096 and read['requested']==read['returned']==4096
         and read['status']==0, 'COMPLETION')
    need(w['process_start']<=read['start']<read['end']<=w['process_end'], 'LIFECYCLE')
    return 'MODEL_CONTROL_PASS; native decoder/profile/token/consent remain UNQUALIFIED'

def fixture():
    mapping=dict(kind='basic-single-extent',extent_count=1,disk=0,disk_start=MIB,
                 base_sectors=0,sector=512,cluster=4096,runs=[[0,512,100]])
    m=dict(scope='SYNTHETIC_ONLY',token=dict(integrity='Medium',elevated=False,origin='ordinary-terminal'),
           profile=dict(keywords=sorted(KEYWORDS),collectors=1,providers=1,stacks=[],buffer_kib=64,buffers=64),
           unknown_schema=[],pointer_header=8,
           file=dict(length=2*MIB,allocation=2*MIB,prepared_before_baseline=True,sparse=False,compressed=False,
                     reparse=False,fresh_output=True,id_before='MODEL-FILE',id_after='MODEL-FILE',cleanup_id='MODEL-FILE',
                     alignment=4096,buffer_address=0x100000),before=mapping,after=copy.deepcopy(mapping),
           window=dict(start=0,process_start=1,process_end=100,drained=110,stop=120,events_lost=0,buffers_lost=0),
           requests=[],edges=[],leaves=[],read=dict(offset=2*MIB-4096,requested=4096,returned=4096,status=0,start=90,end=95))
    for i in range(4):
        root=10*i+1; offset=i*512*1024
        m['requests'].append(dict(irp=root,file_key=2,start=10+20*i,end=25+20*i,offset=offset,requested=512*1024,returned=512*1024,status=0))
        m['edges'].append(dict(parent=root,child=root+1,time=15+20*i))
        physical=mapped(mapping,offset,512*1024)[0][1]
        m['leaves'].append(dict(irp=root+1,file_key=2,time=20+20*i,disk=0,offset=physical,bytes=512*1024))
    return m
