"""Run unchanged shipped judge/parser with a bounded-memory XML input shim."""
import argparse
import hashlib
import json
import sys
import tempfile
import types
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

archive = Path(sys.argv[1]).resolve()
expected_zip = '9b23466b502f386bc3c12ac8a6674710d0caf9491358c2c654bb5717d7cbd755'
h = hashlib.sha256()
with archive.open('rb') as f:
    for b in iter(lambda:f.read(1048576), b''): h.update(b)
assert h.hexdigest() == expected_zip
z = zipfile.ZipFile(archive)
code = z.read('a6check.py')
assert hashlib.sha256(code).hexdigest() == '227ceed2f1ca8817447c4103983c72b16a060b1d3323de22c805289b621bd1ef'
m = types.ModuleType('returned_checker')
exec(compile(code, 'authenticated-a6check.py', 'exec'), m.__dict__)
trace_sha = hashlib.sha256()

class Root:
    def iter(self):
        class Reader:
            def __init__(self, raw): self.raw = raw
            def read(self, size=-1):
                b = self.raw.read(size)
                trace_sha.update(b)
                return b
        with z.open('verify.xml') as raw:
            it = ET.iterparse(Reader(raw), events=('start', 'end'))
            _, root = next(it)
            for kind, elem in it:
                if kind == 'end' and elem.tag.rsplit('}',1)[-1] == 'Event':
                    yield elem
                    root.remove(elem)
                    elem.clear()

old_text, old_sha, old_fromstring = m.read_text, m.sha256, ET.fromstring
sentinel = object()
m.read_text = lambda p: sentinel if p == 'verify.xml' else old_text(p)
# The input hash is filled after the streaming parser consumes the entire XML.
m.sha256 = lambda p: 'pending-stream-sha256' if p == 'verify.xml' else old_sha(p)
ET.fromstring = lambda text: Root() if text is sentinel else old_fromstring(text)
with tempfile.TemporaryDirectory() as td:
    for name in ['tapectl.exe','geometry.txt','verify-out.txt','tracer-exits.txt',
                 'wpr-stop-err.txt','wpr-stop-out.txt','tracerpt-err.txt','tracerpt-out.txt']:
        (Path(td)/name).write_bytes(z.read(name))
    a = argparse.Namespace(format='etw-xml',trace='verify.xml',pid=4596,capacity=4296015872,
        geometry=str(Path(td)/'geometry.txt'),target='rehearsal.img',disk=0,
        exe=str(Path(td)/'tapectl.exe'),sha256='82798af2899e9364b9c9bfaa2021daf6cc51ccd0c6562598d50e0a86944bb7a9',
        stdout=str(Path(td)/'verify-out.txt'),tracer_log=str(Path(td)/'tracer-exits.txt'),exit_code=0,
        diagnostics=[str(Path(td)/name) for name in ['wpr-stop-err.txt','wpr-stop-out.txt','tracerpt-err.txt','tracerpt-out.txt']])
    result = m.judge(a)
    result['inputs']['trace']['sha256'] = trace_sha.hexdigest()
    for k in ['geometry','exe','stdout','tracer_log']:
        result['inputs'][k]['path'] = Path(result['inputs'][k]['path']).name
    for d in result['inputs']['diagnostics']: d['path'] = Path(d['path']).name
    result['notes'] = [s.replace(td+'/', '') for s in result['notes']]
    Path(sys.argv[2]).write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,indent=2,sort_keys=True))
