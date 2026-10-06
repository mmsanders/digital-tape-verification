#!/usr/bin/env python3
"""Independent expectations; Software supplies only a native capture transport.

Transport command receives request.json response.json and launches the real candidate.
It must not supply PASS, expectations, finding judgments or synthetic observations.
"""
import argparse
import copy
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path
from oracle import REFUSALS, policy, trace_audit, provision_order, P2_START
from fixtures import build

def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def symbol_absent(binary, symbols):
    data=Path(binary).read_bytes()
    assert b'TAPECTL_TEST_FACTS' not in data
    assert 'tapectl_test_facts_seam' not in symbols

def capture_identity(request,response):
    # Provenance failures cannot count as killed candidate mutants.
    assert response['case']==request['case']
    assert response['capture_origin']=='native-candidate'
    assert re.fullmatch('[0-9a-f]{64}',response['binary_sha256'])
    assert re.fullmatch('[0-9a-f]{40}',response['head_sha'])
    assert response['request_sha256']==request['request_sha256']
    assert response['platform']==request['platform']
    assert response['capture_artifacts'], 'missing raw native capture'
    assert response.get('control_applied')==request.get('control')

def audit_response(request,response):
    capture_identity(request,response)
    t=response['trace']; assert t['operation']==request['command']
    assert t['platform']==request['platform']
    trace_audit(t)
    if 'expected_refusal' in request:
        assert response['exit']==3 and t.get('refusal')==request['expected_refusal']
        assert request['expected_refusal'] in response['stdout']+response['stderr']
    if request.get('required_null'):
        binds=[e for e in t['events'] if e['kind']=='engine_bind']
        assert binds and all(e['write_is_null'] for e in binds)
    if request.get('require_large_io'):
        ios=[e for e in t['events'] if e['kind'] in ('read','write')]
        assert any(e['offset']>0xffffffff for e in ios),'no authenticated >4GiB I/O'
    if request.get('required_read_failure'):
        failed=[e for e in t['events'] if e['kind']=='read' and not e['success']]
        assert failed and all(e['phase']=='service' and e['referenced_chunk'] for e in failed)
        assert response['exit']==1 and 'READ_ERROR SIDE A FRAME ' in response['stdout']+response['stderr']
    if request.get('required_flush_failure'):
        fs=[e for e in t['events'] if e['kind']=='flush' and not e['os_success']]
        assert fs and response['exit']!=0 and not t.get('success')
    if request.get('required_native_flush'):
        assert any(e['kind']=='write' for e in t['events'])
        assert any(e['kind']=='flush' and e['os_success'] for e in t['events'])
    if request.get('required_provision_order'): provision_order(t)
    if request.get('expected_failure'):
        assert response['exit']==request['expected_failure']
        assert request['failure_text'] in response['stdout']+response['stderr']
        assert not any(e['kind'] in ('write','write_open') for e in t['events'])
        assert not t.get('success')
        return True
    if not request.get('expected_refusal') and not request.get('required_read_failure') and not request.get('required_flush_failure'):
        assert response['exit']==0 and t.get('success')
    return True

