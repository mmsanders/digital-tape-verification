"""Verification352 final612 byte/archive audit. No extraction/launch/build/payload execution."""
import argparse,copy,hashlib,importlib.util,io,json,os,struct,subprocess,sys,zipfile
from pathlib import Path
V=Path(os.environ.get('VERIFICATION_REPO',Path(__file__).resolve().parents[2]))
sys.path.insert(0,str(V/'tests/windows_cards_receipts_r1'));import candidate as judge
SOURCE='fce1d644f03ed1220e40133be0c33bd30e519203';PACKAGER='e8f6197540cbf423428c2956a2c37687513a63e4'
ZIP='Digital-Tape-Windows11-x64-replacement-candidate.zip'
ZIPHASH='f6a908296e26db5eb17e55f89674be263b7b6afd7d6b26a3f2c30e5f721ae3ac'
APPHASH='ccae0cf5098aed601fd17b4af1c0d62a33ad28dfb734add1c5df3a67df807c96'
INGEST='3895f3f356c91b8a9fe870c33694da64bf2765df308bef118d657c1be4bb9a20'
TAPECTL='44ef26869ba2d01a8a183660a2c7a050d0e7e9ff37c40b727131512739ea6ded'
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pe(b):
    assert b[:2]==b'MZ';at=struct.unpack_from('<I',b,60)[0];assert b[at:at+4]==b'PE\0\0'
    machine=struct.unpack_from('<H',b,at+4)[0];magic=struct.unpack_from('<H',b,at+24)[0];sub=struct.unpack_from('<H',b,at+24+68)[0]
    assert machine==0x8664 and magic==0x20b;return dict(machine='AMD64',optional_header='PE32+',subsystem=sub)
