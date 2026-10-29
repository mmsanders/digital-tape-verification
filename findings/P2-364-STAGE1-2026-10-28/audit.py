"""Reproduce bounded Stage1 file/source checks, with no Product execution."""
import argparse, hashlib, importlib.util, json, sys
from pathlib import Path
REPO=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(REPO/'tests/c1_closeout_r1'))
import static_check, pe_manifest

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(inputs):
    source=inputs/'baseline/host/ingest'
    static=static_check.qualify(source)
    binary=inputs/'bin/Digital-Tape'
    members={}
    for name in ('digital-tape.exe','tapectl.exe','ingest.exe'):
        p=binary/name; raw=p.read_bytes(); manifest=pe_manifest.inspect(raw)
        members[name]=dict(sha256=sha(p),bytes=len(raw),policy=pe_manifest.invoker(manifest),**manifest)
    assert members['ingest.exe']['sha256']=='3895f3f356c91b8a9fe870c33694da64bf2765df308bef118d657c1be4bb9a20'
    zipped=inputs/'candidate/software624-windows-candidate-8c142d3b9d38/Digital-Tape-Windows11-x64-make-candidate.zip'
    assert sha(zipped)=='20221d65592334baaf5c51b4ab958cc1d6c4e59b70e5caddea1cae10fc97db77'
    a6=json.loads((inputs/'a6-ci/c1-a6-offset-control/a6-result.json').read_text())
    assert a6['control']=='killed' and a6['observations'][-1]['exit']!=0
    return dict(product_input='262466d354dac779b0fda9d712a2d75b73eeec33',verification_input='5512a2d0d7bd8135f4a10016d9469c612340737a',
        ingest_tree='835078995d4e9cc2424f9ea8d6f11304b45f783f',static=static,
        source_inventory={p.relative_to(source).as_posix():sha(p) for p in sorted(source.rglob('*')) if p.is_file() and p.suffix=='.rs' and 'vendor' not in p.parts},
        candidate_head='8c142d3b9d382d5d48fd648ec53a11b0d59a805c',zip_sha256=sha(zipped),members=members,
        a6_workflow=40791300942,a6=a6,scope='offline/source and private-image controls; no physical or native experiment')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('inputs',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    a.out.write_text(json.dumps(run(a.inputs),indent=2)+'\n')
