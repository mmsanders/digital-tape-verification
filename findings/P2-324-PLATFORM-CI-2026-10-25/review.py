"""Offline r2 blocker replay over original hosted evidence; no Product/browser/child execution."""
import hashlib,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'tests/windows_interactions_r2'))
import contract,summary
HEAD='2decba2f2d38bcd6add6390ffc285e2864bf22ca'
for name,v in json.loads((HERE/'manifest.json').read_bytes()).items():
    b=(HERE/'raw'/name).read_bytes();assert len(b)==v['bytes'] and hashlib.sha256(b).hexdigest()==v['sha256'],name
reports={}
for folder in ['current','pre584']:
    result=json.loads((HERE/'raw'/folder/'interactions.json').read_bytes())
    raw=json.loads((HERE/'raw'/folder/'interactions.raw.json').read_bytes())
    assert result['source_head']==HEAD and len(result['cases'])==len(raw)==32
    for id,x in result['cases'].items():
        assert x['before']==raw[id]['captures']['before'] and x['after']==raw[id]['captures']['after']
        assert x['event_order']==[s['step'] for s in raw[id]['steps']] and raw[id]['page_errors']==[]
    reports[folder]=summary.summarize(result,HEAD)
    wire=summary.encode(reports[folder]);assert json.loads(wire.encode('cp1252'))==reports[folder]
assert reports['current']['qualified'] and reports['current']['passed']==32
assert reports['pre584']['qualified'] is False and reports['pre584']['passed']==19
probe=json.loads((HERE/'raw/selection-direction-probe.json').read_bytes())
assert probe['platform']=='win32' and probe['browser']=='155.0.4283.62'
assert probe['rows'][0]['set']==[4,4,'none'] and probe['rows'][0]['read']==[4,4,'forward']
assert probe['rows'][-1]['read']==[0,4,'backward']
try:json.loads((HERE/'raw/pre584/summary.json').read_bytes().decode('cp1252'))
except json.JSONDecodeError:pass
else:raise AssertionError('original truncated summary changed')
print('PASS retained current32/32 and pre58419/32 under corrected r2; originals/authentication/Unicode summary intact. CI/source merge clearance still pending repaired head; ZERO Product/browser execution.')
