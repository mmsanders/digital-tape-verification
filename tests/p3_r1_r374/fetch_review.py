"""Fetch/check permanent raw assets, safely unpack, then independently replay."""
import hashlib,json,sys,urllib.request,zipfile
from pathlib import Path
from review_retained import review
ROOT=Path(__file__).resolve().parents[2]
pins=json.loads((ROOT/'findings/P3-R1-374/EVIDENCE.json').read_text())
out=Path(sys.argv[1]).resolve();out.mkdir(parents=True,exist_ok=True);dirs=[]
for asset in pins['assets']:
    p=out/asset['name']
    if not p.exists():
        with urllib.request.urlopen(pins['release']+'/'+p.name,timeout=60)as r,p.open('wb')as f:
            while True:
                b=r.read(1024*1024)
                if not b:break
                f.write(b)
    assert p.stat().st_size==asset['bytes']and hashlib.sha256(p.read_bytes()).hexdigest()==asset['sha256']
    dest=out/p.stem;dest.mkdir(exist_ok=True)
    with zipfile.ZipFile(p)as z:
        assert sum(i.file_size for i in z.infolist())<2*1024**3
        for i in z.infolist():
            assert not Path(i.filename).is_absolute()and '..'not in Path(i.filename).parts
            assert (i.external_attr>>16)&0o170000!=0o120000
            assert (dest/i.filename).resolve().is_relative_to(dest)
        z.extractall(dest)
    dirs.append(dest)
result=review(*dirs);(out/'SUMMARY.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
