"""Authenticate the original exact-head CI artifact before parsing any contents."""
import hashlib,sys,zipfile
from pathlib import Path
root=Path(__file__).resolve().parents[2]
p=root/'findings/P3-R1-SW642/arm-evidence.zip'
assert p.stat().st_size==279011
assert hashlib.sha256(p.read_bytes()).hexdigest()=='16bb28c20b700318b95c1b22d9faed951218b2b7a1c377907ed29137337ede52'
out=Path(sys.argv[1]).resolve();out.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(p)as z:
    assert sum(i.file_size for i in z.infolist())<2*1024**2
    for i in z.infolist():
        assert not Path(i.filename).is_absolute()and '..'not in Path(i.filename).parts
        assert (i.external_attr>>16)&0o170000!=0o120000
        assert (out/i.filename).resolve().is_relative_to(out)
    z.extractall(out)
print('PASS original ARM evidence ZIP identity; safe extraction')
