"""Run independent semantic fixtures; never accepts a firmware or physical run."""
import argparse,copy,json
from pathlib import Path
from cases import catalog
from rules import evaluate_normalized_fixture

def observations(fn):
 out=[]
 for case in catalog():
  try:
   actual=fn(copy.deepcopy(case['record']),copy.deepcopy(case['context']))
   good=all(actual.get(k)==v for k,v in case['expected'].items())
   good=good and all(actual[k] is False for k in ('accepted','physical_run','candidate_executed')) and actual['binding']=='UNBOUND_SERIAL_DECLARATION'
  except Exception as e:actual={'exception':repr(e)};good=False
  out.append(dict(case=case['case'],expected=case['expected'],actual=actual,passed=good))
 return out

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--selftest',action='store_true',required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 out=observations(evaluate_normalized_fixture);assert all(x['passed'] for x in out),json.dumps([x for x in out if not x['passed']])
 src=Path(__file__).with_name('rules.py').read_text()
 mutations=[
 ('ignore-missing-or-mismatched-human-entry',"check=record.get('michael_check')","check=dict(date='SIM',build=context['candidate_build'],criterion=criterion,tried='SIM',log_sha256=context['raw_log_sha256'],numbers=numbers(measured),verdict='acceptable')"),
 ('waive-strict-underruns','if count!=0:','if False:'),
 ('waive-PM-escalation','if elapsed*5>target*6:','if False:'),
 ('accept-149999us-delay','elapsed>=context[\'injected_delay_us\']','elapsed>=149999'),
 ('retired-CID-gate',"criterion=context['criterion']","criterion=context['criterion']\n if record and not record.get('cid'):return result('invalid','CID_required')"),
 ('retired-instrument-gate',"criterion=context['criterion']","criterion=context['criterion']\n if record and not record.get('instrument'):return result('invalid','instrument_required')"),
 ('host-clock-accepted',"measured.get('origin')!='mcu'","False"),
 ('wrong-log-identity-accepted',"record.get('log_sha256')!=context['raw_log_sha256']","False"),
 ]
 detected=[]
 for name,old,new in mutations:
  assert old in src,name
  scope={};exec(compile(src.replace(old,new),name,'exec'),scope)
  failures=[x['case'] for x in observations(scope['evaluate_normalized_fixture']) if not x['passed']]
  assert failures,name;detected.append(dict(control=name,detecting_cases=failures))
 # Fixed blanket outcomes must disagree with the independent expected catalog.
 for outcome in ('eligible_normalized_fixture','invalid'):
  assert any(c['expected']['rule_outcome']!=outcome for c in catalog());detected.append(dict(control='blanket-'+outcome))
 result=dict(mode='semantic-fixture-selftest-only',cases=out,controls_detected=detected,passed=True,accepted=False,physical_run=False,candidate_executed=False,binding='UNBOUND_SERIAL_DECLARATION')
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(dict(cases=len(out),controls=len(detected),passed=True,binding=result['binding'],accepted=False)))
if __name__=='__main__':main()
