"""Offline original545/548 review. No Product execution, extraction or UI API."""
import argparse
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import zipfile

FLOW='7ce6a97decdc610bf52fa7233254d86e055d7597'
PREVIEW='ca8444975213da99d756694add762883cae7d004'
INV545='d3d6243fd61f6cb20e1f2a17e0654b8d9b400b682b1615528da54a6e7770202e'
INV548='abbd7994b317fc53946830689e5adbdbf104867eda4855b11dae34fd8a097c1c'
ZIP548='6092ae4d744b11d8bc8db7abfcd3a38e8cb203db13cc9fcfe0b5f720a9e86629'

def sha(b): return hashlib.sha256(b).hexdigest()
def read(p): return json.loads(p.read_bytes())
def git(repo, ref, path):
    return subprocess.check_output(['git','-C',str(repo),'show',ref+':'+path])
def blob(b): return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def load(p,name):
    spec=importlib.util.spec_from_file_location(name,p)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def methods(root,sub,commit,repo,key):
    rows=read(root/'METHOD-INVENTORY.json')
    for e in rows:
        data=(root/sub/e['path']).read_bytes()
        assert sha(data)==e['sha256'] and blob(data)==e[key]
        assert data==git(repo,commit,e['path']), 'publication mismatch'
    return len(rows)

def review(workspace,repo):
    flow=workspace/'software545';preview=workspace/'software548'
    inv=flow/'private/INVENTORY.private.json'
    assert len(inv.read_bytes())==2784 and sha(inv.read_bytes())==INV545
    rows=read(inv);assert len(rows)==17
    names=set()
    for e in rows:
        p=flow/e['path'];assert p.is_relative_to(flow) and p.is_file()
        data=p.read_bytes();assert len(data)==e['bytes'] and sha(data)==e['sha256']
        names.add(e['path'])
    actual={p.relative_to(flow).as_posix() for p in flow.rglob('*') if p.is_file()}
    assert actual==names|{'private/INVENTORY.private.json'},'unlisted UI evidence'
    assert methods(flow,'published-7ce6a97d',FLOW,repo,'git_blob')==6
    session=read(flow/'private/UI-01/session.private.json')
    stop=read(flow/'private/UI-STOP.private.json')
    request=read(flow/'private/approval-request.private.json')
    context=session['context']
    assert context['token_elevated'] is False and context['effective_admin'] is False
    assert context['tool_route']=='approved-exec-command-require-escalated'
    assert context['CurrentBuildNumber']=='26200' and context['UBR']==9457
    assert context['EditionID']=='Core' and context['DisplayVersion']=='25H2'
    assert request['method']==FLOW and request['request']['sandbox_permissions']=='require_escalated'
    assert session['source_head']=='45695aa0edb8a757db5074d17c39eda12bcda888'
    original=workspace/'software538/portable-45695aa0'
    assert session['app_sha256']==sha((original/'digital-tape.exe').read_bytes())
    assert session['build_sha256']==sha((original/'BUILD.json').read_bytes())
    assert session['pid']>0 and session['forced_cleanup'] is True and session['exit']==1
    seconds=(session['end_utc_ns']-session['start_utc_ns'])/1e9
    assert 240<=seconds<250
    for n in ['stdout.bin','stderr.bin']:
        data=(flow/'private/UI-01'/n).read_bytes()
        assert not data and session[n]==dict(bytes=0,sha256=sha(data))
    assert session['ui']=='UNEXECUTED' and session['argv']==[]
    assert stop['actual_tool_result']=='Computer Use app approval timed out'
    assert stop['ui_inputs']==[] and stop['screenshot_captured'] is False
    assert stop['page_observed'] is False and stop['normal_quit'] is False
    assert stop['relaunch'] is False and stop['inventory_observation']['title']=='Digital Tape'
    target=stop['inventory_observation']['app']
    assert target.lower()=='process:'+str(original/'digital-tape.exe').lower()
    assert stop['approval']==dict(exec_command='GRANTED/executed',ui_app_access='TIMED OUT')
    cmd=request['request']['cmd']
    for value in [session['source_head'],session['app_sha256'],'ui_process.py',str(original)]:
        assert value in cmd
    assert methods(preview,'published-ca844497',PREVIEW,repo,'blob')==4
    inv548=preview/'PREVIEW-INVENTORY.json';assert sha(inv548.read_bytes())==INV548
    pmanifest=read(inv548);data=(preview/pmanifest['archive']['name']).read_bytes()
    assert len(data)==2428934 and sha(data)==ZIP548
    assert pmanifest['archive']['bytes']==len(data) and pmanifest['archive']['sha256']==sha(data)
    package=preview/'portable-preview'
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        assert len(z.infolist())==5
        for e in pmanifest['members']:
            b=z.read(e['name']);assert len(b)==e['bytes'] and sha(b)==e['sha256']
            assert b==(package/e['name']).read_bytes()
            if e['name'].endswith('.exe'):assert b==(original/e['name']).read_bytes()
        build=json.loads(z.read('BUILD.json'))
        guide=z.read('README.txt').decode()
        old=read(original/'BUILD.json')
        assert {k:v for k,v in build.items() if k not in ['preview','scope']}=={k:v for k,v in old.items() if k!='scope'}
        assert build['preview']['ui_status']=='UNEXECUTED'
        assert 'NOT been demonstrated' in guide and 'Those commands were not driven through the app.' in guide
        assert 'Computer Use app-access approval timed out' in guide
        assert 'Full APP/INGEST/CLI A6/G2 remain' in guide
        # Reconstruct the declared deterministic ZIP in memory; never execute the producer packager.
        out=io.BytesIO()
        with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as rebuilt:
            for name in sorted(z.namelist()):
                info=zipfile.ZipInfo(name,date_time=(2026,10,23,13,50,0))
                info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
                rebuilt.writestr(info,z.read(name))
        assert out.getvalue()==data,'nonreproducible ZIP'
    oracle=load(repo/'tests/windows_preview_r1/archive.py','preview_oracle')
    registry=json.loads(git(repo,PREVIEW,'tests/windows_preview_r1/clearances.json'))
    packaging=oracle.check(data,registry)
    assert sha((preview/'package_preview.py').read_bytes())=='5d740e7035992d389d360151e3dc4dbcca729db8ed2a1ab3854624ab4b7fcc7d'
    assert (preview/'archive-check.stderr').read_bytes()==b''
    return dict(ui_disposition='BLOCKED; no UI acceptance',ui_inventory_files=17,
                ui_inventory_sha256=INV545,helper_files_authenticated=6,
                interaction_seconds=seconds,forced_cleanup=True,exit=1,
                ui_receipt_limit='Producer retained tool-error summary; no independent capture or signed tool transcript',
                argv_limit='Published supervisor leaves argv empty; command recovered only from approval request plus authenticated Popen source',
                preview_disposition='BOUNDED PACKAGING PASS; UI/foreign-cwd integration HELD',
                preview_inventory_sha256=INV548,preview_method_files_authenticated=4,
                zip_bytes=len(data),zip_sha256=ZIP548,deterministic_zip=True,
                packaging_predicate=packaging,product_executions=0)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--workspace',type=Path,required=True)
    p.add_argument('--verification',type=Path,required=True);a=p.parse_args()
    print(json.dumps(review(a.workspace,a.verification),indent=2))
