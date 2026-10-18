"""Direct actual Product parser/static binding; unchanged independent judgments."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys,shutil,tempfile
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'tests/wp15_app1a_r1'))
import cases,parser_runner,static_controls
HEAD='ecca8c1304ba9511d78791e92ed35fac494f2a27'
def call(a,**k):return subprocess.run(list(map(str,a)),check=True,**k)
def before_marker(app,checker):
 snippets={'ordinary':'fn verification_g1_control() { let _ = std::fs::File::open("CONTROL_FILE"); }',
 'unix-read':'fn verification_g1_control() { let target = "/dev/rdisk99"; let _ = std::fs::File::open(target); }',
 'windows-alias':r'fn verification_g1_control() { use std::fs::OpenOptions as Alias; let target = r"\\.\PhysicalDrive99"; let _ = Alias::new().read(true).open(target); }',
 'partition-write':'fn verification_g1_control() { let target = "/dev/disk99s1"; let _ = std::fs::OpenOptions::new().write(true).open(target); }'}
 results={}
 for name,snippet in {'baseline':None,**snippets}.items():
  with tempfile.TemporaryDirectory() as t:
   dst=Path(t)/'app';shutil.copytree(app,dst,ignore=shutil.ignore_patterns('target','.git'))
   owned=Path(t)/'ordinary';owned.write_text('private ordinary file\n')
   if snippet:
    p=dst/'src/jobdir.rs';body=p.read_text();assert '#[cfg(test)]' in body
    p.write_text(body.replace('#[cfg(test)]',snippet.replace('CONTROL_FILE',str(owned))+'\n#[cfg(test)]',1))
   r=subprocess.run(['python3',str(checker),'--root',str(dst)],capture_output=True,text=True)
   results[name]=dict(exit=r.returncode,stdout=r.stdout,stderr=r.stderr)
   assert (r.returncode==0)==(name in ['baseline','ordinary']),(name,results[name])
 return results

def run(product,out):
 assert subprocess.check_output(['git','-C',str(product),'rev-parse','HEAD']).decode().strip()==HEAD
 out.mkdir(parents=True,exist_ok=True);app=product/'host/app';checker=product/'tools/app1a/g1_static.py'
 static={str(p.relative_to(app)):static_controls.run(app,str(p.relative_to(app)),['python3',str(checker),'--root','.']) for p in sorted((app/'src').glob('*.rs'))}
 (out/'static.json').write_text(json.dumps(static,indent=2)+'\n')
 (out/'before-marker.json').write_text(json.dumps(before_marker(app,checker),indent=2)+'\n')
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
