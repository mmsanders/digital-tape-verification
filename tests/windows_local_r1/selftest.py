"""Pure independent detection controls; no Product/native execution."""
import importlib.util
from pathlib import Path
import tempfile

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('local_route', HERE/'local_route.py')
route = importlib.util.module_from_spec(spec)
spec.loader.exec_module(route)


def rejected(fn, *args):
    try:
        fn(*args)
    except (AssertionError, OSError):
        return
    raise AssertionError('negative survived')


with tempfile.TemporaryDirectory(dir=Path.cwd(), prefix='.v277-authoring-') as tmp:
    root = Path(tmp)
    assert root.resolve().parent == Path.cwd().resolve()
    source, out = root/'source.wav', root/'out.wav'
    route.make_wav(source, 44101)
    out.write_bytes(source.read_bytes())
    route.compare_wav(source, out)
    good = out.read_bytes()
    for bad in (good[:-4], good+b'\0'*4, good[:-1]+bytes([good[-1]^1])):
        out.write_bytes(bad)
        rejected(route.compare_wav, source, out)
    out.write_bytes(good)
    assert route.ordinary(source).is_file()
    assert route.ordinary(root, True).is_dir()
    for s in ('\\\\.\\PhysicalDrive1', '\\\\?\\Volume{a}', '\\\\server\\share',
              '/dev/sda', '\\Device\\Harddisk1', 'C:/owned/file:stream'):
        rejected(route.ordinary, s)
    rejected(route.ordinary, root)
    rejected(route.ordinary, source, True)
    m = route.mbr(route.LARGE//512)
    assert len(m) == 512
    for i in (450, 466, 510):
        changed = bytearray(m); changed[i] ^= 1
        assert changed != m
print('PASS: exact WAV positive/3 tail controls; ordinary-file positive/8 path-type negatives; large MBR distinct defect controls; ZERO Product/native calls')
