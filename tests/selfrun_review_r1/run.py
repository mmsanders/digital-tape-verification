"""Review-discovered plan5 grammar regressions; old bindings immutable."""
import argparse,json,sys,subprocess
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'selfrun_plan5_r1'))
from fixtures import fixture,digest
from run import write_case,invoke

def cases():
 return [('valid-null-CID-unit-record',lambda p:None,True),('empty-model-photos',lambda p:p['card_model'].update(photos=[]),False),('empty-brand-line',lambda p:p['card_model'].update(brand_line=''),False),('empty-unit-label',lambda p:p['card_unit'].update(label=''),False),('unit-object-wrong-type',lambda p:p.update(card_unit=[]),False),('zero-t-sched',lambda p:p.update(t_sched_us=0),False),('boolean-t-sched',lambda p:p.update(t_sched_us=True),False)]

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--judge',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--record-known-findings',action='store_true');a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=False);obs=[]
 for name,edit,valid in cases():
  p,r,_,_,_=fixture();edit(p);p['plan_digest']=digest(p)
  for row in r:
   row['plan_digest']=p['plan_digest']
   if isinstance(p['card_unit'],dict):row['card_unit']=p['card_unit']['label']
  work=a.out/'work';write_case(work,p,r);q=invoke(a.judge,['judge','--plan','plan.json','--serial','serial.log','--build-record','build.json','--hex','firmware.hex','--json','verdict.json'],work)
  f=work/'verdict.json';report=json.loads(f.read_text()) if f.exists() else {};good=q.returncode==(0 if valid else 2) and report.get('verdict','FAIL')==('PASS' if valid else 'FAIL') and 'Traceback' not in q.stderr
  obs.append(dict(case=name,expected_exit=0 if valid else 2,exit=q.returncode,verdict=report.get('verdict'),qualifying=report.get('qualifying'),problems=report.get('problems'),stderr=q.stderr[-1200:],passed=good))
 failed={c['case'] for c in obs if not c['passed']}
 expected={n for n,e,v in cases() if not v}
 if a.record_known_findings:
  import hashlib
  assert hashlib.sha256(a.judge.read_bytes()).hexdigest()=='c4ae0dc33f2e47299e10c2606aaf03b61c07dd5f5fb306f5ea7a65cd43520976'
  assert failed==expected
 result=dict(known_findings_reproduced=a.record_known_findings and failed==expected,mode='review-discovered-actual-plan5-CLI',cases=obs,passed=all(c['passed'] for c in obs),candidate_executed=True,accepted=False,physical_run=False)
 (a.out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));return 0 if result['passed'] or result['known_findings_reproduced'] else 1
if __name__=='__main__':raise SystemExit(main())
