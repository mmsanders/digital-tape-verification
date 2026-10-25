"""Offline review of retained Software578 controlled evidence; no Product execution."""
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
HEAD = '18f424f66bbd0ad9c9f74c930d524627a3a6cf82'
HASHES = {
    'discovery.json': '37a783c6b0a82c3bd9e9b6c06698ebb3fc114dced159c0bb6e7936e125703f75',
    'discovery.raw.json': '3c6bcdcf3077e66566c0e74a7057a11ef55aa529ae1ab48631d57b7e7bdb8c1e',
}
for name, want in HASHES.items():
    assert hashlib.sha256((HERE/'raw'/name).read_bytes()).hexdigest() == want
spec = importlib.util.spec_from_file_location('discovery318', ROOT/'tests/windows_discovery_r1/contract.py')
oracle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(oracle)
oracle.controls()
result = json.loads((HERE/'raw/discovery.json').read_text())
print(oracle.qualify(result, HEAD))
raw = json.loads((HERE/'raw/discovery.raw.json').read_text())
assert len(raw['rows']) == len(oracle.CASES) == 23
assert {r['id'] for r in raw['rows']} == {c['id'] for c in oracle.CASES}
for r in raw['rows']:
    expected = result['rows'][r['id']]
    assert r['view']['card_line'] == expected['line']
    assert r['view']['make_enabled'] is False
    assert r['id_specific'] == expected['id_specific']
for name, diagnostic in [('zero-unprobed', '3 not checked'), ('enum-unavailable', 'CARDS_ENUM_UNAVAILABLE')]:
    r = next(r for r in raw['rows'] if r['id'] == name)
    assert diagnostic in r['details']
    assert r['view']['view'] == 'empty' and r['view']['message'] is None
    assert r['view']['details_available'] is False
child = json.loads((HERE/'raw/child-build.json').read_text())
assert child['source'] == HEAD and child['version'] == 'tapectl-wp15-s2+'+HEAD[:12]
assert child['sha256'] == result['child']['sha256']
assert child['engine_tree'] == oracle.ENGINE and child['test_build'] is False
assert 'HEAD_ID='+HEAD[:12] in child['build_command']
assert child['build_command'].endswith('../build/host/tapectl.exe')
for path, pair in child['crosswalk']['blobs'].items():
    if path != 'host/tapectl.c':
        assert pair['current'] == pair['accepted']
print('PASS retained-evidence authentication/replay; V318-02 diagnostic availability gap reproduced in actual controlled views')
print('V318-01 is a source-level interleaving proof; no Rust/native execution claimed. Overall CHANGES REQUIRED.')
