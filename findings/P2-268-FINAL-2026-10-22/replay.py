"""Authenticate a final capability STOP as data. No helper/denied-path execution."""
import argparse,ast,hashlib,io,json,urllib.request,zipfile
from pathlib import Path
HEAD='5e3f6d03d7ba7d0a18c9ee365e908b47928abaab'
URL='https://raw.githubusercontent.com/mmsanders/Digital-Tape/'+HEAD+'/docs/REVIEW/software525/correction2/failed-logical-attempt.zip'
def sha(b):return hashlib.sha256(b).hexdigest()
def blob(b):return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--archive',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 raw=a.archive.read_bytes() if a.archive else urllib.request.urlopen(URL).read()
 assert len(raw)==12288 and sha(raw)=='cea01facdcaa6de4185cc456ad72ae7a34e748b3ea5a47d714de563e1edbe4f8' and blob(raw)=='706a4ff52ffb496a266efb4c7c3681de0ffe1d81'
 z=zipfile.ZipFile(io.BytesIO(raw));ns=z.namelist();assert len(ns)==len(set(ns))==6
 pins={'FAILURE.json':'6a53d8dd907f9f09e02456e87e188481f55dacec','source/controller.py':'5612402e8dd3c7e675683aefa0585fb6f87339e6','source/run_correction2.py':'0ff7eedaa0bb935be7f5e6bd7d7c433de286daf4','source/task_adapter.py':'fb257be87339e7decf35276aa8027f64d861e8af','sw525-correction2-stderr.bin':'a9326f5dccd03f5645e2361291408abd30656198','sw525-correction2-stdout.bin':'e69de29bb2d1d6434b8b29ae775ad8c2e48c5391'}
 assert set(ns)==set(pins);f={n:z.read(n) for n in ns}
 for n,b in f.items():assert blob(b)==pins[n]
 d=json.loads(f['FAILURE.json']);assert set(d['files'])==set(ns)-{'FAILURE.json'}
 for n,v in d['files'].items():assert len(f[n])==v['bytes'] and sha(f[n])==v['sha256']
 assert d['producer_exit']==1 and d['actual_children']==d['product_calls']==d['logical_cases_completed']==0
 assert d['original_final_parent_cpu'] is d['original_final_allocation'] is d['original_final_ledger'] is None
 assert f['sw525-correction2-stdout.bin']==b'' and len(f['sw525-correction2-stderr.bin'])==1173
 stderr=f['sw525-correction2-stderr.bin'];assert b'PermissionError' in stderr and b'WinError 5' in stderr and b'fresh-task' in stderr and b'line 166' in stderr
 # Preserve actual raw CRLF bytes; explicitly compare semantic unchanged controller separately.
 c=f['source/controller.py'];assert len(c)==10605 and sha(c)=='4c8d973093966b8431eb34560786e3848e22891f5b6e402520df57a1040f03de'
 lf=c.replace(b'\r\n',b'\n');assert len(lf)==10390 and blob(lf)=='923eb001989ccbd808633a42357c1d8d3b5c2d2d'
 assert ast.dump(ast.parse(c),include_attributes=False)==ast.dump(ast.parse(lf),include_attributes=False)
 result=dict(candidate=HEAD,original_archive_sha256=sha(raw),members=6,inventory_entries=5,byte_authentication='PASS',producer_exit=1,stop='FINAL_CAPABILITY_AND_ACCOUNTING_STOP',binding_cases_completed=0,actual_children=0,Product_calls_by_review=0,A3_binding='UNESTABLISHED',A4_binding='UNESTABLISHED',original_final_CPU='MISSING',original_final_allocation='MISSING',producer_final_ledger='MISSING',cumulative_budget='UNESTABLISHED',controller_adapter='HELD',C270_dependency='NOT_SATISFIED',Verification268='CLOSE_AT_FINAL_STOP',Verification270='OPEN_PENDING_DEPENDENCY',consolidated_corrections=2,new_correction_authorized=False)
 a.out.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf-8',newline='\n');print('PASS original failed evidence authentication; controller HELD and no retry')
if __name__=='__main__':main()
