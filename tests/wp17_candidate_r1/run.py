"""Exact-head FW-1 execution, retaining the published bootstrap expectation.

Expectations come from p3_r1_r374, WP14 fixtures and frozen golden MANIFEST.
No Software assertions or private test results are imported as an oracle.
"""
import argparse,hashlib,json,shlex,struct,subprocess,sys,tempfile,wave
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
HEAD='ee478a913613a16a90e38c85112fb67cbbf53887'
sys.path.insert(0,str(ROOT/'tests/p3_r1_r374'));import wp17 as W
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def command(args,cwd=None):
    p=subprocess.run([str(x)for x in args],cwd=cwd,capture_output=True,text=True)
    assert p.returncode==0,(args,p.returncode,p.stdout,p.stderr)
    return p
def adapter_command(product,fw):
    return ' '.join(shlex.quote(str(x))for x in [sys.executable,product/'firmware/bench/host/partition_adapter.py','--fwhost',fw])
def partitions(product,fw,out):
    sys.path.insert(0,str(ROOT/'tests/wp14_r1'));import fixtures,oracle
    adapter=adapter_command(product,fw)
    # Execute the published gate verbatim and retain its actual failure.
    try:W.partition(adapter,out/'published-partition')
    except AssertionError as e:published=dict(result='FAIL',assertion=str(e))
    else:published=dict(result='PASS')
    # Separate complete observation matrix; no changed/waived bootstrap expectation.
    total=oracle.P2_START+fixtures.BLOCKS;clean=oracle.mbr(total);sig=bytearray(clean);sig[440]^=1
    cases=[('clean',clean,True),('disk-signature',bytes(sig),True),('bootstrap',bytes([1])+clean[1:],False)]
    for name,offset in [('signature',510),('p1-type',450),('p2-type',466),('p1-start',454),('p1-size',458),('p2-start',470),('p2-size',474),('extra-entry',478),('p2-boot',462)]:
        b=bytearray(clean);b[offset]^=1;cases.append((name,bytes(b),False))
    rows=[]
    with tempfile.TemporaryDirectory()as td:
        for name,mbr,want in cases:
            p=Path(td)/(name+'.img');fixtures.build(p,whole=True)
            with p.open('r+b')as f:f.write(mbr)
            before=p.read_bytes();n=fixtures.BLOCKS;start=oracle.P2_START
            request=dict(image=str(p),sectors=total,reads=[0,n-1,-1,n],writes=[dict(lba=1,hex='a5'*512),dict(lba=-1,hex='5a'*512),dict(lba=n,hex='5a'*512)])
            proc=subprocess.run(shlex.split(adapter),input=json.dumps(request),capture_output=True,text=True);assert proc.returncode==0
            result=json.loads(proc.stdout);after=p.read_bytes();checks=[]
            if result['accepted']:
                assert(result['start'],result['blocks'])==(start,n)
                assert result['read_hex']==[before[start*512:(start+1)*512].hex(),before[-512:].hex()]
                assert result['write_absolute_lba']==[start+1]and result['out_of_range_refused']is True
                expected=bytearray(before);expected[(start+1)*512:(start+2)*512]=bytes.fromhex('a5'*512)
                assert after==expected;checks=['first/last read','write translation','bounds refused','all other bytes unchanged']
            else:assert after==before;checks=['refused without byte changes']
            rows.append(dict(name=name,expected_accepted=want,actual=result,result='PASS'if result['accepted']is want else'FAIL',checks=checks,
                             input_sha256=hashlib.sha256(before).hexdigest(),output_sha256=hashlib.sha256(after).hexdigest()))
    assert published==dict(result='FAIL',assertion='bootstrap')
    assert [r['name']for r in rows if r['result']=='FAIL']==['bootstrap']
    return dict(published=published,rows=rows,disposition='HOLD on bootstrap spec/test disagreement; no expectation changed')
