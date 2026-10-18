"""Authenticate Software observations and apply independent parsers/status judgments."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys,zipfile
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'tests/wp15_app1a_r1'));import cases,parser_runner,oracle
sys.path.insert(0,str(ROOT/'tests/wp16_shipping_exhaustion_r1'));import runner

def sha(b):return hashlib.sha256(b).hexdigest()
def folders(argv):
 out=[];i=1
 while i<len(argv):
  a=argv[i]
  if a=='--':return out+argv[i+1:]
  if a in ['--out','--length','--report','--report-nonce']:i+=2;continue
  if not a.startswith('-'):out.append(a)
  i+=1
 return out

def replay(directory,out):
 directory.mkdir(parents=True,exist_ok=True);results=[]
 census={c['id']:c for c in json.loads((ROOT/'tests/wp16_ingest_stage1/CENSUS.json').read_text())['cases']}
 for pin in json.loads((HERE/'INPUTS.json').read_text()):
  p=directory/(str(pin['id'])+'.zip')
  if not p.exists():
   with p.open('wb') as f:subprocess.run(['gh','api',f"repos/mmsanders/Digital-Tape/actions/artifacts/{pin['id']}/zip"],stdout=f,check=True)
  assert sha(p.read_bytes())==pin['digest'].removeprefix('sha256:'),pin['id']
  rec=dict(artifact=pin['id'],name=pin['name'],zip_sha256=sha(p.read_bytes()))
  with zipfile.ZipFile(p) as z:
   ns=z.namelist()
   if 'parser-binding.json' in ns:
    rows=[c for c in cases.corpus() if c['tool']=='ingest'];assert rows==[json.loads(l) for l in z.read('adapter-stdin.jsonl').decode().splitlines()]
    parser_runner.compare(rows,[json.loads(l) for l in z.read('adapter-stdout.jsonl').decode().splitlines()]);rec['actual_parser_rows_replayed']=len(rows)
   ship=next((n for n in ns if n.startswith('shipping/') and n.endswith('.json')),None)
   if ship:
    j=json.loads(z.read(ship));rec.update(binary_sha256=j['binary_sha256'],shipping_rows=len(j['sweep']),platform=j['platform'])
    if j['platform']=='macos':rec['capability']='UNEXECUTED enforceable shipping exhaustion'
    else:
     bad=[];load_failed=0;positive=j['positive_unlimited']['published']
     for r in j['sweep']:
      if r['version']['exit']!=0:load_failed+=1;continue
      c=r['case'];row=dict(load=dict(exit=r['version']['exit'],timed_out=False,stdout=r['version']['stdout_head']),case=dict(exit=c['exit'],timed_out=False,stderr=c['stderr']),foreign_unchanged=c['unrelated_unchanged'],unexpected_entries=c['owned_stage_left'],dest_exists=c['dest_exists'],pair=c.get('published'))
      b=runner.judge(row,positive)
      if b:bad.append(dict(limit=r['limit_mib'],violations=b))
     assert not bad,bad;rec.update(load_failures_excluded=load_failed,shipping_contract_rows_pass=len(j['sweep'])-load_failed)
   if 's1-matrix/S1-MATRIX.json' in ns:
    j=json.loads(z.read('s1-matrix/S1-MATRIX.json'));s=j['summary'];count=reports=census_exits=0
    for r in j['rows']:
     if r['verdict']=='UNEXECUTED':continue
     count+=1
     if r['name'] in census:
      want=census[r['name']]['expected_exit'];assert (r['exit']!=0 if want is None else r['exit'] in want if isinstance(want,list) else r['exit']==want),(r['name'],r['exit'],want);census_exits+=1
     prefix='s1-matrix/runs/'+r['run']+'/'
     assert sha(z.read(prefix+'stdout'))==r['stdout_sha256'];assert sha(z.read(prefix+'stderr'))==r['stderr_sha256']
     if r['report_sha256'] is not None:
      raw=z.read(prefix+'report.jsonl');assert sha(raw)==r['report_sha256'];parsed=oracle.parse(raw,'ingest',r['version'].removeprefix('ingest '),cases.NONCE,r['exit'],folders(r['argv']))
      assert (parsed is not None)==r['report_valid'],r['name']
      if parsed and parsed['refusal']:assert parsed['refusal']['id']==r['refusal_id']
      reports+=1
     assert r['verdict']=='PASS',(r['name'],r['verdict'])
    assert count==s['runs']==s['pass'];rec.update(process_receipts_replayed=count,census_exits_compared=census_exits,report_files_reparsed=reports,observed_ids=s['observed_ids'],gaps=s['unexecuted'])
    smoke=json.loads(z.read('ingest-process/RESULT.json'));assert len(smoke['results'])==12;rec['smoke_rows']=12
   for n in ns:
    if n.startswith('equivalence-'):
     j=json.loads(z.read(n));assert len(j['results'])==1905 and all(r['identical'] for r in j['results']);rec['equivalence_receipts']=1905;rec['equivalence_scope']='Software comparator observations; audited version metadata normalization, not a new independent full math campaign'
  results.append(rec)
 out.write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--artifacts',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();replay(a.artifacts,a.out)
