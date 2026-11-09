"""Independent synthetic ATOM mapping / production-minimum judge controls, V398."""
import argparse,copy,hashlib,importlib.util,json,struct,subprocess,sys
from pathlib import Path

def pattern(n):return struct.pack('<I',n)*128

def fixture():
 p=dict(plan_version=3,run_id='SYNTHETIC-V398-NOT-A-CARD-RUN',sku='SYNTHETIC-MODEL',revision='SYNTHETIC',card_cid='SYNTHETIC-CID',block=1000000,neighbour_offsets=['-2','-1','+1','+2'],planned_attempts=1001,required_qualifying=1000,extends=None,trials=[dict(iteration=n,cut_offset_fraction=0.5) for n in range(1,1002)])
 core={k:p[k] for k in ('run_id','sku','revision','card_cid','block','neighbour_offsets')};core['trials']=[[t['iteration'],t['cut_offset_fraction']] for t in p['trials']]
 p['plan_digest']=hashlib.sha256(json.dumps(core,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 nb={o:(bytes([i+10])*512).hex() for i,o in enumerate(p['neighbour_offsets'])};rows=[]
 for n in range(1,1002):
  rows.append(dict(run_id=p['run_id'],iteration=n,sku=p['sku'],revision=p['revision'],card_cid=p['card_cid'],plan_digest=p['plan_digest'],precondition_ok=True,precondition_readback_hex=pattern(n-1).hex(),neighbour_baseline=dict(nb),neighbours=dict(nb),readback_hex=pattern(n if n%2 else n-1).hex(),bus_mode='spi',busy_line='MISO',sck_hz=4000000,payload_complete=True,data_response_accepted=True,busy_entry_us=100,busy_sampled_us=149,cut_us=150,busy_deassert_us=None if n<=1000 else 140,firmware_build='1'*40,vcard_off_mv=0,card_cid_after_cut=p['card_cid']))
 return p,rows

def scenarios():
 def tear(r,index):
  n=r[index]['iteration'];r[index]['readback_hex']=(pattern(n-1)[:256]+pattern(n)[256:]).hex()
 return [
 ('clean-1000-plus-one-miss',lambda p,r:None,dict(verdict='PASS',qualifying=1000,torn_iterations=[])),
 ('planted-tear-qualifying',lambda p,r:tear(r,500),dict(verdict='FAIL',torn_iterations=[501])),
 ('planted-tear-on-miss',lambda p,r:tear(r,1000),dict(verdict='FAIL',torn_iterations=[1001],damage_on_non_qualifying=[1001])),
 ('corrupt-target',lambda p,r:r[500].update(readback_hex=(b'\xff'*512).hex()),dict(verdict='FAIL',corrupt_iterations=[501])),
 ('neighbour-damage-on-miss',lambda p,r:r[1000]['neighbours'].update({'+1':(b'\xff'*512).hex()}),dict(verdict='FAIL',neighbour_damage=[[1001,'+1']],damage_on_non_qualifying=[1001])),
 ('999-does-not-reach-minimum',lambda p,r:r[999].update(busy_deassert_us=140),dict(verdict='FAIL',qualifying=999)),
 ('operator-cannot-shrink-minimum',lambda p,r:(p.update(required_qualifying=0),r[999].update(busy_deassert_us=140)),dict(verdict='FAIL',qualifying=999,required_qualifying=1000)),
 ('duplicate-does-not-earn-credit',lambda p,r:r.append(copy.deepcopy(r[0])),dict(verdict='FAIL',qualifying=1000)),
 ('missing-attempt-cannot-be-dropped',lambda p,r:r.pop(),dict(verdict='FAIL',reported=1000)),
 ('wrong-plan-link',lambda p,r:r[500].update(plan_digest='0'*64),dict(verdict='FAIL',qualifying=999)),
 ('no-accepted-data-response',lambda p,r:r[999].update(data_response_accepted=False),dict(verdict='FAIL',qualifying=999)),
 ]

def agrees(actual,want):return all(actual.get(k)==v for k,v in want.items())

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--judge',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=False)
 observations=[]
 for name,edit,want in scenarios():
  p,rows=fixture();edit(p,rows);d=a.out/name;d.mkdir()
  # Exact declared mapping: keep raw serial; strip only the five-byte ATOM prefix.
  raw='SYNTHETIC BOOT; NOT REAL EVIDENCE\n'+''.join('ATOM '+json.dumps(r,separators=(',',':'))+'\n' for r in rows)
  (d/'serial.log').write_text(raw,encoding='utf-8');mapped=''.join(line[5:]+'\n' for line in raw.splitlines() if line.startswith('ATOM '));assert [json.loads(l) for l in mapped.splitlines()]==rows
  (d/'run.jsonl').write_text(mapped,encoding='utf-8');(d/'plan.json').write_text(json.dumps(p),encoding='utf-8')
  q=subprocess.run([sys.executable,str(a.judge.resolve()),'judge','--plan',str(d/'plan.json'),'--results',str(d/'run.jsonl'),'--json',str(d/'verdict.json')],capture_output=True,text=True)
  actual=json.loads((d/'verdict.json').read_text());passed=agrees(actual,want) and q.returncode==(0 if want['verdict']=='PASS' else 2)
  if name=='duplicate-does-not-earn-credit':passed=passed and any('duplicate' in x for x in actual['problems'])
  if name=='missing-attempt-cannot-be-dropped':passed=passed and any('planned but not reported' in x for x in actual['problems'])
  observations.append(dict(case=name,expected=want,observed={k:actual[k] for k in set(want)|{'problems','verdict','qualifying'}},exit=q.returncode,passed=passed,serial_sha256=hashlib.sha256(raw.encode()).hexdigest(),mapped_sha256=hashlib.sha256(mapped.encode()).hexdigest()))
 spec=importlib.util.spec_from_file_location('v398_candidate',a.judge);m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
 p,rows=fixture();normal=m.classify;m.classify=lambda data,n:'NEW'
 p1,r1=copy.deepcopy(p),copy.deepcopy(rows);scenarios()[1][1](p1,r1);mutant=m.judge([p1],r1);assert not agrees(mutant,scenarios()[1][2]);m.classify=normal
 # Probes are disclosures of the known unimplemented method delta, not clearance tests.
 probes=[]
 for name,edit in [
 ('stale-busy-sample',lambda p,r:r[0].update(busy_sampled_us=101,cut_us=50000)),
 ('card-not-powered-off',lambda p,r:r[0].update(vcard_off_mv=3300)),
 ('different-after-cut-CID',lambda p,r:r[0].update(card_cid_after_cut='OTHER')),
 ('mixed-firmware-build',lambda p,r:r[0].update(firmware_build='2'*40)),
 ('missing-firmware-build',lambda p,r:[x.pop('firmware_build') for x in r]),
 ('CID-unavailable',lambda p,r:(p.update(card_cid=None),[x.update(card_cid=None,card_cid_after_cut=None) for x in r])),
 ('completed-before-cut-reads-OLD-PM-policy-needed',lambda p,r:r[1000].update(readback_hex=pattern(1000).hex()))]:
  p,r=fixture();edit(p,r)
  if name=='CID-unavailable':
   # Retain the declared digest binding when deliberately changing identity.
   core={k:p[k] for k in ('run_id','sku','revision','card_cid','block','neighbour_offsets')};core['trials']=[[t['iteration'],t['cut_offset_fraction']] for t in p['trials']];p['plan_digest']=hashlib.sha256(json.dumps(core,sort_keys=True,separators=(',',':')).encode()).hexdigest()
   for x in r:x['plan_digest']=p['plan_digest']
  actual=m.judge([p],r);probes.append(dict(probe=name,verdict=actual['verdict'],qualifying=actual['qualifying'],problems=actual['problems'][:3],completed_write_reverted=actual['completed_write_reverted']))
 result=dict(mode='independent-synthetic-ATOM-mapping-and-production-judge',judge_sha256=hashlib.sha256(a.judge.read_bytes()).hexdigest(),cases=observations,passed=all(x['passed'] for x in observations),controls_detected=['always-NEW-classifier'],method_delta_probes=probes,physical_run=False,accepted=False,method_clearance=False)
 (a.out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in result.items() if k not in ('cases','method_delta_probes')}));return 0 if result['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
