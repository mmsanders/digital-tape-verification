"""Authenticate and independently replay retained 365-fault evidence, without reruns."""
import gzip,hashlib,io,json,sys,urllib.request,zipfile
from pathlib import Path
from crash import replay_faults
out=Path(sys.argv[1]).resolve()
initial=out/'initial.img.gz'
if not initial.exists():
    url='https://github.com/mmsanders/digital-tape-verification/releases/download/evidence-210-return-2026-10-19-743f829/load1.zip'
    raw=urllib.request.urlopen(url,timeout=60).read()
    assert len(raw)==1611126 and hashlib.sha256(raw).hexdigest()=='ad5b62a702d5e3b1fd61ca3671492abd24a032aa76fea845e1de8a5e5309afbf'
    want='1d677f4c0e1fbeda0dd4d8c7cdb4211095f82342c4ca2b62fe7a51037bb83d8c'
    with zipfile.ZipFile(io.BytesIO(raw))as z:
        names=[n for n in z.namelist()if n.endswith('/initial/'+want+'.img.gz')];assert names
        b=z.read(names[0]);assert hashlib.sha256(gzip.decompress(b)).hexdigest()==want;initial.write_bytes(b)
    (out/'INITIAL-PROVENANCE.json').write_text(json.dumps(dict(url=url,archive_sha256=hashlib.sha256(raw).hexdigest(),entry=names[0],initial_sha256=want,
        note='Prior retained raw initial image, carried by exact SHA; first #374 run recorded this hash on every actual input but did not preserve a second copy of baseline bytes'),indent=2)+'\n')
print(json.dumps(replay_faults(out),indent=2))
