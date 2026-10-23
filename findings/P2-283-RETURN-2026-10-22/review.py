"""Offline actual542 review. No Product execution, native call or raw publication."""
import argparse
import copy
import hashlib
import importlib.util
import json
import ntpath
from pathlib import Path
import struct
import subprocess
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
sys.path.insert(0,str(ROOT/'tests/windows_app_start_r2'))
from context import admit
spec=importlib.util.spec_from_file_location('oracle283',ROOT/'tests/wp15_app1a_r1/oracle.py')
oracle=importlib.util.module_from_spec(spec);spec.loader.exec_module(oracle)
METHOD='a039fdfd2ea1304dd09d3c4ec713ff6b41b71fe7'
INVENTORY='b2048312aefa3043f07cd38a6a63ea6c60ac7991a0eb649a33a4d23fdceeaf5e'
VERSION='0.1.1 INGEST-1 arithmetic-profile INGEST1-AP4'
WAV='48f1b3c7ce7fe27a90469364f841803087a9d274a4af9a4ec8ee195a2846ac18'


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def norm(p): return ntpath.normcase(ntpath.normpath(str(p)))


def window(r):
    assert r['native_window_ready'] and r['close_posted'] and r['graceful_exit']
    assert not r['forced_owned_cleanup'] and r['exit']==0 and r['capture_complete']
    assert not r.get('error') and not r.get('capture_error')
    assert r['ui_interaction']=='UNEXECUTED' and r['page_readiness'].startswith('UNEXECUTED')
    assert r['ready_elapsed_ms']<=r['close_elapsed_ms']<=20000
    assert len(r['samples'])==3
    for i,s in enumerate(r['samples']):
        assert s['seq']==i and s['pid']==r['pid'] and s['start_ticks']==r['process_start_ticks']
        assert s['handle']==r['samples'][0]['handle'] and s['title']=='Digital Tape'
        assert s['visible'] and s['responding'] and s['top_level'] and s['owner_handle']==0 and not s['ambiguous']
        matching=[x for x in s['observed_owned_windows'] if x['title']=='Digital Tape' and x['visible'] and x['top_level'] and x['owner_handle']==0]
        assert len(matching)==1 and matching[0]['handle']==s['handle']
        assert all(x['pid']==r['pid'] for x in s['observed_owned_windows'])
        if i: assert 250<=s['elapsed_ms']-r['samples'][i-1]['elapsed_ms']<=1500 and s['utc']>r['samples'][i-1]['utc']
    assert r['samples'][-1]['elapsed_ms']-r['samples'][0]['elapsed_ms']>=1000
    f=r['preclose_owned_windows'];assert len(f)==1
    for key in ['pid','handle','title','visible','responding','top_level','owner_handle']: assert f[0][key]==r['samples'][-1][key]
    assert r['launch_utc']<r['samples'][0]['utc']<r['close_requested_utc']<r['end_utc']
    # UTC duration contains capture overhead, so <10s is a conservative quit bound here.
    import datetime
    t=lambda s:datetime.datetime.fromisoformat(s.replace('Z','+00:00'))
    assert (t(r['end_utc'])-t(r['close_requested_utc'])).total_seconds()<10


