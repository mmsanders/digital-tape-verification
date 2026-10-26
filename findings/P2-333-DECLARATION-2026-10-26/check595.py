"""Offline expected workflow controls; never dispatches a workflow."""
import hashlib,json
from pathlib import Path
p=Path(__file__).parent
def check(b):
    expected=json.loads((p/'EXPECTED.json').read_text())
    assert hashlib.sha256(b).hexdigest()==expected['expected_workflow_sha256']
    assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==expected['expected_workflow_blob']
    gate=b"    if: github.event_name == 'workflow_dispatch'\n"
    assert b.count(gate)==2
    for job in [b'stage1-packet',b'win11-script-rehearsal']:
        block=b.split(b'  '+job+b':\n',1)[1]
        assert gate in block.split(b'    steps:',1)[0]
if __name__=='__main__':
    b=(p/'ingest-expected.yml').read_bytes();check(b)
    for bad in [b.replace(b"    if: github.event_name == 'workflow_dispatch'\n",b'',1),b.replace(b'cargo test --release --locked',b'cargo test --release'),b.replace(b'os: [ubuntu-latest, macos-latest, windows-latest]',b'os: [ubuntu-latest]')]:
        try:check(bad)
        except AssertionError:continue
        raise AssertionError('workflow mutation survived')
    print('PASS expected workflow identity +3 causal negatives; ZERO Product/build/dispatch execution')
