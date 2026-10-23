"""Independent offline actual546 review; never executes Product or producer scripts."""
import argparse
import hashlib
import importlib.util
import json
import ntpath
from pathlib import Path
import struct
import subprocess
import zipfile

CANDIDATE='cd996a2e91fbbc6daca520438fef5f6c79dc94b5'
METHOD='ce8b9c114d622156ae3f4600776846baf5a0d79c'
INVENTORY='9b1b9b09dbd7efa8cc9ab2b370fbfd8d01853e8afefa904579aa47dca27c6e9f'
CHILD='3895f3f356c91b8a9fe870c33694da64bf2765df308bef118d657c1be4bb9a20'
FIXTURE='48f1b3c7ce7fe27a90469364f841803087a9d274a4af9a4ec8ee195a2846ac18'

def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):return json.loads(p.read_bytes())
def git(repo,ref,path):return subprocess.check_output(['git','-C',str(repo),'show',ref+':'+path])
def blob(b):return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def module(path,name):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def norm(s):return ntpath.normcase(ntpath.normpath(str(s)))

def review(w,v,p):
    r=w/'software546';base=r/'private/ACTUAL-01';work=base/'run'
    inv=r/'private/INVENTORY.private.json';assert len(inv.read_bytes())==13870 and sha(inv.read_bytes())==INVENTORY
    inventory=read(inv);assert inventory['candidate']==CANDIDATE and inventory['source_files_verified']==32
    entries=inventory['files'];assert len(entries)==80
    for e in entries:
        rel=Path(e['path']);assert not rel.is_absolute() and '..' not in rel.parts
        data=(r/rel).read_bytes();assert len(data)==e['bytes'] and sha(data)==e['sha256'],e['path']
    # One subsequently written return narrative is not original experiment evidence.
    assert {x.relative_to(r).as_posix() for x in r.rglob('*') if x.is_file()}=={e['path'] for e in entries}|{'private/INVENTORY.private.json','ACTUAL-RETURN.md'}
    for e in read(r/'METHOD-INVENTORY.json'):
        data=(r/'published-ce8b9c11'/e['path']).read_bytes()
        assert data==git(v,METHOD,e['path']) and blob(data)==e['blob'] and sha(data)==e['sha256']
    source=read(r/'SOURCE-GIT-BLOBS.json');assert len(source)==32
    for e in source:
        data=(r/'source'/e['path']).read_bytes();assert data==git(p,CANDIDATE,e['path']) and blob(data)==e['sha']
    with zipfile.ZipFile(r/'downloads/backend-adapter.zip') as z:
        assert set(z.namelist())=={'ADAPTER-BUILD.json','cases.json','lifecycle_adapter.exe'}
        for n in z.namelist():assert z.read(n)==(r/'adapter-cd996a2e'/n).read_bytes()
    assert sha((r/'downloads/backend-adapter.zip').read_bytes())=='a4057bcd557f4f43c7c6051d86a41712319fc1a61b8b91d8edd355359942fde1'
    assert sha((r/'downloads/backend-build-evidence.zip').read_bytes())=='d7cf951976d723707d03239a1f0db87cd2f0c53c4dc93aebc2c8cefa9e77c67e'
    with zipfile.ZipFile(r/'downloads/backend-build-evidence.zip') as z:
        build_names=z.namelist()
        assert {'rustc.txt','cargo.txt','source-tree.txt','unit.stdout','unit.stderr','binding.stdout','binding.stderr','compile.stdout','compile.stderr'}<=set(build_names)
        unit=z.read('unit.stdout').decode();binding=z.read('binding.stdout').decode()
        assert 'test result: ok.' in unit and 'test result: ok.' in binding
        for e in source:
            assert e['sha'] in z.read('source-tree.txt').decode()
    session=read(base/'SESSION.private.json')
    assert sha((base/'SESSION.private.json').read_bytes())=='c5a4efa90deb55361c23ed34285ebb6387d827a970d4810afb30c535db337dbc'
    assert session['source_head']==CANDIDATE and session['exit']==session['judge_exit']==0 and not session.get('forced_owned_cleanup')
    ctx=session['context'];assert not ctx['effective_admin'] and not ctx['token_elevated']
    assert ctx['tool_route']=='approved-exec-command-require-escalated' and ctx['CurrentBuildNumber']=='26200' and ctx['UBR']==9457
    approved=read(r/'private/approval-result.private.json');assert approved['decision'].startswith('GRANTED') and approved['completion']['exit_code']==0
    assert not approved['effective_admin'] and not approved['token_elevated']
    build=session['build'];assert build==read(r/'adapter-cd996a2e/ADAPTER-BUILD.json')
    assert build['source_head']==CANDIDATE and build['independent_method']==METHOD and build['run']=='39966646516'
    assert build['adapter_sha256']==session['driver_sha256']=='1ce482f50db4d8995f44871d2041feb5088f34d500e0dced18657793aa356066'
    assert sha((r/'adapter-cd996a2e/lifecycle_adapter.exe').read_bytes())==build['adapter_sha256']
    lock=(r/'source/host/app/Cargo.lock').read_bytes()
    assert b'\r' not in lock and sha(lock.replace(b'\n',b'\r\n'))==build['lock_sha256']
    assert sha((r/'adapter-cd996a2e/cases.json').read_bytes())==build['cases_sha256']
    lifecycle=module(v/'tests/windows_app_jobs_r1/lifecycle.py','lifecycle286')
    assert read(r/'cases.json')==read(r/'adapter-cd996a2e/cases.json')==dict(state_cases=lifecycle.CASES,sequences=lifecycle.SEQUENCES)
    trace=read(work/'trace.json');assert sha((work/'trace.json').read_bytes())=='2e6350c6885a2b8b49c071b685db5fa6bd9506331167e1931d01f43e2b00abb3'
    result=lifecycle.qualify(trace,CANDIDATE)
    argv=session['argv'];assert len(argv)==5 and norm(argv[0])==norm(r/'adapter-cd996a2e/lifecycle_adapter.exe') and norm(argv[1])==norm(work)
    assert sha(Path(argv[3]).read_bytes())==CHILD and sha(Path(argv[4]).read_bytes())==FIXTURE
    assert norm(session['cwd'])==norm(base) and session['pid']>0
    assert session['start_ns']<session['end_ns'] and (session['end_ns']-session['start_ns'])/1e9<300
    oracle=module(v/'tests/wp15_app1a_r1/oracle.py','oracle286')
    rows=read(work/'trace.raw.json');assert len(rows)==2
    receipts=[];pair_sha={}
    for i,(case,exit,folder) in enumerate([('P0',0,'Music'),('P1',2,'Empty')]):
        raw=work/'raw'/case;rec=read(raw/'receipt.json');receipts.append(rec)
        assert session['start_ns']<=rec['start_ns']<rec['end_ns']<=session['end_ns']
        assert (rec['end_ns']-rec['start_ns'])/1e9<120 and rec['exit']==exit and rec['pid']>0
        assert rec['version']==lifecycle.VERSION
        args=rec['argv'];assert len(args)==11 and norm(args[0])==norm(argv[3])
        assert args[1]=='--report' and norm(args[2])==norm(rec['report']) and args[3:5]==['--report-nonce',rec['nonce']]
        assert args[5]=='--out' and norm(args[6])==norm(rec['dest']) and args[7:10]==['--length','3600','--'] and norm(args[10])==norm(work/folder)
        job=work/'app-private/jobs'/case;assert norm(rec['cwd'])==norm(job)
        assert norm(Path(rec['report']).parent)==norm(job/'control') and norm(rec['dest'])==norm(job/'out/DEST')
        for name,key in [('stdout.bin','stdout'),('stderr.bin','stderr'),('report.jsonl','report_bytes')]:
            assert (raw/name).read_bytes()==bytes(rec[key])
        parsed=oracle.parse(bytes(rec['report_bytes']),'ingest',rec['version'],rec['nonce'],exit,[folder]);assert parsed is not None
        row=rows[i];assert row['case']==case and row['drop_next']=='RunIngest' and row['checking'] and row['applied'] and row['generation']==1
        if exit==0:
            m=read(raw/'manifest.json');audio=(raw/'audio.wav').read_bytes()
            assert row['pair_present'] and row['visible']['view']=='Ready' and row['manifest']==m
            assert m['schema']==1 and m['contract']=='INGEST-1' and m['target_seconds']==3600 and m['capacity_frames']==158760000 and m['total_frames']==88200
            assert len(audio)==352844 and struct.unpack('<4sI4s4sIHHIIHH4sI',audio[:44])==(b'RIFF',352836,b'WAVE',b'fmt ',16,1,2,44100,176400,4,16,b'data',352800)
            assert sha(audio)==m['wav_sha256'] and len(m['sources'])==1 and m['sources'][0]['source_sha256']==FIXTURE
            assert oracle.message('ingest',0,parsed,True)==('success',None)
            pair_sha={n:sha((raw/n).read_bytes()) for n in ['audio.wav','manifest.json']}
        else:
            assert row['pair_present'] is False and row['visible']['view']=='Problem' and row['refusal']=='FOLDER_EMPTY'
            assert parsed['refusal']['id']=='FOLDER_EMPTY' and oracle.message('ingest',2,parsed)==('folder-nonmusic','0')
            assert not (raw/'audio.wav').exists() and not (raw/'manifest.json').exists()
        assert row['visible']['details']==bytes(rec['stderr']).decode() and not row['visible']['make_enabled']
        assert not job.exists()
    assert receipts[0]['end_ns']<receipts[1]['start_ns'] and receipts[0]['nonce']!=receipts[1]['nonce']
    files=read(work/'filesystem.private.json');assert files['completed_removed']==[True,True] and files['superseded_removed']
    assert files['collision_exists_after_cleanup'] is False
    assert bytes(files['collision_marker_original'])==b'digital-tape app job directory v1\n'
    assert (work/'foreign.txt').read_bytes()==b'UNCHANGED\n' and sha((work/'foreign.txt').read_bytes())==files['sentinel_sha256']
    assert (work/'app-private/jobs/foreign/keep').read_bytes()==bytes(files['foreign_bytes'])==b'FOREIGN\n'
    assert sha((work/'Music/song.wav').read_bytes())==files['source_sha256']==FIXTURE
    assert sorted(x.name for x in (work/'app-private/jobs').iterdir())==['foreign']
    return dict(candidate=CANDIDATE,method=METHOD,inventory_files=80,inventory_sha256=INVENTORY,
                supplemental_return_sha256=sha((r/'ACTUAL-RETURN.md').read_bytes()),
                source_blobs=32,method_files=3,build_lock_checkout='exact Git LF to Windows CRLF',typed_state_cases=8,delivery_sequences=5,
                actual_p0_exit=0,actual_p1_exit=2,actual_p1_id='FOLDER_EMPTY',pair_sha256=pair_sha,
                predicate=result,scope='backend lifecycle/ordinary jobs/real production runner only',
                actual_UI='UNEXECUTED',product_executions_in_review=0)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--workspace',type=Path,required=True);p.add_argument('--verification',type=Path,required=True)
    p.add_argument('--product',type=Path,required=True);p.add_argument('--output',type=Path);a=p.parse_args()
    result=review(a.workspace,a.verification,a.product);text=json.dumps(result,indent=2)+'\n'
    if a.output:a.output.write_text(text)
    print(text)
