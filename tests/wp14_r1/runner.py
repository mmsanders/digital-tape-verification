#!/usr/bin/env python3
"""Black-box image checks against an explicitly supplied candidate binary.

This runs image cases. Native observation/loop gates are separate, mandatory.
Physical devices are intentionally not accepted as arguments to this runner.
"""
import argparse
import hashlib
import json
import re
import shutil
import struct
import subprocess
import tempfile
from pathlib import Path
from oracle import UUID, P2_START, geometry, minimum_blocks, mbr, fat16_readme, layout_findings, safe_view
from fixtures import build

HERE = Path(__file__).resolve().parent
GOLDEN = HERE.parent/'golden'

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def compare_wav(source, output):
    # Exact length/bytes. No invented zero padding or dropped last frame.
    # ADR164 explicitly forbids a tail tolerance.
    with Path(source).open('rb') as a, Path(output).open('rb') as b:
        while True:
            x,y=a.read(1024*1024),b.read(1024*1024)
            assert x==y, 'round-trip bytes/length differ'
            if not x: break

def make_wav(path,frames):
    # Nonzero stereo pattern with distinct left/right and positions in a block.
    pattern=b''.join(struct.pack('<hh',i*251-16000,15000-i*239) for i in range(128))
    data_bytes=frames*4
    with Path(path).open('wb') as f:
        f.write(struct.pack('<4sI4s4sIHHIIHH4sI',b'RIFF',36+data_bytes,b'WAVE',b'fmt ',
                            16,1,2,44100,176400,4,16,b'data',data_bytes))
        page=pattern*2048
        pages,tail=divmod(data_bytes,len(page))
        for _ in range(pages): f.write(page)
        f.write((page[:tail]))

def make_c60(path): make_wav(path,3600*44100)

