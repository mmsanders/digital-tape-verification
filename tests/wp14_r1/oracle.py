"""Independent WP14 contract oracles. No Product imports or implementation reads."""
import hashlib
import itertools
import struct
from pathlib import Path

BLOCK = 512
P1_START, P1_BLOCKS, P2_START = 2048, 32768, 34816
UUID = bytes.fromhex('00112233445566778899aabbccddeeff')
REFUSALS = ('REFUSE_NOT_WHOLE_DEVICE', 'REFUSE_NOT_REMOVABLE',
            'REFUSE_TOO_LARGE', 'REFUSE_SYSTEM_DISK', 'REFUSE_FOREIGN_MOUNT',
            'REFUSE_ERASE_NOT_CONFIRMED')

def geometry(length_s, blocks):
    frames = length_s * 44100
    chunks = (frames + 131071) // 131072
    return (0 < frames <= 0xffffffff and blocks > 2048 and
            2048 + chunks * 1024 <= blocks - 1)

def minimum_blocks(length_s):
    return 2048 + ((length_s * 44100 + 131071) // 131072) * 1024 + 1

def mbr(sectors, uuid=UUID, fat_type=0x0e):
    assert P2_START < sectors <= P2_START + 0xffffffff
    data = bytearray(BLOCK)
    data[440:444] = uuid[:4]
    for off, typ, start, count in ((446, fat_type, P1_START, P1_BLOCKS),
                                    (462, 0xda, P2_START, sectors-P2_START)):
        struct.pack_into('<B3sB3sII', data, off, 0, b'\xfe\xff\xff', typ,
                         b'\xfe\xff\xff', start, count)
    data[510:512] = b'\x55\xaa'
    return bytes(data)

def exact_recognition(data, sectors):
    # §2 enumerates signature, entries 1/2 and entries 3/4. It does not
    # enumerate bootstrap/disk-signature bytes in recognition.
    expected = mbr(sectors)
    return len(data) == BLOCK and data[446:512] == expected[446:512]

def layout_findings(data, sectors, uuid=None):
    """Validation oracle, not a replacement recognizer. Reachability is held."""
    assert len(data) == BLOCK
    expected = mbr(sectors, uuid or UUID)
    bad_types = any(data[i] != expected[i] for i in (450, 466))
    declared_end = sum(struct.unpack_from('<II', data, 470))
    truncated = declared_end > sectors
    masked, want = bytearray(data), bytearray(expected)
    for i in (450, 466): masked[i] = want[i]
    if truncated: masked[474:478] = want[474:478]
    # UUID may be unknown to a validation caller; A1 passes it explicitly.
    if uuid is None: masked[440:444] = want[440:444]
    out = []
    if bad_types: out.append('PARTITION_TYPE')
    if truncated: out.append('PARTITION_TRUNCATED')
    if masked != want: out.append('MBR_LAYOUT')
    return out

def policy(facts, provision=False, erase_matches=True):
    checks = (not facts['whole'], not (facts['removable'] or facts['sd_bus']),
              facts['bytes'] > 1 << 37, facts['holds_os'], facts['foreign_mount'],
              provision and not erase_matches)
    return next((name for name, fail in zip(REFUSALS, checks) if fail), None)

def permitted_subsets(base, writes):
    """Distinct-sector epoch. No proof claim for repeated writes to an LBA."""
    assert len({lba for lba, _ in writes}) == len(writes)
    states = set()
    for bits in itertools.product((False, True), repeat=len(writes)):
        landed = dict(base)
        for take, (lba, value) in zip(bits, writes):
            if take: landed[lba] = value
        states.add(tuple(sorted(landed.items())))
    return states

def fat16_readme(image, label):
    """Read FAT16 independently; allow BPB choices the contract leaves free."""
    with Path(image).open('rb') as f:
        f.seek(P1_START * BLOCK); boot = f.read(BLOCK)
        assert boot[510:512] == b'\x55\xaa', 'FAT boot signature'
        bps = struct.unpack_from('<H', boot, 11)[0]
        spc, reserved, fats, roots, total16, media, fatsecs = struct.unpack_from('<BHBHHBH', boot, 13)
        total = total16 or struct.unpack_from('<I', boot, 32)[0]
        hidden = struct.unpack_from('<I', boot, 28)[0]
        assert bps == BLOCK and spc == 4 and reserved > 0 and fats > 0
        assert total == P1_BLOCKS and hidden == P1_START
        rootsecs = (roots * 32 + BLOCK - 1)//BLOCK
        clusters = (total - reserved - fats * fatsecs - rootsecs)//spc
        assert 4085 <= clusters < 65525 and fatsecs*BLOCK >= (clusters+2)*2
        fat_start = P1_START + reserved
        f.seek(fat_start*BLOCK); fat = f.read(fatsecs*BLOCK)
        assert fat[:3] == bytes((media, 255, 255))
        for i in range(1, fats):
            f.seek((fat_start+i*fatsecs)*BLOCK); assert f.read(len(fat)) == fat
        root_start = fat_start + fats*fatsecs
        f.seek(root_start*BLOCK); root = f.read(rootsecs*BLOCK)
        entries, labels = [], []
        for i in range(0, len(root), 32):
            e = root[i:i+32]
            if not e[0]: break
            if e[0] == 0xe5 or e[11] == 0x0f: continue
            if e[11] & 8:
                labels.append(e[:11]); continue
            entries.append(e)
        effective_labels = labels or ([boot[43:54]] if boot[38] == 0x29 else [])
        assert effective_labels == [b'DIGITALTAPE'], 'FAT volume label'
        assert len(entries) == 1 and entries[0][:11] == b'README  TXT'
        entry = entries[0]
        cluster = struct.unpack_from('<H', entry, 26)[0]
        length = struct.unpack_from('<I', entry, 28)[0]
        data_start = root_start + rootsecs
        content, visited = bytearray(), set()
        while cluster < 0xfff8:
            assert 2 <= cluster <= clusters+1 and cluster not in visited
            visited.add(cluster)
            f.seek((data_start+(cluster-2)*spc)*BLOCK); content.extend(f.read(spc*BLOCK))
            cluster = struct.unpack_from('<H', fat, cluster*2)[0]
        want = ('This is a Digital Tape cartridge.\r\nLabel: '+label+
                '\r\nPlease do not format or erase this card on a computer.\r\n'
                'Use the Digital Tape app to load music onto it.\r\n').encode('utf-8')
        assert bytes(content[:length]) == want, 'README bytes'
        return {'clusters': clusters, 'readme_sha256': hashlib.sha256(want).hexdigest()}

def trace_audit(trace):
    """Audit normalized observations; instrumentation/binding must be authenticated."""
    operation, events = trace['operation'], trace['events']
    if trace.get('refusal'):
        assert trace['exit'] == 3
        assert not any(e['kind'] in ('write_open', 'write') for e in events)
        assert trace['refusal'] in REFUSALS
    if operation == 'verify':
        assert not any(e['kind'] in ('write_open', 'write') for e in events)
        bindings = [e for e in events if e['kind'] == 'engine_bind']
        if trace.get('engine_used', True): assert bindings
        assert all(e['write_is_null'] for e in bindings)
    pending = False
    for e in events:
        if e['kind'] == 'write':
            assert e['issued_before_return'] and not e.get('coalesced', False)
            assert e['offset'] >= 0 and e['offset'] + e['bytes'] <= trace['target_bytes']
            pending = True
        if e['kind'] == 'flush' and e['success']:
            assert e['os_call'] == {'linux':'fsync','macos':'F_FULLFSYNC','windows':'FlushFileBuffers'}[trace['platform']]
            assert e['os_success'], 'flush reported success after OS failure'
            pending = False
    if trace.get('success') and operation in ('provision','load','promote','record','reset-b','respool'):
        assert not pending, 'successful command left writes unflushed'
