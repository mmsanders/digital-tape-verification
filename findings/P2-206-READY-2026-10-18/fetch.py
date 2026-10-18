"""Authenticate immutable Verification206 controls; --raw includes corrected rehearsal212MB."""
import argparse,hashlib,json,pathlib,urllib.request,zipfile
HERE=pathlib.Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--out',type=pathlib.Path,required=True);p.add_argument('--raw',action='store_true');a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
for pin in json.loads((HERE/'EVIDENCE.json').read_text())['assets']:
 if pin['name'].startswith('ingest-') and not a.raw:continue
 dst=a.out/pin['name']
 if not dst.exists():
  with urllib.request.urlopen(pin['url'],timeout=60) as r,dst.open('wb') as f:
   while b:=r.read(1024*1024):f.write(b)
 assert dst.stat().st_size==pin['bytes'] and hashlib.sha256(dst.read_bytes()).hexdigest()==pin['sha256']
 if pin['name']=='verification206-controls.zip':
  with zipfile.ZipFile(dst) as z:
   assert z.testzip() is None
   j=json.loads(z.read('RESULT.json'));assert j['disposition']=='PASS bounded transport corrections'
   rows=j['controls'];assert len(rows)==8
   assert {(r['script'],r['case']) for r in rows}=={(s,c) for s in ['original','corrected'] for c in ['complete','missing-record','exit-mismatch','byte-difference']}
   for r in rows:
    bad=r['case']!='complete';stop=bad and r['script']=='corrected'
    assert r['summary_exit']==int(bad) and r['tail_exit']==int(stop)
    assert r['zip']==r['send']==(not stop) and not r['stderr']
    if stop:assert r['stopped']
   for name,_,sha in j['pins']:assert hashlib.sha256(z.read(name)).hexdigest()==sha
 print('Authenticated',pin['name'],pin['sha256'])
print('PASS bounded correction receipts; Server mechanics only, not Windows11/Product acceptance.')
