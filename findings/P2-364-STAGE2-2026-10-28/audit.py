"""Rejudge retained actual command observations with the immutable S3 runner."""
import argparse, hashlib, importlib.util, json, subprocess, sys, tempfile, zipfile
from pathlib import Path
REPO=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(REPO/'tests/c1_closeout_r1'))
import pe_manifest
HEAD='8c142d3b9d382d5d48fd648ec53a11b0d59a805c'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(inputs):
    runner=REPO/'tests/wp15_cards_make_r1/runner.py'
    results={};inputs=inputs.resolve()
    with tempfile.TemporaryDirectory() as tmp:
        for platform in ('linux','windows'):
            root=inputs/'make'/('wp15-make-624-'+platform)
            if platform=='linux':root=root/'s3'
            b=json.loads((root/'BUNDLE.json').read_text());assert b['source_sha']==HEAD
            out=Path(tmp)/(platform+'.json')
            p=subprocess.run([sys.executable,'-B',str(runner),str(root),'--out',str(out)],capture_output=True)
            assert p.returncode==0,p.stderr.decode()
            judgment=json.loads(out.read_text());assert judgment==json.loads((root/'JUDGED.json').read_text())
            assert len(judgment['rows'])==(31 if platform=='linux' else 10)
            results[platform]=dict(bundle_sha256=sha(root/'BUNDLE.json'),files_authenticated=len(b['files']),
                positive_control=b['observer'],judgment=judgment,unjudged=b['unjudged'])
        negative=inputs/'make/wp15-make-624-linux/s3-negative'
        p=subprocess.run([sys.executable,'-B',str(runner),str(negative),'--out',str(Path(tmp)/'negative.json')],capture_output=True)
        assert p.returncode!=0 and b'write_callback_null' in p.stderr,p.stderr.decode()
        results['negative']=dict(exit=p.returncode,stderr=p.stderr.decode().replace(str(REPO),'<verification>'))
    build=inputs/'candidate/software624-build-evidence-8c142d3b9d38/BUILD.json'
    declaration=json.loads(build.read_text());assert declaration['source_head']==HEAD
    zipped=inputs/'candidate/software624-windows-candidate-8c142d3b9d38/Digital-Tape-Windows11-x64-make-candidate.zip'
    assert sha(zipped)=='20221d65592334baaf5c51b4ab958cc1d6c4e59b70e5caddea1cae10fc97db77'
    members={}
    with zipfile.ZipFile(zipped) as z:
        for name in ('digital-tape.exe','tapectl.exe','ingest.exe'):
            names=[n for n in z.namelist() if n.split('/')[-1]==name];assert len(names)==1
            raw=z.read(names[0]);digest=hashlib.sha256(raw).hexdigest()
            assert digest==declaration['members'][name]['sha256']
            result=pe_manifest.inspect(raw);members[name]=dict(sha256=digest,bytes=len(raw),policy=pe_manifest.invoker(result),**result)
            if name=='tapectl.exe':
                assert b'tapectl-wp15-s2+8c142d3b9d38' in raw
                assert b'TAPECTL_TEST_FACTS' not in raw and b'TAPECTL_TEST_PAUSE' not in raw
            if name=='digital-tape.exe':
                for pin in ('5186a1e05e0df753512baadf102be9d19fa8b315336c1286dfbb7cc82d85e24a','3895f3f356c91b8a9fe870c33694da64bf2765df308bef118d657c1be4bb9a20'):
                    assert pin.encode() in raw,'compiled app child pin absent'
    checks=json.loads((inputs/'product-checks.json').read_text(encoding='utf-8-sig'))
    assert all(x['state'] in ('SUCCESS','SKIPPED','NEUTRAL') for x in checks)
    g1=json.loads((inputs/'make/wp15-make-624-g1/g1-controls.json').read_text())
    assert {k:v['exit'] for k,v in g1.items()}=={'baseline':0,'ordinary-positive':0,'unix-read-negative':1,'windows-alias-negative':1,'partition-write-negative':1}
    return dict(head=HEAD,scope='bounded retained-command and byte/source disposition; C2 NOT CLEARED',
        source_tree=declaration['source_tree'],host_tree=declaration['host_tree'],engine_tree=declaration['engine_tree'],
        zip_sha256=sha(zipped),members=members,s3=results,g1=g1,product_check_states={s:sum(x['state']==s for x in checks) for s in sorted({x['state'] for x in checks})},
        artifact_metadata={n:json.loads((inputs/(n+'-artifacts.json')).read_text(encoding='utf-8-sig')) for n in ('make','candidate')})
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('inputs',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    a.out.write_text(json.dumps(run(a.inputs),indent=2)+'\n')
