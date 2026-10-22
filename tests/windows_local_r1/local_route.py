"""Verification277 finite Windows no-card route. No Product imports/native observer.

All outputs stay in one newly created ordinary owned directory. Preserve on failure.
Sparse file is a regular-file surrogate, never physical A6 evidence.
"""
import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import struct
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'wp14_r1'))
from oracle import UUID, P2_START, minimum_blocks, mbr, fat16_readme
from runner import make_wav, compare_wav, reject_control, fat_controls

SHIP = '82798af2899e9364b9c9bfaa2021daf6cc51ccd0c6562598d50e0a86944bb7a9'
LIMIT = 1 << 30
LARGE = (1 << 32) + (1 << 20)


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def ordinary(path, directory=False):
    """Reject device/UNC/ADS and every existing reparse component before use."""
    s = str(path)
    assert not s.startswith(('\\\\', '//', '/dev/', '\\Device\\')), 'device/UNC target'
    assert ':' not in s[2:], 'alternate stream'
    p = Path(path).absolute()
    for q in [p, *p.parents]:
        st = q.lstat()
        assert not stat.S_ISLNK(st.st_mode), 'symlink'
        assert not getattr(st, 'st_file_attributes', 0) & 0x400, 'reparse point'
    assert p.is_dir() if directory else p.is_file(), 'ordinary type'
    return p


def sparse(f):
    import msvcrt
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    fn = kernel.DeviceIoControl
    fn.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_void_p,
                   ctypes.c_uint32, ctypes.c_void_p, ctypes.c_uint32,
                   ctypes.POINTER(ctypes.c_uint32), ctypes.c_void_p]
    fn.restype = ctypes.c_int32
    done = ctypes.c_uint32()
    if not fn(msvcrt.get_osfhandle(f.fileno()), 0x900C4, None, 0,
              None, 0, ctypes.byref(done), None):
        raise ctypes.WinError(ctypes.get_last_error())


def allocated(path):
    k = ctypes.WinDLL('kernel32', use_last_error=True)
    fn = k.GetCompressedFileSizeW
    fn.argtypes = [ctypes.c_wchar_p, ctypes.POINTER(ctypes.c_uint32)]
    fn.restype = ctypes.c_uint32
    high = ctypes.c_uint32()
    ctypes.set_last_error(0)
    low = fn(str(path), ctypes.byref(high))
    err = ctypes.get_last_error()
    if low == 0xffffffff and err:
        raise ctypes.WinError(err)
    return (high.value << 32) | low


