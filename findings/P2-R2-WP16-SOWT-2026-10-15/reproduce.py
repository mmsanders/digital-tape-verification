"""Reproduce P2V16-002 using generated CC0 bytes, never Product code."""
import argparse,hashlib,json,struct,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent

def parse(path):
    data=path.read_bytes();assert data[:4]==b'FORM' and data[8:12]==b'AIFC'
    at=12;result={'file':path.name,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
    while at<len(data):
        tag=data[at:at+4];size=int.from_bytes(data[at+4:at+8],'big');body=data[at+8:at+8+size]
        assert len(body)==size
        if tag==b'COMM':
            channels,frames,bits=struct.unpack_from('>HIH',body)
            result.update(channels=channels,declared_frames=frames,declared_bits=bits,compression=body[18:22].decode())
        if tag==b'SSND':result['pcm_bytes']=len(body)-8
        at+=size+8+size%2
    result['frames_at_declared_precision']=result['pcm_bytes']//(result['declared_bits']//8)//result['channels']
    result['frames_at_registered_sowt16']=result['pcm_bytes']//2//result['channels']
    return result

def run(decode=False):
    records=[]
    for name in ('sowt16.aif','sowt24.aif'):
        p=HERE/name;r=parse(p)
        assert r['declared_frames']==r['frames_at_declared_precision']==256 and r['compression']=='sowt'
        if decode:
            args=['ffmpeg','-v','error','-nostdin','-xerror','-i',str(p),'-f','f64le','-acodec','pcm_f64le','-']
            result=subprocess.run(args,capture_output=True);assert result.returncode==0
            r['ffmpeg_decoded_frames']=len(result.stdout)//8//r['channels'];r['stderr']=result.stderr.decode()
            r['argv']=[v.replace(str(HERE),'{FINDING}') for v in args]
            assert r['ffmpeg_decoded_frames']==r['frames_at_registered_sowt16']
        records.append(r)
    assert records[0]['frames_at_registered_sowt16']==256 and records[1]['frames_at_registered_sowt16']==384
    return records
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--decode',action='store_true');ap.add_argument('--out',type=Path);a=ap.parse_args()
    records=run(a.decode)
    if a.out:a.out.write_text(json.dumps(records,indent=2)+'\n')
    print('P2V16-002: sowt16 agrees at256 frames; sowt24 has256 declared vs384 registered16-bit frames; ruling required')
