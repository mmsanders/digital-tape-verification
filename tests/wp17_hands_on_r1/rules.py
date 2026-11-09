"""Verifier semantic fixtures for ADR208. NOT a firmware/log adapter or acceptance API."""
TARGET_US={'F3':100000,'F4':200000}
def integer(v):return isinstance(v,int) and not isinstance(v,bool) and v>=0
def numbers(measured):return {k:measured[k] for k in ('elapsed_us','entries','underruns_during_commit') if k in measured}
def evaluate_normalized_fixture(record,context):
 def result(outcome,reason,target_met=None):
  return dict(rule_outcome=outcome,reason=reason,target_met=target_met,accepted=False,physical_run=False,candidate_executed=False,binding='UNBOUND_SERIAL_DECLARATION')
 criterion=context['criterion']
 if record is None or criterion=='F4' and not context.get('future_recording_contract',False):return result('not_run','observation_absent_or_recording_deferred')
 if not isinstance(record,dict) or not isinstance(record.get('measured'),dict):return result('invalid','record_shape')
 measured=record['measured'];elapsed=measured.get('elapsed_us')
 if not integer(elapsed):return result('invalid','timer_value')
 if measured.get('origin')!='mcu' or (measured.get('start_event'),measured.get('end_event'))!=tuple(context['events']):return result('invalid','measurement_boundaries')
 if record.get('build')!=context['candidate_build'] or record.get('criterion')!=criterion or record.get('log_sha256')!=context['raw_log_sha256']:return result('mismatch','candidate_or_raw_log_identity')
 target=TARGET_US[criterion];met=elapsed<target
 if context.get('injected_delay_us') is not None:
  return result('control_detected' if elapsed>=context['injected_delay_us'] else 'mismatch','injected_delay_observed' if elapsed>=context['injected_delay_us'] else 'injected_delay_underreported',met)
 check=record.get('michael_check')
 if not isinstance(check,dict) or any(not isinstance(check.get(k),str) or not check[k] for k in ('date','build','criterion','tried','log_sha256','verdict')):return result('invalid','michael_entry_missing_or_incomplete',met)
 if (check['build'],check['criterion'],check['log_sha256'])!=(context['candidate_build'],criterion,context['raw_log_sha256']) or check.get('numbers')!=numbers(measured):return result('mismatch','michael_entry_does_not_match',met)
 if check['verdict'] not in ('acceptable','not acceptable'):return result('invalid','verdict_value',met)
 if criterion=='F4':
  if measured.get('entries')!=4096 or measured.get('card')!=context['slowest_card']:return result('mismatch','required_commit_setup',met)
  count=measured.get('underruns_during_commit')
  if not integer(count):return result('invalid','underrun_observation_missing',met)
  if 'underruns_before' in measured or 'underruns_after' in measured:
   before,after=measured.get('underruns_before'),measured.get('underruns_after')
   if not integer(before) or not integer(after) or after-before!=count:return result('mismatch','underrun_delta',met)
  if count!=0:return result('not_acceptable','strict_underruns',met)
 if check['verdict']=='not acceptable':return result('not_acceptable','michael_declined',met)
 if elapsed*5>target*6:
  decision=context.get('verified_pm_decision',{})
  wanted=(context['candidate_build'],criterion,context['raw_log_sha256'],elapsed)
  got=(decision.get('build'),decision.get('criterion'),decision.get('log_sha256'),decision.get('elapsed_us'))
  if got!=wanted or not decision.get('reference'):return result('pending_pm','miss_over_twenty_percent',met)
 return result('eligible_normalized_fixture','record_matches_method_rules',met)