def review(r):
    inv=r/'private/ACTUAL-RETURN-INVENTORY.json';assert sha(inv)==INVENTORY
    files=load(inv)['files'];assert len(files)==38 and len({e['path'] for e in files})==38
    for e in files:
        rel=Path(e['path']);assert not rel.is_absolute() and '..' not in rel.parts
        p=r/rel;assert p.stat().st_size==e['bytes'] and sha(p)==e['sha256'],e['path']
    method=load(r/'METHOD-INVENTORY.json');assert method['commit']==METHOD and len(method['files'])==9
    for e in method['files']:
        p=r/'published-a039fdfd'/e['path'];data=p.read_bytes()
        assert data==subprocess.check_output(['git','-C',str(ROOT),'show',METHOD+':'+e['path']])
        assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==e['git_blob']
    # Original source/build/artifact admission carries from280, with retained pin recheck.
    for e in load(r/'private/intake-bindings.private.json')['files']:
        p=Path(e['path']);assert p.stat().st_size==e['bytes'] and sha(p)==e['sha256']
    appdir=r/'private/A0-r2-01';childdir=r/'private/P0-P1-r2-01'
    a=load(appdir/'launch.private.json');c=load(childdir/'RESULT.private.json');window(a)
    for ctx in [a['context'],c['context']]:
        admit(ctx);assert ctx['CurrentBuildNumber']=='26200' and ctx['UBR']==9457 and ctx['EditionID']=='Core' and ctx['DisplayVersion']=='25H2'
    assert not a['recorder_effective_admin'] and a['context']['parent_pid']==a['parent_pid']
    assert a['context']==load(appdir/'context.private.json')
    for kind in ['app','child']:
        req=load(r/f'private/{kind}-approval-request.private.json');out=load(r/f'private/{kind}-approval-result.private.json')
        assert req['tool']==out['tool']=='exec_command' and req['method']==METHOD
        assert req['request']['sandbox_permissions']=='require_escalated' and 'prefix_rule' not in req['request']
        assert out['decision'].startswith('GRANTED') and out['completion']['exit_code']==0
        assert 'No separate approval reason exposed' in out['decision_reason']
        assert 'approved-exec-command-require-escalated' in req['request']['cmd']
        assert 'published-a039fdfd' in req['request']['cmd'] and norm(req['request']['workdir'])==norm(c['context']['cwd'])
    assert (r/'private/app-helper.stdout').read_bytes()==(appdir/'launch.private.json').read_bytes()
    for stream in ['stdout','stderr']:
        p=appdir/(stream+'.bin');assert p.read_bytes()==b'' and sha(p)==a[stream+'.bin_sha256']
    assert len(c['results'])==2
    for row,expected in zip(c['results'],[0,2]):
        case=row['case'];assert row['exit']==expected and row['expected_exit']==expected and row['pid']>0
        assert row['report_version']==VERSION and not row.get('timeout') and not row.get('forced_owned_cleanup')
        argv=row['argv'];assert len(argv)==10 and argv[1]=='--out' and argv[3:5]==['--length','3600'] and argv[5]=='--report' and argv[7:9]==['--report-nonce',row['nonce']]
        assert norm(argv[2])==norm(childdir/(case+'-dest')) and norm(argv[6])==norm(childdir/'control'/(case+'.jsonl'))
        assert norm(argv[9])==norm(childdir/row['folder_name']) and norm(row['cwd'])==norm(childdir)
        assert row['binary_sha256']==a['pins']['ingest.exe']==sha(Path(argv[0]))
        report=childdir/'control'/(case+'.jsonl');parsed=oracle.parse(report.read_bytes(),'ingest',VERSION,row['nonce'],expected,[row['folder_name']])
        assert parsed is not None and parsed==row['parsed_report']
        for name,path in [('report',report),('stdout',childdir/(case+'.stdout')),('stderr',childdir/(case+'.stderr'))]:
            assert row[name]==dict(exists=True,bytes=path.stat().st_size,sha256=sha(path))
        assert row['end_utc_ns']>=row['start_utc_ns']
        if expected==0:
            dest=childdir/'P0-dest';assert sorted(p.name for p in dest.iterdir())==['audio.wav','manifest.json']
            m=load(dest/'manifest.json');data=(dest/'audio.wav').read_bytes()
            assert m['schema']==1 and m['contract']=='INGEST-1' and m['target_seconds']==3600 and m['capacity_frames']==158760000 and m['total_frames']==88200
            assert len(data)==352844 and struct.unpack('<4sI4s4sIHHIIHH4sI',data[:44])==(b'RIFF',352836,b'WAVE',b'fmt ',16,1,2,44100,176400,4,16,b'data',352800)
            assert m['wav_sha256']==sha(dest/'audio.wav') and len(m['sources'])==1 and m['sources'][0]['source_sha256']==WAV
            for name in ['audio.wav','manifest.json']: assert row['pair'][name]==dict(bytes=(dest/name).stat().st_size,sha256=sha(dest/name))
            assert oracle.message('ingest',0,parsed,True)==('success',None)
        else:
            assert parsed['refusal']['id']=='FOLDER_EMPTY' and not (childdir/'P1-dest').exists()
            assert oracle.message('ingest',2,parsed)==('folder-nonmusic','0')
    assert c['results'][0]['end_utc_ns']<c['results'][1]['start_utc_ns']
    assert sha(childdir/'Music/song.wav')==WAV and (childdir/'foreign.txt').read_bytes()==b'UNCHANGED\n'
    module=a['own_webview_modules'];assert len(module)==1 and module[0]['name']=='EmbeddedBrowserWebView.dll'
    assert module[0]['version']=='155.0.4283.62' and module[0]['sha256']=='4c0d799ae06d2de2fce8cb56d11b4e0046832476562074246a17a6e702a9f951'
    assert a['selected_webview2_runtime'].startswith('UNAVAILABLE')
    print('PASS actual38-file retained inventory,9 exact helper blobs, approvals/non-admin contexts, ordered ready/quit and direct P0/P1/report/pair. ZERO Product execution.')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--transport',type=Path);args=p.parse_args()
    if args.transport: review(Path(ntpath.normpath(str(args.transport.absolute()))))
    else:
        r=load(HERE/'RESULT.json');assert r['method']==METHOD and r['private_inventory_sha256']==INVENTORY
        assert r['actual_UI']=='UNEXECUTED' and r['scope']=='native window/normal quit + direct P0/P1 only'
        print('PASS sanitized review bounds; actual private observations unavailable in CI')
