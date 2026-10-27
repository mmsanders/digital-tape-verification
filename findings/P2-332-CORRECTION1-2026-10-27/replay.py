"""Independent offline replay of Software594's original CI bytes. No Product code."""
import base64,copy,hashlib,json,sys,tempfile,zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tests/windows_diagnostics_r2'))
import receipts,cases,regressions
p=Path(__file__).parent
archive=p/'evidence594.zip'
assert receipts.sha(archive.read_bytes())=='5ddd35b7a10037c4ccde38c5e9203422ce1688f3f7439f511dffd705031d561d'
tmp=tempfile.TemporaryDirectory(prefix='verification594-offline-')
root=Path(tmp.name)/'raw'
with zipfile.ZipFile(archive) as z:
    for info in z.infolist():
        dest=Path(tmp.name)/info.filename
        assert dest.resolve().is_relative_to(Path(tmp.name).resolve()) and info.file_size<20*1024*1024
        if not info.is_dir():dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(z.read(info))
result={}
for f in sorted(root.glob('*/envelope-*.json')):
    tag=f.stem[9:];expect=(f.parent/('expect-'+tag+'.txt')).read_text().strip()
    if expect=='oracle-gap':expect='complete'
    files=receipts.unpack(json.loads(f.read_text())['files'])
    try:
        receipts.validate(files,expect=='complete')
        regressions.limit_stops([json.loads(x) for x in files['records.jsonl'].splitlines()])
        outcome='valid-'+expect
        assert expect!='invalid','invalid original accepted'
    except (AssertionError,KeyError,TypeError,ValueError):
        if expect!='invalid':raise
        outcome='rejected-invalid'
    result[f.relative_to(root).as_posix()]=dict(expect=expect,outcome=outcome,envelope_sha256=receipts.sha(f.read_bytes()),records_sha256=receipts.sha(files['records.jsonl']))
# Directly compare captures with harness originals; never trust a projected PASS flag.
compared=0
for f in root.glob('*/envelope-*.json'):
    tag=f.stem[9:];files=receipts.unpack(json.loads(f.read_text())['files'])
    for line in files['records.jsonl'].splitlines():
        try:r=json.loads(line)
        except ValueError:break
        if r['kind']=='blob':
            d=r['data'];original=f.parent/f'original-{tag}-{d["role"]}.bin'
            if original.exists():assert files[d['leaf']]==original.read_bytes();compared+=1
        if r['kind']=='audio':
            original=f.parent/f'original-{tag}-audio.json'
            if original.exists():
                a=json.loads(original.read_text());assert all(a[k]==r['data'][k] for k in ['sha256','bytes']);compared+=1
for f in root.glob('*/parity.json'):
    for pair in json.loads(f.read_text()).values():cases.parity(pair['off'],pair['on'])
faults=json.loads((root/'C24-C25/faults.json').read_text())
for fault in faults['faults'].values():cases.parity(faults['healthy'],fault['projection'])
c=json.loads((root/'C01-C02/command.json').read_text());cases.command(c['actual'],c['expected'])
con=json.loads((root/'C01-C02/console.json').read_text());assert con['C01']['child']['pid']==con['C01']['receipt']['pid'] and not con['C01']['child']['console_window']
assert not con['runner_console_window'] and not con['C02']['child']['console_window']
# A real positive must pass before each mutation is shown to fail for its own cause.
env=root/'C03-C17-C18/envelope-success.json';files=receipts.unpack(json.loads(env.read_text())['files']);receipts.validate(files)
rows=[json.loads(x) for x in files['records.jsonl'].splitlines()]
at=lambda k:next(i for i,r in enumerate(rows) if r['kind']==k)
mutations=[('pid',lambda r:r[at('child-terminal')]['data'].update(pid=1)),('nonce',lambda r:r[at('child-launch')]['data'].update(nonce='0'*32)),('generation',lambda r:r[at('child-terminal')]['data'].update(generation=999)),('hash',lambda r:r[at('blob')]['data'].update(sha256='0'*64)),('wait',lambda r:r.pop(at('child-terminal'))),('cleanup',lambda r:r.insert(at('child-launch')+1,r.pop(at('cleanup'))))]
for name,mutate in mutations:
    rr=copy.deepcopy(rows);mutate(rr)
    for i,r in enumerate(rr):r['seq']=i
    ff=dict(files);ff['records.jsonl']=receipts.encode(rr)
    try:receipts.validate(ff)
    except (AssertionError,KeyError,TypeError,ValueError):continue
    raise AssertionError('actual mutation survived:'+name)
