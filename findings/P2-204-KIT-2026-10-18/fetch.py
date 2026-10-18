"""Authenticate durable Verification204 receipts. --raw also fetches original 212MB rehearsal."""
import argparse,hashlib,json,pathlib,urllib.request,zipfile
HERE=pathlib.Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--out',type=pathlib.Path,required=True);p.add_argument('--raw',action='store_true');a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
for pin in json.loads((HERE/'EVIDENCE.json').read_text())['assets']:
 if pin['name'].startswith('ingest-') and not a.raw:continue
 dst=a.out/pin['name']
 if not dst.exists():
  with urllib.request.urlopen(pin['url'],timeout=60) as r,dst.open('wb') as f:
   while b:=r.read(1024*1024):f.write(b)
 assert dst.stat().st_size==pin['bytes']
 assert hashlib.sha256(dst.read_bytes()).hexdigest()==pin['sha256']
 if pin['name']=='verification204-controls.zip':
  with zipfile.ZipFile(dst) as z:
   assert z.testzip() is None
   r=json.loads(z.read('RESULT.json'));ok,bad=r['controls']
   assert r['disposition'].startswith('RED')
   assert (ok['direct_summary_exit'],ok['tail_exit'],ok['packet_created'],ok['send_instruction'])==(0,0,True,True)
   assert (bad['direct_summary_exit'],bad['tail_exit'],bad['packet_created'],bad['send_instruction'])==(1,0,True,True)
   assert hashlib.sha256(z.read('win11_packet.ps1')).hexdigest()=='9d8506670df30bbbc547c6c5757d9370e152ed55cfa4cd8378bd9e1f1337f502'
   assert hashlib.sha256(z.read('summarize_packet.py')).hexdigest()=='dd18e797210da43021f1bac187bfdeb7b6a5f6ae7e9ae18d3098de8f9cf79f4a'
 print('Authenticated',pin['name'],pin['sha256'])
print('RED reproduced: failed summary still packaged. This is not collection readiness.')
