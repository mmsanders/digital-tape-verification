"""Offline retained live-1 record authentication. ZERO child/app/device execution."""
import copy,datetime,hashlib,importlib.util,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
NONCE='154abcdcabdabea5199b812735fbe464'
SHA='44ef26869ba2d01a8a183660a2c7a050d0e7e9ff37c40b727131512739ea6ded'
VERSION='tapectl-wp15-s2+f9306c2c5a42'
EXE=r'C:\Users\mrtro\claude\software-only\live578\tapectl.exe'
JOB=r'C:\Users\mrtro\claude\software-only\live578\job'
REPORT=JOB+'\\cards-'+NONCE+'.jsonl'
spec=importlib.util.spec_from_file_location('accepted_app1a',ROOT/'tests/wp15_app1a_r1/oracle.py')
prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
def digest(b):return hashlib.sha256(b).hexdigest()
def check(pre,post,out,err,report):
    assert pre['exe']==EXE and pre['cwd']==JOB
    assert pre['argv']==[EXE,'cards','--report',REPORT,'--report-nonce',NONCE]
    assert pre['exe_sha256']==SHA and pre['exe_bytes']==493712
    assert pre['job_entries_before']==[] and pre['report_exists_before'] is False
    assert pre['user']=='mrtro' and pre['elevated'] is False
    assert pre['os']=='Windows-11-10.0.26200-SP0'
    assert post['exit']==0 and post['note'] is None and post['report_exists']
    assert post['job_entries_after']==['cards-'+NONCE+'.jsonl']
    assert post['stdout_bytes']==len(out)==41 and post['stderr_bytes']==len(err)==0
    assert post['stdout.bin_sha256']==digest(out)=='8a5de7c42d95751e2a76f41840ffdfb5a3cf807d3366a94dc3a3d81955eccad2'
    assert post['stderr.bin_sha256']==digest(err)=='e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
    assert post['report_sha256']==digest(report)=='adc5dd8f9f02db072714547975c6796c5de1643bb56599ff92532449b31d62b1'
    assert out==b'{"t":"summary","offered":0,"unprobed":0}\n' and err==b''
    parsed=prior.parse(report,'tapectl cards',VERSION,NONCE,0)
    assert parsed is not None and parsed['refusal'] is None
    rows=[json.loads(x) for x in report.decode().splitlines()]
    assert rows==[dict(t='start',tool='tapectl cards',version=VERSION,nonce=NONCE),dict(t='progress',step='enumerate',done=1,total=1),dict(t='end',exit=0)]
    elapsed=(datetime.datetime.fromisoformat(post['ended_utc'])-datetime.datetime.fromisoformat(pre['started_utc'])).total_seconds()
    assert 0<=elapsed<60
    return elapsed
for name,v in json.loads((HERE/'manifest.json').read_bytes()).items():
    b=(HERE/'raw'/name).read_bytes();assert len(b)==v['bytes'] and digest(b)==v['sha256'],name
pre=json.loads((HERE/'raw/invocation.json').read_bytes());post=json.loads((HERE/'raw/terminal.json').read_bytes())
out=(HERE/'raw/stdout.bin').read_bytes();err=(HERE/'raw/stderr.bin').read_bytes();report=(HERE/'raw/report.jsonl').read_bytes()
elapsed=check(pre,post,out,err,report)
for kind in ['wrong-argv','elevated','wrong-hash','nonzero-exit','bad-report-nonce','changed-stdout']:
    a,b,c,d,e=copy.deepcopy(pre),copy.deepcopy(post),out,err,report
    if kind=='wrong-argv':a['argv'][1]='make'
    elif kind=='elevated':a['elevated']=True
    elif kind=='wrong-hash':a['exe_sha256']='0'*64
    elif kind=='nonzero-exit':b['exit']=1
    elif kind=='bad-report-nonce':e=e.replace(NONCE.encode(),b'0'*32)
    elif kind=='changed-stdout':c=c.replace(b'"offered":0',b'"offered":1')
    try:check(a,b,c,d,e)
    except AssertionError:continue
    raise AssertionError('record negative control survived: '+kind)
print(f'PASS admitted live-1 original bytes/context/argv/hash/exit/report crosscheck; offered0/unprobed0, recorded interval {elapsed:.6f}s;6 negative controls detected. No new executable run or G1/UI/Make claim.')