rr=copy.deepcopy(rows);rr[3]['seq']=99;ff=dict(files);ff['records.jsonl']=receipts.encode(rr)
try:receipts.validate(ff)
except AssertionError:pass
else:raise AssertionError('seq mutation survived')
# Original C22 shows records continue after a blob-limit event: a source finding.
f=root/'C22/envelope-blob.json';ff=receipts.unpack(json.loads(f.read_text())['files']);rr=[json.loads(x) for x in ff['records.jsonl'].splitlines()]
i=next(i for i,r in enumerate(rr) if r['kind']=='missing' and r['data']['role']=='stdout')
result['C22_limit_continuation']=[r['kind'] for r in rr[i+1:]]

assert result['C22_limit_continuation']==['incomplete']
for case in ['C06-before-report','C07-before-report']:
    f=root/case/'envelope-cancel.json';fl=receipts.unpack(json.loads(f.read_text())['files']);r=[json.loads(x) for x in fl['records.jsonl'].splitlines()]
    assert any(x['kind']=='missing' and x['data']['role']=='report' for x in r)
    assert not any(x['kind']=='blob' and x['data']['role']=='report' for x in r)
    assert any(x['kind']=='child-terminal' and x['data']['cancelled'] for x in r)
    assert any(x['kind']=='cleanup' and x['data']['result']=='removed' for x in r)
    assert r[-1]['kind']=='session-end' and r[-1]['data']['complete'] is False
for tag in ['exact','over']:
    f=root/'C21-footer'/('envelope-'+tag+'.json');fl=receipts.unpack(json.loads(f.read_text())['files']);lines=fl['records.jsonl'].splitlines(keepends=True)
    assert all(len(x)<=65536 for x in lines)
    if tag=='exact':assert len(lines[-1])==65536
    else:assert json.loads(lines[-1])['kind']=='incomplete' and json.loads(lines[-1])['data']['reason']=='footer-line-over-limit'
stale=root/'C20-binding/envelope-stale.json';fl=receipts.unpack(json.loads(stale.read_text())['files']);r=[json.loads(x) for x in fl['records.jsonl'].splitlines()]
assert r[0]['data']['source_commit'] is None and not r[-1]['data']['complete']
unmeasured=root/'C20-binding/envelope-unmeasured.json';fl=receipts.unpack(json.loads(unmeasured.read_text())['files']);r=[json.loads(x) for x in fl['records.jsonl'].splitlines()]
assert not r[0]['data']['app_path'] and not r[0]['data']['app_sha256'] and r[-1]['data']['complete'] is False
result['focused_findings']={'F332-1':'closed at corrected head only','F332-2':'closed at corrected head only','F332-3':'closed at corrected head only'}

result['comparison_count']=compared
result['C02']='UNEXECUTED positive console contrast; both observed helper console associations false'
result['actual_mutations_rejected']=7
if '--write' in sys.argv:(p/'REPLAY.json').write_text(json.dumps(result,indent=2)+'\n')
else:assert result==json.loads((p/'REPLAY.json').read_text())
print('PASS',len([k for k in result if k.endswith(".json")]),'original envelopes;',compared,'capture comparisons;7 actual mutations;3 corrections verified; C02 UNEXECUTED; ZERO Product/process execution')
tmp.cleanup()
