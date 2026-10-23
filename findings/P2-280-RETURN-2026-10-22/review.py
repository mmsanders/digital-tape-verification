"""Offline retained-evidence review; NEVER launches Product or changes originals."""
import argparse
import copy
import hashlib
import importlib.util
import json
import ntpath
from pathlib import Path
import struct
import subprocess
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SPEC = importlib.util.spec_from_file_location('app280_oracle', ROOT/'tests/wp15_app1a_r1/oracle.py')
oracle = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(oracle)
SOURCE = '45695aa0edb8a757db5074d17c39eda12bcda888'
METHOD = 'cf7d96977e89a0692b54d273fe29b3d12223b6d5'
INVENTORY = '157055c1d72b9965e773c0a26efb93c6c5a26c7af17cbb72eb310c3a586ee734'
VERSION = '0.1.1 INGEST-1 arithmetic-profile INGEST1-AP4'
OBJECTS = {}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))


def git(repo, ref, path):
    key=(str(repo),ref,path)
    if key in OBJECTS: return OBJECTS[key]
    return subprocess.check_output(['git', '-C', str(repo), 'show', ref+':'+path])


def prime(repo, requests):
    # One read-only Git process; preserve exact blob lengths/newlines.
    raw=subprocess.check_output(['git','-C',str(repo),'cat-file','--batch'],
                                input=''.join(ref+':'+path+'\n' for ref,path in requests).encode())
    offset=0
    for ref,path in requests:
        end=raw.index(b'\n',offset);header=raw[offset:end].split()
        assert len(header)==3 and header[1]==b'blob'
        size=int(header[2]);offset=end+1
        OBJECTS[(str(repo),ref,path)]=raw[offset:offset+size]
        offset+=size;assert raw[offset:offset+1]==b'\n';offset+=1
    assert offset==len(raw)


def classify(launch, child):
    assert launch['source'] == SOURCE and launch['window_fact']
    assert len(launch['window_samples']) == 1
    sample = launch['window_samples'][0]
    assert sample['responding'] and sample['main_window_handle'] != 0
    assert sample['main_window_title'] == ''
    assert launch['close_main_window_return'] and not launch['graceful_exit']
    assert launch['forced_owned_cleanup'] and launch['exit'] == -1
    assert launch['capture_complete'] and launch['ui_interaction'] == 'UNEXECUTED'
    assert launch['visual_observation'] == 'UNEXECUTED'
    assert len(child['results']) == 1
    row = child['results'][0]
    assert row['case'] == 'P0-reported-success' and row['exit'] == 1
    assert row['expected_report_version'] == VERSION
    return dict(overall='STOP: no startup/normal-quit or positive child plumbing clearance',
                A0='owned process/window metadata observed; normal quit not established',
                P0='real child exit1; positive row failed',
                unexecuted=['P1','U0','U1','U2','N0','N1'],source_integration_clearance=False)


def controls():
    # Synthetic projections qualify this review, never represent new execution.
    l=dict(source=SOURCE,window_fact=True,window_samples=[dict(responding=True,main_window_handle=1,main_window_title='')],
           close_main_window_return=True,graceful_exit=False,forced_owned_cleanup=True,exit=-1,
           capture_complete=True,ui_interaction='UNEXECUTED',visual_observation='UNEXECUTED')
    c=dict(results=[dict(case='P0-reported-success',exit=1,expected_report_version=VERSION)])
    assert not classify(l,c)['source_integration_clearance']
    for key,value in [('source','wrong'),('graceful_exit',True),('forced_owned_cleanup',False),
                      ('exit',0),('capture_complete',False),('ui_interaction','PASS')]:
        q=copy.deepcopy(l);q[key]=value
        try: classify(q,c)
        except AssertionError: continue
        raise AssertionError('detecting control survived: '+key)
    for replacement in [[],[dict(case='P0-reported-success',exit=0,expected_report_version=VERSION)]]:
        try: classify(l,dict(results=replacement))
        except AssertionError: continue
        raise AssertionError('child detecting control survived')
    print('PASS:8 review detecting controls; ZERO app/child execution')


