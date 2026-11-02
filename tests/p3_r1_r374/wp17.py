"""Independent FW-1 expectations; no firmware imports."""
import argparse, hashlib, json, shlex, struct, subprocess, sys, tempfile, wave
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PIN='d96b4245e04d74078f8938744b1394c3018516f7'

def sha(b): return hashlib.sha256(b).hexdigest()
def pcm(path):
    with wave.open(str(path),'rb') as w:
        assert (w.getnchannels(),w.getsampwidth(),w.getframerate(),w.getcomptype())==(2,2,44100,'NONE')
        return w.readframes(w.getnframes())
def compare(ref, actual):
    assert ref and len(ref)%4==0 and ref==actual, 'PCM length/sample mismatch'
def budget(data,bss,instance,rodata,stack=None):
    assert all(type(x)is int and x>=0 for x in (data,bss,instance,rodata))
    assert data+bss+instance<=200*1024, 'RAM exceeds 200 KiB'
    assert rodata<=32*1024, 'engine rodata exceeds 32 KiB'
    if stack is not None: assert type(stack)is int and 0<=stack<=8192, 'stack exceeds 8 KiB'
    return dict(ram=data+bss+instance,rodata=rodata,stack=stack,stack_status='PENDING' if stack is None else 'PASS')
def rejects(fn,*args):
    try: fn(*args)
    except AssertionError: return
    raise AssertionError('negative control did not fail')
def enginecheck(product):
    product=Path(product).resolve()
    tree=subprocess.check_output(['git','-C',str(product),'rev-parse','HEAD:engine'],text=True).strip()
    assert tree==PIN, 'changed engine tree'
    assert not subprocess.check_output(['git','-C',str(product),'status','--porcelain','--untracked-files=all','--','engine'],text=True).strip(), 'engine worktree differs'
    return tree
def host(product,out):
    product=Path(product).resolve();out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
    tree=enginecheck(product)
    refs=ROOT/'tests/golden'
    for line in (refs/'SHA256SUMS').read_text().splitlines():
        if line.strip():
            h,n=line.split(maxsplit=1);assert sha((refs/n.lstrip('*')).read_bytes())==h
    results=[]
    (product/'build/tests/golden').mkdir(parents=True,exist_ok=True)
    for line in (refs/'MANIFEST').read_text().splitlines():
        if not line.strip() or line.startswith('#'): continue
        name,rel,cmd=line.split(maxsplit=2);dest=out/(name+'.wav')
        env=__import__('os').environ.copy();env['GOLDEN_OUT']=str(dest)
        p=subprocess.run(['bash','-c',cmd],cwd=product,env=env,capture_output=True,text=True)
        (out/(name+'.log')).write_text(p.stdout+p.stderr)
        assert p.returncode==0, name+': command failed'
        ref=(ROOT/rel).read_bytes();actual=dest.read_bytes();assert ref==actual, name+': WAV mismatch'
        raw=pcm(dest);compare(pcm(ROOT/rel),raw)
        mutant=bytes([raw[0]^1])+raw[1:];rejects(compare,raw,mutant)
        results.append(dict(name=name,wav_sha256=sha(actual),pcm_sha256=sha(raw),frames=len(raw)//4,
                            rate_scope='scrub vector' if name.startswith('scrub-') else '1x',altered_sample='REJECTED'))
    report=dict(engine_tree=tree,goldens=results,target='PENDING bench capture')
    (out/'HOST.json').write_text(json.dumps(report,indent=2)+'\n');return report
def partition(adapter,out):
    # Reuse independent WP-14 fixtures, never candidate layout code as expectation.
    sys.path.insert(0,str(ROOT/'tests/wp14_r1'))
    import fixtures,oracle
    out=Path(out);out.mkdir(parents=True,exist_ok=True);rows=[]
    total=oracle.P2_START+fixtures.BLOCKS
    clean=oracle.mbr(total)
    signature=bytearray(clean);signature[440]^=1
    cases=[('clean',clean,True),('disk-signature',bytes(signature),True),('bootstrap',bytes([1])+clean[1:],False)]
    for name,offset in [('signature',510),('p1-type',450),('p2-type',466),('p1-start',454),('p1-size',458),('p2-start',470),('p2-size',474),('extra-entry',478),('p2-boot',462)]:
        b=bytearray(clean);b[offset]^=1;cases.append((name,bytes(b),False))
    for name,mbr,ok in cases:
        path=(out/(name+'.img')).resolve();fixtures.build(path,whole=True)
        with path.open('r+b')as f:f.write(mbr)
        before=path.read_bytes();start=oracle.P2_START;n=fixtures.BLOCKS
        request=dict(image=str(path),sectors=total,reads=[0,n-1,-1,n],writes=[dict(lba=1,hex=('a5'*512)),dict(lba=-1,hex=('5a'*512)),dict(lba=n,hex=('5a'*512))])
        p=subprocess.run(shlex.split(adapter),input=json.dumps(request),text=True,capture_output=True,check=True)
        r=json.loads(p.stdout);assert r['accepted']is ok,name
        after=path.read_bytes()
        if ok:
            assert (r['start'],r['blocks'])==(start,n)
            assert r['read_hex']==[before[start*512:(start+1)*512].hex(),before[-512:].hex()]
            assert r['write_absolute_lba']==[start+1] and r['out_of_range_refused']is True
            expected=bytearray(before);expected[(start+1)*512:(start+2)*512]=bytes.fromhex('a5'*512)
            assert after==expected,'write escaped view or legal write not applied'
        else: assert after==before,'refused layout changed'
        rows.append(dict(name=name,accepted=ok,result='PASS'))
        path.unlink()
    (out/'PARTITION.json').write_text(json.dumps(rows,indent=2)+'\n');return rows
def selftest():
    compare(b'\x00\x01\x02\x03',b'\x00\x01\x02\x03')
    for b in (b'',b'\x01\x01\x02\x03',bytes(8)): rejects(compare,b'\x00\x01\x02\x03',b)
    budget(0,0,204800,32768,8192)
    for args in [(0,204801,0,0,0),(0,0,0,32769,0),(0,0,0,0,8193),(-1,0,0,0,0)]:rejects(budget,*args)
    assert PIN!='0'*40 # real tree drift is checked against candidate git objects by host().
    return dict(pcm_controls=3,budget_controls=4,result='PASS')
if __name__=='__main__':
    a=argparse.ArgumentParser();s=a.add_subparsers(dest='cmd',required=True)
    s.add_parser('selftest');p=s.add_parser('host');p.add_argument('--product',required=True);p.add_argument('--out',required=True)
    p=s.add_parser('pcm');p.add_argument('reference');p.add_argument('capture')
    p=s.add_parser('budget');p.add_argument('values',type=int,nargs='+');p.add_argument('--static-only',action='store_true')
    p=s.add_parser('partition');p.add_argument('--adapter',required=True);p.add_argument('--out',required=True)
    p=s.add_parser('enginecheck');p.add_argument('product')
    x=a.parse_args()
    if x.cmd=='selftest':r=selftest()
    elif x.cmd=='host':r=host(x.product,x.out)
    elif x.cmd=='pcm':compare(pcm(x.reference),Path(x.capture).read_bytes());r='PASS PCM'
    elif x.cmd=='partition':r=partition(x.adapter,x.out)
    elif x.cmd=='enginecheck':r=enginecheck(x.product)
    else:
        assert len(x.values)==(4 if x.static_only else 5);r=budget(*x.values)
    print(json.dumps(r,indent=2))
