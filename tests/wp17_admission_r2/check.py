"""ADR-202 admission correction. No previous package or expectation is rewritten."""
import argparse,copy,hashlib,json,struct,subprocess,sys,tempfile,wave
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
HEAD='ee478a913613a16a90e38c85112fb67cbbf53887'
sys.path.insert(0,str(ROOT/'tests/wp14_r1'));import fixtures,oracle

def digest(b):return hashlib.sha256(b).hexdigest()
def git(repo,*args):return subprocess.check_output(['git','-C',str(repo),*args])
def carry(product):
    pins=json.loads((ROOT/'tests/wp17_admission_r2/AUTHORITY.json').read_text())
    assert git(product,'rev-parse','HEAD').decode().strip()==HEAD
    assert not git(product,'status','--porcelain','--untracked-files=all','--','engine','host','firmware').strip()
    assert git(product,'rev-parse','HEAD:engine').decode().strip()==pins['engine_tree']
    assert git(product,'rev-parse','HEAD:firmware/bench').decode().strip()==pins['firmware_tree']
    for pin in pins['predecessors']:
        subprocess.run(['git','-C',str(ROOT),'merge-base','--is-ancestor',pin['commit'],'HEAD'],check=True)
    for item in pins['carried_files']:
        original=git(ROOT,'show',item['commit']+':'+item['path'])
        current=git(ROOT,'show','HEAD:'+item['path'])
        assert original==current and digest(original)==item['sha256'],item['path']
    # Inspect retained facts only; do not render another frame or run a fault campaign.
    for label in ('WINDOWS','GCC','CLANG'):
        r=json.loads((ROOT/'findings/P3-R1-SW642'/(label+'-RESULT.json')).read_text())
        assert r['head']==HEAD and r['engine_tree']==pins['engine_tree']
        assert(r['memory']['gate']['ram'],r['memory']['gate']['rodata'])==(191600,1040)
        assert r['memory']['gate']['stack_status']=='PENDING'
        rows=r['firmware_host']['results'];assert len(rows)==14
        assert {x['name']for x in rows}=={'play-1x-quiet','play-1x-fortissimo','splice','overdub','overwrite','reset-b','promote'}
        assert {x['mode']for x in rows}=={'det','live'}
        assert sum(len(x['controls'])for x in rows)==28
        for x in rows:
            assert x['facts']['result']==x['facts']['underruns']==x['facts']['card_writes']==0 and x['image_unchanged']
            assert x['facts']['sha256']==x['pcm_sha256']
            ref=ROOT/'tests/golden/ref'/(x['name']+'.wav')
            assert digest(ref.read_bytes())==x['reference_sha256']
            with wave.open(str(ref),'rb')as wav:
                assert(wav.getnchannels(),wav.getsampwidth(),wav.getframerate())==(2,2,44100)
                assert x['facts']['frames']==wav.getnframes()
                assert digest(wav.readframes(wav.getnframes()))==x['pcm_sha256']
    return dict(candidate=HEAD,engine=pins['engine_tree'],firmware=pins['firmware_tree'],predecessor_files=len(pins['carried_files']),
                f1='carried: seven normal-rate vectors, det/live, PCM payloads; no WAV/PCM hash conflation',
                f2='carried: RAM 191600; engine rodata 1040; target instance/stack pending',
                f6='carried: full engine/port tree unchanged',stage_a='carried: 365 actual faults PASS; six unavailable cuts not executed',
                rig='carried NOT CLEARED; no method re-review',execution='partition/view/diagnostics only')

def cases(total):
    base=oracle.mbr(total);out=[dict(name='clean',mbr=base,accepted=True,diagnostic='OK')]
    positives=[('bootstrap-first',{0:1},'MBR_LAYOUT'),('bootstrap-last',{439:1},'MBR_LAYOUT'),
               ('bootstrap-all',{i:0xa5 for i in range(440)},'MBR_LAYOUT'),
               ('disk-signature',{i:0x3c for i in range(440,444)},'OK'),
               ('reserved-444',{444:1},'MBR_LAYOUT'),('reserved-445',{445:1},'MBR_LAYOUT'),
               ('reserved-both',{444:0x5a,445:0xa5},'MBR_LAYOUT'),
               ('prefix-combined',{i:0x5a for i in range(446)},'MBR_LAYOUT')]
    for name,changes,diagnostic in positives:
        b=bytearray(base)
        for off,v in changes.items():b[off]=v
        out.append(dict(name=name,mbr=bytes(b),accepted=True,diagnostic=diagnostic))
    for name,offset in [('signature-510',510),('signature-511',511),('p1-status',446),('p1-chs-start',447),('p1-type',450),
                        ('p1-chs-end',451),('p1-start',454),('p1-size',458),('p2-status',462),('p2-chs-start',463),
                        ('p2-type',466),('p2-chs-end',467),('p2-start',470),('p2-size',474),('entry3',478),('entry4',494)]:
        b=bytearray(base);b[offset]^=1;out.append(dict(name=name,mbr=bytes(b),accepted=False))
    for name,start,count in [('zero-extent',oracle.P2_START,0),('overflow-extent',0xfffffff0,0x40),
                             ('past-card',oracle.P2_START,total-oracle.P2_START+1)]:
        b=bytearray(base);struct.pack_into('<II',b,470,start,count);out.append(dict(name=name,mbr=bytes(b),accepted=False))
    return out