def run(binary, base, head, receipt):
    assert os.name == 'nt', 'actual route requires local Windows'
    assert re.fullmatch('[0-9a-f]{40}', head), 'full source pin required'
    binary = ordinary(binary)
    assert digest(binary) == SHIP, 'exact shipping binary mismatch; stop before launch'
    base = ordinary(base, True)
    assert receipt.parent.absolute() == base and re.fullmatch(r'v277-[a-z0-9-]+\.json', receipt.name), 'receipt must be fresh direct child of owned base'
    # No supplied Product target argument exists; every target is created below.
    root = base / ('verification277-' + os.urandom(16).hex())
    root.mkdir(exist_ok=False)
    ordinary(root, True)
    report = {'schema': 1, 'source_head': head, 'binary_sha256': SHIP,
              'root': str(root), 'platform': sys.getwindowsversion()._asdict()
              if hasattr(sys.getwindowsversion(), '_asdict') else str(sys.getwindowsversion()),
              'runtime': sys.version, 'runtime_image': sys.executable,
              'cases': [], 'controls': [], 'commands': [], 'physical_a6': False,
              'verdict': 'INCOMPLETE'}
    report['method_sha256'] = digest(Path(__file__))
    report['runtime_sha256'] = digest(Path(sys.executable))
    start = time.monotonic()

    def save():
        receipt.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')

    def budget():
        assert time.monotonic() - start < 1500, 'headroom stop before next case'
        n = sum(allocated(p) for p in root.iterdir() if p.is_file())
        report['allocated_bytes'] = n
        assert n < LIMIT - (128 << 20), 'allocation headroom stop'

    def invoke(argv, code=0, token=None, observational=False):
        budget()
        idx = len(report['commands'])
        row = {'argv': list(map(str, argv)), 'start_utc_ns': time.time_ns()}
        report['commands'].append(row)
        save()
        with (root / (str(idx) + '.stdout')).open('xb') as out, (root / (str(idx) + '.stderr')).open('xb') as err:
            p = subprocess.Popen(list(map(str, argv)), stdout=out, stderr=err)
            row['pid'] = p.pid
            try:
                row['exit'] = p.wait(timeout=min(120, max(1, 1790 - (time.monotonic()-start))))
            except subprocess.TimeoutExpired:
                p.kill()  # only this owned child, never basename/session termination
                row['exit'] = p.wait(timeout=10)
                row['timeout'] = True
        row['end_utc_ns'] = time.time_ns()
        row['stdout_sha256'] = digest(root / (str(idx) + '.stdout'))
        row['stderr_sha256'] = digest(root / (str(idx) + '.stderr'))
        save()
        assert not row.get('timeout'), 'owned child timeout; stop'
        text = (root / (str(idx) + '.stdout')).read_bytes() + (root / (str(idx) + '.stderr')).read_bytes()
        if not observational:
            assert row['exit'] == code, row
            if token is not None:
                assert token.encode() in text, 'missing expected output'
        return text

    try:
        # O1 fixed harmless child: native process/exit/stdout/stderr capture, no FFI.
        f = root / 'ordinary.bin'
        f.write_bytes(b'owned verification277\n')
        assert f.read_bytes() == b'owned verification277\n'
        before = digest(f)
        g = root / 'renamed.bin'
        f.rename(g)
        assert digest(g) == before and not f.exists()
        invoke([sys.executable, '-I', '-c', 'import sys;print("owned-out");print("owned-err",file=sys.stderr);sys.exit(7)'], 7, 'owned-out')
        assert b'owned-err' in (root / '0.stderr').read_bytes()
        report['cases'].append('O1-owned-file-and-child')
        # Identity observations: these switches are not new promised CLI semantics.
        for args in ([], ['--help'], ['--version']):
            invoke([binary, *args], observational=True)
        report['cases'].append('I0-shipping-start-help-version-observed')
        wav = root / 'source.wav'
        make_wav(wav, 44101)  # non-block tail, two channels, nonzero final frame
        image = root / 'small.img'
        size = (P2_START + minimum_blocks(9)) * 512
        invoke([binary, 'provision', image, '--label', 'V277', '--length-s', '9',
                '--image-bytes', size, '--uuid', UUID.hex(), '--epoch', '315532800'])
        with image.open('rb') as f:
            assert f.read(512) == mbr(size // 512)
        fat16_readme(image, 'V277', 315532800)
        report['controls'].extend(fat_controls(image, 'V277', 315532800))
        invoke([binary, 'load', image, wav])
        before = digest(image)
        invoke([binary, 'verify', image], token='OK')
        assert digest(image) == before, 'verify changed owned image'
        report['image_verify'] = {'before_sha256': before, 'after_sha256': digest(image)}
        for side in ('A', 'B'):
            output = root / ('dump-' + side + '.wav')
            invoke([binary, 'dump', image, '--side', side, '-o', output])
            compare_wav(wav, output)
            if side == 'A':
                good = output.read_bytes()
                for name, bad in [('tail-drop', good[:-4]), ('tail-add', good+b'\0'*4),
                                  ('last-sample', good[:-1]+bytes([good[-1]^1]))]:
                    output.write_bytes(bad)
                    reject_control(compare_wav, wav, output)
                    report['controls'].append(name)
                output.write_bytes(good)
        report['cases'].append('I1-small-shipping-image-roundtrip')
        # A7: first overlength frame, refuse before mutation; no exhaustion campaign.
        over = root / 'over.wav'
        make_wav(over, 9*44100+1)
        invoke([binary, 'load', image, over], 2, 'Too long by 1 s')
        assert digest(image) == before, 'overlength changed owned image'
        report['overlength'] = {'before_sha256': before, 'after_sha256': digest(image)}
        report['cases'].append('I2-overlength-zero-byte-change')
        with image.open('r+b') as f:
            f.seek(450); f.write(b'\x0b')
        bad_hash = digest(image)
        invoke([binary, 'verify', image], 1, 'PARTITION_TYPE')
        assert digest(image) == bad_hash, 'negative verify changed image'
        report['negative_verify'] = {'before_sha256': bad_hash, 'after_sha256': digest(image)}
        report['cases'].append('I3-wrong-type-negative')
        # S1: explicitly sparse file. No VHD/mount/device operation exists here.
        big = root / 'sparse.img'
        with big.open('x+b') as f:
            sparse(f)
            f.truncate(LARGE)
            for off, data in [(0, b'LOW'), ((1<<31)+512, b'MID'), ((1<<32)+512, b'HIGH')]:
                f.seek(off); f.write(data)
            f.flush(); os.fsync(f.fileno())
            for off, data in [(0, b'LOW'), ((1<<31)+512, b'MID'), ((1<<32)+512, b'HIGH')]:
                f.seek(off); assert f.read(len(data)) == data, '64bit offset alias'
        report['sparse'] = {'logical_bytes': big.stat().st_size, 'allocated_before': allocated(big)}
        report['sparse']['before_samples'] = [{'offset': off, 'bytes_hex': data.hex()} for off, data in
            [(0, b'LOW'), ((1<<31)+512, b'MID'), ((1<<32)+512, b'HIGH')]]
        report['sparse']['file_id'] = big.stat().st_ino
        report['sparse']['attributes'] = big.stat().st_file_attributes
        assert big.stat().st_file_attributes & 0x200, 'sparse flag missing'
        budget()
        invoke([binary, 'provision', big, '--label', 'V277', '--length-s', '9',
                '--image-bytes', LARGE, '--uuid', UUID.hex(), '--epoch', '315532800'])
        with big.open('rb') as f:
            assert f.read(512) == mbr(LARGE//512)
        fat16_readme(big, 'V277', 315532800)
        invoke([binary, 'verify', big], token='OK')
        report['sparse']['allocated_after'] = allocated(big)
        with big.open('rb') as f:
            report['sparse']['after_samples'] = []
            for off in (0, (1<<31)+512, (1<<32)+512, LARGE-512):
                f.seek(off)
                report['sparse']['after_samples'].append({'offset': off, 'bytes_hex': f.read(512).hex()})
        report['cases'].append('S1-64bit-regular-sparse-file-and-shipping-geometry')
        budget()
        assert digest(binary) == SHIP, 'binary changed during route'
        report['verdict'] = 'PASS finite local no-card rows only'
    except Exception as e:
        report['verdict'] = 'STOP'
        report['error'] = type(e).__name__ + ': ' + str(e)
        raise
    finally:
        report['elapsed_seconds'] = time.monotonic() - start
        report['inventory'] = [{'name': p.name, 'bytes': p.stat().st_size,
                                'sha256': digest(p)} for p in root.iterdir()
                               if p.is_file() and p.stat().st_size < (128 << 20)]
        # Sparse image is retained locally; never hash/zip all logical zero holes.
        save()


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--binary', type=Path, required=True)
    p.add_argument('--base', type=Path, required=True)
    p.add_argument('--source-head', required=True)
    p.add_argument('--receipt', type=Path, required=True)
    a = p.parse_args()
    assert not a.receipt.exists(), 'fresh receipt required'
    ordinary(a.receipt.parent, True)
    run(a.binary, a.base, a.source_head, a.receipt)
