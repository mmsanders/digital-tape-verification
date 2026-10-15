"""Authenticate the non-importable authoring checkpoint and pending-cell census."""
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent

def run():
    pins=json.loads((HERE/'PINS.json').read_text());assert pins['status']=='INCOMPLETE_NONIMPORTABLE' and pins['finding']=='P2V16-002'
    raw=(HERE/'authority/WP16-INGEST-CONTRACT.md').read_bytes();assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==pins['contract_blob']
    for name,key in [('encoded-seed.tar.gz','seed_sha256'),('CENSUS.json','census_sha256')]:assert hashlib.sha256((HERE/name).read_bytes()).hexdigest()==pins[key]
    census=json.loads((HERE/'CENSUS.json').read_text());assert len(census['rows'])==6 and len(census['cases'])==1767
    pending=[c for c in census['cases'] if c.get('ruling_required')];assert len(pending)==90 and all(c['ruling_required']=='P2V16-002' for c in pending)
    assert len({c['id'] for c in census['cases']})==1767
    evidence=json.loads((HERE/'evidence/fixture-validation.json').read_text());assert len(evidence)==1704
    assert sum(x['check']=='PENDING_CONTRACT_RULING' for x in evidence)==90
    controls=json.loads((HERE/'evidence/controls.json').read_text());assert len(controls)==48 and any(x['kind']=='causal-control' for x in controls)
    assert len(json.loads((HERE/'evidence/calibration.json').read_text()))==162
    if (HERE/'FILES.json').exists():
        files=json.loads((HERE/'FILES.json').read_text())
        for name,sha in files.items():assert hashlib.sha256((HERE/name).read_bytes()).hexdigest()==sha,name
    print('Checkpoint pins PASS;90 pending cells retained;NOT IMPORTABLE')
if __name__=='__main__':run()
