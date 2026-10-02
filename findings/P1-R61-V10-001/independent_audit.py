"""Issue 141 independent identity, supersession and carried evidence audit.

Usage: python3 independent_audit.py /absolute/product /absolute/verification
Evidence inputs are siblings of this script; neither repository is modified.
"""
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import sys

P, V = map(Path, sys.argv[1:3])
E = Path(__file__).resolve().parent
HEAD = 'db31c2919523fa821cf665058f4f883bf7403aae'
PUB = '5ca24fb9c0773e715889c235c339ef035e87d63b'
IMP = 'a34d409d388707ca37678fe0cad530b7154acd4f'
def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], text=True).strip()
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):
    return json.loads(p.read_text())

assert git(P, 'rev-parse', 'HEAD') == HEAD
assert git(P, 'rev-parse', 'HEAD^{tree}') == 'c8c19d5cc8db5086b24201f9cbb8eea31fcaf47f'
assert git(V, 'rev-parse', 'HEAD') == 'd99044b55ab17c09d5413040f3f4dc5ff27fd757'
subprocess.run(['git','-C',str(V),'merge-base','--is-ancestor',PUB,'HEAD'],check=True)
history = git(P,'rev-list','--reverse','9c362949d6441a2b6920f684b150ae38d4bbd56c..HEAD').splitlines()
assert [h[:7] for h in history] == ['56619e8','a34d409','44dbf61','f31ef48','db31c29']
assert int(git(V,'show','-s','--format=%ct',PUB)) < int(git(P,'show','-s','--format=%ct',IMP))
decls = load(P/'tests/IMPORTS.json')['packages']
for path, tree in [('tests/wp10_residue_d10','e1b885301768d7b541a5704c526881a800d7116b'),('tests/wp10_backlog_r54','05aae3f798fbb6d2e6eba72f3d2e38b0c722ca9d')]:
    assert git(V,'rev-parse',PUB+':'+path) == tree
    assert git(P,'rev-parse',IMP+':'+path) == tree
    assert git(P,'rev-parse','HEAD:'+path) == tree
    assert not git(P,'log','--format=%H',IMP+'..HEAD','--',path)
    d = next(d for d in decls if d['path']==path)
    assert d['source_commit']==PUB and d['tree']==tree
for commit in history:
    files = git(P,'diff-tree','--no-commit-id','--name-only','-r',commit).splitlines()
    packages = [d['path'] for d in decls]
    touched = [f for f in files if any(f.startswith(p+'/') for p in packages)]
    engine = [f for f in files if f.startswith(('engine/','firmware/'))]
    assert not (touched and engine)
    if commit != IMP: assert not touched
for ref in ['f31ef48','HEAD']:
    assert git(P,'rev-parse',ref+':engine') == '5bbe9b4e51fabf38eaf78c9ed26faf90b0b62495'
assert not git(P,'diff','--name-only','f31ef48','HEAD','--','tests/wp10_residue_adapter/wp10res_adapter.c','tests/wp10_residue_adapter/run_product.py')
record=P/'tests/wp10_residue_d10/SUPERSESSION.json'
assert sha(record)=='6cc313cf38652874e9b734d7719e678f07c7fada8b4b5480483920c2388d91f2'
s1,s2,s3=load(record)['superseded']
def ranges(entry,key):
    return {i for g in entry[key] for lo,hi in g['index_ranges'] for i in range(lo,hi+1)}
retired=ranges(s1,'representatives'); rebinding=ranges(s2,'groups')
assert len(retired)==22604 and len(rebinding)==5110
print('PASS identity / Structural Rule 1 / unchanged verifier trees and adapter; exact head',HEAD)

# S2: compare raw line identity, then remove only the changed trace field.
old=P/'tests/wp10_backlog_r54_adapter/evidence/p1-r54-product/observations.jsonl.gz'
new=E/'s2/observations.jsonl.gz'
changed=set(); n=0
with gzip.open(old,'rb') as a, gzip.open(new,'rb') as b:
    for i,(x,y) in enumerate(itertools.zip_longest(a,b)):
        assert x is not None and y is not None
        ox,oy=json.loads(x),json.loads(y)
        assert ox['index']==oy['index']==i
        if x!=y:
            changed.add(i)
            assert i in rebinding and ox['row']==oy['row']==2
            assert ox['rerun'].pop('trace_sha256') != oy['rerun'].pop('trace_sha256')
            assert ox==oy, ('unexpected S2 field change',i)
        n+=1
assert n==68854 and changed==rebinding
print('PASS S2: exactly 5110 changed rerun.trace_sha256 only; 63744 byte-identical; final media/mounts unchanged')

# S1: independently count the retired indices and all resurrected cells in the accepted stream.
accepted=P/'tests/wp10_final_adapter/evidence/p1-r55-product/wp10-final-r54-product-observations.jsonl.gz'
fresh=E/'s1/wp10-final-r54-product-observations.jsonl.gz'
sys.path.insert(0,str(P/'tests/wp10_final_r54'))
import oracle as final_oracle
changes=set(); resurrected=[]; n=0
with gzip.open(accepted,'rb') as a, gzip.open(fresh,'rb') as b:
    for i,(x,y) in enumerate(itertools.zip_longest(a,b)):
        assert x is not None and y is not None
        ox,oy=json.loads(x),json.loads(y)
        assert ox['index']==oy['index']==i
        if x!=y: changes.add(i)
        if ox['row']==4 and final_oracle.identity_violation(ox): resurrected.append(i)
        n+=1
assert n==207584 and changes==retired
assert len(resurrected)==48 and set(resurrected)<=retired
print('PASS S1: 22604 retired and changed; all 48 resurrected cells included; 184980 byte-identical')

# WP-13: authenticate every artifact member, issued/criteria spec bytes and source inventory.
ci=E/'wp13-ci'
for f in load(ci/'manifest.json')['files']:
    p=ci/f['path']; assert p.stat().st_size==f['bytes'] and sha(p)==f['sha256']
prov=load(ci/'PROVENANCE.json'); ev=load(ci/'evidence.json')
assert prov['product_commit']==HEAD and prov['product_tree']==git(P,'rev-parse','HEAD^{tree}')
assert prov['spec_bundle']=='DRAFT-9' and prov['issued_spec_bundle']=='DRAFT-10'
for path,d in prov['issued_spec_hashes'].items(): assert sha(P/path)==d
for path,d in prov['spec_hashes'].items(): assert sha(P/'tests/embedded_readiness_draft9'/path)==d
assert prov['evidence_sha256']==sha(ci/'evidence.json')
assert prov['result_sha256']==sha(ci/'result.json')
assert load(ci/'result.json')['overall_pass']
inventory=ev['indirect_calls']['source_inventory']
assert len(inventory)==16
for row in inventory: assert sha(P/row['path'])==row['sha256']
assert (ci/'result.json').read_bytes()==(E/'wp13-independent-result.json').read_bytes()
print('PASS WP13 CI artifact member hashes, exact-head identity, DRAFT9 criteria / DRAFT10 issued reporting')
print('PASS WP13 16/16 exact candidate source inventory hashes; independent six-gate replay identical')
print('PASS independent supplementary audits')
