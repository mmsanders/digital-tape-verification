#!/usr/bin/env python3
"""Black-box image checks against an explicitly supplied candidate binary.

This runs only the unaffected subset. It never reports whole-package acceptance.
Physical devices are intentionally not accepted as arguments to this runner.
"""
import argparse
import hashlib
import json
import shutil
import struct
import subprocess
import tempfile
from pathlib import Path
from oracle import UUID, P2_START, geometry, minimum_blocks, mbr, fat16_readme
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
    # The issue's named WP11 "tail rule" is missing from the issued contract.
    with Path(source).open('rb') as a, Path(output).open('rb') as b:
        while True:
            x,y=a.read(1024*1024),b.read(1024*1024)
            assert x==y, 'round-trip bytes/length differ'
            if not x: break

def make_c60(path):
    # Nonzero stereo pattern with distinct left/right and positions in a block.
    frames=3600*44100
    pattern=b''.join(struct.pack('<hh',i*251-16000,15000-i*239) for i in range(128))
    data_bytes=frames*4
    with Path(path).open('wb') as f:
        f.write(struct.pack('<4sI4s4sIHHIIHH4sI',b'RIFF',36+data_bytes,b'WAVE',b'fmt ',
                            16,1,2,44100,176400,4,16,b'data',data_bytes))
        page=pattern*2048
        pages,tail=divmod(data_bytes,len(page))
        for _ in range(pages): f.write(page)
        f.write((page[:tail]))

def run(binary, full_c60=False):
    evidence=[]
    def invoke(*args, code=0, token=None):
        result=subprocess.run([str(binary),*map(str,args)],capture_output=True,text=True,timeout=1800)
        evidence.append({'argv':list(map(str,args)),'exit':result.returncode,
                         'stdout':result.stdout,'stderr':result.stderr})
        assert result.returncode==code, evidence[-1]
        if token: assert token in result.stdout+result.stderr, evidence[-1]
    with tempfile.TemporaryDirectory(prefix='wp14-verifier-') as tmp:
        work=Path(tmp)
        sources=sorted((GOLDEN/'ref').glob('*.wav'))
        assert len(sources)==10
        if full_c60:
            make_c60(work/'c60.wav'); sources.append(work/'c60.wav')
        for source in sources:
            seconds=3600 if source.name=='c60.wav' else 60
            blocks=max(minimum_blocks(seconds),65537)
            image=work/'bare.img'
            invoke('format',image,'--blocks',blocks,'--uuid',UUID.hex(),'--epoch',315532800,
                   '--label','WP14','--length-s',seconds)
            invoke('load',image,source)
            before=sha(image)
            invoke('verify',image,token='OK')
            assert before==sha(image), 'verify changed bare image'
            for side in ('A','B'):
                out=work/'dump.wav'
                invoke('dump',image,'--side',side,'-o',out)
                compare_wav(source,out)
            evidence.append({'case':'bare-roundtrip-'+source.name,'source_sha256':sha(source)})
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
        short=work/'short.wav'
        payload=b'\x01\x00\x02\x00'*44101
        short.write_bytes(struct.pack('<4sI4s4sIHHIIHH4sI',b'RIFF',36+len(payload),b'WAVE',
                          b'fmt ',16,1,2,44100,176400,4,16,b'data',len(payload))+payload)
        cap=work/'capacity.img'
        invoke('format',cap,'--blocks',65537,'--uuid',UUID.hex(),'--epoch',315532800,
               '--label','one second','--length-s',1)
        before=sha(cap)
        invoke('load',cap,short,code=2)
        assert before==sha(cap), 'capacity refusal changed target'
        assert 'long' in (evidence[-1]['stdout']+evidence[-1]['stderr']).lower(), 'missing plain overage'
        # E1 layout is proposed, not authorized. Caller explicitly opts into this check.
        # Mirror read/write at >4 GiB exercised by every mount on this sparse image.
        large=work/'card.img'; size=64_000_000_000
        invoke('provision',large,'--label','WP14','--length-s',60,'--uuid',UUID.hex(),
               '--epoch',315532800,'--image-bytes',size)
        with large.open('rb') as f:
            assert f.read(512)==mbr(size//512), 'MBR byte mismatch'
        fat=fat16_readme(large,'WP14')
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
        evidence.append({'case':'proposed-E1-large-image','fat':fat,'mirror_offset':size-512})
    return {'kind':'candidate-unaffected-image-subset','binary_sha256':sha(binary),
            'full_c60':full_c60,'whole_package_accepted':False,'observations':evidence}

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('binary',type=Path)
    parser.add_argument('--full-c60',action='store_true')
    parser.add_argument('--proposed-e1',action='store_true',required=True,
                        help='explicitly acknowledge E1 is not owner-approved')
    args=parser.parse_args()
    print(json.dumps(run(args.binary.resolve(),args.full_c60),indent=2))
