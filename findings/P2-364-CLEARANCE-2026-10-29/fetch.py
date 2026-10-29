"""Fetch immutable public CI review inputs; no Product execution."""
import argparse,hashlib,urllib.request,zipfile
from pathlib import Path
URL='https://github.com/mmsanders/digital-tape-verification/releases/download/evidence-364-final-2026-10-29/verification364-final-inputs.zip'
SHA='b809b605e102b873ab28ebe25789f6e1318d0f6625e80c0af870ab19fdb09a88'
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('destination',type=Path);a=p.parse_args()
    assert not a.destination.exists();a.destination.mkdir(parents=True)
    archive=a.destination/'inputs.zip';urllib.request.urlretrieve(URL,archive)
    assert hashlib.sha256(archive.read_bytes()).hexdigest()==SHA
    with zipfile.ZipFile(archive) as z:
        for n in z.namelist():assert (a.destination/n).resolve().is_relative_to(a.destination.resolve())
        z.extractall(a.destination)
    print(SHA,'authenticated')
