"""Exact-head host bindings; records Product failures, never grants acceptance."""
import argparse,hashlib,json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'tests/wp15_app1a_r1'))
import cases,static_controls,ingest_process
HEAD4='8e7b39e648314c8940423ce9ed551f29812fe6da'
HEAD1='ea445e1c8004c92484946d7408b296bb20bd1b6b'
def call(args,**kw):return subprocess.run(list(map(str,args)),check=True,**kw)
def fetch(dst,head):
 call(['git','init','-q',dst]);call(['git','-C',dst,'fetch','--depth=1','https://github.com/mmsanders/Digital-Tape.git',head]);call(['git','-C',dst,'checkout','--detach','FETCH_HEAD'])
 assert subprocess.check_output(['git','-C',dst,'rev-parse','HEAD']).decode().strip()==head

def static(app,out):
 # Run the unchanged published runner first. Then record all rows, including those
 # its fail-fast assertion cannot reach. The snippets and expectations are unchanged.
 checker=str(app.parents[1]/'tools/app1a/g1_static.py')
 result={}
 for entry in ['src/lib.rs','src/jobdir.rs']:
  try:static_controls.run(app,entry,['python3',checker,'--root','.']); result[entry]='all controls PASS'
  except AssertionError as e:result[entry]=str(e)
 # A function after a cfg(test) module is still ordinary shipping Rust. Appending is
 # exactly the published control, not changing the analyzer or a Product source head.
 snippets={'ordinary':'fn verification_g1_control() { let _ = std::fs::File::open("CONTROL_FILE"); }',
 'unix-read':'fn verification_g1_control() { let target = "/dev/rdisk99"; let _ = std::fs::File::open(target); }',
 'windows-alias':r'fn verification_g1_control() { use std::fs::OpenOptions as Alias; let target = r"\\.\PhysicalDrive99"; let _ = Alias::new().read(true).open(target); }',
 'partition-write':'fn verification_g1_control() { let target = "/dev/disk99s1"; let _ = std::fs::OpenOptions::new().write(true).open(target); }'}
 rows=[]
 for placement in ['append','prepend']:
  for name,snippet in {'baseline':None,**snippets}.items():
   with tempfile.TemporaryDirectory() as t:
    dst=Path(t)/'app';shutil.copytree(app,dst,ignore=shutil.ignore_patterns('target','.git'))
    control=Path(t)/'ordinary';control.write_text('ordinary file only\n')
    p=dst/'src/jobdir.rs'
    if snippet:
     s=snippet.replace('CONTROL_FILE',str(control));p.write_text(p.read_text()+'\n'+s+'\n' if placement=='append' else p.read_text().replace('#[cfg(test)]',s+'\n#[cfg(test)]',1))
    r=subprocess.run(['python3',checker,'--root',str(dst)],capture_output=True,text=True)
    rows.append(dict(placement=placement,case=name,exit=r.returncode,stdout=r.stdout,stderr=r.stderr))
 result['rows']=rows;(out/'static.json').write_text(json.dumps(result,indent=2)+'\n')
 assert all(x['exit']==0 for x in rows if x['placement']=='append'),rows
 assert all(x['exit']!=0 for x in rows if x['placement']=='prepend' and x['case'] in ['unix-read','windows-alias','partition-write']),rows
 print('REPRODUCED: static analyzer misses three shipping-code negatives after cfg(test); before-marker controls detect all three')

def expected(c):
 kind,fact=c['message']
 if c['exit']==0:return None # Pair validation is outside this parser/message binding.
 if kind=='generic':return 'Something went wrong. Nothing else on your computer was changed.'
 if kind=='overage':
  m,s=divmod(fact,60);duration=(f'{m} min' if m else '')+(' ' if m and s else '')+(f'{s} s' if s or not m else '')
  return f'This music is {duration} too long for a 60-minute cartridge. Take some songs out and drop the folder again.'
 if kind in ['unusable','protected','folder-nonmusic']:
  o,_,name=str(fact).partition('/');folder=c['folders'][int(o)];name=name or folder
  if kind=='unusable':return f'"{name}" can\'t be used. Take it out of the folder.'
  if kind=='protected':return f'"{name}" is copy-protected, so it can\'t go on a cartridge. Take it out of the folder.'
  return f'The folder "{folder}" has something in it that isn\'t music. Use a folder with only songs in it.'
 raise AssertionError(c)

def parser(app,out,work):
 bind=work/'parser';shutil.copytree(HERE/'parser',bind)
 pins={}
 for n in ['report.rs','messages.rs']:
  p=app/'src'/n;pins[n]=hashlib.sha256(p.read_bytes()).hexdigest();shutil.copyfile(p,bind/'src'/n)
 call(['cargo','build','--release','--manifest-path',bind/'Cargo.toml'])
 rows=[c for c in cases.corpus() if c['tool']=='ingest']
 r=subprocess.run([str(bind/'target/release/verification-app-parser-binding')],input=''.join(json.dumps(c)+'\n' for c in rows),capture_output=True,text=True,check=True)
 got=[json.loads(l) for l in r.stdout.splitlines()];assert len(got)==len(rows)
 results=[dict(case=c,actual=g,expected_rendered=expected(c),validity_match=g['valid']==c['valid'],message_match=g['rendered']==expected(c)) for c,g in zip(rows,got)]
 result=dict(head=HEAD4,source_sha256=pins,total=len(rows),validity_mismatches=sum(not x['validity_match'] for x in results),message_mismatches=sum(not x['message_match'] for x in results),rows=results)
 (out/'parser.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='rows'}))
 # This is a finding reproduction, not a gate asserting Product passes.
 assert any(x['case']['name']=='ingest:duplicate-key' and not x['validity_match'] for x in results)
 assert any(x['case']['name']=='ingest:spaced-json' and not x['validity_match'] for x in results)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--static-only',type=Path);a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True)
 if a.static_only:static(a.static_only.resolve(),a.out);return
 with tempfile.TemporaryDirectory(prefix='verification196-') as t:
  w=Path(t);p4=w/'s4';fetch(p4,HEAD4);static(p4/'host/app',a.out);parser(p4/'host/app',a.out,w)
  p1=w/'s1';fetch(p1,HEAD1);call(['cargo','build','--release','--locked'],cwd=p1/'host/ingest')
  binary=p1/'host/ingest/target/release/ingest';sha=hashlib.sha256(binary.read_bytes()).hexdigest()
  version=subprocess.check_output([str(binary),'--version'],text=True).strip();version=version.removeprefix('ingest ')
  sources=w/'sources';call(['python3','-B',ROOT/'tests/wp16_ingest_stage1/asset.py','--destination',sources])
  source=sources/'assets/ordinary.wav';assert hashlib.sha256(source.read_bytes()).hexdigest()=='d36663d1e4f05abaac699a6c14e0fa86724db9b4decdb8c96abe0c9d1f645821'
  processout=a.out/'ingest-process';result={'head':HEAD1,'sha256':sha,'version':version,'scope':'CI rebuilt source head, not byte identity with Software shipping artifact'}
  try:result['rows']=ingest_process.run(binary,sha,version,source,processout);result['result']='PASS bounded process smoke'
  except AssertionError as e:result['result']='CORRECTION';result['assertion']=str(e);import traceback;result['traceback']=traceback.format_exc()
  (a.out/'ingest-summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
