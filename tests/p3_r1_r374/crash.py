"""Execute the explicitly issued remaining coordinates; judge with immutable oracles."""
import copy,gzip,hashlib,importlib.util,json,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def load(path,name):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def sha(b):return hashlib.sha256(b).hexdigest()
def cpu():
    import resource
    return sum(r.ru_utime+r.ru_stime for r in (resource.getrusage(resource.RUSAGE_SELF),resource.getrusage(resource.RUSAGE_CHILDREN)))
def admit(out,start,estimate=30):
    used=608.49+cpu()-start
    size=sum(p.stat().st_size for p in out.rglob('*')if p.is_file())
    assert used+estimate<7200 and size+64*1024**2<2*1024**3,'resource stop before next case'
    return dict(prior_reported_upper_cpu=608.49,current_measured_cpu=cpu()-start,artifact_bytes=size,next_case_cpu_allowance=estimate)
def fault_review(p,r,initial,L,O):
    if r['kind']=='actual-fault-execution':O.host_fault(r)
    seam=json.loads((p/'seam-trace.json').read_text());assert seam['exit']==r['exit']
    assert r['actual_input_sha256']==r['pristine_input_sha256']==sha(initial)
    assert r['source_wav_sha256']==L.VOICE
    work=bytearray(initial);events=[];w=f=0
    for e in seam['events']:
        if e['kind']=='write':
            data=bytes.fromhex(e['data_hex']);assert len(data)==e['bytes'] and e['offset']%512==len(data)%512==0
            if e['ok']:work[e['offset']:e['offset']+len(data)]=data
            events.append(dict(t='W',ordinal=w,offset=e['offset'],bytes=e['bytes'],failed=not e['ok'],fault=e.get('fault')));w+=1
        elif e['kind']=='flush':events.append(dict(t='F',ordinal=f,os_call=e['os_call'],failed=not e['success'],os_error=e['os_error'],fault=e.get('fault')));f+=1
    assert events==r['load_events'] and (w,f)==(r['op_calls'],r['op_barriers'])
    failed=[e for e in events if e['failed']]
    if r['kind']=='actual-fault-execution':
        assert len(failed)==1
        assert (failed[0]['t'],failed[0]['ordinal'])==('W'if r['requested']['kind']=='write'else'F',r['requested']['ordinal'])
    else:assert not failed and r['exit']==0 and(w,f)==(353,52)
    assert bytes(work)==gzip.decompress((p/'image-after.img.gz').read_bytes())and sha(work)==r['image_after_sha256']
    return L.check(r['post_failure_remount'])
def faults(product,out):
    sys.path.insert(0,str(product/'tools/wp10-narrow'));import s467_load as T
    sys.path.insert(0,str(ROOT/'findings/P2-SUBSET-ROWS-2026-10-17'))
    import load_rows as L
    O=load(ROOT/'tests/wp10_narrow_supplement_r1/oracle.py','independent_fault_oracle')
    plan=json.loads((ROOT/'tests/wp10_subset_extension_r1/PLAN.json').read_text());coords=plan['load_remaining_deferred'];assert len(coords)==365
    o=T.Out(out);tmp=out/'working';tmp.mkdir();w=T.rl.make_worker(tmp);initial=w.base.read_bytes()
    assert sha(initial)==T.PLAN['baseline']['initial_sha256']
    o.put('initial.img.gz',gzip.compress(initial,6))
    source=T.sd.sha_file(T.rl.SOURCE);start=cpu();rows=[];admissions=[]
    name,r=T.run_fault(o,w,tmp,'none',None,initial,source)
    assert fault_review(out/'faults'/name,r,initial,L,O)=='new/new'
    for n,c in enumerate(coords):
        admissions.append(admit(out,start));name,r=T.run_fault(o,w,tmp,c['kind'],c['ordinal'],initial,source)
        state=fault_review(out/'faults'/name,r,initial,L,O)
        rows.append(dict(coordinate=c,state=state,result='PASS',record='faults/'+name+'/record.json'))
        if n%25==0:print(json.dumps(dict(completed=n+1,cpu=cpu()-start)),flush=True)
    bad=copy.deepcopy(r);bad['fault_fired']=False
    try:O.host_fault(bad)
    except AssertionError:control='REJECTED missing actual fault'
    else:raise AssertionError('fault control missed')
    bad=copy.deepcopy(r['post_failure_remount']);bad['dump_A']['wav_sha256']=L.VOICE;bad['dump_B']['wav_sha256']=L.EMPTY
    try:L.check(bad)
    except AssertionError:state_control='REJECTED impossible new/empty pair'
    else:raise AssertionError('state control missed')
    report=dict(executed=365,prior_executed_carried=39,total=404,failures=0,rows=rows,controls=[control,state_control],
                cpu_seconds=cpu()-start,admissions=admissions,scope='actual host fault/working effects and cold remount; not physical power loss')
    o.put_json('FAULTS.json',report);o.put_json('FILES.json',o.files)
    import shutil;shutil.rmtree(tmp)
    return report
