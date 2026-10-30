"""Read-only audit of Michael's private C2 files. Never executes Product tools.

Usage: python audit.py PRIVATE_PACKET_DIR --candidate CLEARED_REFERENCE_ZIP --out AUDIT.json
PRIVATE_PACKET_DIR contains the two original returned ZIPs. No extraction needed.
Public CI runs --selftest only; raw music/screens remain private.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import struct
import zipfile

PINS = {
    'digital-tape.exe': 'aafb1f3444a9ddcaee599d3c1efb4dcc7e4d78dae82a0d61913abc25b80ad667',
    'tapectl.exe': '0d92bee784c25a41b96c7a864a50d8199c1a2ae6361f225e8b54b303b7f53477',
    'ingest.exe': '3895f3f356c91b8a9fe870c33694da64bf2765df308bef118d657c1be4bb9a20',
}
ZIP_PIN = 'b8a689cfbe926202b6d982dcdc5e5eaaa810d13a180556381d04811f9177ceab'
HEAD = '5101e3f32f259beeca91dd829f83d60edd6c2a22'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def text(data):
    return data.decode('utf-16') if data.startswith((b'\xff\xfe', b'\xfe\xff')) else data.decode('utf-8-sig')


def log_check(data, verify=False):
    lines = [line.strip() for line in text(data).splitlines() if line.strip()]
    require(lines == (['OK', 'exit=0'] if verify else ['exit=0']), 'unexpected CLI result')


def wav_check(data):
    require(len(data) >= 44, 'short WAV')
    riff, size, wave, fmt, fmt_size, encoding, channels, rate, byte_rate, align, bits, tag, payload = struct.unpack('<4sI4s4sIHHIIHH4sI', data[:44])
    require((riff, wave, fmt, tag) == (b'RIFF', b'WAVE', b'fmt ', b'data'), 'noncanonical WAV chunks')
    require((fmt_size, encoding, channels, rate, byte_rate, align, bits) == (16, 1, 2, 44100, 176400, 4, 16), 'wrong PCM profile')
    require(size == len(data) - 8 and payload == len(data) - 44 and payload % 4 == 0, 'invalid WAV lengths')
    return dict(bytes=len(data), sha256=sha(data), frames=payload // 4, rate=rate, channels=channels, bits=bits, seconds=payload / 176400)


def equal_dumps(a, b):
    first, second = wav_check(a), wav_check(b)
    require(a == b, 'dump sides differ')
    return first, second


def archive(path):
    raw = path.read_bytes()
    result = {}
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        for member in z.infolist():
            if member.is_dir():
                continue
            name = member.filename.replace('\\', '/').rsplit('/', 1)[-1]
            require(name not in result, 'ambiguous duplicate basename')
            result[name] = z.read(member)
    return result, dict(bytes=len(raw), sha256=sha(raw))


def audit(root, candidate):
    cli, cli_zip = archive(root / 'Digital-Tape-C2.zip')
    screens, screen_zip = archive(root / 'evidence-C2.zip')
    require(sha(candidate.read_bytes()) == ZIP_PIN, 'cleared reference candidate ZIP mismatch')
    build = json.loads(text(cli['BUILD.json']))
    require(build['source_head'] == HEAD, 'candidate head mismatch')
    for name, pin in PINS.items():
        require(sha(cli[name]) == pin, 'returned binary mismatch: ' + name)
        require(build['members'][name]['sha256'] == pin, 'BUILD member mismatch')
    results = {}
    for prefix in ('C2-', 'C2-remake-'):
        log_check(cli[prefix + 'verify.txt'], verify=True)
        for side in 'AB':
            log_check(cli[prefix + 'dump-' + side + '.txt'])
        a, b = equal_dumps(cli[prefix + 'A.wav'], cli[prefix + 'B.wav'])
        logged_hashes = re.findall(r'(?im)^SHA256\s+([0-9a-f]{64})\s+', text(cli[prefix + 'dump-hashes.txt']))
        require([h.lower() for h in logged_hashes] == [a['sha256'], b['sha256']], 'hash transcript mismatch')
        lengths = re.findall(r'(?m)^\s*(C2-[\w-]*[AB]\.wav)\s+(\d+)\s*$', text(cli[prefix + 'dump-lengths.txt']))
        require(dict(lengths) == {prefix + 'A.wav': str(a['bytes']), prefix + 'B.wav': str(b['bytes'])}, 'length transcript mismatch')
        results[prefix] = dict(verify='OK', verify_exit=0, dump_exits=[0, 0], sides_equal=True, A=a, B=b)
    return dict(
        scope='Read-only private raw-byte audit; screenshot judgments are manual in DISPOSITION.md; no Product execution',
        source_head=HEAD, candidate_zip_sha256=ZIP_PIN, member_sha256=PINS,
        packets={'Digital-Tape-C2.zip': cli_zip, 'evidence-C2.zip': screen_zip},
        members={name: dict(bytes=len(data), sha256=sha(data)) for name, data in sorted(cli.items())},
        screenshots_and_notes={name: dict(bytes=len(data), sha256=sha(data)) for name, data in sorted(screens.items())},
        cartridge=results,
        first_and_remake_equal=cli['C2-A.wav'] == cli['C2-remake-A.wav'],
        result='PASS: candidate identity, six CLI exits, two A/B pairs, four PCM files and transcripts',
    )


def selftest():
    pcm = bytes(range(64))
    wav = struct.pack('<4sI4s4sIHHIIHH4sI', b'RIFF', 36 + len(pcm), b'WAVE', b'fmt ', 16, 1, 2, 44100, 176400, 4, 16, b'data', len(pcm)) + pcm
    equal_dumps(wav, wav)
    log_check(b'OK\r\nexit=0\r\n', True)
    log_check('exit=0\r\n'.encode('utf-16'))
    controls = [
        lambda: equal_dumps(wav, wav[:-1] + b'!'),
        lambda: wav_check(wav[:-4]),
        lambda: wav_check(wav[:24] + struct.pack('<I', 48000) + wav[28:]),
        lambda: log_check(b'OK\nexit=1\n', True),
        lambda: log_check(b'exit=0\n', True),
        lambda: log_check(b'exit=1\n'),
    ]
    for control in controls:
        try:
            control()
        except ValueError:
            continue
        raise ValueError('negative control survived')
    print('PASS: synthetic valid PCM and logs; six corrupt/mismatched/failing controls rejected. No human evidence replayed.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', nargs='?', type=Path)
    parser.add_argument('--candidate', type=Path)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--selftest', action='store_true')
    args = parser.parse_args()
    if args.selftest:
        selftest()
    else:
        require(args.root is not None and args.candidate is not None and args.out is not None, 'root/candidate/out required')
        result = audit(args.root, args.candidate)
        args.out.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
        print(result['result'])
