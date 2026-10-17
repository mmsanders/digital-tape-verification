"""Reauthenticate retained ZIPs/inner inventories; no engine/campaign execution."""
import argparse,hashlib,json
from pathlib import Path,PurePosixPath
HERE=Path(__file__).resolve().parent
def run(root,out):
    manifest=HERE.parent/'P2-WP10-SUBSET-R2-2026-10-17/artifacts.json';artifacts=json.loads(manifest.read_text());files=0;bundles=[]
    for a in artifacts:
        z=root/(a['name']+'.zip');b=z.read_bytes();assert len(b)==a['size_in_bytes'] and hashlib.sha256(b).hexdigest()==a['digest'].split(':')[1]
        base=root/a['name'];names=set()
        for l in (base/'SHA256SUMS').read_text().splitlines():
            h,n=l.split(None,1);n=str(PurePosixPath(n.lstrip('*')))
            assert not PurePosixPath(n).is_absolute() and '..' not in PurePosixPath(n).parts and n not in names
            names.add(n);assert hashlib.sha256((base/n).read_bytes()).hexdigest()==h;files+=1
        assert names|{'SHA256SUMS'}=={str(p.relative_to(base)) for p in base.rglob('*') if p.is_file()}
        bundles.append(dict(id=a['id'],name=a['name'],sha256=a['digest'],bytes=len(b),indexed_files=len(names)))
    r=dict(artifact_manifest_sha256=hashlib.sha256(manifest.read_bytes()).hexdigest(),ZIPs=len(bundles),indexed_files=files,bundles=bundles)
    out.write_text(json.dumps(r,indent=2)+'\n');print(len(bundles),'ZIPs,',files,'indexed members authenticated')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args();run(a.root,a.out)
