"""Independent semantic inputs/expected outcomes, all explicitly SYNTHETIC."""
import copy,hashlib
from rules import numbers
RAW_SHA=hashlib.sha256(b'SYNTHETIC NORMALIZATION FIXTURE; NOT REAL SERIAL EVIDENCE').hexdigest()
def make_check(record):
 return dict(date='2026-11-08',build=record['build'],criterion=record['criterion'],tried='SYNTHETIC fixture; not a Michael check',log_sha256=record['log_sha256'],numbers=numbers(record['measured']),verdict='acceptable')
def base(criterion='F3',elapsed=None):
 context=dict(criterion=criterion,candidate_build='SYNTHETIC-BUILD-ID',raw_log_sha256=RAW_SHA,events=('wake_interrupt','first_non_silent_frame_handed_to_i2s') if criterion=='F3' else ('tape_commit_enter','tape_commit_return'))
 m=dict(elapsed_us=elapsed if elapsed is not None else (99000 if criterion=='F3' else 199000),origin='mcu',start_event=context['events'][0],end_event=context['events'][1])
 if criterion=='F4':context.update(future_recording_contract=True,slowest_card='SYNTHETIC-CARD-B');m.update(entries=4096,card='SYNTHETIC-CARD-B',underruns_during_commit=0,underruns_before=10,underruns_after=10)
 r=dict(build=context['candidate_build'],criterion=criterion,log_sha256=RAW_SHA,measured=m,provenance='simulation');r['michael_check']=make_check(r);return r,context

def catalog():
 cases=[]
 def add(name,expected,criterion='F3',elapsed=None,edit=None,reason=None,met=None):
  r,c=base(criterion,elapsed)
  if edit:edit(r,c)
  want=dict(rule_outcome=expected)
  if reason is not None:want['reason']=reason
  if met is not None:want['target_met']=met
  cases.append(dict(case=name,record=r,context=c,expected=want))
 yes='eligible_normalized_fixture'
 add('warm-fast-acceptable',yes,met=True)
 add('warm-fast-feels-wrong','not_acceptable',edit=lambda r,c:r['michael_check'].update(verdict='not acceptable'))
 add('warm-equality-recorded-miss',yes,elapsed=100000,met=False)
 add('warm-exactly-twenty-percent-miss',yes,elapsed=120000,met=False)
 add('warm-over-twenty-percent','pending_pm',elapsed=120001)
 def pm(r,c):c['verified_pm_decision']=dict(build=r['build'],criterion=r['criterion'],log_sha256=RAW_SHA,elapsed_us=r['measured']['elapsed_us'],reference='SYNTHETIC PM context; not a real decision')
 add('warm-over-twenty-with-reviewed-PM-context',yes,elapsed=121000,edit=pm)
 add('product-PM-boolean-cannot-waive','pending_pm',elapsed=121000,edit=lambda r,c:r.update(pm_approval=True))
 add('missing-michael-entry','invalid',edit=lambda r,c:r.pop('michael_check'))
 add('wrong-michael-build','mismatch',edit=lambda r,c:r['michael_check'].update(build='OTHER'))
 add('wrong-log-build','mismatch',edit=lambda r,c:r.update(build='OTHER'))
 add('wrong-michael-log-hash','mismatch',edit=lambda r,c:r['michael_check'].update(log_sha256='0'*64))
 add('wrong-raw-log-hash','mismatch',edit=lambda r,c:r.update(log_sha256='0'*64))
 add('wrong-michael-numbers','mismatch',edit=lambda r,c:r['michael_check']['numbers'].update(elapsed_us=1))
 add('missing-check-date','invalid',edit=lambda r,c:r['michael_check'].pop('date'))
 add('missing-tried-description','invalid',edit=lambda r,c:r['michael_check'].pop('tried'))
 add('wrong-check-criterion','mismatch',edit=lambda r,c:r['michael_check'].update(criterion='F4'))
 add('unknown-verdict','invalid',edit=lambda r,c:r['michael_check'].update(verdict='probably'))
 add('host-clock-not-firmware','invalid',edit=lambda r,c:r['measured'].update(origin='host'))
 add('wrong-wake-event','invalid',edit=lambda r,c:r['measured'].update(start_event='capture_started'))
 add('wrong-first-frame-event','invalid',edit=lambda r,c:r['measured'].update(end_event='first_service_call'))
 add('missing-measurement','invalid',edit=lambda r,c:r.pop('measured'))
 add('negative-duration','invalid',edit=lambda r,c:r['measured'].update(elapsed_us=-1))
 add('boolean-duration','invalid',edit=lambda r,c:r['measured'].update(elapsed_us=True))
 add('non-numeric-duration','invalid',edit=lambda r,c:r['measured'].update(elapsed_us='NaN'))
 add('no-target-observation','not_run',edit=lambda r,c:r.clear())
 cases[-1]['record']=None
 def control(r,c):c['injected_delay_us']=150000;r.pop('michael_check')
 add('150ms-injection-accurate','control_detected',elapsed=150000,edit=control,met=False)
 add('150ms-injection-underreported','mismatch',elapsed=149999,edit=control,reason='injected_delay_underreported')
 add('150ms-injection-later-log-is-detecting','control_detected',elapsed=160000,edit=control)
 add('CID-absent-is-unknown-not-failure',yes)
 add('CID-null-does-not-gate',yes,edit=lambda r,c:r.update(cid=None))
 add('debug-instruments-do-not-cure-missing-entry','invalid',edit=lambda r,c:(r.pop('michael_check'),r.update(instrument='SIM',calibration='SIM',timebase='SIM')))
 add('commit-fast-acceptable',yes,criterion='F4',met=True)
 add('commit-exact-twenty-percent',yes,criterion='F4',elapsed=240000,met=False)
 add('commit-over-twenty-percent','pending_pm',criterion='F4',elapsed=240001)
 add('commit-below-max-entry-setup','mismatch',criterion='F4',edit=lambda r,c:r['measured'].update(entries=4095))
 add('commit-wrong-card-context','mismatch',criterion='F4',edit=lambda r,c:r['measured'].update(card='OTHER'))
 def underrun(r,c):r['measured'].update(underruns_during_commit=1,underruns_after=11);r['michael_check']=make_check(r)
 add('commit-underrun-cannot-be-waived','not_acceptable',criterion='F4',edit=underrun,reason='strict_underruns')
 add('commit-no-underrun-counter','invalid',criterion='F4',edit=lambda r,c:r['measured'].pop('underruns_during_commit'))
 add('commit-false-zero-counter-delta','mismatch',criterion='F4',edit=lambda r,c:r['measured'].update(underruns_after=11))
 add('commit-feels-wrong','not_acceptable',criterion='F4',edit=lambda r,c:r['michael_check'].update(verdict='not acceptable'))
 add('current-WP17-recording-deferred','not_run',criterion='F4',edit=lambda r,c:c.update(future_recording_contract=False))
 # Setup/counter omission cases must reach their intended factual predicate;
 # regenerate only the matching human-number transcription for those inputs.
 for case in cases:
  if case['case'] in ('commit-below-max-entry-setup','commit-no-underrun-counter'):
   case['record']['michael_check']=make_check(case['record'])
 return cases
