"""Audit retained Windows native-format failure; never execute the Windows binary.

Default: committed full-scan facts + exact raw excerpt + unchanged helper.
--archive ZIP: also reproduce the full unchanged-parser result from the original
98MB attachment, without loading a 1.77GB XML DOM. Raw release retention is pending.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import types
import xml.etree.ElementTree as ET
import zipfile

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--archive', type=Path)
a = p.parse_args()
here = Path(__file__).resolve().parent
manifest = json.loads((here/'SHA256SUMS.json').read_text())
for name, sha in manifest.items():
    assert hashlib.sha256((here/name).read_bytes()).hexdigest() == sha, name
root = here.parents[1]
old = root/'findings/P2-R1-WP14-428-R6-2026-10-14-evidence/offcard-rehearsal.zip'
with zipfile.ZipFile(old) as z:
    code = z.read(next(n for n in z.namelist() if n.endswith('a6check.py')))
assert hashlib.sha256(code).hexdigest() == '227ceed2f1ca8817447c4103983c72b16a060b1d3323de22c805289b621bd1ef'
m = types.ModuleType('accepted_helper')
exec(compile(code, 'accepted-a6check.py', 'exec'), m.__dict__)

v = m.Verdict()
events = m.parse_etw_xml((here/'native-excerpt.xml').read_text(), v)
assert events == []  # Provider Guid is not EventGuid; no native class recognized
assert v.held == ['ETW: no EventTrace header; loss counters unknown']
native = ET.parse(here/'native-excerpt.xml').getroot()
ns = {'e':'http://schemas.microsoft.com/win/2004/08/events/event',
      't':'http://schemas.microsoft.com/win/2004/08/events/trace'}
assert len(native) == 5
header = native[0]
data = {c.get('Name'):(c.text or '').strip() for c in header.findall('e:EventData/e:Data',ns)}
assert data['EventsLost'] == data['BuffersLost'] == '0'
bad = [e for e in native if e.find('e:ProcessingErrorData',ns) is not None]
assert len(bad) == 2
assert all(e.find('e:EventData',ns) is None for e in bad)
assert {e.find('t:ExtendedTracingInfo/t:EventGuid',ns).text.strip('{}') for e in bad} == {
    m.G_FILEIO,m.G_THREAD}
# A provider-field-only correction still has undecoded Read and Thread records.
# Do not implement a Product parser fix here or infer their missing fields.
assert all(e.find('e:ProcessingErrorData/e:ErrorCode',ns).text == '15005' for e in bad)
summary = json.loads((here/'native-summary.json').read_text())
assert summary['events'] == 1232801
assert summary['missing_timestamp'] == summary['timestamp_adjacent_inversions'] == 0
assert summary['schema_errors'][m.G_FILEIO+':67:15005'] == summary['classes'][m.G_FILEIO+':67'] == 41684
assert summary['schema_errors'][m.G_FILEIO+':68:15005'] == summary['classes'][m.G_FILEIO+':68'] == 8769
for op in (1,2,3,4):
    assert summary['schema_errors'][m.G_THREAD+':'+str(op)+':15005'] == summary['classes'][m.G_THREAD+':'+str(op)]
assert not set(summary['providers']) & {m.G_HEADER,m.G_PROC,m.G_THREAD,m.G_DISKIO,m.G_FILEIO}
result = json.loads((here/'independent-checker.json').read_text())
assert result['verdict'] == 'FAIL' and len(result['fail']) == len(result['held']) == 2
assert result['last_sector_reads'] == [] and result['exit']['recorded'] == 0
assert result['inputs']['trace']['sha256'] == summary['xml_sha256']
if a.archive:
    with tempfile.TemporaryDirectory() as td:
        out = Path(td)/'replayed.json'
        subprocess.run([sys.executable,'-B',str(here/'check_stream.py'),str(a.archive.resolve()),str(out)],check=True,capture_output=True)
        assert json.loads(out.read_text()) == result
    print('Original ZIP authenticated; full unchanged helper FAIL exactly reproduced with streaming XML input')
else:
    print('Committed full-scan facts and exact native excerpt audited; full archive replay NOT run')
print('PASS means reproducible rejection; native/physical Windows A6 remains HELD')
