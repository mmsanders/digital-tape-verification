"""Read-only replay of private Software534 originals. NEVER executes Product.

Public validation is consistency/control checking, not private raw authentication.
No native API, observer, privilege query, sparse whole hash or test rerun.
"""
import argparse
import copy
import datetime
import hashlib
import json
import ntpath
from pathlib import Path
import struct
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO/'tests/wp14_r1'))
from oracle import mbr, fat16_readme

PINS = {
    'capability.private.json': '3b65734905d26632138406bd8a0de417ee907714c98d12004958074639c99363',
    'capability.ps1': '897473a781fb42375c1345a44e1f681d55a899ff7669f53716bd9d4307b9212f',
    'child.stdout.txt': '61b4ba2123e716d14fe0d35556af714dcac26179deb28fc61c72527d38b739a7',
    'child.stderr.txt': '6cee4e182bd18ceb24089436ee649ef22be21f4827aaa6d998e37993dd0bb177',
    'local-run-1/v277-local.json': '29c238596dcedc6b0591c8dacd8900bcc261ffc748c32a03906e8d5bedef488d',
    'RUN-INVENTORY.json': '3ed08b613c3b3285d5bdf67178bd8d66c8e806f7a820d1592ca4685b3525c87e',
    'RUNTIME-INVENTORY.private.json': '632c7c099bfd6189ee08dbf6ec92ef525a228c28e472036633dac5a150feaefa',
    'ingest-version/RECEIPT.json': '07abf7c8ba28a90981053acec4cc16e98fd2f1454400027eae0dd97ce287eda7',
}
SHIP = '82798af2899e9364b9c9bfaa2021daf6cc51ccd0c6562598d50e0a86944bb7a9'
METHOD = '105ff70129de7c4de2b8f4298fb787cb29937b23b98824b006dd2c854c87cb03'
RUNTIME = 'b07b03b9ba866a341a3c13ee69710fbc8d43d4ce2523dee13f6df5c25378d15b'
SOURCE = '5e2df5aaf23e9ed0e230c444a40650da9459ddb2'
CANDIDATE = 'fce6efa71e4db0e2da8e6f8725ade692a8177f4a'
EXITS = [7, 2, 2, 2, 0, 0, 0, 0, 0, 2, 1]
CASES = ['O1-owned-file-and-child', 'I0-shipping-start-help-version-observed',
         'I1-small-shipping-image-roundtrip', 'I2-overlength-zero-byte-change',
         'I3-wrong-type-negative']
CONTROLS = ['FAT-sector-size', 'FAT-cluster-size', 'FAT-boot-signature',
            'README-content', 'UTC-create-date', 'UTC-mod-time', 'UTC-access-date',
            'UTC-creation-fraction', 'tail-drop', 'tail-add', 'last-sample']


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha(p):
    assert Path(p).stat().st_size < 128 << 20, 'never whole-hash sparse/large raw'
    return sha_bytes(Path(p).read_bytes())


def load(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))


