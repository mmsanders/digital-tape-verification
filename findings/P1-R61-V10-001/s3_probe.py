"""Observe and retain all 4,032 S3 remount answers through the real public binding."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

P=Path(sys.argv[1]).resolve()
E=Path(__file__).resolve().parent
sys.path.insert(0,str(P/'tests/format_dup_identity_draft8'))
import planner
import oracle
record=json.loads((P/'tests/wp10_residue_d10/SUPERSESSION.json').read_text())
s3=next(x for x in record['superseded'] if x['id']=='S3')
indices={i for g in s3['groups'] for lo,hi in g['index_ranges'] for i in range(lo,hi+1)}
proc=subprocess.Popen([sys.executable,str(P/'tests/format_dup_identity_adapter/adapter.py')],
                      stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True,cwd=P)
hello=json.loads(proc.stdout.readline())
assert hello['adapter_kind']=='product' and hello['raw_observation_only']
count=0
out=E/'s3-observations.jsonl'
with out.open('w') as f:
    for i,case in enumerate(planner.iter_cases()):
        if i not in indices: continue
        proc.stdin.write(json.dumps(case)+'\n'); proc.stdin.flush()
        obs=json.loads(proc.stdout.readline())
        oracle.validate_case(case,obs)
        assert obs['actual_remount_result']=='TAPE_ERR_BAD_MAGIC', (i,obs)
        f.write(json.dumps({'index':i,'case':case,'observation':obs},sort_keys=True,separators=(',',':'))+'\n')
        count+=1
proc.stdin.write('{"command":"done"}\n'); proc.stdin.flush(); proc.stdin.close()
assert proc.wait(timeout=30)==0
assert count==4032
print('PASS S3: 4032/4032 real-product remount answers BAD_MAGIC; no migration')
print('raw stream sha256',hashlib.sha256(out.read_bytes()).hexdigest())