def review(transport, product):
    invpath=transport/'private/ACTUAL-RETURN-INVENTORY.json'
    assert sha(invpath.read_bytes()) == INVENTORY
    inv=load(invpath);assert len(inv['files']) == 23
    sources=load(transport/'SOURCE-INVENTORY.json')
    prime(product,[(ref,e['path']) for section,ref in [('app_files',SOURCE),('child_files','35b23cacae886d9b3693b7104f581d8646ea5667')] for e in sources[section]])
    names=set()
    for e in inv['files']:
        rel=Path(e['path']);assert not rel.is_absolute() and '..' not in rel.parts
        assert e['path'] not in names;names.add(e['path'])
        data=(transport/rel).read_bytes()
        assert len(data)==e['bytes'] and sha(data)==e['sha256'],e['path']
    for section,folder,ref in [('app_files','source',SOURCE),('child_files','child-source','35b23cacae886d9b3693b7104f581d8646ea5667')]:
        entries=load(transport/'SOURCE-INVENTORY.json')[section]
        assert len(entries)==(26 if section=='app_files' else 157)
        for e in entries:
            data=(transport/folder/e['path']).read_bytes()
            assert len(data)==e['bytes'] and sha(data)==e['sha256']
            assert data==git(product,ref,e['path']),e['path']
    pub=transport/'published-cf7d9697'
    admission=load(transport/'private/prelaunch-admission.private.json')
    assert admission['method']==METHOD and admission['available_bytes']>=256*1024*1024
    for e in admission['files']:
        data=(pub/e['path']).read_bytes()
        assert data==git(ROOT,METHOD,e['path'])
        assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==e['git_blob']
    assert (pub/'g1_static.py').read_bytes()==git(product,'ecca8c1304ba9511d78791e92ed35fac494f2a27','tools/app1a/g1_static.py')
    for filename,pin in [('software538-windows-portable.zip','d45b2e78d5fd3017a1a3427201605fa0d9ff747527fac37e5c3847ec346fb0fd'),
                         ('software538-build-evidence.zip','01b2c0143d817732e52fec3a466c089eb974225680d979d1340a92100892be07')]:
        assert sha((transport/'downloads'/filename).read_bytes())==pin
    bundle=transport/'portable-45695aa0';build=load(bundle/'BUILD.json')
    assert build['source_head']==SOURCE and build['child_version']==VERSION
    with zipfile.ZipFile(transport/'downloads/software538-windows-portable.zip') as z:
        assert set(z.namelist())=={'digital-tape.exe','ingest.exe','tapectl.exe','BUILD.json','README.txt'}
        for name in z.namelist(): assert z.read(name)==(bundle/name).read_bytes()
    for e in build['files']:
        data=(bundle/e['name']).read_bytes();assert len(data)==e['bytes'] and sha(data)==e['sha256']
    launchdir=transport/'private/A0-cf7d9697-01';childdir=transport/'private/P0-P1-cf7d9697-01'
    launch=load(launchdir/'launch.private.json');child=load(childdir/'RESULT.private.json')
    result=classify(launch,child);row=child['results'][0]
    assert launch['build_sha256']==sha((bundle/'BUILD.json').read_bytes())
    for e in build['files']: assert launch['pins'][e['name']]==e['sha256']
    for stream in ['stdout','stderr']:
        assert (launchdir/(stream+'.bin')).read_bytes()==b''
        assert launch[stream+'.bin_sha256']==sha(b'')
        assert row[stream+'_sha256']==sha((childdir/('P0-reported-success.'+stream)).read_bytes())
    assert launch['pid']>0 and row['pid']>0 and row['end_utc_ns']>=row['start_utc_ns']
    stderr=(childdir/'P0-reported-success.stderr').read_bytes()
    assert b'Access is denied. (os error 5)' in stderr and b'cannot read folder' not in stderr
    argv=row['argv'];assert len(argv)==10 and argv[1:2]==['--out'] and argv[3:5]==['--length','3600']
    assert argv[5]=='--report' and argv[7:9]==['--report-nonce',row['nonce']]
    for actual,expected in [(argv[0],bundle/'ingest.exe'),(argv[2],childdir/'P0-reported-success-dest'),
                            (argv[6],childdir/'control/P0-reported-success.jsonl'),(argv[9],childdir/'Music')]:
        assert ntpath.normcase(ntpath.normpath(actual))==ntpath.normcase(ntpath.normpath(str(expected)))
    assert row['binary_sha256']==build['child_pin']
    data=(childdir/'control/P0-reported-success.jsonl').read_bytes()
    parsed=oracle.parse(data,'ingest',VERSION,row['nonce'],1,['Music'])
    assert parsed and parsed['refusal']==dict(t='refusal',id='IO_FOLDER',subject='0')
    assert oracle.message('ingest',1,parsed)==('generic',None)
    assert oracle.parse(data,'ingest',VERSION,'0'*32,1,['Music']) is None
    assert not (childdir/'P0-reported-success-dest').exists()
    assert not list(childdir.glob('P1-*')) and (childdir/'foreign.txt').read_bytes()==b'UNCHANGED\n'
    audio=(childdir/'Music/song.wav').read_bytes()
    assert len(audio)==44+88200*4
    assert struct.unpack('<4sI4s4sIHHIIHH4sI',audio[:44])==(b'RIFF',36+88200*4,b'WAVE',b'fmt ',16,1,2,44100,176400,4,16,b'data',88200*4)
    result.update(source=SOURCE,method=METHOD,private_inventory_sha256=INVENTORY,
                  authenticated_private_files=23,authenticated_app_sources=26,authenticated_child_sources=157,
                  report='current nonce/version/tool, IO_FOLDER subject0, end1; generic fallback in existing oracle only',
                  source_root_cause='unclassified; retained stderr shape matches non-Unix folder canonicalization error path',
                  os_limit='receipt Windows10.0.26200 X64; exact edition/UBR and selected WebView2 version not bound',
                  UI='all actual UI controls/visual state unexecuted')
    assert result==load(HERE/'RESULT.json'), 'sanitized publication must equal actual offline review'
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--transport',type=Path);p.add_argument('--product-repo',type=Path);a=p.parse_args()
    controls()
    published=load(HERE/'RESULT.json')
    assert published['method']==METHOD and published['source']==SOURCE
    assert published['private_inventory_sha256']==INVENTORY and published['source_integration_clearance'] is False
    assert published['unexecuted']==['P1','U0','U1','U2','N0','N1']
    if a.transport:
        assert a.product_repo
        review(Path(ntpath.normpath(str(a.transport.absolute()))),a.product_repo)