def requests(platform,backing):
    base={'whole':True,'removable':True,'sd_bus':False,'bytes':64_000_000_000,
          'holds_os':False,'foreign_mount':False,'virtual':False}
    cases=[]
    for i,name in enumerate(REFUSALS):
        facts=dict(base)
        for key,val in list(zip(('whole','removable','bytes','holds_os','foreign_mount'),
                               (False,False,(1<<37)+1,True,True)))[i:]: facts[key]=val
        cases.append({'case':'safety-'+name,'command':'provision','facts':facts,
                      'erase_matches':False,'expected_refusal':name,'control':None})
        # The corresponding bad-candidate control bypasses ONLY this policy refusal;
        # other later failures are cleared, so causal identity is observable.
        isolated=dict(base)
        if i<5: isolated[('whole','removable','bytes','holds_os','foreign_mount')[i]]=(False,False,(1<<37)+1,True,True)[i]
        cases.append({'case':'safety-bypass-'+name,'command':'provision','facts':isolated,
                      'erase_matches':i!=5,'expected_refusal':name,'control':'bypass-'+name,
                      'expect_oracle_reject':True})
    for command in ('verify','play','scrub','dump'):
        cases.append({'case':'readonly-'+command,'command':command,'facts':base,'required_null':True,'control':None})
        cases.append({'case':'nonnull-'+command,'command':command,'facts':base,'required_null':True,
                      'control':'nonnull-binding','expect_oracle_reject':True})
    for command in ('provision','load','verify','dump','play','scrub','record','promote','reset-b','respool'):
        cases.append({'case':'large-'+command,'command':command,'facts':base,'require_large_io':True,'control':None})
    for name,changes,erase,refusal in (
        ('ceiling-equality',{'bytes':1<<37},True,None),
        ('ceiling-over',{'bytes':(1<<37)+1},True,'REFUSE_TOO_LARGE'),
        ('sd-bus-exception',{'removable':False,'sd_bus':True},True,None),
        ('non-removable',{'removable':False,'sd_bus':False},True,'REFUSE_NOT_REMOVABLE'),
        ('own-P1-mounted',{'mounted':['1:owned'],'layout_ok':True},True,None),
        ('foreign-P1-mounted',{'foreign_mount':True,'layout_ok':False},True,'REFUSE_FOREIGN_MOUNT'),
        ('unmount-failure',{'mounted':['1:owned'],'layout_ok':True},True,'REFUSE_FOREIGN_MOUNT'),
    ):
        case={'case':name,'command':'provision','facts':dict(base,**changes),'erase_matches':erase,
              'control':'unmount-error' if name=='unmount-failure' else None}
        if refusal: case['expected_refusal']=refusal
        cases.append(case)
    cases.extend([
        {'case':'provision-order','command':'provision','facts':base,'erase_matches':True,
         'required_provision_order':True,'seed_nonzero_mbr':True,'control':None},
        {'case':'provision-order-control','command':'provision','facts':base,'erase_matches':True,
         'required_provision_order':True,'seed_nonzero_mbr':True,'control':'mbr-first','expect_oracle_reject':True},
        {'case':'geometry-zero-write','command':'provision','facts':base,'erase_matches':True,
         'geometry_too_small':True,'expected_failure':1,'failure_text':'TAPE_ERR_GEOMETRY','control':None},
        {'case':'capacity-zero-write','command':'load','facts':base,'label_seconds':1,'source_frames':44101,
         'expected_failure':2,'failure_text':'Too long by 1 s for a 1-second cartridge','control':None},
    ])
    for mutation,token in (('torn-primary','NEEDS_REPAIR'),('both-superblocks-bad','MOUNT TAPE_ERR_'),
                           ('flipped-a-entry','MOUNT TAPE_ERR_NO_VALID_INDEX'),('degraded-b','SIDE_B_DEGRADED')):
        for control in (None,'suppress-finding'):
            cases.append({'case':mutation+('-control' if control else ''),'command':'verify','facts':base,
                          'fixture':mutation,'required_null':True,'expected_failure':1,'failure_text':token,
                          'control':control,'expect_oracle_reject':bool(control)})
    for mutation in ('clean','invalid-standby'):
        cases.append({'case':'fixture-'+mutation,'command':'verify','facts':base,'fixture':mutation,
                      'required_null':True,'control':None})
    cases.extend([
        {'case':'native-flush','command':'load','facts':base,'control':None,'required_native_flush':True},
        {'case':'native-noop-flush','command':'load','facts':base,'control':'noop-flush','expect_oracle_reject':True,'required_native_flush':True},
        {'case':'native-flush-failure','command':'load','facts':base,'control':'flush-error','required_flush_failure':True},
        {'case':'referenced-read-failure','command':'verify','facts':base,'required_null':True,
         'control':'referenced-read-error','required_read_failure':True},
        {'case':'seam-absent-production','command':'symbols','facts':base,'binary_kind':'shipped','control':None},
        {'case':'seam-present-control','command':'symbols','facts':base,'binary_kind':'test','control':None,
         'expect_oracle_reject':True},
        {'case':'production-loop-refusal','command':'verify','facts':base,'binary_kind':'shipped',
         'logical_target':'/dev/loopN','expected_refusal':'REFUSE_NOT_WHOLE_DEVICE','control':None},
        {'case':'production-virtual-refusal','command':'verify','facts':base,'binary_kind':'shipped',
         'target_setup':'actual-virtual-device','expected_refusal':
         'REFUSE_NOT_WHOLE_DEVICE' if platform=='linux' else 'REFUSE_NOT_REMOVABLE','control':None},
    ])
    for case in cases:
        case.update(platform=platform,backing=str(backing),target_bytes=64_000_000_000)
        case.setdefault('erase_matches',True)
        if case['case']=='ceiling-equality': case['target_bytes']=1<<37
        if case.get('geometry_too_small'):
            case['target_bytes']=(P2_START+6144)*512
            case['facts']=dict(base,bytes=case['target_bytes'])
            case['label_seconds']=9
        case.setdefault('binary_kind','test')
    return cases

def run(transport,platform):
    results=[]
    with tempfile.TemporaryDirectory(prefix='wp14-native-') as temp:
        root=Path(temp); backing=root/'backing.img'
        # Transport provisions its 64GB sparse target from this seed and binds its
        # actual native port. The verifier-owned seed contains referenced audio.
        build(backing,whole=True)
        for request in requests(platform,backing):
            if request['case']=='production-loop-refusal' and platform!='linux':
                # This is a Linux naming rule, not a Windows/macOS skip claim.
                continue
            if request.get('fixture'):
                fixture=root/(request['case']+'.img'); build(fixture,request['fixture'],whole=True)
                request['backing']=str(fixture); request['target_bytes']=fixture.stat().st_size
                request['facts']=dict(request['facts'],bytes=fixture.stat().st_size)
            req=root/'request.json'; out=root/'response.json'
            request['request_sha256']=hashlib.sha256(json.dumps(request,sort_keys=True).encode()).hexdigest()
            req.write_text(json.dumps(request,indent=2)+'\n')
            if out.exists(): out.unlink()
            subprocess.run([*transport,str(req),str(out)],check=True,timeout=1800)
            response=json.loads(out.read_text())
            capture_identity(request,response)
            if request['command']=='symbols':
                assert response['binary_sha256']==digest(response['binary_path'])
                assert isinstance(response['symbols'],str)
            try:
                if request['command']=='symbols':
                    symbol_absent(response['binary_path'],response['symbols'])
                else: audit_response(request,response)
            except AssertionError:
                if not request.get('expect_oracle_reject'): raise
                verdict='control-killed'
            else:
                assert not request.get('expect_oracle_reject'),'candidate control survived '+request['case']
                verdict='observations-pass'
            results.append({'case':request['case'],'verdict':verdict,'response':response})
    return {'kind':'native-candidate-cases','platform':platform,'results':results,'accepted':False}

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--platform',required=True,choices=['linux','macos','windows'])
    ap.add_argument('transport',nargs='+'); args=ap.parse_args()
    print(json.dumps(run(args.transport,args.platform),indent=2))
