"""Independent generated-container writers and encoded interval readers.

All PCM sources are mathematical signals dedicated to CC0. FFmpeg encodes only
the lossy/container fixtures; no FFmpeg decoded bytes are universal goldens.
"""
import hashlib
import math
import struct
from pathlib import Path
import numpy as np


def pcm_bytes(x,bits,endian='little',unsigned=False):
    q=np.rint(np.asarray(x)*(2**(bits-1))).astype(np.int64)
    assert np.max(np.abs(q),initial=0)<2**(bits-1)
    if unsigned:q=q+2**(bits-1)
    return b''.join(int(v).to_bytes((bits+7)//8,endian,signed=not unsigned) for v in q.ravel())


def chunk(tag,data,endian='<'):
    return tag+struct.pack(endian+'I',len(data))+data+(b'\0' if len(data)%2 else b'')


def wave(x,rate,bits=16,floating=False,extensible=False,mask=None):
    x=np.asarray(x);channels=x.shape[1];width=bits//8
    data=x.astype('<f%d'%width).tobytes() if floating else pcm_bytes(x,bits,unsigned=bits==8)
    tag=3 if floating else 1
    fmt=struct.pack('<HHIIHH',0xfffe if extensible else tag,channels,rate,rate*channels*width,channels*width,bits)
    if extensible:
        if mask is None:mask=4 if channels==1 else 3
        fmt+=struct.pack('<HHI',22,bits,mask)+struct.pack('<IHH8s',tag,0,0x10,b'\x80\0\0\xaa\0\x38\x9b\x71')
    body=b'WAVE'+chunk(b'fmt ',fmt)+chunk(b'data',data)
    return b'RIFF'+struct.pack('<I',len(body))+body


def extended80(rate):
    exponent=int(math.floor(math.log2(rate)))
    mantissa=int(rate*2**(63-exponent))
    return struct.pack('>HQ',exponent+16383,mantissa)


def aiff(x,rate,bits=16,compression=None):
    channels=x.shape[1]
    data=pcm_bytes(x,bits,'little' if compression==b'sowt' else 'big')
    comm=struct.pack('>HIH',channels,len(x),bits)+extended80(rate)
    if compression is not None:comm+=compression+b'\0\0'
    body=(b'AIFC' if compression is not None else b'AIFF')
    if compression is not None:body+=chunk(b'FVER',struct.pack('>I',0xA2805140),'>')
    body+=chunk(b'COMM',comm,'>')+chunk(b'SSND',bytes(8)+data,'>')
    return b'FORM'+struct.pack('>I',len(body))+body


def crc(data,width,poly):
    state=0
    for b in data:
        state^=b<<(width-8)
        for _ in range(8):state=((state<<1)^poly if state&(1<<(width-1)) else state<<1)&((1<<width)-1)
    return state


def flac(x,rate,bits):
    """RFC9639 verbatim/independent-channel frames, including all8..32 bit depths."""
    channels=x.shape[1];n=len(x);assert n<=65535
    packed=(rate<<44)|((channels-1)<<41)|((bits-1)<<36)|n
    info=struct.pack('>HH',n,n)+bytes(6)+packed.to_bytes(8,'big')+hashlib.md5(pcm_bytes(x,bits)).digest()
    header=b'\xff\xf8\x70'+bytes([(channels-1)<<4])+b'\0'+struct.pack('>H',n-1)
    header+=bytes([crc(header,8,0x07)])
    values=np.rint(x*(2**(bits-1))).astype(np.int64)
    bitstream=''
    for channel in range(channels):
        bitstream+='00000010' # zero padding, VERBATIM subframe type, no wasted bits
        bitstream+=''.join(format(int(v)&((1<<bits)-1),'0%db'%bits) for v in values[:,channel])
    bitstream+='0'*((-len(bitstream))%8)
    payload=int(bitstream,2).to_bytes(len(bitstream)//8,'big') if bitstream else b''
    frame=header+payload;frame+=struct.pack('>H',crc(frame,16,0x8005))
    return b'fLaC'+b'\x80\0\0\x22'+info+frame


def boxes(data,start=0,end=None):
    end=len(data) if end is None else end
    at=start
    while at<end:
        if at+8>end:raise ValueError('truncated BMFF box')
        size,tag=struct.unpack_from('>I4s',data,at);head=8
        if size==1:size=struct.unpack_from('>Q',data,at+8)[0];head=16
        if size==0:size=end-at
        if size<head or at+size>end:raise ValueError('bad BMFF size')
        yield tag,at+head,at+size,at
        at+=size


def descendants(data,start=0,end=None):
    for tag,a,b,box_start in boxes(data,start,end):
        yield tag,a,b,box_start
        if tag in (b'moov',b'trak',b'mdia',b'minf',b'stbl',b'edts'):
            yield from descendants(data,a,b)


def bmff_interval(data):
    found=list(descendants(data));get=lambda tag:next((a,b) for t,a,b,_ in found if t==tag)
    a,b=get(b'mvhd');version=data[a];movie_scale=struct.unpack_from('>I',data,a+(20 if version else 12))[0]
    a,b=get(b'mdhd');version=data[a];rate=struct.unpack_from('>I',data,a+(20 if version else 12))[0]
    a,b=get(b'elst');version=data[a];count=struct.unpack_from('>I',data,a+4)[0]
    entries=[];pos=a+8
    for _ in range(count):
        duration,media=struct.unpack_from('>Qq' if version else '>Ii',data,pos);pos+=16 if version else 8
        integer,fraction=struct.unpack_from('>hh',data,pos);pos+=4
        entries.append((duration,media,integer,fraction))
    if len(entries)!=1 or entries[0][2:]!=(1,0):raise ValueError('unsupported edit interval')
    duration,head,*_=entries[0]
    if duration*rate%movie_scale:raise ValueError('fractional edit endpoint')
    effective=duration*rate//movie_scale
    a,b=get(b'stsz');packets=struct.unpack_from('>I',data,a+8)[0];raw=packets*1024
    if head<0 or effective<=0 or head+effective>raw:raise ValueError('out of range edit')
    return dict(input_rate=rate,raw_frames=raw,trim_head=head,trim_tail=raw-head-effective,
                effective_frames=effective,trim_evidence='bmff_edit',movie_timescale=movie_scale,
                presentation_duration=duration,decoder_priming=1024)


def mp3_interval(data):
    at=0
    if data[:3]==b'ID3':at=10+sum((data[6+i]&127)<<(7*(3-i)) for i in range(4))
    frames=[];first=None
    while at+4<=len(data):
        h=int.from_bytes(data[at:at+4],'big')
        if h>>21!=0x7ff:break
        v=(h>>19)&3;layer=(h>>17)&3;bi=(h>>12)&15;ri=(h>>10)&3
        if v==1 or layer!=1 or bi in (0,15) or ri==3:raise ValueError('not admitted LayerIII')
        rate=[44100,48000,32000][ri]//(1 if v==3 else 2 if v==2 else 4)
        kbps=([0,32,40,48,56,64,80,96,112,128,160,192,224,256,320] if v==3 else [0,8,16,24,32,40,48,56,64,80,96,112,128,144,160])[bi]
        count=1152 if v==3 else 576;length=(144000 if v==3 else 72000)*kbps//rate+((h>>9)&1)
        if at+length>len(data):raise ValueError('truncated MP3 frame')
        frames.append((at,length));first=first or (h,rate,count)
        at+=length
    if not frames:raise ValueError('no MP3 frames')
    h,rate,count=first;start,length=frames[0];mono=((h>>6)&3)==3;v=(h>>19)&3
    side=(17 if mono else 32) if v==3 else (9 if mono else 17)
    xing=start+4+(0 if (h>>16)&1 else 2)+side
    if data[xing:xing+4] not in (b'Xing',b'Info'):return dict(input_rate=rate,raw_frames=len(frames)*count,trim_head=0,trim_tail=0,effective_frames=len(frames)*count,trim_evidence='none')
    flags=int.from_bytes(data[xing+4:xing+8],'big');p=xing+8
    declared=None
    for mask,width in [(1,4),(2,4),(4,100),(8,4)]:
        if flags&mask:
            if mask==1:declared=int.from_bytes(data[p:p+4],'big')
            p+=width
    tag=data[p:p+36]
    if len(tag)<36:raise ValueError('missing LAME-compatible tag')
    delay=(tag[21]<<4)|(tag[22]>>4);padding=((tag[22]&15)<<8)|tag[23]
    if declared!=len(frames)-1:raise ValueError('Xing frame census disagrees')
    raw=declared*count
    if delay+padding>=raw:raise ValueError('invalid MP3 interval')
    # Encoder interval is independent of decoder synthesis latency. FFmpeg's raw
    # PCM origin adds529 and removes529 from the tail; alternative decoder origins
    # must declare an equivalent mapping, never guess/remove extra presentation.
    return dict(input_rate=rate,raw_frames=raw,trim_head=delay+529,trim_tail=padding-529,
                effective_frames=raw-delay-padding,trim_evidence='xing_lame',encoder_delay=delay,
                encoder_padding=padding,decoder_priming=529,encoder_tag=tag[:9].decode('ascii','replace'),
                encoded_audio_frames=declared,samples_per_frame=count)


def generated_pcm(data):
    """Independent decoder for the generated RIFF PCM/float families only."""
    if data[:4]!=b'RIFF' or data[8:12]!=b'WAVE':raise ValueError('generated WAVE required')
    at=12;fmt=None;payload=None
    while at+8<=len(data):
        tag=data[at:at+4];size=int.from_bytes(data[at+4:at+8],'little');body=data[at+8:at+8+size]
        if len(body)!=size:raise ValueError('truncated generated WAVE')
        if tag==b'fmt ':fmt=body
        if tag==b'data':payload=body
        at+=8+size+(size%2)
    code,ch,rate,_,_,bits=struct.unpack_from('<HHIIHH',fmt)
    if code==0xfffe:code=int.from_bytes(fmt[24:28],'little')
    if code==3:x=np.frombuffer(payload,dtype='<f%d'%(bits//8)).astype(float)
    elif code==1:
        width=bits//8
        x=np.array([int.from_bytes(payload[i:i+width],'little',signed=bits!=8) for i in range(0,len(payload),width)],float)
        if bits==8:x-=128
        x/=2**(bits-1)
    else:raise ValueError('unsupported generated PCM tag')
    return x.reshape(-1,ch),rate