def judge(case,r,before,after,n):
    assert r['accepted']is case['accepted'],'admission expectation'
    if not case['accepted']:
        assert after==before,'refused card changed';return
    start=oracle.P2_START
    assert(r['start'],r['blocks'])==(start,n),'view extent'
    assert r['read_hex']==[before[start*512:(start+1)*512].hex(),before[-512:].hex()],'view reads'
    assert r['write_absolute_lba']==[start+1],'write offset'
    assert r['out_of_range_refused']is True,'view bounds'
    want=bytearray(before);want[(start+1)*512:(start+2)*512]=bytes.fromhex('a5'*512)
    assert after==want,'raw write escaped P2 or wrong data'

def rejects(case,r,before,after,n):
    try:judge(case,r,before,after,n)
    except AssertionError as e:return str(e)
    raise AssertionError('negative control undetected')

def run(product,fw,tapectl,out):
    authenticated=carry(product);n=fixtures.BLOCKS;total=oracle.P2_START+n;rows=[];controls={}
    adapter=[sys.executable,str(product/'firmware/bench/host/partition_adapter.py'),'--fwhost',str(fw)]
    with tempfile.TemporaryDirectory()as td:
        for case in cases(total):
            path=Path(td)/(case['name']+'.img');fixtures.build(path,whole=True)
            with path.open('r+b')as f:f.write(case['mbr'])
            before=path.read_bytes();verification=None
            if case['accepted']:
                p=subprocess.run([str(tapectl),'verify',str(path)],capture_output=True,text=True)
                assert path.read_bytes()==before,'desktop verify changed input'
                if case['diagnostic']=='OK':assert p.returncode==0 and p.stdout=='OK\n',(case['name'],p.stdout,p.stderr)
                else:assert p.returncode==1 and'MBR_LAYOUT'in p.stdout.splitlines(),(case['name'],p.stdout,p.stderr)
                verification=dict(exit=p.returncode,stdout=p.stdout,stderr=p.stderr,image_unchanged=True)
            request=dict(image=str(path),sectors=total,reads=[0,n-1,-1,n],writes=[dict(lba=1,hex='a5'*512),dict(lba=-1,hex='5a'*512),dict(lba=n,hex='5a'*512)])
            p=subprocess.run(adapter,input=json.dumps(request),capture_output=True,text=True);assert p.returncode==0,(p.stdout,p.stderr)
            response=json.loads(p.stdout);after=path.read_bytes();judge(case,response,before,after,n)
            if case['name']=='clean':
                bad=copy.deepcopy(response);bad['out_of_range_refused']=False
                controls['bounds']=rejects(case,bad,before,after,n)
                bad=copy.deepcopy(response);bad['write_absolute_lba']=[1]
                controls['wrong-offset-report']=rejects(case,bad,before,after,n)
                bad_image=bytearray(before);bad_image[512:1024]=bytes.fromhex('a5'*512)
                controls['wrong-offset-raw-bytes']=rejects(case,response,before,bytes(bad_image),n)
            if case['name']=='signature-510':
                bad=copy.deepcopy(response);bad['accepted']=True
                controls['blanket-accept']=rejects(case,bad,before,after,n)
            rows.append(dict(name=case['name'],expected_accepted=case['accepted'],mbr_hex=case['mbr'].hex(),
                             response=response,verify=verification,before_sha256=digest(before),after_sha256=digest(after),result='PASS'))
    assert len(rows)==28 and sum(r['expected_accepted']for r in rows)==9 and len(controls)==4
    result=dict(authority='ADR-202 / Verification378',authenticated=authenticated,rows=rows,controls=controls,
                admitted=9,refused=19,failures=0,disposition='CLEARED exact ee478a91 for authorized off-target integration scope',
                target='F1 target PCM/I2S, stack, timing, controls/removal pending; no physical/media/safety/batching clearance')
    out.mkdir(parents=True,exist_ok=True);(out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items()if k not in('rows',)},indent=2));return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--product',type=Path,required=True);p.add_argument('--fwhost',type=Path,required=True);p.add_argument('--tapectl',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    run(a.product.resolve(),a.fwhost.resolve(),a.tapectl.resolve(),a.out.resolve())
