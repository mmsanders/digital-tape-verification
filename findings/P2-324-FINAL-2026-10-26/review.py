"""Offline authentication/replay of Software584's exact green-head records."""
import hashlib,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[1]/'tests/windows_interactions_r2'))
import contract,summary
HEAD='3104e04e99a25933a34f0eae38fef6fd39b26802'
for name,v in json.loads((HERE/'manifest.json').read_bytes()).items():
    b=(HERE/'raw'/name).read_bytes()
    assert len(b)==v['bytes'] and hashlib.sha256(b).hexdigest()==v['sha256'],name
for folder,passed in [('current',32),('pre584',18)]:
    result=json.loads((HERE/'raw'/folder/'interactions.json').read_bytes())
    raw=json.loads((HERE/'raw'/folder/'interactions.raw.json').read_bytes())
    assert result['source_head']==HEAD and result['browser']=='155.0.4283.62'
    assert list(result['cases'])==list(raw)==[c['id'] for c in contract.CASES]
    for id,x in result['cases'].items():
        assert x['before']==raw[id]['captures']['before'] and x['after']==raw[id]['captures']['after']
        assert x['event_order']==[s['step'] for s in raw[id]['steps']] and raw[id]['page_errors']==[]
        assert raw[id]['rpc'] and raw[id]['calls']
    observed=summary.summarize(result,HEAD)
    assert observed==json.loads((HERE/'raw'/folder/'summary.json').read_bytes())
    assert observed['passed']==passed and observed['qualified']==(folder=='current')
    assert json.loads(summary.encode(observed).encode('cp1252'))==observed
    q=(HERE/'raw'/folder/'qualifier.txt').read_text(encoding='utf-8-sig')
    assert ('qualifier exit 0' if folder=='current' else 'expected nonzero') in q
current=json.loads((HERE/'raw/current/interactions.json').read_bytes())
contract.qualify(current,HEAD)
bad=json.loads(json.dumps(current));bad['cases']['E-ascii-caret']['after']['label_value']='stale'
try:contract.qualify(bad,HEAD)
except AssertionError:pass
else:raise AssertionError('retained-record stale-label control did not fail')
print('PASS exact retained32/32; old renderer18/32 rejected; raw/summary/order/Unicode authentication; stale-label negative. ZERO Product/browser execution.')
