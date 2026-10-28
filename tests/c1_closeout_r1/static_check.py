"""Bounded own-host/G1 source gate. Never executes Product or opens a device."""
import argparse, json, re
from pathlib import Path

RULES = {
    'raw-windows-device': r'PhysicalDrive|GLOBALROOT|HarddiskVolume|\\\\[.?]\\(?:Volume|[A-Za-z]:)',
    'raw-posix-device': r'/dev/(?:r?disk|sd[a-z]|mmcblk|nvme|loop|mapper/)',
    'device-control': r'\b(?:DeviceIoControl|NtDeviceIoControlFile|IOCTL_DISK_\w+|IOCTL_STORAGE_\w+|FSCTL_\w+|BLKGETSIZE\w*|BLKFLSBUF)\b',
    'native-device-open': r'\b(?:NtOpenFile|NtCreateFile|CreateFile[AW]|CreateFile2)\s*\(',
    'engine-or-layout': r'\b(?:tape_mount|tape_format|tape_dev|TAPEFS|LBA_CHUNK_BASE)\b',
}
EXTENSIONS = {'.rs', '.c', '.h', '.cpp', '.js', '.mjs', '.ts', '.html'}

def scan(root):
    root = Path(root)
    files = sorted(p for p in root.rglob('*') if p.is_file() and p.suffix in EXTENSIONS
                   and not {'target','vendor','node_modules','.git','tests'}.intersection(p.relative_to(root).parts))
    assert files, 'no first-party source scanned'
    hits = []
    for p in files:
        for line, text in enumerate(p.read_text(encoding='utf-8').splitlines(), 1):
            for rule, pattern in RULES.items():
                if re.search(pattern, text):
                    hits.append(dict(path=p.relative_to(root).as_posix(), line=line, rule=rule))
    return dict(files=[p.relative_to(root).as_posix() for p in files], hits=hits)

if __name__ == '__main__':
    p=argparse.ArgumentParser(); p.add_argument('root',type=Path); a=p.parse_args()
    result=scan(a.root); print(json.dumps(result,indent=2)); raise SystemExit(bool(result['hits']))