def replay_faults(out):
    sys.path.insert(0,str(ROOT/'findings/P2-SUBSET-ROWS-2026-10-17'))
    import load_rows as L
    O=load(ROOT/'tests/wp10_narrow_supplement_r1/oracle.py','independent_fault_oracle')
    pins=json.loads((out/'FILES.json').read_text())
    for name,h in pins.items():
        p=(out/name).resolve();assert p.is_relative_to(out.resolve()) and sha(p.read_bytes())==h
    report=json.loads((out/'FAULTS.json').read_text());assert report['executed']==365 and report['failures']==0
    # Reconstruct the pristine baseline using the complete neighbor's actual successful
    # writes reversed is not sufficient: require the retained exact initial bytes.
    # The prior transport always creates this same independent provisioned baseline.
    initial=gzip.decompress((out/'initial.img.gz').read_bytes())
    plan=json.loads((ROOT/'tests/wp10_subset_extension_r1/PLAN.json').read_text())
    assert [r['coordinate']for r in report['rows']]==plan['load_remaining_deferred']
    for row in report['rows']:
        p=out/row['record'];r=json.loads(p.read_text())
        assert r['requested']['kind']==row['coordinate']['kind'] and r['requested']['ordinal']==row['coordinate']['ordinal']
        assert fault_review(p.parent,r,initial,L,O)==row['state']
    return dict(executed=365,raw_replay='PASS',cpu_seconds=report['cpu_seconds'])
def longcuts(product,out):
    sys.path.insert(0,str(product/'tests/wp10_subset_binding'));import run_respool as RR;import subset_driver as SD
    sys.path.insert(0,str(ROOT/'findings/P2-SUBSET-ROWS-2026-10-17'))
    R=load(ROOT/'findings/P2-WP10-SUBSET-R2-2026-10-17/replay.py','independent_replay374')
    CP=load(ROOT/'findings/P2-SUBSET-ROWS-2026-10-17/respool_copy.py','copy374')
    tmp=out/'working';tmp.mkdir(parents=True);ev=out/'lane4';ev.mkdir()
    c=SD.Campaign(RR,ev,RR.make_worker(tmp),tmp);rows=[];start=cpu()
    for unit in (63,64,65,127,128,129):
        admit(out,start)
        result,dev,projections=c.run(('no_lower_run','pass1'),label='no_lower_run/pass1/'+str(unit),cut_unit=str(unit));c.runs.flush()
        row=json.loads((ev/'runs.jsonl').read_text().splitlines()[-1]);hist=R.trace(ev,row['trace'])
        initial=gzip.decompress((ev/'initial'/(row['initial_sha256']+'.img.gz')).read_bytes());assert sha(initial)==row['initial_sha256']
        CP.check(initial,hist,'no_lower_run')
        actual=sum(e['t']=='W'and e.get('phase')=='op'for e in hist)
        assert actual==row['worker']['op_units']==3 and result['operation_result']=='TAPE_OK' and not result['cut_fired']
        assert all(e['t']!='CUT'for e in hist)
        rows.append(dict(requested_unit=unit,actual_units=actual,result='PROVED_UNAVAILABLE on exact no_lower_run/pass1 fixture',trace=row['trace']))
    c.close()
    report=dict(requests=6,executed_cuts=0,proved_unavailable=6,rows=rows,cpu_seconds=cpu()-start,
                scope='exact fixture completed after three units; no replacement or broader long-copy acceptance')
    (out/'LONG.json').write_text(json.dumps(report,indent=2)+'\n')
    import shutil;shutil.rmtree(tmp);return report
if __name__=='__main__':
    product=Path(sys.argv[1]).resolve();out=Path(sys.argv[2]).resolve();out.mkdir(parents=True,exist_ok=True)
    assert subprocess.check_output(['git','-C',str(product),'rev-parse','HEAD:engine'],text=True).strip()=='d96b4245e04d74078f8938744b1394c3018516f7'
    if len(sys.argv)>3 and sys.argv[3]=='long':r=longcuts(product,out)
    else:r=faults(product,out)
    print(json.dumps({k:v for k,v in r.items()if k not in ('rows','admissions')},indent=2))
