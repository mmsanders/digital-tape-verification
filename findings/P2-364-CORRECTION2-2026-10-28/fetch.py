"""Fetch immutable public CI review inputs; no Product execution."""
import argparse,hashlib,urllib.request,zipfile
from pathlib import Path
URL='https://github.com/mmsanders/digital-tape-verification/releases/download/evidence-364-correction2-2026-10-28/verification364-correction2-inputs.zip'
SHA='d5605a161bc0d669dab5293b5dbe989691f74651adce18db72ac395276941b3e'
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('destination',type=Path);a=p.parse_args()
    assert not a.destination.exists();a.destination.mkdir(parents=True)
    archive=a.destination/'inputs.zip';urllib.request.urlretrieve(URL,archive)
    assert hashlib.sha256(archive.read_bytes()).hexdigest()==SHA
    with zipfile.ZipFile(archive) as z:
        for n in z.namelist():assert (a.destination/n).resolve().is_relative_to(a.destination.resolve())
        z.extractall(a.destination)
    print(SHA,'authenticated')
