import collections
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

z = zipfile.ZipFile(sys.argv[1])
counts = collections.Counter()
errors = collections.Counter()
samples, target, headers, threads = [], [], [], set()
provider_counts, guid_counts = collections.Counter(), collections.Counter()
n = missing_time = backwards = 0
previous = None
sha = hashlib.sha256()

class Reader:
    def __init__(self, raw): self.raw = raw
    def read(self, size=-1):
        b = self.raw.read(size)
        sha.update(b)
        return b

def num(s):
    try: return int(s, 16) if s.lower().startswith('0x') else int(s)
    except (ValueError, AttributeError): return None

with z.open('verify.xml') as raw:
    it = ET.iterparse(Reader(raw), events=('start', 'end'))
    _, root = next(it)
    for kind, e in it:
        if kind != 'end' or e.tag.rsplit('}', 1)[-1] != 'Event': continue
        n += 1
        d, s = {}, {}
        for c in e.iter():
            tag = c.tag.rsplit('}', 1)[-1]
            if tag == 'Provider' and c.get('Guid'): s['provider'] = c.get('Guid').strip('{}').lower()
            elif tag == 'EventGuid': s['guid'] = (c.text or '').strip('{}').lower()
            elif tag == 'Opcode' and (c.text or '').strip().isdigit(): s.setdefault('opcode', int(c.text))
            elif tag == 'TimeCreated': s['time'] = c.get('SystemTime')
            elif tag == 'Execution': s['execution'] = dict(c.attrib)
            elif tag == 'ErrorCode': s['schema_error'] = c.text
            elif tag == 'Data' and c.get('Name'): d[c.get('Name')] = (c.text or '').strip()
        provider_counts[s.get('provider', '(absent)')] += 1
        guid_counts[s.get('guid', '(absent)')] += 1
        key = str(s.get('guid')) + ':' + str(s.get('opcode'))
        counts[key] += 1
        if 'schema_error' in s: errors[key+':'+s['schema_error']] += 1
        t = s.get('time')
        if not t: missing_time += 1
        if t and previous and t < previous: backwards += 1
        if t: previous = t
        row = {'event_index': n, **s, 'data': d}
        if n <= 1: headers.append(row)
        if num(d.get('ProcessId')) == 4596 and 'TThreadId' in d: threads.add(d['TThreadId'])
        belongs = num(s.get('execution', {}).get('ProcessID')) == 4596 or num(d.get('ProcessId')) == 4596 or d.get('TTID') in threads or d.get('IssuingThreadId') in threads
        named = any('rehearsal.img' in v.lower() or 'tapectl.exe' in v.lower() for v in d.values())
        if belongs or named: target.append(row)
        if len(samples) < 30 and s.get('guid') in ['90cbdc39-4a3e-11d1-84f4-0000f80464e3', '3d6fa8d4-fe05-11d0-9dda-00c04fd7ba7c']:
            if not any(q.get('guid') == s.get('guid') and q.get('opcode') == s.get('opcode') for q in samples): samples.append(row)
        root.remove(e)
        e.clear()
        if n % 200000 == 0: print('events', n, file=sys.stderr, flush=True)

out = {'events': n, 'xml_sha256': sha.hexdigest(), 'missing_timestamp': missing_time,
       'timestamp_adjacent_inversions': backwards, 'providers': dict(provider_counts),
       'event_guids': dict(guid_counts), 'classes': dict(counts), 'schema_errors': dict(errors),
       'headers': headers, 'target_threads': sorted(threads), 'target_or_named': target, 'samples': samples}
Path(sys.argv[2]).write_text(json.dumps(out, indent=2, sort_keys=True)+'\n')
print(json.dumps({k:out[k] for k in ['events','xml_sha256','missing_timestamp','timestamp_adjacent_inversions','providers','schema_errors','target_threads']}))
print('target/named records', len(target))
