"""Fetch original evidence transports, hash-check and safely unpack; never execute payloads."""
import argparse, hashlib, json, subprocess, zipfile
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('directory', type=Path)
parser.add_argument('--fetch', action='store_true', help='Download missing original Actions artifacts using gh')
args = parser.parse_args()
manifest = json.loads(Path(__file__).with_name('ASSETS.json').read_text())
args.directory.mkdir(parents=True, exist_ok=True)
for name, expected in manifest['assets'].items():
    target = args.directory / name
    if not target.exists() and args.fetch:
        artifact = manifest['source_artifacts'][name]
        with target.open('xb') as output:
            subprocess.run(['gh', 'api', f'repos/mmsanders/Digital-Tape/actions/artifacts/{artifact}/zip'], stdout=output, check=True)
    data = target.read_bytes()
    assert len(data) == expected['bytes'], name
    assert hashlib.sha256(data).hexdigest() == expected['sha256'], name
    if name in {'candidate-container.zip', 'evidence-container.zip', 'failed-evidence-container.zip'}:
        destination = args.directory / name.removesuffix('.zip')
        with zipfile.ZipFile(target) as archive:
            for member in archive.infolist():
                path = destination / member.filename
                assert destination.resolve() in path.resolve().parents, member.filename
                assert not member.is_dir(), member.filename
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(archive.read(member))
    print(name, expected['sha256'])
print('Verified transports only; no executable, helper, build or native observation ran.')
