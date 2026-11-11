"""New public G1/G2/G3 vectors. Expected values authored before implementation."""
import copy,json
from support import *
def timing():
 out=[]
 def add(name,edit,status='ok',usage=False,**wanted):
  s=old_scenario();edit(s);out.append(dict(name=name,input=s,usage=usage,wanted=dict(status=status,**wanted)))
 add('clock-changed',lambda s:s['blocks'][0].update(cpu_hz=150000000),'clock_changed',elapsed_us='-',cycles='-',cpu_hz='600000000',millis='99',engine_us='-')
 add('unchanged-explicit-clock',lambda s:s['blocks'][0].update(cpu_hz=600000000),elapsed_us='99000')
 add('mount-precedes-clock-wrap-timeout',lambda s:(s.update(mount=-1),s['blocks'][0].update(cpu_hz=150000000,ms=7100)),'mount_failed',elapsed_us='-',cycles='-',millis='0',engine_us='-')
 add('clock-precedes-wrap-timeout',lambda s:s['blocks'][0].update(cpu_hz=150000000,ms=7100),'clock_changed',elapsed_us='-',cycles='-',millis='7000',engine_us='-')
 add('wrap-precedes-timeout-and-nonzero',lambda s:s['blocks'][0].update(ms=7100),'wrap',elapsed_us='-',cycles='-',millis='7000')
 add('timeout-precedes-nonzero',lambda s:s['blocks'][0].update(ms=2100),'timeout',elapsed_us='-',cycles='-',millis='2000')
 add('6999ms-is-timeout-not-wrap',lambda s:s['blocks'][0].update(ms=7099),'timeout',millis='6999')
 add('1999ms-can-close-ok',lambda s:s['blocks'][0].update(ms=2099,cycles=1199401000),elapsed_us='1999000',millis='1999')
 add('empty-blocks-timeout',lambda s:s.update(blocks=[]),'timeout',elapsed_us='-',cycles='-',millis='0',engine_us='-')
 add('runs-out-retains-first-engine',lambda s:s.update(blocks=[dict(cycles=6001000,ms=110,engine_frames=128,nonzero=False)]),'timeout',millis='0',engine_us='10000')
 add('earlier-engine-before-clock-change',lambda s:s.update(blocks=[dict(cycles=6001000,ms=110,engine_frames=128,nonzero=False),dict(cycles=12001000,ms=120,engine_frames=128,nonzero=True,cpu_hz=150000000)]),'clock_changed',engine_us='10000',millis='20')
 add('nonzero-with-zero-engine-frames',lambda s:s['blocks'][0].update(engine_frames=0),usage=True)
 add('unknown-scenario-key',lambda s:s.update(unknown=0),usage=True)
 add('unknown-block-key',lambda s:s['blocks'][0].update(unknown=0),usage=True)
 for k in ('cpu_hz','t0_cycles','t0_ms','inject_us','mount','warm','position'):
  add('noninteger-scenario-'+k,lambda s,k=k:s.update({k:1.5}),usage=True)
 for k in ('cycles','ms','engine_frames','cpu_hz'):
  add('noninteger-block-'+k,lambda s,k=k:s['blocks'][0].update({k:1.5}),usage=True)
 return out