def git(repo,ref):return subprocess.check_output(['git','-C',str(repo),'rev-parse',ref]).decode().strip()
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path);p.add_argument('--product',type=Path);p.add_argument('--out',type=Path);p.add_argument('--self-check',action='store_true');a=p.parse_args()
    if a.self_check:
        r=read(Path(__file__).with_name('RESULT.json'));assert r['zip']['sha256']==ZIPHASH and r['app']['sha256']==APPHASH
        assert len(r['members'])==5 and r['compilation_attempts']==1 and r['uploaded_candidates']==1
        assert r['product_executions']==0 and len(r['negative_controls'])==3
        print('PASS publication integrity; actual archive replay separately recorded; ZERO payload execution');return
    assert a.root and a.product and a.out
    root=a.root;c=root/'candidate';e=root/'build';zbytes=(c/ZIP).read_bytes();assert sha(zbytes)==ZIPHASH and len(zbytes)==2552029
    registry=read(e/'REGISTRY.draft.json');record=read(e/'RECORD.json');facts=read(e/'facts.json');attempt=read(e/'attempt.json')
    verdict=judge.check(zbytes,registry,record)
    independent=copy.deepcopy(registry)
    independent['authority']='Verification352 exact612 BUILD/ARCHIVE byte audit ONLY; source clearance6fa36426 carried; runtime UNISSUED'
    independent['allowed_claims']=['direct ingest positive','direct ingest empty-folder refusal']
    judge.check(zbytes,independent,record)
    independent_bytes=(json.dumps(independent,indent=2)+'\n').encode()
    a.out.with_name('REGISTRY.json').write_bytes(independent_bytes)
    assert read(e/'prior-attempts.json')==[] and record['final_build_count']==1 and attempt['run_attempt']==1 and attempt['exit']==0
    assert attempt['started_at']=='2026-10-28T14:12:55Z' and attempt['finished_at']=='2026-10-28T14:17:06Z'
    assert record['candidate_attempts'][0]['started_at']==attempt['started_at'] and record['candidate_attempts'][0]['finished_at']==attempt['finished_at']
    assert facts['packager_source']==PACKAGER and facts['source_head']==SOURCE
    for key,ref in [('source_tree',SOURCE+'^{tree}'),('host_app_tree',SOURCE+':host/app'),('tools_app_tree',SOURCE+':tools/app'),('engine_tree',SOURCE+':engine')]:assert facts[key]==git(a.product,ref),key
    assert git(a.product,'7d1fd979:host/app')==facts['host_app_tree']=='e658e8b227c8df08ed9cb0dbabc31852cdc48fa8'
    assert subprocess.check_output(['git','-C',str(a.product),'show',SOURCE+':host/app/Cargo.lock'])==(e/'Cargo.lock').read_bytes()
    assert sha((e/'Cargo.lock').read_bytes())==(e/'Cargo.lock.sha256').read_text().strip()
    assert read(e/'build-argv.json')==['cargo','build','--release','--locked','--bin','digital-tape']
    assert read(e/'compile-env.json')==record['compile_env'] and all(read(e/'pins-in-app.json').values())
    assert 'Finished `release` profile [optimized]' in (e/'app-build.stderr.txt').read_text()
    inv=read(c/'INVENTORY.json');assert inv==read(e/'INVENTORY.json')
    assert inv['archive']==dict(name=ZIP,bytes=len(zbytes),sha256=ZIPHASH)
    assert (c/'MANUAL-TEST-SHEET.txt').read_bytes()==(e/'MANUAL-TEST-SHEET.txt').read_bytes()
    assert (c/'MANUAL-TEST-SHEET.txt').read_text()==record['manual_sheet']
    with zipfile.ZipFile(io.BytesIO(zbytes)) as z:
        assert z.testzip() is None
        members={n:dict(bytes=len(z.read(n)),sha256=sha(z.read(n))) for n in z.namelist()}
        assert {x['name']:dict(bytes=x['bytes'],sha256=x['sha256']) for x in inv['members']}==members
        assert members['digital-tape.exe']==dict(bytes=5057536,sha256=APPHASH)
        assert members['ingest.exe']==dict(bytes=889856,sha256=INGEST) and members['tapectl.exe']==dict(bytes=493712,sha256=TAPECTL)
        build=json.loads(z.read('BUILD.json'));app=z.read('digital-tape.exe')
        assert z.read('BUILD.json')==(e/'BUILD.json').read_bytes() and z.read('README.txt')==(e/'README.txt').read_bytes()
        assert build['source_head']==SOURCE and build['packager_source']==PACKAGER and build['diagnostics_default']=='OFF'
        assert all(x.encode('ascii') in app for x in record['compile_env'].values())
        # Accepted Provenance::bound_source binds the measured exe and compiled pins
        # to sibling BUILD.json. It does not embed/claim a compile-time source hash.
        assert build['files'][0]['sha256']==sha(app) and b'--diagnostic-receipts' in app
        pes={n:pe(z.read(n)) for n in ['digital-tape.exe','ingest.exe','tapectl.exe']};assert pes['digital-tape.exe']['subsystem']==2
        assert build['preview']['demonstrated']==['direct ingest positive','direct ingest empty-folder refusal']
        assert build['preview']['ui_status']=='UNEXECUTED' and not build['preview']['make_enabled']
    runs=read(root/'runs.json')['runs'];candidate_runs=[x for x in runs if x['path']=='.github/workflows/windows-candidate-612.yml']
    assert len(candidate_runs)==1 and candidate_runs[0]['id']==40703625246 and candidate_runs[0]['run_attempt']==1
    assert not any(x['path'] in ['.github/workflows/windows-candidate-build.yml','.github/workflows/windows-candidate-585.yml'] for x in runs)
    jobs=read(root/'jobs.json')['jobs'];assert len(jobs)==2 and all(x['conclusion']=='success' for x in jobs)
    neg=[]
    for name,mutate in [('wrong old tapectl pin',lambda g,r:g['components']['tapectl.exe'].update(sha256='82798af2899e9364b9c9bfaa2021daf6cc51ccd0c6562598d50e0a86944bb7a9')),('false attempt count',lambda g,r:r.update(final_build_count=2)),('native admission promoted',lambda g,r:r['diagnostics'].update(native_session_admission='READY'))]:
        g,r=copy.deepcopy(registry),copy.deepcopy(record);mutate(g,r)
        try:judge.check(zbytes,g,r)
        except AssertionError:neg.append(name+' REJECTED');continue
        raise AssertionError(name)
    result=dict(scope='BUILD/ARCHIVE ONLY; no runtime admission',product_source=SOURCE,packager_source=PACKAGER,source_crosswalk={k:facts[k] for k in ['source_tree','host_app_tree','tools_app_tree','engine_tree']},zip=inv['archive'],app=members['digital-tape.exe'],members=members,pe_headers=pes,judge=verdict,negative_controls=neg,compilation_attempts=1,uploaded_candidates=1,children_rebuilt=0,attempt=attempt,api_candidate_artifact=12822109981,api_build_artifact=12823816475,source_integration='PR615;122SUCCESS;merged2026-10-28T05:35:10Z',candidate_ci_runs=runs,independent_registry_sha256=sha(independent_bytes),product_executions=0)
    result['retained_file_manifest']={x.relative_to(root).as_posix():dict(bytes=x.stat().st_size,sha256=sha(x.read_bytes())) for folder in [c,e] for x in sorted(folder.rglob('*')) if x.is_file()}
    result['sidecars']={n:dict(bytes=(c/n).stat().st_size,sha256=sha((c/n).read_bytes())) for n in ['INVENTORY.json','MANUAL-TEST-SHEET.txt']}
    a.out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:result[k] for k in ['zip','app','judge','negative_controls','compilation_attempts','uploaded_candidates','sidecars','product_executions']},indent=2))
if __name__=='__main__':main()
