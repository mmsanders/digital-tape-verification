"""Fetch and authenticate immutable >1MiB raw evidence; replay original red judgment."""
import argparse,hashlib,json,sys,urllib.request,zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[1]/'tests/wp16_shipping_exhaustion_r1'))
from runner import BASE,judge
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();pin=json.loads((HERE/'EVIDENCE.json').read_text())
 if not a.out.exists():
  with urllib.request.urlopen(pin['url'],timeout=60) as r,a.out.open('wb') as f:
   while b:=r.read(1024*1024):f.write(b)
 assert a.out.stat().st_size==pin['bytes'] and hashlib.sha256(a.out.read_bytes()).hexdigest()==pin['sha256'],'raw release identity mismatch'
 with zipfile.ZipFile(a.out) as z:j=json.loads(z.read('RESULT.json'))
 assert j['binary_sha256']==BASE and j['contract_pass'] is False and j['platform']=='win32'
 pos=next(r for r in j['rows'] if r['limit_mib'] is None)['pair']
 for r in j['rows']:assert judge(r,pos)==r['violations']
 six=next(r for r in j['rows'] if r['limit_mib']==6)
 assert six['load']['exit']==0 and six['case']['exit']==0xC0000409 and six['violations']
 print('Authenticated immutable raw release; replay confirms original shipping6MiB contract RED, not candidate acceptance')
