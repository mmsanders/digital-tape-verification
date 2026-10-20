import json
from pathlib import Path
from supplement import controls
p=Path(__file__).parent
r=json.loads((p/'RESULT.json').read_text())
assert len(controls())==21
assert r['events_streamed']==948634 and r['old_checker_verdict']=='FAIL'
assert r['amended_method']['verdict']=='HELD' and not r['amended_method']['excluded']
assert r['all_logkey_file_writes']==r['all_logkey_disk_writes']==129
assert r['distinct_logkey_names']==1
assert not r['records_with_both_request_ids_in_named_fields'] and not r['records_with_both_request_ids_in_payload']
for row in r['native_identity_audit']:
 assert row['disk']==0 and not row['request_equal'] and row['same_request_size_disk_matches']==0
 assert row['same_key_size_disk_candidates']>1
 assert row['disk_offset']-row['file_offset']==row['offset_delta']==3261169664
print('PASS bounded retained audit consistency and21 controls; amended HELD preserved; no full-capture CI claim')
