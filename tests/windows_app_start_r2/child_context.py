"""One approved-context P0; P1 only after P0 PASS. Originals survive all assertions."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import time
from context import ROUTE,admit,current,ordinary

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('app283_oracle',HERE.parent/'wp15_app1a_r1/oracle.py')
oracle=importlib.util.module_from_spec(spec);spec.loader.exec_module(oracle)
PIN='3895f3f356c91b8a9fe870c33694da64bf2765df308bef118d657c1be4bb9a20'
WAV='48f1b3c7ce7fe27a90469364f841803087a9d274a4af9a4ec8ee195a2846ac18'
VERSION='0.1.1 INGEST-1 arithmetic-profile INGEST1-AP4'


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def capture(row,report,dest,out,err):
    # Record authentic observations BEFORE expected-exit/pair assertions.
    row['end_utc_ns']=time.time_ns()
    for stream,p in [('stdout',out),('stderr',err),('report',report)]:
        row[stream]=dict(exists=p.exists(),bytes=p.stat().st_size if p.exists() else None,sha256=sha(p) if p.exists() else None)
    row['dest_exists']=dest.exists()
    row['dest_names']=sorted(p.name for p in dest.iterdir()) if dest.is_dir() else []
    row['retained_pair']={name:dict(bytes=(dest/name).stat().st_size,sha256=sha(dest/name)) for name in ['audio.wav','manifest.json'] if (dest/name).is_file() and not (dest/name).is_symlink()}
    row['parsed_report']=oracle.parse(report.read_bytes(),'ingest',VERSION,row['nonce'],row['exit'],[row['folder_name']]) if report.exists() and row['exit'] is not None else None


def run(a):
    binary=a.binary.absolute();work=a.work.absolute();fixture=a.fixture.absolute()
    ordinary(work.parent,True);assert not work.exists();work.mkdir()
    result=dict(scope='DIRECT real S1; not app UI',context=None,results=[],verdict='STOP')
    def save(): (work/'RESULT.private.json').write_text(json.dumps(result,indent=2)+'\n')
    try:
        ordinary(work,True)
        result['context']=current(a.tool_context);save();admit(result['context'])
        ordinary(binary);ordinary(fixture)
        assert sha(binary)==PIN and sha(fixture)==WAV and fixture.stat().st_size==352844
        assert shutil.disk_usage(work).free>=256*1024*1024
        bundle=binary.parent;build=json.loads((bundle/'BUILD.json').read_text(encoding='utf-8-sig'))
        assert build['source_head']=='45695aa0edb8a757db5074d17c39eda12bcda888'
        assert build['s1_source']=='35b23cacae886d9b3693b7104f581d8646ea5667' and build['child_pin']==PIN and build['child_version']==VERSION
        assert build['s1_tree']=='835078995d4e9cc2424f9ea8d6f11304b45f783f'
        result['build_sha256']=sha(bundle/'BUILD.json')
        music=work/'Music';music.mkdir();shutil.copyfile(fixture,music/'song.wav')
        empty=work/'Empty';empty.mkdir();control=work/'control';control.mkdir()
        sentinel=work/'foreign.txt';sentinel.write_bytes(b'UNCHANGED\n')
        result['fixture_sha256']=sha(music/'song.wav');result['sentinel_sha256']=sha(sentinel);save()
        for case,folder,expected in [('P0',music,0),('P1',empty,2)]:
            nonce=os.urandom(16).hex();report=control/(case+'.jsonl');dest=work/(case+'-dest')
            out=work/(case+'.stdout');err=work/(case+'.stderr')
            argv=[str(binary),'--out',str(dest),'--length','3600','--report',str(report),'--report-nonce',nonce,str(folder)]
            row=dict(case=case,argv=argv,cwd=str(work),nonce=nonce,folder_name=folder.name,expected_exit=expected,
                     report_version=VERSION,binary_sha256=PIN,start_utc_ns=time.time_ns(),exit=None,pid=None)
            result['results'].append(row);save()
            p=None
            try:
                with out.open('xb') as stdout,err.open('xb') as stderr:
                    p=subprocess.Popen(argv,cwd=work,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr);row['pid']=p.pid;save()
                    try: row['exit']=p.wait(timeout=120)
                    except subprocess.TimeoutExpired:
                        row['timeout']=True;p.kill();row['exit']=p.wait(timeout=10)
            finally:
                if p is not None and p.poll() is None:
                    row['forced_owned_cleanup']=True;p.kill();row['exit']=p.wait(timeout=10)
                capture(row,report,dest,out,err);save()
            assert not row.get('timeout') and not row.get('forced_owned_cleanup') and row['exit']==expected
            assert sha(music/'song.wav')==WAV and sentinel.read_bytes()==b'UNCHANGED\n'
            parsed=row['parsed_report'];assert parsed is not None
            if case=='P0':
                assert row['dest_names']==['audio.wav','manifest.json']
                manifest=json.loads((dest/'manifest.json').read_bytes());audio=(dest/'audio.wav').read_bytes()
                row['pair']={n:dict(bytes=(dest/n).stat().st_size,sha256=sha(dest/n)) for n in row['dest_names']};save()
                assert manifest['schema']==1 and manifest['contract']=='INGEST-1'
                assert manifest['target_seconds']==3600 and manifest['capacity_frames']==158760000 and manifest['total_frames']==88200
                assert len(audio)==44+88200*4 and struct.unpack('<4sI4s4sIHHIIHH4sI',audio[:44])==(b'RIFF',36+88200*4,b'WAVE',b'fmt ',16,1,2,44100,176400,4,16,b'data',88200*4)
                assert manifest['wav_sha256']==sha(dest/'audio.wav') and len(manifest['sources'])==1 and manifest['sources'][0]['source_sha256']==WAV
                assert oracle.message('ingest',0,parsed,True)==('success',None)
            else:
                assert parsed['refusal']['id']=='FOLDER_EMPTY' and not dest.exists()
                assert oracle.message('ingest',2,parsed)==('folder-nonmusic','0')
            row['verdict']='PASS';save()
        result['verdict']='DIRECT P0/P1 PASS; app UI unexecuted'
    except BaseException as e:
        result['error']=repr(e);raise
    finally: save()


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--binary',type=Path,required=True);p.add_argument('--work',type=Path,required=True)
    p.add_argument('--fixture',type=Path,required=True);p.add_argument('--tool-context',required=True,choices=[ROUTE]);run(p.parse_args())
