"""Authenticated bounded Stage3 review; only new fixed rows, no Product execution."""
import argparse,hashlib,json,re,subprocess,sys,urllib.request,zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(inputs,out,release=None):
 inputs.mkdir(parents=True,exist_ok=True);out.mkdir(parents=True,exist_ok=True)
 pins=json.loads((HERE/'INPUTS.json').read_text())
 for pin in pins:
  p=inputs/pin['name']
  if not p.exists():
   url=release.rstrip('/')+'/'+p.name if release else pin.get('url')
   if url:
    with urllib.request.urlopen(url,timeout=60)as r,p.open('wb')as f:
     while b:=r.read(1024*1024):f.write(b)
   else:
    with p.open('wb')as f:subprocess.run(['gh','api',f"repos/mmsanders/Digital-Tape/actions/artifacts/{pin['id']}/zip"],stdout=f,check=True)
  assert p.stat().st_size==pin['bytes']and sha(p)==pin['sha256']
 root=out/'raw';root.mkdir(exist_ok=True)
 with zipfile.ZipFile(inputs/'return.zip')as z:
  for i in z.infolist():assert not Path(i.filename).is_absolute()and'..'not in Path(i.filename).parts and(i.external_attr>>16)&0o170000!=0o120000
  z.extractall(root)
 for script,args,name in [('host.py',['--inputs',str(inputs)],'HOST'),('subset.py',['--lane','lane3'],'LANE3'),('subset.py',['--lane','lane4'],'LANE4')]:
  subprocess.run([sys.executable,'-B',str(HERE/script),str(root),*args,'--out',str(out/(name+'.json'))],check=True)
 results={n:json.loads((out/(n+'.json')).read_text())for n in ['HOST','LANE3','LANE4']}
 measured={}
 for n in ['load','dup','stage3']:
  t=(root/('time-'+n+'.txt')).read_text();u=float(re.search(r'User time \(seconds\): ([0-9.]+)',t)[1]);s=float(re.search(r'System time \(seconds\): ([0-9.]+)',t)[1]);measured[n]=round(u+s,2)
 summary=dict(source='55552ad4fe57e99827ab8eb016044d0486017877',engine='d96b4245e04d74078f8938744b1394c3018516f7',
              model='c6cb573d654d337fef2f616f11cce0cee74e8968',plan='3a72a3cfebcea0e80bebb864f4e349dc1be02a50',
              inputs=pins,output_sha256={n+'.json':sha(out/(n+'.json'))for n in results},
              host={k:v for k,v in results['HOST'].items()if k!='faults'},
              subsets={n:{k:v for k,v in results[n].items()if k!='rows'}for n in ['LANE3','LANE4']},
              cpu=dict(current_CI_measured=measured,earlier_CI_measured=13.02,local_reported_measured=302.4,
                       local_unmeasured_reported_bound=220,reported_upper_total=round(sum(measured.values())+13.02+302.4+220,2),
                       scope='CI times authenticated; local measurements/bound reported by Software, not independently established; cap7200'),
              remaining=['365 fixed deferred load coordinates','six no_lower_run cuts absent from its actual3-unit operation',
                         'no repeated-LBA epoch in returned lanes','finite large-epoch samples, not exhaustive arbitrary subsets',
                         'overall443 integration/base and native/physical/atomicity/target holds unchanged'],
              narrative_corrections=['global minimum original remount row exists and exactly matches retained load1',
                                     'current workflow reran Tiers1/2;80 original files byte-identical,56 differ; prior acceptance carries'],
              disposition='bounded fixed Stage3 observations PASS with explicit unavailable/unexecuted/sample gaps; no overall443 acceptance')
 (out/'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--inputs',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--release');a=p.parse_args();run(a.inputs,a.out,a.release)