def replay(base):
    # Pure lexical dot-segment normalization for the supplied local transport root.
    # Does not rewrite originals, map aliases, or issue a native capability probe.
    base = Path(ntpath.normpath(str(base)))
    for name, pin in PINS.items():
        assert sha(base/name) == pin, name
    cap = load(base/'capability.private.json')
    assert cap['token'] == dict(system=False, admin_sid_present=False, effective_admin=False)
    assert cap['os']['CurrentBuild'] == '26200' and cap['os']['UBR'] == 9457
    assert cap['child']['exit'] == 7 and cap['child']['completed']
    assert (base/'child.stdout.txt').read_bytes() == cap['child']['stdout'].encode()
    assert (base/'child.stderr.txt').read_bytes() == cap['child']['stderr'].encode()
    assert sha(Path(cap['owned_file']['path'])) == cap['owned_file']['before_sha256'].lower() == cap['owned_file']['after_sha256'].lower()
    assert sha(Path(cap['child']['exe'])) == cap['child']['exe_sha256'].lower()
    ingest = load(base/'ingest-version/RECEIPT.json')
    assert ingest['exit'] == 0 and not ingest['timed_out']
    assert sha(base/'ingest-version/ingest.exe') == ingest['binary_sha256'] == ingest['binary_after_sha256'] == 'd923613badda95baeb387d5415d5212a5dedb7c5c7144b21874479babd178f5b'
    assert (base/'ingest-version/stdout.txt').read_bytes() == ingest['stdout'].encode() == b'ingest 0.1.1 INGEST-1 arithmetic-profile INGEST1-AP4\n'
    assert (base/'ingest-version/stderr.txt').read_bytes() == b''
    inv = load(base/'RUN-INVENTORY.json')
    run_base = (base/'local-run-1').resolve()
    assert len(inv['files']) == 33
    listed = set()
    for row in inv['files']:
        p = (run_base/Path(row['path'].replace('\\', '/'))).resolve()
        assert p.is_relative_to(run_base) and p not in listed
        listed.add(p)
        assert p.stat().st_size == row['bytes']
        if row['sha256'] is None:
            assert p.name == 'sparse.img' and row['bytes'] == 4296015872
        else:
            assert sha(p) == row['sha256']
    assert {p.resolve() for p in run_base.rglob('*') if p.is_file()} == listed
    runtime = load(base/'RUNTIME-INVENTORY.private.json')
    assert len(runtime['files']) == 168
    for f in runtime['files']:
        p = Path(f['path'])
        assert p.stat().st_size == f['bytes'] and sha(p) == f['sha256']
    dep = load(base/'WP14-IMPORT.json')
    assert dep['tree'] == 'e1ef171ffdd7464314b4b838a7d904b1a94f5409' and len(dep['files']) == 41
    for f in dep['files']:
        p = base/'method'/f['path']
        assert p.stat().st_size == f['bytes'] and sha(p) == f['sha256']
    assert sha(base/'method/tests/windows_local_r1/local_route.py') == METHOD
    assert sha(base/'shipping/tapectl.exe') == SHIP
    r = load(run_base/'v277-local.json')
    launch = load(run_base/'LAUNCH.json')
    assert launch['method_publication'] == '6c999edaaeec53ee10ca1bede97ab87e69ee7fb7'
    assert launch['method_tree'] == 'e5f5e4ec07e3569deb68692c6722218e7197f1f0'
    assert launch['method_sha256'].lower() == r['method_sha256'] == METHOD
    assert sha(Path(launch['python'])) == launch['python_sha256'].lower() == r['runtime_sha256'] == RUNTIME
    assert launch['PYTHONOPTIMIZE'] is None and launch['exit'] == 1 and not launch['timed_out']
    assert r['source_head'] == SOURCE and r['binary_sha256'] == SHIP
    assert r['cases'] == CASES and r['controls'] == CONTROLS
    assert r['verdict'] == 'STOP' and r['error'] == 'AssertionError: allocation headroom stop'
    assert 'allocation headroom stop' in (run_base/'runner.stderr.txt').read_text()
    root = Path(r['root']).resolve()
    assert root.parent == run_base
    assert [x['exit'] for x in r['commands']] == EXITS
    assert len({x['pid'] for x in r['commands']}) == 11
    expected = [
        [launch['python'], '-I', '-c', 'import sys;print("owned-out");print("owned-err",file=sys.stderr);sys.exit(7)'],
        [str(base/'shipping/tapectl.exe')], [str(base/'shipping/tapectl.exe'), '--help'],
        [str(base/'shipping/tapectl.exe'), '--version'],
        [str(base/'shipping/tapectl.exe'), 'provision', str(root/'small.img'), '--label', 'V277', '--length-s', '9', '--image-bytes', '20972032', '--uuid', '00112233445566778899aabbccddeeff', '--epoch', '315532800'],
        [str(base/'shipping/tapectl.exe'), 'load', str(root/'small.img'), str(root/'source.wav')],
        [str(base/'shipping/tapectl.exe'), 'verify', str(root/'small.img')],
        [str(base/'shipping/tapectl.exe'), 'dump', str(root/'small.img'), '--side', 'A', '-o', str(root/'dump-A.wav')],
        [str(base/'shipping/tapectl.exe'), 'dump', str(root/'small.img'), '--side', 'B', '-o', str(root/'dump-B.wav')],
        [str(base/'shipping/tapectl.exe'), 'load', str(root/'small.img'), str(root/'over.wav')],
        [str(base/'shipping/tapectl.exe'), 'verify', str(root/'small.img')],
    ]
    def normalized(argv):
        return [s.replace('\\', '/') for s in argv]
    command_facts = []
    prior_end = 0
    for i, row in enumerate(r['commands']):
        assert normalized(row['argv']) == normalized(expected[i]), i
        assert prior_end <= row['start_utc_ns'] <= row['end_utc_ns']
        prior_end = row['end_utc_ns']
        for stream in ('stdout', 'stderr'):
            assert sha(root/f'{i}.{stream}') == row[f'{stream}_sha256']
        command_facts.append({'index': i, 'exit': row['exit'],
                              'stdout_sha256': row['stdout_sha256'], 'stderr_sha256': row['stderr_sha256']})
    assert (root/'0.stdout').read_bytes() == b'owned-out\r\n'
    assert (root/'0.stderr').read_bytes() == b'owned-err\r\n'
    assert (root/'6.stdout').read_bytes() == b'OK\n'
    assert b'Too long by 1 s for a 9-second cartridge' in (root/'9.stderr').read_bytes()
    assert (root/'10.stdout').read_bytes() == b'PARTITION_TYPE\n'
    for pair in ('image_verify', 'overlength', 'negative_verify'):
        assert r[pair]['before_sha256'] == r[pair]['after_sha256']
    original = (root/'small.img').read_bytes()
    assert len(original) == 20972032 and sha_bytes(original) == r['negative_verify']['after_sha256']
    assert original[450] == 0x0b
    healed = bytearray(original); healed[450] = 0x0e
    assert healed[:512] == mbr(len(original)//512)
    assert sha_bytes(healed) == r['image_verify']['before_sha256'] == r['overlength']['before_sha256']
    fat16_readme(root/'small.img', 'V277', 315532800)
    frames = 44101
    pattern = b''.join(struct.pack('<hh', i*251-16000, 15000-i*239) for i in range(128))
    pcm = (pattern*((frames+127)//128))[:frames*4]
    wav = struct.pack('<4sI4s4sIHHIIHH4sI', b'RIFF', 36+len(pcm), b'WAVE', b'fmt ', 16, 1, 2, 44100, 176400, 4, 16, b'data', len(pcm))+pcm
    for name in ('source.wav', 'dump-A.wav', 'dump-B.wav'):
        assert (root/name).read_bytes() == wav
    sparse = r['sparse']
    assert sparse['logical_bytes'] == sparse['allocated_before'] == 4296015872
    assert sparse['attributes'] & 0x200 and r['allocated_bytes'] == 4298790617
    assert sparse['before_samples'] == [dict(offset=0, bytes_hex=b'LOW'.hex()), dict(offset=2147484160, bytes_hex=b'MID'.hex()), dict(offset=4294967808, bytes_hex=b'HIGH'.hex())]
    # Read exactly retained marker intervals; no full sparse hash, write or new API probe.
    with (root/'sparse.img').open('rb') as f:
        for sample in sparse['before_samples']:
            b = bytes.fromhex(sample['bytes_hex']); f.seek(sample['offset'])
            assert f.read(len(b)) == b
    def time(s):
        return datetime.datetime.fromisoformat(s.replace('Z', '+00:00'))
    parent_wall = (time(launch['end_utc'])-time(launch['start_utc'])).total_seconds()
    assert parent_wall + launch['prior_new_test_wall_seconds_upper_bound'] < 96
    result = dict(schema=1, product_main='75f867712138b8e436b2cb30ba82e5590cb584ee',
                  candidate=CANDIDATE, shipping_source=SOURCE, shipping_sha256=SHIP,
                  method_publication=launch['method_publication'], method_sha256=METHOD,
                  private_original_pins=PINS, original_inventory_files=33,
                  runtime_inventory_entries=168, imported_wp14_files=41,
                  os=cap['os'], effective_admin=False, runtime_sha256=RUNTIME,
                  completed_cases=CASES, detecting_controls=CONTROLS, commands=command_facts,
                  parent_exit=1, timeout=False, local_test_wall_upper_seconds=95.493,
                  canonical_frames=frames, canonical_bytes=len(wav), canonical_sha256=sha_bytes(wav),
                  image_hashes={k:r[k] for k in ('image_verify','overlength','negative_verify')},
                  sparse_logical_bytes=4296015872, sparse_reported_bytes=4296015872,
                  root_reported_bytes=4298790617, final_inventory_reported_bytes=inv['reported_total_allocation'],
                  sparse_attribute=544, marker_rereads='three exact retained intervals match',
                  large_shipping_commands=0, allocation_scope='NOT COMPLIANT; bounded allocation not established',
                  sparse_verdict='PARTIAL / STOP before shipping large-image commands',
                  overall_windows_wp14='HELD: retained physical A6 request/offset bridge unresolved',
                  native_collection='INELIGIBLE: measured Administrator prerequisite absent',
                  raw_publication=False, physical_test=False, retry=False,
                  replay_scope='private raw read-only authentication; ZERO Product/helper/native execution')
    validate(result)
    return result


def validate(r):
    assert r['schema'] == 1 and r['candidate'] == CANDIDATE
    assert r['shipping_source'] == SOURCE and r['shipping_sha256'] == SHIP
    assert r['method_sha256'] == METHOD and r['runtime_sha256'] == RUNTIME
    assert r['private_original_pins'] == PINS
    assert r['os']['CurrentBuild'] == '26200' and r['os']['UBR'] == 9457
    assert r['os']['architecture'] == 'X64' and r['os']['EditionID'] == 'Core'
    assert r['completed_cases'] == CASES and r['detecting_controls'] == CONTROLS
    assert [c['exit'] for c in r['commands']] == EXITS
    assert r['parent_exit'] == 1 and not r['timeout'] and r['local_test_wall_upper_seconds'] < 96
    assert r['original_inventory_files'] == 33 and r['runtime_inventory_entries'] == 168
    assert r['canonical_frames'] == 44101 and r['canonical_bytes'] == 176448
    assert r['canonical_sha256'] == 'b3b824e492523cb0b1b428b8a81a874707d3d978141386ce461f74c15dddb712'
    for p in r['image_hashes'].values():
        assert p['before_sha256'] == p['after_sha256']
    assert r['sparse_logical_bytes'] == r['sparse_reported_bytes'] == 4296015872
    assert r['root_reported_bytes'] == 4298790617 and r['final_inventory_reported_bytes'] == 4298806840
    assert r['large_shipping_commands'] == 0 and r['sparse_attribute'] == 544
    assert r['allocation_scope'] == 'NOT COMPLIANT; bounded allocation not established'
    assert r['sparse_verdict'].startswith('PARTIAL / STOP')
    assert r['overall_windows_wp14'].startswith('HELD:') and not r['effective_admin']
    assert not r['raw_publication'] and not r['physical_test'] and not r['retry']


def selftest(result):
    validate(result)
    mutations = [('parent_exit', 0), ('shipping_sha256', '0'*64),
                 ('large_shipping_commands', 2), ('allocation_scope', 'PASS'),
                 ('overall_windows_wp14', 'PASS'), ('effective_admin', True),
                 ('raw_publication', True), ('retry', True)]
    for key, value in mutations:
        changed = copy.deepcopy(result); changed[key] = value
        try:
            validate(changed)
        except AssertionError:
            continue
        raise AssertionError('report mutation survived: '+key)
    print('PASS public consistency and 8 detecting controls; no private raw/Windows/Product execution claimed')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--software-root', type=Path)
    p.add_argument('--out', type=Path)
    p.add_argument('--check-public', type=Path)
    a = p.parse_args()
    if a.check_public:
        selftest(load(a.check_public))
    else:
        assert a.software_root and a.out
        r = replay(a.software_root.resolve())
        a.out.write_text(json.dumps(r, indent=2, sort_keys=True)+'\n', encoding='utf-8', newline='\n')
        print('PASS read-only private-original replay; bounded component results, S1 STOP and overall WP14 HELD')