def goldens(product,fw,tapectl,out):
    rows=[];manifest=ROOT/'tests/golden/MANIFEST'
    with tempfile.TemporaryDirectory()as td:
        td=Path(td)
        for line in manifest.read_text().splitlines():
            if not line.strip()or line.startswith('#'):continue
            name,reference,commands=line.split(maxsplit=2)
            if name.startswith('scrub-'):continue
            ref=W.pcm(ROOT/reference);image=td/(name+'.img');chains=commands.split(' && ')
            prepare=[shlex.split(c)for c in chains[:-1]]
            first=prepare[0];assert first[1]=='format';blocks=int(first[first.index('--blocks')+1])
            # Same declared P2 block count, UUID, epoch, label and timeline; wrap in
            # the published WP14 whole-card layout so the firmware device view runs.
            tail=first[3:];i=tail.index('--blocks');del tail[i:i+2]
            command([tapectl,'provision',image,*tail,'--image-bytes',str((34816+blocks)*512)],product)
            for args in prepare[1:]:
                args[0]=str(tapectl);args[2]=str(image)
                command(args,product)
            last=shlex.split(chains[-1]);side=last[last.index('--side')+1];start=last[last.index('--from')+1]if'--from'in last else'0'
            for mode in ('det','live'):
                before=sha(image);raw=td/'output.pcm'
                base=[fw,'golden',image,'--side',side,'--from',start,'--frames',str(len(ref)//4),'--mode',mode,'-o',raw]
                p=command(base,product);facts=json.loads(p.stdout);actual=raw.read_bytes();W.compare(ref,actual)
                assert facts['result']==0 and facts['frames']==len(ref)//4 and facts['underruns']==facts['card_writes']==0
                assert facts['sha256']==hashlib.sha256(actual).hexdigest()and sha(image)==before
                controls=[]
                for control in ('flip','rate'):
                    q=command(base+['--control',control],product);bad=raw.read_bytes();assert bad!=ref
                    at=next((i for i,(a,b)in enumerate(zip(ref,bad))if a!=b),min(len(ref),len(bad)))
                    controls.append(dict(name=control,observed=json.loads(q.stdout),mismatch_offset=at,expected_hex=ref[at:at+8].hex(),actual_hex=bad[at:at+8].hex()))
                    assert sha(image)==before
                rows.append(dict(name=name,mode=mode,reference_sha256=sha(ROOT/reference),pcm_sha256=hashlib.sha256(actual).hexdigest(),facts=facts,controls=controls,image_unchanged=True))
    assert len(rows)==14;return dict(results=rows,normal_vectors=7,modes=2,negative_controls=28,scope='firmware portable path on host; no target/I2S claim')
def symbol(elf,name):
    b=Path(elf).read_bytes();assert b[:6]==b'\x7fELF\x01\x01'
    h=struct.unpack_from('<HHIIIIIHHHHHH',b,16);off=h[5];entry=h[10];count=h[11]
    sections=[struct.unpack_from('<IIIIIIIIII',b,off+i*entry)for i in range(count)]
    for s in sections:
        if s[1]!=2:continue
        strings=sections[s[6]];text=b[strings[4]:strings[4]+strings[5]]
        for i in range(s[4],s[4]+s[5],s[9]):
            n,value,size,info,other,index=struct.unpack_from('<IIIBBH',b,i)
            if text[n:text.find(b'\0',n)].decode()==name:return size,value,index
    raise AssertionError('ELF symbol absent: '+name)
def memory(folder):
    folder=Path(folder)
    for line in(folder/'SHA256SUMS').read_text().splitlines():
        h,n=line.split();assert sha(folder/n)==h
    lines=(folder/'firmware.map').read_text().split('Linker script and memory map',1)[1].splitlines()
    sums=dict(data=0,bss=0,rodata=0,common=0);entries=[];section=None
    for line in lines:
        fields=line.split()
        if not fields:continue
        if line.startswith(' ')and(fields[0].startswith('.')or fields[0]=='COMMON'):
            section=fields[0];fields=fields[1:]
        elif not fields[0].startswith('0x'):section=None;continue
        if len(fields)<3 or not fields[0].startswith('0x')or not fields[1].startswith('0x'):continue
        if 'libtape_engine.a('not in' '.join(fields[2:]):continue
        kind=next((k for k in ('data','bss','rodata')if section=='.'+k or(section or'').startswith('.'+k+'.')),None)
        if section=='COMMON':kind='common'
        if kind:
            size=int(fields[1],16);sums[kind]+=size;entries.append(dict(section=section,bytes=size,object=' '.join(fields[2:])))
    assert entries,'engine input sections not identified'
    instance,address,index=symbol(folder/'firmware.elf','fw_engine_instance')
    result=W.budget(sums['data'],sums['bss']+sums['common'],instance,sums['rodata'])
    assert result['ram']==191600 and result['rodata']==1040
    return dict(sections=sums,instance=instance,instance_address=address,instance_section_index=index,gate=result,input_sections=entries,
                elf_sha256=sha(folder/'firmware.elf'),map_sha256=sha(folder/'firmware.map'),stack='PENDING target measurement')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--product',type=Path,required=True);p.add_argument('--fwhost',type=Path,required=True);p.add_argument('--tapectl',type=Path,required=True);p.add_argument('--arm',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    product=a.product.resolve();out=a.out.resolve();out.mkdir(parents=True,exist_ok=True)
    assert command(['git','-C',product,'rev-parse','HEAD']).stdout.strip()==HEAD
    engine=W.enginecheck(product);report=dict(head=HEAD,engine_tree=engine,binaries=dict(fwhost=sha(a.fwhost),tapectl=sha(a.tapectl)),
                                            memory=memory(a.arm),partition=partitions(product,a.fwhost.resolve(),out))
    (out/'PARTIAL.json').write_text(json.dumps(report,indent=2)+'\n')
    report['firmware_host']=goldens(product,a.fwhost.resolve(),a.tapectl.resolve(),out)
    (out/'RESULT.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(head=HEAD,engine=engine,ram=report['memory']['gate'],partition_failures=['bootstrap'],firmware_host_comparisons=14,controls=28,disposition='HOLD pending PM bootstrap decision'),indent=2))
