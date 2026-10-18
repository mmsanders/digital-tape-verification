"""Durable raw release fetch/authentication and independent offline replay."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys,urllib.request,zipfile
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'tests/wp16_shipping_exhaustion_r1'));import runner
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
 for pin in json.loads((HERE/'EVIDENCE.json').read_text()):
  archive=a.out/(pin['kind']+'.zip')
  if not archive.exists():
   with urllib.request.urlopen(pin['url'],timeout=60) as r,archive.open('wb') as f:
    while b:=r.read(1024*1024):f.write(b)
  assert archive.stat().st_size==pin['bytes'] and runner.sha(archive)==pin['sha256'],'release archive identity'
  dst=a.out/pin['kind'];dst.mkdir(exist_ok=True)
  with zipfile.ZipFile(archive) as z:
   for i in z.infolist():assert not Path(i.filename).is_absolute() and '..' not in Path(i.filename).parts and (i.external_attr>>16)&0o170000!=0o120000
   z.extractall(dst)
  if pin['kind']=='disposition':
   subprocess.run([sys.executable,'-B',str(HERE/'replay.py'),'--artifacts',str(dst/'inputs'),'--out',str(a.out/'REPLAY.json')],check=True)
  else:
   j=json.loads((dst/'RESULT.json').read_text());b=json.loads((dst/'BUILD.json').read_text());assert runner.sha(dst/'ingest.exe')==b['binary_sha256']==j['binary_sha256']
   positive=j['rows'][0]['pair'];assert j['contract_pass'] is True
   for n,r in enumerate(j['rows']):
    assert not runner.judge(r,positive)
    d=dst/f'row-{n}'
    for role in ['load','case']:
     for stream in ['stdout','stderr']:assert runner.sha(d/(role+'.'+stream))==r[role][stream+'_sha256']
    if r['pair']:
     for name,sha in r['pair'].items():assert runner.sha(d/'published-DEST'/name)==sha
   six=next(r for r in j['rows'] if r['limit_mib']==6);assert six['case']['exit']==1 and six['load']['exit']==0
 print('PASS durable releases authenticated; raw independent shipping and returned report/parser observations replayed. Full holds remain.')