def run(binary):
    evidence=[]
    def invoke(*args, code=0, token=None):
        result=subprocess.run([str(binary),*map(str,args)],capture_output=True,text=True,timeout=1800)
        evidence.append({'argv':list(map(str,args)),'exit':result.returncode,
                         'stdout':result.stdout,'stderr':result.stderr})
        assert result.returncode==code, evidence[-1]
        if token: assert token in result.stdout+result.stderr, evidence[-1]
    with tempfile.TemporaryDirectory(prefix='wp14-verifier-') as tmp:
        work=Path(tmp)
        # Paired entropy options and byte-counted labels fail before mutation.
        for options in (['--uuid',UUID.hex()],['--epoch','1'],['--label',''],
                        ['--label','é'*17],['--label','x'*33]):
            target=work/'usage.img'; target.write_bytes(b'unchanged-sentinel')
            invoke('provision',target,'--image-bytes',64_000_000,'--length-s',9,*options,code=2)
            assert target.read_bytes()==b'unchanged-sentinel'
        random_image=work/'entropy.img'
        invoke('provision',random_image,'--label','é'*16,'--length-s',9,
               '--image-bytes',(P2_START+minimum_blocks(9))*512)
        assert re.fullmatch(r'uuid [0-9a-f]{32}\nepoch [0-9]+\n',evidence[-1]['stdout'])
        fat16_readme(random_image,'é'*16)
        sources=sorted((GOLDEN/'ref').glob('*.wav'))
        assert len(sources)==10
        make_c60(work/'c60.wav'); sources.append(work/'c60.wav')
        for source,kind in ((s,k) for s in sources for k in ('bare','whole')):
            seconds=3600 if source.name=='c60.wav' else 60
            blocks=max(minimum_blocks(seconds),65537)
            image=work/'bare.img'
            if kind=='bare':
                invoke('format',image,'--blocks',blocks,'--uuid',UUID.hex(),'--epoch',315532800,
                       '--label','WP14','--length-s',seconds)
            else:
                invoke('provision',image,'--image-bytes',(blocks+P2_START)*512,
                       '--uuid',UUID.hex(),'--epoch',315532800,'--label','WP14','--length-s',seconds)
            invoke('load',image,source)
            before=sha(image)
            invoke('verify',image,token='OK')
            assert before==sha(image), 'verify changed bare image'
            for side in ('A','B'):
                out=work/'dump.wav'
                invoke('dump',image,'--side',side,'-o',out)
                compare_wav(source,out)
            evidence.append({'case':kind+'-roundtrip-'+source.name,'source_sha256':sha(source)})
        # All layout branches are reachable under ADR164; assert exact ordering.
        for off in (0,444,446,447,450,454,458,462,463,466,470,474,478,510):
            image=work/'mbr-finding.img'; build(image,whole=True)
            with image.open('r+b') as f:
                original=f.read(512); damaged=bytearray(original); damaged[off]^=1
                f.seek(0); f.write(damaged)
            expected=layout_findings(damaged,image.stat().st_size//512)
            before=sha(image); invoke('verify',image,code=1)
            lines=evidence[-1]['stdout'].splitlines()+evidence[-1]['stderr'].splitlines()
            observed=[line for line in lines if line in ('MBR_LAYOUT','PARTITION_TYPE','PARTITION_TRUNCATED')]
            assert observed==expected,(off,observed,expected)
            assert before==sha(image)
        image=work/'mbr-multiple.img'; build(image,whole=True)
        with image.open('r+b') as f:
            damaged=bytearray(f.read(512)); damaged[0]=1; damaged[450]^=1
            struct.pack_into('<I',damaged,474,0xffffffff); f.seek(0); f.write(damaged)
        before=sha(image); invoke('verify',image,code=1)
        assert before==sha(image)
        lines=evidence[-1]['stdout'].splitlines()+evidence[-1]['stderr'].splitlines()
        assert [x for x in lines if x in ('MBR_LAYOUT','PARTITION_TYPE','PARTITION_TRUNCATED')]==['MBR_LAYOUT','PARTITION_TYPE','PARTITION_TRUNCATED']
        # Timestamp boundaries/clamping, deterministic explicit identity, UTF8 byte limit.
        for epoch in (0,1,315532799,315532800,315532801,946684799,946684800,0xffffffff):
            image=work/'epoch.img'
            invoke('provision',image,'--label','WP14','--length-s',9,'--uuid',UUID.hex(),
                   '--epoch',epoch,'--image-bytes',(P2_START+minimum_blocks(9))*512)
            assert not evidence[-1]['stdout'].strip()
            fat16_readme(image,'WP14',epoch)
            with image.open('rb') as f:
                f.seek(P2_START*512+120); assert struct.unpack('<I',f.read(4))[0]==epoch
            prior=sha(image)
            invoke('provision',image,'--label','WP14','--length-s',9,'--uuid',UUID.hex(),
                   '--epoch',epoch,'--image-bytes',(P2_START+minimum_blocks(9))*512)
            assert prior==sha(image)
        for mutation,code,token in (('clean',0,'OK'),('invalid-standby',0,'OK'),
                                    ('torn-primary',1,'NEEDS_REPAIR'),
                                    ('both-superblocks-bad',1,'MOUNT TAPE_ERR_'),
                                    ('flipped-a-entry',1,'MOUNT TAPE_ERR_NO_VALID_INDEX'),
                                    ('degraded-b',1,'SIDE_B_DEGRADED')):
            image=work/(mutation+'.img'); build(image,mutation)
            before=sha(image)
            invoke('verify',image,code=code,token=token)
            assert before==sha(image),'verify repaired/corrupted '+mutation
        # Geometry refusal must preserve an existing file, not truncate it first.
        sentinel=work/'geometry.img'; sentinel.write_bytes(b'unchanged-sentinel')
        invoke('provision',sentinel,'--label','WP14','--length-s',60,'--uuid',UUID.hex(),
               '--epoch',315532800,'--image-bytes',(P2_START+minimum_blocks(60)-1)*512,
               code=1,token='TAPE_ERR_GEOMETRY')
        assert sentinel.read_bytes()==b'unchanged-sentinel', 'geometry refusal modified target'
        # Capacity: label 1 second, source 1 frame too long; create a canonical WAV.
        for seconds,excess,want in ((1,1,'1 s for a 1-second'),
                                    (60,1,'1 s for a 1-minute'),
                                    (1,60*44100,'1 min for a 1-second'),
                                    (1,60*44100+1,'1 min 1 s for a 1-second')):
            short=work/'short.wav'; make_wav(short,seconds*44100+excess)
            cap=work/'capacity.img'
            invoke('format',cap,'--blocks',minimum_blocks(seconds),'--uuid',UUID.hex(),'--epoch',315532800,
                   '--label','capacity','--length-s',seconds)
            before=sha(cap); invoke('load',cap,short,code=2)
            assert before==sha(cap), 'capacity refusal changed target'
            assert ('Too long by '+want+' cartridge') in evidence[-1]['stdout']+evidence[-1]['stderr']
        # Mirror read/write at >4 GiB exercised by every mount on this sparse image.
        large=work/'card.img'; size=64_000_000_000
        invoke('provision',large,'--label','WP14','--length-s',60,'--uuid',UUID.hex(),
               '--epoch',315532800,'--image-bytes',size)
        with large.open('rb') as f:
            assert f.read(512)==mbr(size//512), 'MBR byte mismatch'
        fat=fat16_readme(large,'WP14',315532800)
        invoke('load',large,GOLDEN/'src/quiet.wav')
        invoke('verify',large,token='OK')
        for side in ('A','B'):
            out=work/'dump.wav'; invoke('dump',large,'--side',side,'-o',out)
            compare_wav(GOLDEN/'src/quiet.wav',out)
        for command in ('reset-b','promote','respool'):
            invoke(command,large)
        invoke('play',large,'--side','A','--from',0,'--frames',128,'--rate',1,'-o',work/'play.wav')
        invoke('scrub',large,'--side','A','--from',128,'--schedule','-1:129','-o',work/'scrub.wav')
        invoke('record',large,'--at',0,'--mode','overwrite',GOLDEN/'src/voice.wav')
        old_size=large.stat().st_size
        with large.open('rb') as f: old_mbr=f.read(512)
        invoke('format',large,'--blocks',65537,'--uuid',UUID.hex(),'--epoch',315532800,
               '--label','WP14','--length-s',60,code=2)
        assert large.stat().st_size==old_size
        with large.open('rb') as f: assert f.read(512)==old_mbr
        evidence.append({'case':'approved-E1-large-image','fat':fat,'mirror_offset':size-512})
    return {'kind':'candidate-image-cases','binary_sha256':sha(binary),
            'full_c60':True,'whole_package_accepted':False,'observations':evidence}

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('binary',type=Path)
    args=parser.parse_args()
    print(json.dumps(run(args.binary.resolve()),indent=2))
