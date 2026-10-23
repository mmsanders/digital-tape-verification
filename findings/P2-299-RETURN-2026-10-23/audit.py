"""Independent read-only qualification of retained 557 originals. No Product execution."""
import argparse, hashlib, importlib.util, json, re, subprocess, zipfile
from pathlib import Path

HEAD='32e742321180a69a9d74ce1cd3b712e219cdf25d'
MAIN='c421c84e701182b94ebb9cfb5437c3274d58aec2'
REF='bf2381c9c187c14ce65cc501b13f9eb512c99693'
VER='d8276b033c6c1aa553d823d0d993ed407cbfc726'
SIZE=20972032
CASES=['positive','initial-query-failure','unknown-safety','policy-refusal','provision-failure','load-failure','verify-failure','media-change','media-remove','query-failure']
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def git(repo,*args):return subprocess.check_output(['git','-C',str(repo),*args])
def audit(root,product,verification):
    r=root/'software557';base=r/'private/MATRIX-01'
    inv=json.loads((base/'INVENTORY.private.json').read_text())
    assert sha(base/'INVENTORY.private.json')=='b20412468c9f5d84e47bf3390db9f3495d77fa5b9dde79e77576dcc15d20d36d'
    assert inv['closed'] and len(inv['files'])==108
    assert len({e['path'] for e in inv['files']})==108
    for e in inv['files']:
        p=base/e['path'];assert p.is_relative_to(base) and p.stat().st_size==e['bytes'] and sha(p)==e['sha256'],e['path']
    assert {p.relative_to(base).as_posix() for p in base.rglob('*') if p.is_file()}=={e['path'] for e in inv['files']}|{'INVENTORY.private.json'}
    assert sum(e['bytes'] for e in inv['files'])==421447994
    supplemental=json.loads((r/'SUPPLEMENTAL-INVENTORY.json').read_text())
    assert sha(r/'SUPPLEMENTAL-INVENTORY.json')=='14058089be0a23f286a80dd84940d25a1b5f76fc4695127d9f9e269d16d9b0f7'
    for e in supplemental['supplemental_files']:
        p=r/e['path'];assert p.is_relative_to(r) and p.stat().st_size==e['bytes'] and sha(p)==e['sha256']
    s=json.loads((base/'SESSION.private.json').read_text());t=json.loads((base/'trace.private.json').read_text())
    assert s['source_head']==t['source_head']==HEAD and s['matrix_attempts']==1
    assert not s['context']['token_elevated'] and not s['context']['effective_admin']
    assert s['context']['os'].startswith('Windows-11-') and s['context']['architecture']=='AMD64'
    elapsed=(s['end_ns']-s['start_ns'])/1e9;assert 0<elapsed<600
    assert [c['mode'] for c in s['children']]==['reference','composition']
    for c in s['children']:
        assert c['pid']>0 and c['exit']==0 and not c['forced_cleanup']
        assert s['start_ns']<c['start_ns']<c['end_ns']<s['end_ns']
        assert c['argv']==[str(r/'bundle-32e74232'/(c['mode']+'.exe')),str(base/'matrix'),s['fixture']]
        assert c['cwd']==str(base/'matrix')
    assert sha(Path(s['fixture']))==s['fixture_sha256']=='48f1b3c7ce7fe27a90469364f841803087a9d274a4af9a4ec8ee195a2846ac18'
    assert sha(r/'run_local.py')==s['driver_sha256']
    assert s['free_after_materialization']>=1024**3 and s['source_unchanged'] and s['sentinel_unchanged']
    twins=[p for pair in s['twins_before'].values() for p in pair]
    assert len(twins)==len({p['identity'] for p in twins})==20
    zero=hashlib.sha256(bytes(SIZE)).hexdigest()
    for p in twins:
        assert p['bytes']==SIZE and p['allocated_bytes']>=SIZE and p['initial_sha256']==zero
        assert p['ordinary_owned'] and not p['reparse'] and not p['sparse'] and not p['truncate'] and p['open_mode']=='existing'
    meta=json.loads((r/'bundle-32e74232/BUILD.json').read_text(encoding='utf-8-sig'))
    assert meta==s['build'] and meta['source_head']==HEAD and meta['reference_source']==REF and meta['executions']==0
    assert meta['method']=='a901272c91c781c9278c4abe6e36d68bcfa5fb79' and meta['port_addendum']=='420e5cf3172376c5edeb95aeb73733c84a83d201'
    with zipfile.ZipFile(r/'internal-adapters.zip') as z:
        for name,pin in meta['binaries'].items():
            assert sha(r/'bundle-32e74232'/name)==pin
            assert hashlib.sha256(z.read(name)).hexdigest()==pin
    assert git(product,'rev-parse',HEAD+'^{tree}').decode().strip()=='7ef52b3660aad8016616795acccd1b2162c5fb41'
    changed=set(git(product,'diff','--name-only',MAIN,HEAD).decode().splitlines())
    assert changed=={'.github/workflows/internal-make-core.yml','docs/REVIEW/software557/OPERATION-EXTRACTION.json','docs/REVIEW/software557/PORT-CHRONOLOGY.json',
                    *('host/internal_make/'+n for n in ['README.md','adapter.c','build.sh','core.c','core.h','observe.h','run_local.py']), 'host/tapectl.c','host/target.c','host/target.h'}
    subprocess.run(['git','-C',str(product),'merge-base','--is-ancestor',MAIN,HEAD],check=True)
    for name in ['engine','spec']:
        assert git(product,'rev-parse',HEAD+':'+name)==git(product,'rev-parse',MAIN+':'+name)
        assert git(product,'rev-parse',HEAD+':'+name).decode().strip()==meta[name+'_tree']
    assert git(product,'ls-tree','-r',HEAD,'engine','host').decode().splitlines()==meta['source_blobs']
    for path,blob in meta['reference_blobs'].items():assert git(product,'rev-parse',REF+':'+path).decode().strip()==blob
    assert git(product,'show',HEAD+':host/internal_make/run_local.py')==(r/'run_local.py').read_bytes()
    for name,pin in s['method_files'].items():
        p=r/'method'/name;data=p.read_bytes();assert sha(p)==pin
        assert data==git(verification,'show',VER+':'+name.replace('\\','/'))
    spec=importlib.util.spec_from_file_location('frozen299',r/'method/tests/windows_make_core_r1/oracle.py')
    oracle=importlib.util.module_from_spec(spec);spec.loader.exec_module(oracle)
    assert {x['case'] for x in t['rows']}==set(CASES) and len(t['rows'])==10
    summary=[]
    for row in t['rows']:
        case=row['case'];raw={};ev={};out={};hashes={}
        for i,mode in enumerate(['reference','composition']):
            prefix=base/'matrix'/f'{case}.{mode}'
            raw[mode]=json.loads(Path(str(prefix)+'.result.json').read_text())
            ev[mode]=[json.loads(x) for x in Path(str(prefix)+'.events.jsonl').read_text().splitlines()]
            out[mode]=Path(str(prefix)+'.stdout.bin').read_bytes();image=Path(str(prefix)+'.img')
            hashes[mode]=sha(image);assert image.stat().st_size==SIZE
            assert raw[mode]['source_head']==HEAD and raw[mode]['case']==case and raw[mode]['mode']==mode
            assert all(e['file_id']==s['twins_before'][case][i]['identity'] for e in ev[mode] if 'file_id' in e)
        assert hashes['reference']==hashes['composition'] and out['reference']==out['composition']
        assert raw['reference']['exit']==raw['composition']['exit']==row['exit']
        assert row['events']==ev['composition'] and row['terminal']==raw['composition']['terminal']
        assert row['open_attempt_count']==raw['composition']['open_attempt_count']
        for mode in raw:
            assert row[('baseline' if mode=='reference' else 'composition')+'_stdout_hex']==out[mode].hex()
            assert row[('baseline' if mode=='reference' else 'composition')+'_image_sha256']==hashes[mode]
        faults={mode:[e for e in ev[mode] if e.get('fault_injected')] for mode in ev}
        if case in ['provision-failure','load-failure','verify-failure']:
            assert len(faults['reference'])==len(faults['composition'])==1
            keys=['phase','op','offset','length','ordinal','result','os_error_code']
            assert {k:faults['reference'][0][k] for k in keys}=={k:faults['composition'][0][k] for k in keys}
            assert faults['composition'][0]['result']==-1 and faults['composition'][0]['os_error_code']==6
        else:assert not faults['reference'] and not faults['composition']
        if case in CASES[1:4]:assert not ev['composition'] and hashes['composition']==zero
        else:
            assert len([e for e in ev['composition'] if e['op']=='close'])==1
            if case=='positive':assert len([e for e in ev['reference'] if e['op']=='authorized-open'])==3
        oracle.check(row)
        summary.append(dict(case=case,exit=row['exit'],opens=row['open_attempt_count'],image_sha256=hashes['composition'],stdout_hex=out['composition'].hex(),
                            fault=[{k:e[k] for k in ['phase','op','offset','length','ordinal','result','os_error_code']} for e in faults['composition']]))
    q=root/'software547/preaddendum-quarantine';chron=json.loads((q/'CHRONOLOGY.json').read_text())
    for e in chron['files']:assert sha(q/Path(e['path']).name)==e['sha256']
    final=json.loads(git(product,'show',HEAD+':docs/REVIEW/software557/PORT-CHRONOLOGY.json'))
    assert not final['earlier_scaffold_built_or_run'] and final['quarantine_preserved']
    assert hashlib.sha256(git(product,'show',HEAD+':host/internal_make/adapter.c')).hexdigest()==final['candidate_adapter_sha256']
    return dict(candidate=HEAD,product_main=MAIN,verification_main=VER,original_files=108,original_bytes=421447994,
                inventory_sha256=sha(base/'INVENTORY.private.json'),elapsed_seconds=elapsed,rows=summary,
                no_Product_execution=True,scope='retained ordinary-file internal component ONLY',
                chronology='Pre-addendum unbuilt private scaffold retained; no retroactive test-first claim. Final published port follows independent302.')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    result=audit(a.root,a.root/'Digital-Tape',a.root/'verification277-local')
    a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
