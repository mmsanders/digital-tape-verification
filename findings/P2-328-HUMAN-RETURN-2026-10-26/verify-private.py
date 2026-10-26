"""Read-only retained-file authentication. Does not decode/authenticate gestures or run Product."""
import argparse,hashlib,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
def verify(raw,kit):
    m=json.loads((HERE/'authentication.json').read_bytes())
    for name,v in m['private_sources'].items():
        b=(raw/name).read_bytes();assert len(b)==v['bytes'] and hashlib.sha256(b).hexdigest()==v['sha256'],name
    index=(kit/'receipts/INDEX-328.json').read_bytes();assert hashlib.sha256(index).hexdigest()==m['producer_index_sha256']
    before=json.loads((raw/'before-receipts.json').read_text(encoding='utf-8-sig'))
    after=json.loads((raw/'after-stop-receipts.json').read_text(encoding='utf-8-sig'))
    assert before['candidate_sha256']==m['before_candidate_pins'] and not before['candidate_mismatch']
    assert before['kit_files']==after['kit_files'] and not after['changed_vs_before']
    assert len(before['kit_files'])==12
    for name,v in before['kit_files'].items():
        b=(kit/name).read_bytes();assert len(b)==v['bytes'] and hashlib.sha256(b).hexdigest()==v['sha256'],name
    snapshot=json.loads((raw/'app-identity-snapshot-1-zero.json').read_text(encoding='utf-8-sig'))
    assert snapshot['count']==0 and snapshot['image_sha256'] is None
    # Exact written results against already frozen independent LABELS after-values.
    sys.path.insert(0,str(HERE.parents[1]/'tests/windows_screen_r1'))
    import contract as screen
    notes=(raw/'OPERATOR notes.txt').read_text(encoding='utf-8-sig')
    for i,row in enumerate(screen.LABELS[:7],1):assert f'{i}. '+row['after'] in notes.splitlines()
    print('PASS private supplied-record hashes/index/before-after12 files/label-note bytes/late zero snapshot. NO UI authenticity or full method/child/IPC acceptance follows.')
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--raw',type=Path,required=True);p.add_argument('--kit',type=Path,required=True);a=p.parse_args();verify(a.raw,a.kit)
