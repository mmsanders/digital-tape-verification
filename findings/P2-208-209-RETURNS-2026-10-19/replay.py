"""Replay exact returned raw evidence. No new Product campaign or acceptance shortcut."""
import argparse, hashlib, importlib.util, json, re, subprocess, sys, urllib.request, zipfile
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def module(name, path):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m

def attempts(trace, report):
    """Independently recover exclusive report fd and every write until its close.
    This input is a single-threaded command; refuse unexpected partial trace lines.
    fd reuse after close cannot be mistaken for report writes.
    """
    fd = None; created = False; out = []
    for line in trace.splitlines():
        body = re.sub(r'^\d+\s+', '', line)
        if body.startswith('openat('):
            m = re.fullmatch(r'openat\([^,]+, "((?:\\x[0-9a-f]{2})*)", ([A-Z_|]+)(?:, [0-7]+)?\) = (-?\d+)(?: .*)?', body)
            if m:
                name = bytes.fromhex(m[1].replace('\\x', '')).decode()
                if name in (report, Path(report).name) and int(m[3]) >= 0:
                    assert fd is None
                    fd = int(m[3]); created = 'O_CREAT' in m[2] and 'O_EXCL' in m[2]
        if fd is not None and body.startswith(f'write({fd},'):
            m = re.fullmatch(r'write\(\d+, "((?:\\x[0-9a-f]{2})*)", (\d+)\) = (-?\d+)(?: (\w+) .*)?', body)
            assert m, ('unparsed report write', body)
            req = bytes.fromhex(m[1].replace('\\x', '')); assert len(req) == int(m[2])
            out.append(dict(requested_hex=req.hex(), written=max(0,int(m[3])), error=m[4] if int(m[3]) < 0 else None))
        if fd is not None and body.startswith(f'close({fd})'):
            fd = None
    assert created and out
    return out

def replay(directory, output, release=None):
    directory.mkdir(parents=True, exist_ok=True)
    # cards runner imports its sibling oracle by name; report oracle is separately loaded.
    sys.path.insert(0, str(ROOT/'tests/wp15_cards_make_r1'))
    cards = module('cards_runner', ROOT/'tests/wp15_cards_make_r1/runner.py')
    faults = module('fault_oracle', ROOT/'tests/wp15_report_faults_r1/oracle.py')
    result = {'scope':'bounded returned rows only; no overall Product/native acceptance', 'artifacts':[]}
    for pin in json.loads((HERE/'INPUTS.json').read_text()):
        archive = directory/(pin['name']+'.zip')
        if not archive.exists():
            if release:
                with urllib.request.urlopen(release.rstrip('/')+'/'+archive.name,timeout=60) as r, archive.open('wb') as f:
                    while data := r.read(1024*1024): f.write(data)
            else:
                with archive.open('wb') as f:
                    subprocess.run(['gh','api',f"repos/mmsanders/Digital-Tape/actions/artifacts/{pin['id']}/zip"], stdout=f, check=True)
        assert archive.stat().st_size == pin['bytes']
        assert hashlib.sha256(archive.read_bytes()).hexdigest() == pin['sha256']
        dst = directory/pin['name']; dst.mkdir(exist_ok=True)
        with zipfile.ZipFile(archive) as z:
            for i in z.infolist():
                assert not Path(i.filename).is_absolute() and '..' not in Path(i.filename).parts
                assert (i.external_attr >> 16) & 0o170000 != 0o120000
            z.extractall(dst)
        rec = dict(pin)
        if pin['name'] == 'cards-linux':
            judged = cards.run(dst/'bundle')
            assert judged['source'] == 'ef2712c330fdbc6515bff45c0bee63210f65165a'
            assert len(judged['rows']) == 39
            old = json.loads((dst/'bundle/JUDGED.json').read_text()); assert judged == old
            rec['rows'] = judged['rows']; rec['binary'] = judged['binary']
        elif pin['name'].startswith('report-'):
            rows = []; s = json.loads((dst/'SUMMARY.json').read_text()); rec['facts'] = s['facts']
            for row in s['rows']:
                r = json.loads((dst/row['record']).read_text())
                b = json.loads((dst/row['neighbour']).read_text()); faults.baseline(b)
                for a,k in [('exit','exit'),('stdout_hex','stdout_hex'),('stderr_hex','stderr_hex'),('pair','pair')]:
                    assert r['baseline_'+a] == b[k]
                assert r['baseline_report_hex'] == b['report_hex']
                assert r['sources_before'] == b['sources_before']
                q = dict(position=row['fault_position'],exit=r['exit'],retained_bytes=len(bytes.fromhex(r['report_hex'])),free=r['free'])
                if pin['name'] == 'report-linux':
                    assert r['binary_sha256'] == '44b87f75463767538928876f9179c269f67aa383de89ebb6914779ac2ca21237'
                    report = r['argv'][r['argv'].index('--report')+1]
                    raw = (dst/f"run{r['run']:03d}.strace").read_text()
                    assert attempts(raw, report) == r['attempts']
                    assert r['free']['exact']; q['judgment'] = faults.writes(r)
                    # Every successful prior request matches the no-fault neighbour, not only a summary.
                    expected = bytes.fromhex(b['report_hex']).splitlines(keepends=True)
                    assert [bytes.fromhex(a['requested_hex']) for a in r['attempts']] == expected[:len(r['attempts'])]
                else:
                    assert not r['attempt_capture_complete']; faults.same_ordinary(r)
                    if pin['name'] == 'report-windows':
                        faults.warning_difference(r['baseline_stderr_hex'],r['stderr_hex'])
                        assert r['free']['exact']
                        q['judgment'] = 'actual Server full-volume warning/publication observation; targeted write position UNPROVEN'
                    else:
                        assert not r['free']['exact'] and r['report_hex'] == b['report_hex'] and r['stderr_hex'] == b['stderr_hex']
                        q['judgment'] = 'NO FAULT REACHED: attempted filler left available bytes; targeted write row UNEXECUTED'
                rows.append(q)
            rec['rows'] = rows
        else:
            rec['judgment'] = 'archive authenticated; supplementary raw e2e observations manually audited, no native absence claim'
        result['artifacts'].append(rec)
    output.write_text(json.dumps(result,indent=2)+'\n')
    print('PASS exact artifact hashes; 39 cards rows; Linux 3 raw write traces; Windows partial and Mac no-fault limits retained')

if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('--artifacts',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--release',help='durable hash-pinned release download base; no GitHub credential required')
    a=p.parse_args();replay(a.artifacts,a.out,a.release)
