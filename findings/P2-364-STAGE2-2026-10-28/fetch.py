"""Fetch/authenticate durable CI evidence; never run a downloaded executable."""
import argparse, hashlib, urllib.request, zipfile
from pathlib import Path
URL='https://github.com/mmsanders/digital-tape-verification/releases/download/evidence-364-c1-2026-10-28/verification364-c1-inputs.zip'
SHA='c6b1130387ef9f111242b896ee048c6e36af326fefe32e5e74250a4110563263'
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('destination',type=Path);a=p.parse_args()
    assert not a.destination.exists();a.destination.mkdir(parents=True)
    archive=a.destination/'inputs.zip';urllib.request.urlretrieve(URL,archive)
    assert hashlib.sha256(archive.read_bytes()).hexdigest()==SHA,'input digest mismatch'
    with zipfile.ZipFile(archive) as z:
        for n in z.namelist():
            assert (a.destination/n).resolve().is_relative_to(a.destination.resolve()),'unsafe archive path'
        z.extractall(a.destination)
    print(SHA,'authenticated; no Product execution')
