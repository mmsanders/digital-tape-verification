"""Direct actual Product parser/static binding; unchanged independent judgments."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys,shutil,tempfile
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'tests/wp15_app1a_r1'))
import cases,parser_runner,static_controls
HEAD='ecca8c1304ba9511d78791e92ed35fac494f2a27'
def call(a,**k):return subprocess.run(list(map(str,a)),check=True,**k)
def run(product,out):
 assert subprocess.check_output(['git','-C',str(product),'rev-parse','HEAD']).decode().strip()==HEAD
 out.mkdir(parents=True,exist_ok=True);app=product/'host/app';checker=product/'tools/app1a/g1_static.py'
 static={str(p.relative_to(app)):static_controls.run(app,str(p.relative_to(app)),['python3',str(checker),'--root','.']) for p in sorted((app/'src').glob('*.rs'))}
 (out/'static.json').write_text(json.dumps(static,indent=2)+'\n')
 with tempfile.TemporaryDirectory() as t:
  bind=Path(t);(bind/'src').mkdir()
  (bind/'Cargo.toml').write_text('[package]\nname="verification201-actual-parser"\nversion="0.0.0"\nedition="2021"\n[dependencies]\nserde="1"\nserde_json={version="=1.0.154",features=["preserve_order"]}\nunicode-normalization="=0.1.25"\n[workspace]\n')
  pins={}
  for n in ['report.rs','messages.rs']:
   p=app/'src'/n;pins[n]=hashlib.sha256(p.read_bytes()).hexdigest();shutil.copyfile(p,bind/'src'/n)
  adapter=(app/'examples/parser_adapter.rs').read_text();pins['original_adapter']=hashlib.sha256(adapter.encode()).hexdigest()
  # Mechanical crate-path plumbing only. Every answer calls the actual Product code.
  adapter='mod report;mod messages;\n'+adapter.replace('use dtapp::','use crate::')
  # Move module docs before module declarations to preserve valid Rust.
  adapter=adapter.replace('mod report;mod messages;\n','',1);pos=adapter.index('use crate::');adapter=adapter[:pos]+'mod report;mod messages;\n'+adapter[pos:]
  (bind/'src/main.rs').write_text(adapter);call(['cargo','build','--release','--manifest-path',bind/'Cargo.toml'])
  rows=[c for c in cases.corpus() if c['tool']=='ingest'];raw=''.join(json.dumps(c)+'\n' for c in rows).encode()
  r=call([bind/'target/release/verification201-actual-parser'],input=raw,capture_output=True)
  got=[json.loads(l) for l in r.stdout.splitlines()];parser_runner.compare(rows,got)
  (out/'parser-stdin.jsonl').write_bytes(raw);(out/'parser-stdout.jsonl').write_bytes(r.stdout)
  result=dict(head=HEAD,source_sha256=pins,actual_parser_cases=len(rows),result='PASS',static_files=len(static),controls_per_file=5)
  (out/'BINDING.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--product',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();run(a.product.resolve(),a.out.resolve())
