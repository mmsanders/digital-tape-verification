"""Offline authentication/review of the retained correction evidence. No Product execution."""
import hashlib,importlib.util,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
HEAD='f9306c2c5a42ebd039edd67b0b7cef6a7d434b2b'
for name,entry in json.loads((HERE/'manifest.json').read_text()).items():
    b=(HERE/name).read_bytes();assert len(b)==entry['bytes'] and hashlib.sha256(b).hexdigest()==entry['sha256'],name
spec=importlib.util.spec_from_file_location('discovery318',ROOT/'tests/windows_discovery_r1/contract.py')
oracle=importlib.util.module_from_spec(spec);spec.loader.exec_module(oracle)
r=json.loads((HERE/'raw/discovery.json').read_bytes());oracle.qualify(r,HEAD)
raw=json.loads((HERE/'raw/discovery.raw.json').read_bytes())
assert len(raw['rows'])==len(oracle.CASES)==23
for actual,c in zip(raw['rows'],oracle.CASES):
    assert actual['id']==c['id'] and actual['ran']['exit']==c['exit']
    assert bytes(actual['ran']['stdout']).decode()==c['stdout']
    assert (bytes(actual['ran']['report']).decode() if actual['ran']['report'] is not None else '')==c['report']
    assert actual['view']['card_line']==oracle.expected(c)['line'] and not actual['view']['make_enabled']
q=json.loads((HERE/'raw/correction1.json').read_bytes());a=q['admission']
assert q['source_head']==HEAD and not q['native_ui'] and not q['live_enumeration']
assert a['paused_after_stop_read'] and a['shutdown_completed_before_resume'] and a['refused']
assert not a['registered'] and a['cards_active'] is None
assert a['child_callbacks']==a['current_publications']==a['emissions_after_resume']==0
assert a['trace'].index('stop-polls')<a['trace'].index('cards:admission-refused')
assert 'cards:worker-start' not in a['trace']
dom=json.loads((HERE/'dom-corrected.json').read_bytes());old=json.loads((HERE/'dom-old-control.json').read_bytes())
assert dom['source_head']==old['source_head']==HEAD and not dom['native_ui'] and not dom['page_errors']
assert dom['renderer_sha256']==hashlib.sha256((HERE/'renderer.mjs').read_bytes()).hexdigest()
assert old['renderer_sha256']==hashlib.sha256((HERE/'old-renderer.mjs').read_bytes()).hexdigest()
assert len(dom['rows'])==len(q['details_views'])==12
diagnostics=0
for id,x in q['details_views'].items():
    v=x['view'];d=dom['rows'][id];need=not(id.endswith('/one64') or id.endswith('/fresh-success-after-failure'))
    assert v['view']==('empty' if id.startswith('empty/') else 'ready')
    assert v['card_details_available']==need and not v['make_enabled']
    assert d['show_details_visible']==need and d['details_visible']==need and d['details_calls']==int(need)
    assert d['card']==v['card_line'] and d['enumerated_items']==0 and d['make_disabled']
    assert d['details_text']==(x['details'] if need else '')
    if need:assert not old['rows'][id]['show_details_visible'];diagnostics+=1
    if id.endswith('/fresh-success-after-failure'):assert 'failed' not in x['details']
assert diagnostics==8
b=json.loads((HERE/'raw/child-build.json').read_bytes())
assert b['source']==HEAD and b['version']=='tapectl-wp15-s2+'+HEAD[:12]
assert b['sha256']==r['child']['sha256']=='44ef26869ba2d01a8a183660a2c7a050d0e7e9ff37c40b727131512739ea6ded'
assert b['engine_tree']==oracle.ENGINE and b['test_build'] is False
assert 'HEAD_ID='+HEAD[:12] in b['build_command'] and b['build_command'].endswith('../build/host/tapectl.exe')
print('PASS exact correction records/hash authentication,23 unchanged modeled rows,stop/admission order,12 renderer rows/8 diagnostics and old-renderer control. No native/child/device execution.')
