"""Authenticate saved evidence; optionally reconstruct into a NEW directory."""
import argparse, base64, gzip, hashlib, json
from pathlib import Path, PurePosixPath
p=argparse.ArgumentParser(); p.add_argument('--quiet', required=True, type=Path); p.add_argument('--out', type=Path); a=p.parse_args()
here=Path(__file__).resolve().parent
m=json.loads((here/'INVENTORY.json').read_text()); compressed=(here/'observations.json.gz').read_bytes()
assert hashlib.sha256(compressed).hexdigest()==m['observations_sha256']
assert len(compressed)==m['observations_bytes']
stored=json.loads(gzip.decompress(compressed)); quiet=a.quiet.read_bytes(); rows=[]
for r in m['members']:
    name=r['path']; path=PurePosixPath(name)
    assert not path.is_absolute() and '..' not in path.parts
    data=quiet if name.lower().endswith('.wav') else base64.b64decode(stored[name],validate=True)
    assert len(data)==r['bytes'] and hashlib.sha256(data).hexdigest()==r['sha256'], name
    rows.append((name,data))
assert set(stored)=={name for name,_ in rows if not name.lower().endswith('.wav')}
if a.out:
    a.out.mkdir(parents=True,exist_ok=False)
    for name,data in rows:
        target=a.out/name; target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(data)
print(json.dumps({'authenticated_members':len(rows),'wav_members':sum(n.lower().endswith('.wav') for n,_ in rows),'reconstructed':str(a.out) if a.out else None}))
