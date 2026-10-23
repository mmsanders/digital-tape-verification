"""Exactly two real bundled-child rows. NOT an app UI run or full INGEST campaign."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import struct
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent/'wp14_r1'))
from runner import make_wav
spec = importlib.util.spec_from_file_location('app_start_oracle', HERE.parent/'wp15_app1a_r1'/'oracle.py')
oracle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(oracle)

PIN = '3895f3f356c91b8a9fe870c33694da64bf2765df308bef118d657c1be4bb9a20'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def ordinary(p, directory=False):
    s=str(p.absolute())
    assert not s.startswith(('\\\\','//','/dev/')) and ':' not in s[2:]
    for q in (p.absolute(), *p.absolute().parents):
        st=q.lstat()
        assert not q.is_symlink() and not getattr(st,'st_file_attributes',0)&0x400
    assert p.is_dir() if directory else p.is_file()


def run(binary, work, version):
    ordinary(binary);ordinary(work.parent, True)
    assert sha(binary)==PIN and not work.exists()
    assert version, 'declared app child report-version pin required before running'
    work.mkdir();music=work/'Music';music.mkdir();empty=work/'Empty';empty.mkdir()
    make_wav(music/'song.wav',88200)
    control=work/'control';control.mkdir();sentinel=work/'foreign.txt';sentinel.write_bytes(b'UNCHANGED\n')
    results=[]
    try:
        for name,folder,expected in [('P0-reported-success',music,0),('P1-empty-refusal',empty,2)]:
            nonce=os.urandom(16).hex();report=control/(name+'.jsonl');dest=work/(name+'-dest')
            argv=[str(binary),'--out',str(dest),'--length','3600','--report',str(report),'--report-nonce',nonce,str(folder)]
            row=dict(case=name,argv=argv,nonce=nonce,expected_report_version=version,start_utc_ns=time.time_ns(),binary_sha256=PIN)
            results.append(row)
            with (work/(name+'.stdout')).open('xb') as out, (work/(name+'.stderr')).open('xb') as err:
                p=subprocess.Popen(argv,stdout=out,stderr=err);row['pid']=p.pid
                try: row['exit']=p.wait(timeout=120)
                except subprocess.TimeoutExpired:
                    p.kill();row['exit']=p.wait(timeout=10);row['timeout']=True
            row['end_utc_ns']=time.time_ns()
            for stream in ('stdout','stderr'):row[stream+'_sha256']=sha(work/(name+'.'+stream))
            assert not row.get('timeout') and row['exit']==expected
            assert sentinel.read_bytes()==b'UNCHANGED\n'
            data=report.read_bytes();row['report_sha256']=sha(report)
            parsed=oracle.parse(data,'ingest',version,nonce,row['exit'],[folder.name])
            assert parsed is not None, 'report/source/version/nonce/exit binding STOP; do not tune expected version'
            if expected==0:
                assert sorted(p.name for p in dest.iterdir())==['audio.wav','manifest.json']
                manifest=json.loads((dest/'manifest.json').read_bytes())
                audio=(dest/'audio.wav').read_bytes()
                assert manifest['schema']==1 and manifest['contract']=='INGEST-1'
                assert manifest['target_seconds']==3600 and manifest['capacity_frames']==158760000
                assert manifest['total_frames']==88200 and len(audio)==44+88200*4
                assert struct.unpack('<4sI4s4sIHHIIHH4sI',audio[:44]) == (b'RIFF',36+88200*4,b'WAVE',b'fmt ',16,1,2,44100,176400,4,16,b'data',88200*4)
                assert manifest['wav_sha256']==sha(dest/'audio.wav')
                assert len(manifest['sources'])==1 and manifest['sources'][0]['source_sha256']==sha(music/'song.wav')
                row['pair']={p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in dest.iterdir()}
                # Offline detecting projections only; never fake an actual child/app outcome.
                wrong_nonce='f'*32 if nonce=='0'*32 else '0'*32
                assert oracle.parse(data,'ingest',version,wrong_nonce,row['exit'],[folder.name]) is None
                assert oracle.parse(data.rsplit(b'\n',2)[0]+b'\n','ingest',version,nonce,row['exit'],[folder.name]) is None
            else:
                assert parsed['refusal']['id']=='FOLDER_EMPTY' and not dest.exists()
                assert oracle.message('ingest',2,parsed)==('folder-nonmusic','0')
    finally:
        (work/'RESULT.private.json').write_text(json.dumps(dict(scope='two DIRECT real S1 process rows, NOT GUI/plumbing through app',results=results),indent=2)+'\n')
    print('Two real child/report rows completed; no app UI, device or full INGEST acceptance claimed')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--binary',type=Path,required=True);p.add_argument('--work',type=Path,required=True);p.add_argument('--report-version',required=True)
    a=p.parse_args();run(a.binary.absolute(),a.work.absolute(),a.report_version)
