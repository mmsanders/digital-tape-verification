"""Independent retained-byte correction review. No Product execution/import."""
import argparse, copy, hashlib, importlib.util, json, subprocess, sys, tempfile, zipfile
from pathlib import Path
REPO=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(REPO/'tests/c1_closeout_r1'))
import g3, make_supplement, pe_manifest
s=importlib.util.spec_from_file_location('correction_boundary',REPO/'tests/wp15_boundary_query_r1/oracle.py')
boundary=importlib.util.module_from_spec(s);s.loader.exec_module(boundary)
HEAD='3963689230cd96e34dd0ee05e160bff6b172c774'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        while b:=f.read(1<<20):h.update(b)
    return h.hexdigest()
def rejected(fn,value):
    try:fn(value)
    except (AssertionError,KeyError,TypeError):return True
    raise AssertionError('actual-observation negative control escaped')
def run(root):
    out=dict(head=HEAD,clearance=False,s3={},supplement={},queries={})
    for name in ('make','g3','candidate'):
        run=json.loads((root/(name+'-run.json')).read_text(encoding='utf-8-sig'))
        assert run==dict(head_sha=HEAD,conclusion='success')
    with tempfile.TemporaryDirectory() as tmp:
        for platform in ('linux','windows'):
            packet=root/'make'/('wp15-make-624-'+platform)
            if platform=='linux':packet=packet/'s3'
            b=json.loads((packet/'BUNDLE.json').read_text());assert b['source_sha']==HEAD
            def raw(n):
                p=(packet/n).resolve();assert p.is_relative_to(packet.resolve())
                assert n in b['files'] and sha(p)==b['files'][n]
                return p
            result=Path(tmp)/(platform+'.json')
            p=subprocess.run([sys.executable,'-B',str(REPO/'tests/wp15_cards_make_r1/runner.py'),str(packet),'--out',str(result)],capture_output=True)
            assert p.returncode==0,p.stderr.decode()
            judged=json.loads(result.read_text());assert len(judged['rows'])==(31 if platform=='linux' else 10)
            assert judged==json.loads((packet/'JUDGED.json').read_text())
            out['s3'][platform]=judged
            supplements=[]
            for row in b.get('supplement',[]):
                r=json.loads(raw(row['record']).read_text())
                for kind in ('report','stdout','stderr'):r[kind+'_hex']=raw(row[kind]).read_bytes().hex()
                r['equivalent_pair']=False
                if 'equivalence' in row:
                    e=row['equivalence'];ps=[json.loads(raw(n).read_text()) for n in e['processes']]
                    make_supplement.old.equivalence(raw(e['stdout'][0]).read_bytes(),[raw(n).read_bytes() for n in e['stdout'][1:]],ps[0]['exit'],[x['exit'] for x in ps[1:]],sha(raw(e['make_image'])),sha(raw(e['separate_image'])))
                    r['equivalent_pair']=True
                supplements.append(dict(name=row['name'],result=getattr(make_supplement,row['kind'])(r)))
                if row['kind']=='own_p1':
                    bad=copy.deepcopy(r)
                    for event in bad['events']:
                        if event['op']=='unmount':event['ok']=False
                    assert rejected(make_supplement.own_p1,bad)
            out['supplement'][platform]=supplements
            queries=[]
            for row in b.get('queries',[]):
                r=json.loads(raw(row['observation']).read_text());r['report_hex']=raw(row['report']).read_bytes().hex()
                assert r['raw_artifact_sha256']==sha(raw(row['trace']))
                queries.append(dict(name=row['name'],result=boundary.check(r)))
                if queries[-1]['result']['id']=='HOST_QUERY_FAILED':
                    bad=copy.deepcopy(r);bad['exit']=3;assert rejected(boundary.check,bad)
            assert len(queries)==(7 if platform=='windows' else 3)
            out['queries'][platform]=queries
            standalones=[]
            for row in b.get('standalone',[]):
                r=json.loads(raw(row['record']).read_text())
                assert r['trace_complete'] and r['exit']==3 and r['refusal']=='REFUSE_FOREIGN_MOUNT'
                assert r['write_opens']==r['writes']==r['unmounts']==0
                standalones.append(dict(name=row['name'],result='refused-no-device-write'))
            if platform=='windows':assert len(standalones)==4
            out.setdefault('standalone',{})[platform]=standalones
    data=root/'g3/wp15-g3-624';reported=json.loads((data/'G3-RESULT.json').read_text());assert reported['source_sha']==HEAD
    rows=reported['rows'];assert g3.check(rows)==28
    ids={'overage-one':'INGEST_TOO_LONG','overage-192':'INGEST_TOO_LONG','protected':'SOURCE_PROTECTED','corrupt':'SOURCE_CORRUPT','nonmusic':'SOURCE_NOT_AUDIO','empty':'FOLDER_EMPTY','source-short':'SOURCE_TOO_SHORT',
         'small':'ENGINE','removed':'CARD_CHANGED','device-io':'ENGINE','host-query':'HOST_QUERY_FAILED','verify-findings':'VERIFY_FINDINGS','wav-truncated':'WAV_TRUNCATED','safety-refusal':'REFUSE_NOT_REMOVABLE','generic-make':'LABEL_INVALID','discovery-unavailable':'CARDS_ENUM_UNAVAILABLE'}
    child=[]
    for r in rows:
        if r['id'] not in ids:continue
        d=data/'cases'/r['id']
        for name,digest in r['raw_sha256'].items():assert sha(d/name)==digest,(r['id'],name)
        process=json.loads((d/'child.process.json').read_text())
        if r['id']=='discovery-unavailable':
            nonce=process['request']['nonce'];version=process['request']['version'];code=process['ran']['exit'];tool='tapectl cards'
        else:
            nonce=process['nonce'];version=process['version'];code=process['exit'];tool='ingest' if 'argv' in process else 'tapectl make'
        raw_report=(d/'child.report.jsonl').read_bytes();assert code==r['exit']
        # Authoritative independent report parser, including HOST_QUERY_FAILED.
        parsed=boundary.prior.parse(raw_report,tool,version,nonce,code,['Music','Other'])
        assert parsed and parsed['refusal']['id']==ids[r['id']],(r['id'],parsed)
        if tool=='tapectl make':
            trace=json.loads((d/'child.trace.json').read_text());assert trace['build']==HEAD
            assert trace['exit']==code
            original=[x for x in raw_report.splitlines() if json.loads(x)['t']!='stderr']
            changed=[x for x in (d/'reworded.report.jsonl').read_bytes().splitlines() if json.loads(x)['t']!='stderr']
            assert original==changed
        elif tool=='ingest':
            assert bytes(process['report_bytes'])==raw_report
            assert bytes(process['stderr'])==(d/'child.stderr').read_bytes()
            assert bytes(process['stdout'])==(d/'child.stdout').read_bytes()
        child.append(dict(id=r['id'],exit=code,refusal=parsed['refusal']['id'],message=r['message'],report_sha256=sha(d/'child.report.jsonl')))
    assert len(child)==16
    out['g3']=dict(rows=28,child_rows=child,app_rows=12,verifier_correction='empty diagnostics permitted only for zero-child rejected drops; native Show-details control not disposed')
    binary=root/'candidate/software624-windows-candidate-3963689230cd/Digital-Tape-Windows11-x64-make-candidate.zip'
    assert sha(binary)=='4d415f99806a934f3429379befc9ad6e0bd50f1688fda4e448d5e48ed8d467c4'
    build=json.loads((root/'candidate/software624-build-evidence-3963689230cd/BUILD.json').read_text());assert build['source_head']==HEAD
    members={}
    with zipfile.ZipFile(binary) as z:
        for name,expected in build['members'].items():
            paths=[n for n in z.namelist() if n.split('/')[-1]==name];assert len(paths)==1
            raw=z.read(paths[0]);assert hashlib.sha256(raw).hexdigest()==expected['sha256']
            manifest=pe_manifest.inspect(raw);members[name]=dict(sha256=expected['sha256'],bytes=len(raw),policy=pe_manifest.invoker(manifest))
    out['candidate']=dict(zip_sha256=sha(binary),members=members,engine_tree=build['engine_tree'])
    regression=root/'regression/c1-not-ready-control/_temp/verifier364-volume-query/RESULT.json'
    observed=json.loads(regression.read_text(encoding='utf-8-sig'))
    assert observed['typed_error_code']==21 and observed['baseline_mounts']>=1 and observed['failed_calls']>=1
    assert observed['failed_mounts']==0 and not observed['query_error_recorded'] and not observed['required_query_fail_stop_pass']
    assert observed['baseline_removable_model_policy']==5 and observed['failed_removable_model_policy']==0
    out['remaining_finding']=observed
    checks=json.loads((root/'product-checks.json').read_text(encoding='utf-8-sig'))
    out['product_checks']={s:sum(x['state']==s for x in checks) for s in sorted({x['state'] for x in checks})}
    return out
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('inputs',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    a.out.write_text(json.dumps(run(a.inputs),indent=2)+'\n')