def bundles():
 out=[]
 def add(name,edit=lambda m,f:None,overall='CONTROL_DETECTED',f3=None,code=0,reason=None,obs=None,control=True):out.append(dict(name=name,edit=edit,overall=overall,f3=f3,exit=code,reason=reason,observations=obs or {},control=control))
 add('candidate-plus-control',f3='CONSISTENT',obs={'SYNTHETIC-F3-1':'CONSISTENT','SYNTHETIC-CONTROL':'CONTROL_DETECTED'})
 add('root-only-candidate',control=False,overall='CONSISTENT',f3='CONSISTENT')
 add('no-candidate-just-control',edit=lambda m,f:m['observations'].pop(0),overall='NOT_RUN',f3='NOT_RUN',reason='no_candidate_observation')
 add('candidate-cannot-cite-sub-build',edit=lambda m,f:m['observations'][0].update(build='builds/control/'),overall='INVALID',f3='INVALID',code=2,reason='build_not_root')
 add('unused-control-build',edit=lambda m,f:m['observations'].pop(1),overall='INVALID',code=2,reason='build_unused')
 add('missing-sub-build-hex',edit=lambda m,f:f.pop('builds/control/firmware.hex'),overall='INVALID',code=2,reason='build_incomplete')
 def duplicate(m,f):
  d=json.loads(f['builds/control/build.json']);d['id']='a'*32;f['builds/control/build.json']=json.dumps(d).encode()
 add('duplicate-build-ID',edit=duplicate,overall='INVALID',code=2,reason='build_duplicate')
 add('capture-cites-other-build-ID',edit=lambda m,f:f.update({'control.log':f['control.log'].replace(b'b'*32,b'a'*32)}),overall='MISMATCH',code=2,reason='build_id_mismatch')
 def env(m,f):
  d=json.loads(f['builds/control/build.json']);d.update(env='teensy41',inject_us=0);f['builds/control/build.json']=json.dumps(d).encode()
 add('control-build-wrong-environment',edit=env,overall='MISMATCH',code=2,reason='control_env_mismatch')
 add('requested-not-a-key',edit=lambda m,f:m.update(requested=['F3']),overall='INVALID',code=2,reason='field_unknown')
 def notrun(m,f):m['observations']=[dict(id='PENDING',sequence=1,kind='candidate',provenance='not_run',reason='SYNTHETIC NOT EXECUTED')]
 add('exact-not-run-shape',edit=notrun,control=False,overall='NOT_RUN',f3='NOT_RUN',obs={'PENDING':'NOT_RUN'})
 add('not-run-extra-capture-forbidden',edit=lambda m,f:(notrun(m,f),m['observations'][0].update(capture='capture.log')),control=False,overall='INVALID',code=2,reason='field_unknown')
 add('not-run-missing-reason',edit=lambda m,f:(notrun(m,f),m['observations'][0].pop('reason')),control=False,overall='INVALID',code=2,reason='field_missing')
 def superseded(m,f):
  a=dict(m['observations'][0],id='EARLY',sequence=1,capture='bad.log',superseded_by='LATER',supersede_reason='SYNTHETIC retry');f['bad.log']=f['capture.log'].replace(b'millis 99',b'millis 90')
  b=dict(m['observations'][0],id='LATER',sequence=2);m['observations']=[b,a]
 add('superseded-mismatch-counts-overall',edit=superseded,control=False,overall='MISMATCH',f3='CONSISTENT',code=2,obs={'EARLY':'MISMATCH','LATER':'CONSISTENT'})
 def actual(m,f,elapsed=99000,verdict='acceptable'):
  am,af=if1.fixture(elapsed=elapsed,verdict=verdict);f['capture.log']=af['capture.log'];m['session']['kind']='physical';m['observations'][0]=am['observations'][0];f.update({k:v for k,v in af.items() if k.startswith('michael/')})
  # artifact was regenerated above; link the synthetic record to current exact image.
  d=json.loads(f['michael/MC-20261110-1.json']);d['firmware_hex_sha256']=SHA(f['firmware.hex']);f['michael/MC-20261110-1.json']=json.dumps(d).encode()
 def decline_and_mismatch(m,f):
  actual(m,f);d=json.loads(f['michael/MC-20261110-1.json']);d.update(verdict='not acceptable',note='SYNTHETIC DECLINE',log_sha256='0'*64);f['michael/MC-20261110-1.json']=json.dumps(d).encode()
 add('mismatch-worse-than-human-decline',edit=decline_and_mismatch,control=False,overall='MISMATCH',f3='MISMATCH',code=2,reason='michael_record_mismatch')
 def decline_and_invalid(m,f):
  decline_and_mismatch(m,f);m['observations'][0]['unknown']=True
 add('invalid-worse-than-mismatch-and-decline',edit=decline_and_invalid,control=False,overall='INVALID',f3='INVALID',code=2,reason='field_unknown')
 def missing(m,f):actual(m,f);m['observations'][0].pop('michael_check')
 add('actual-record-absent-NOT-RUN',edit=missing,control=False,overall='NOT_RUN',f3='NOT_RUN',reason='michael_check_absent')
 add('pending-PM-worse-than-NOT-RUN',edit=lambda m,f:actual(m,f,120001),control=False,overall='PENDING_PM',f3='PENDING_PM',code=1)
 add('human-decline-worse-than-control',edit=lambda m,f:actual(m,f,99000,'not acceptable'),overall='NOT_ACCEPTABLE',f3='NOT_ACCEPTABLE',code=1)
 add('acceptable-miss-at-exact-20-percent',edit=lambda m,f:actual(m,f,120000),control=False,overall='CONSISTENT',f3='CONSISTENT')
 def declined_pending(m,f):
  actual(m,f,99000,'not acceptable');am,af=if1.fixture(elapsed=120001);ob=dict(am['observations'][0],id='PENDING-PM',sequence=3,capture='pending.log',michael_check='michael/MC-20261110-2.json');m['observations'].append(ob);f['pending.log']=af['capture.log'];d=json.loads(af['michael/MC-20261110-1.json']);d.update(id='MC-20261110-2',firmware_hex_sha256=SHA(f['firmware.hex']));f['michael/MC-20261110-2.json']=json.dumps(d).encode()
 add('decline-worse-than-pending-PM',edit=declined_pending,control=False,overall='NOT_ACCEPTABLE',f3='NOT_ACCEPTABLE',code=1,obs={'PENDING-PM':'PENDING_PM','SYNTHETIC-F3-1':'NOT_ACCEPTABLE'})
 add('mixed-control-does-not-mask-candidate-NOT-RUN',edit=missing,overall='NOT_RUN',f3='NOT_RUN',reason='michael_check_absent')
 return out
