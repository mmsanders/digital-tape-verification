"""Offline consistency check for the retained two-build disclosure, no payload execution."""
import hashlib, json, zipfile
from pathlib import Path
p = Path(__file__).parent
assets = json.loads((p/'ASSETS.json').read_text())
for name in ('evidence-container.zip', 'failed-evidence-container.zip'):
    data = (p/name).read_bytes()
    assert len(data) == assets['assets'][name]['bytes']
    assert hashlib.sha256(data).hexdigest() == assets['assets'][name]['sha256']
with zipfile.ZipFile(p/'evidence-container.zip') as archive:
    raw = archive.read('RECORD.json')
    producer = json.loads(raw)
with zipfile.ZipFile(p/'failed-evidence-container.zip') as archive:
    prior = json.loads(archive.read('INVENTORY.json'))
audit = json.loads((p/'AUDIT.json').read_text())
checked = json.loads((p/'CHECKED_RECORD.json').read_text())
assert hashlib.sha256(raw).hexdigest() == audit['producer_record_sha256']
assert producer['final_build_count'] == 1 and checked['final_build_count'] == 2
assert {**producer, 'final_build_count':2} == checked
assert audit['measured_judgments']['actual_compilations'] == 2
assert audit['measured_judgments']['uploaded_candidate_artifacts'] == 1
assert next(x for x in prior['members'] if x['name']=='digital-tape.exe')['sha256'] == audit['process_disclosure']['first_app_sha256']
assert audit['process_disclosure']['first_app_sha256'] != audit['members']['digital-tape.exe']['sha256']
print('PASS retained evidence consistency; overall candidate disposition remains HELD')
