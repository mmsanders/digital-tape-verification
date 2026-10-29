"""Fetch immutable public CI review inputs; no Product execution."""
import argparse,hashlib,urllib.request,zipfile
from pathlib import Path
URL='https://github.com/mmsanders/digital-tape-verification/releases/download/evidence-364-correction1-2026-10-28/verification364-correction1-inputs.zip'
SHA='5226855cc39a1713b6e999c0c78ed532329af259a45903697e4fb3ccff866041'
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('destination',type=Path);a=p.parse_args()
    assert not a.destination.exists();a.destination.mkdir(parents=True)
    archive=a.destination/'inputs.zip';urllib.request.urlretrieve(URL,archive)
    assert hashlib.sha256(archive.read_bytes()).hexdigest()==SHA
    with zipfile.ZipFile(archive) as z:
        for n in z.namelist():assert (a.destination/n).resolve().is_relative_to(a.destination.resolve())
        z.extractall(a.destination)
    print(SHA,'authenticated')
