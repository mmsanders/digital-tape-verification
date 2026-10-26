"""Offline retained-disposition identity check; no Product source/build/corpus execution."""
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
r=json.loads((HERE/'SOURCE-CROSSWALK.json').read_bytes())
assert r['product_main']=='9af79191671b4ce47732dc6cb3da269741ea5e4d'
assert r['trees']['main_host'] is None and r['trees']['main_stage1'] is None
assert r['trees']['459_host']=='b4907b2f209080f3ff730f8af0f6da298c13fbeb'
assert r['trees']['454_host']=='835078995d4e9cc2424f9ea8d6f11304b45f783f'
assert r['trees']['main_app1a']==r['trees']['454_app1a']=='bdd861b693516db2e5244660b3e99ee400d506de'
assert len(r['s1_source_blobs'])==16 and not any(r['same_blob_paths_on_main'].values())
for issue,v in r['independent_reports'].items():
    b=(ROOT/v['path']).read_bytes()
    # Git stores these historical reports with LF; Windows worktrees may use CRLF.
    git_bytes=b.replace(b'\r\n',b'\n')
    assert hashlib.sha256(git_bytes).hexdigest()==v['sha256'],issue
assert set(r['independent_reports'])=={'192','203','214','230','234','242','269'}
print('PASS7 immutable retained report identities and exact source crosswalk metadata; no build/replay/native execution or final integration clearance')
