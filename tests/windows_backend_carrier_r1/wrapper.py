"""Independent carrier predicates. Pure input controls; no build or Product execution."""
import argparse
import copy
import json
from pathlib import Path
import re
import tomllib

DEPS={'serde':{'version':'1','features':['derive']},'serde_json':{'version':'1','features':['preserve_order']},
      'sha2':'0.10','getrandom':'0.3','unicode-normalization':'=0.1.25'}
MODULES={'children','drops','ingest_job','jobdir','label','messages','report','state'}

def manifest(m):
    p=m['package'];assert p['publish'] is False and p['edition']=='2021'
    assert p.get('build',False) is False,'implicit/explicit build script forbidden'
    assert not m.get('bin') and not m.get('build-dependencies') and not m.get('features')
    assert m['lib']['name']=='dtapp' and not m['lib'].get('proc-macro',False)
    assert m['dependencies']==DEPS,'only unchanged required non-GUI dependency constraints'
    assert not m.get('patch') and not m.get('replace')
    assert all(not v.get('dependencies') and not v.get('build-dependencies') for v in m.get('target',{}).values())
    return True

def wrapper(text):
    # New glue may only declare the unchanged modules/paths, no executable Rust logic.
    stripped=re.sub(r'/\*.*?\*/','',text,flags=re.S)
    stripped=re.sub(r'//[^\n]*','',stripped)
    pattern=r'\s*(?:#\[path\s*=\s*"[^"]+"\]\s*)?pub\s+mod\s+([a-z_]+)\s*;'
    names=[];pos=0
    while pos<len(stripped) and stripped[pos:].strip():
        found=re.match(pattern,stripped[pos:]);assert found,'wrapper contains uncovered logic/export/configuration'
        names.append(found[1]);pos+=found.end()
    assert len(names)==len(MODULES) and set(names)==MODULES
    return True

def lock(packages,original):
    known={(p['name'],p['version'],p.get('source')):p.get('checksum') for p in original}
    for p in packages:
        if 'source' not in p:continue # only local package identity may change; source scope reviewed separately
        assert (p['name'],p['version'],p['source']) in known
        assert p.get('checksum')==known[p['name'],p['version'],p['source']]
    return True

def controls():
    m=dict(package=dict(name='component',publish=False,edition='2021',build=False),lib=dict(name='dtapp',path='lib.rs'),dependencies=copy.deepcopy(DEPS))
    manifest(m);wrapper('\n'.join('pub mod '+n+';' for n in sorted(MODULES)))
    bad=[]
    for key,value in [('build','build.rs'),('publish',True)]:
        changed=copy.deepcopy(m);changed['package'][key]=value;bad.append(changed)
    changed=copy.deepcopy(m);changed['dependencies']['tauri']='2';bad.append(changed)
    changed=copy.deepcopy(m);changed['bin']=[dict(name='gui',path='main.rs')];bad.append(changed)
    for changed in bad:
        try:manifest(changed)
        except AssertionError:continue
        raise AssertionError('carrier hazard control survived')
    try:wrapper('pub mod state; fn main() {}')
    except AssertionError:pass
    else:raise AssertionError('uncovered logic survived')
    original=[dict(name='serde',version='1',source='registry',checksum='a')]
    lock(original,original)
    try:lock([dict(name='serde',version='2',source='registry',checksum='a')],original)
    except AssertionError:pass
    else:raise AssertionError('dependency substitution survived')
    print('PASS pure carrier manifest/wrapper/dependency causal controls; ZERO Product/build/runtime')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--manifest',type=Path);a=p.parse_args()
    if a.manifest:manifest(tomllib.loads(a.manifest.read_text(encoding='utf-8-sig')));print('PASS minimum manifest predicates; source/scope/CI review still required')
    else:controls()
