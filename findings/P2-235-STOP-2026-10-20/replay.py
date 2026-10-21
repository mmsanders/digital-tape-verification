"""Authenticate the published preflight-stop receipt, not a native capability test."""
import argparse, hashlib, json
from pathlib import Path
HERE=Path(__file__).resolve().parent
def blob(b): return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def run(observer=None):
 authority=json.loads((HERE/'AUTHORITY.json').read_text())
 files={f['path'].split('/')[-1]:f['sha'] for f in authority['changed_files'] if '/method/' not in f['path']}
 for n in ['RUN-STOP.json','RUN-STOP.md','METHOD-IMPORT.json']:
  assert blob((HERE/n).read_bytes())==files[n], 'original published receipt identity'
 j=json.loads((HERE/'RUN-STOP.json').read_text()); m=json.loads((HERE/'METHOD-IMPORT.json').read_text())
 assert j['method_publication']==m['publication']=='9991eded2ca2892f436088241848a55de4d31b88'
 assert j['method_tree']==m['source_tree']=='944df7d2fc9946c62214829d8c67d7f7c4b0b62e'
 assert authority['intermediate_commit']['parents']==[j['import_commit']]
 assert authority['report_commit']['parents']==[authority['intermediate_commit']['sha']]
 imported={f['path'].split('/')[-1]:f['sha'] for f in authority['imported_files']}
 root=HERE.parents[1]/'tests/wp16_observer_visibility_r1'
 assert len(imported)==len(m['files'])==6
 for f in m['files']:
  b=(root/f['path'].split('/')[-1]).read_bytes()
  assert blob(b)==f['blob']==imported[f['path'].split('/')[-1]]
  assert len(b)==f['bytes'] and hashlib.sha256(b).hexdigest()==f['sha256']
 assert all(c['status']=='completed' and c['conclusion']=='success' for c in authority['checks'])
 assert len(j['privilege_checks'])==2 and all(c['administrative_token'] is False and c['pointer_bits']==64 for c in j['privilege_checks'])
 assert all(v==0 for v in j['execution'].values())
 assert not any(j['evidence'].values()) and j['observer']['tool_not_launched'] is True
 assert j['python_route']['incapable_runtime_claim'] is False
 audit=json.loads((HERE/'LOCAL-AUDIT.json').read_text())
 assert audit['observer_sha256']==j['observer']['sha256'] and audit['observer_bytes']==j['observer']['bytes']
 for a,f in zip(audit['messages'],j['observer']['embedded_requirement_messages']):
  assert a['matches'] is True and a['offset']==f['file_offset'] and a['sha256']==f['sha256'] and a['bytes']==f['bytes']
 assert audit['asInvoker_literal_found'] and not audit['new_token_probe'] and not audit['observer_launched']
 if observer:
  b=observer.read_bytes();assert len(b)==j['observer']['bytes'] and hashlib.sha256(b).hexdigest()==j['observer']['sha256']
  for f in j['observer']['embedded_requirement_messages']:
   part=b[f['file_offset']:f['file_offset']+f['bytes']]
   assert part==f['text'].encode('utf-16le') and hashlib.sha256(part).hexdigest()==f['sha256']
  assert b'level="asInvoker"' in b
 return dict(disposition='HELD at declared observer-privilege prerequisite; conservative preflight stop supported',method_files_authenticated=6,token_facts='authenticated published Software receipts, not a new independent token measurement',observer_identity_and_message_slices='independently checked from unchanged local bytes; optional replay rechecks bytes',rows=[dict(id=n,status='NOT_EXECUTED_PREFLIGHT_PRIVILEGE',visibility='UNQUALIFIED') for n in ['file-read','file-zero','missing-read','nul-zero','nul-read','absent-dos-zero']],actual_calls=0,capture_attempts=0,helper_runtime_incapability_proved=False,observer_launch_failure_measured=False,absence_cleared=False,next_condition='PM-scoped continuation only if an already available authorized administrator capture context exists; no human/security/install/bypass request')
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--observer',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args();r=run(a.observer);a.out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
