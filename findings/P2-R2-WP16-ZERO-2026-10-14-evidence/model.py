"""Independently authored INGEST-1 structural arithmetic; no Product import."""
from decimal import Decimal, ROUND_HALF_EVEN
from pathlib import Path
import functools, hashlib, json, re, struct, unicodedata

RATE=44100
GAP=88200
SEED=0x6D2B79F5
RATES=(7350,8000,11025,12000,16000,22050,24000,32000,44100,48000,64000,88200,96000,176400,192000)
TOP=('schema','contract','tool_version','build_profile','libraries','resampler_profile','meter_profile','dither_profile','target_seconds','capacity_frames','total_frames','wav_sha256','folders','sources','gaps')
SOURCE=('logical_path','source_sha256','container','codec','codec_profile','input_rate','input_channels','raw_frames','trim_head','trim_tail','trim_evidence','effective_frames','output_frames','start_frame','input_lufs','input_dbtp','output_lufs','output_dbtp','target_gain_db','applied_gain_db','peak_limited','loudness_status','loudness_reason','gapless_status')

def digest(data): return hashlib.sha256(data).hexdigest()
def output_frames(n,r):
    assert isinstance(n,int) and n>=0 and r in RATES
    return (n*RATE+r//2)//r
def overage(total,seconds):
    assert seconds>0
    e=max(0,total-seconds*RATE);s=(e+RATE-1)//RATE
    return e,'%02d:%02d'%divmod(s,60)
def fixed(value):
    if value is None: return None
    q=Decimal(str(value)).quantize(Decimal('.000001'),rounding=ROUND_HALF_EVEN)
    if q==0:q=abs(q)
    return format(q,'.6f')
def canonical(obj):
    return (json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)+'\n').encode('utf-8')
def draw(s):
    s=(s ^ ((s<<13)&0xffffffff))&0xffffffff
    s=(s ^ (s>>17))&0xffffffff
    s=(s ^ ((s<<5)&0xffffffff))&0xffffffff
    return s,(s+0.5)/4294967296
def quantize(rows,mono=False,silence=False,seed=SEED):
    out=bytearray();s=seed
    for row in rows:
        if silence:
            out.extend(bytes(4));continue
        vals=[]
        for x in row[:1] if mono else row:
            s,a=draw(s);s,b=draw(s)
            q=round(32768*float(x)+a-b)
            if not -32768<=q<=32767:raise OverflowError('quantizer overflow')
            vals.append(q)
        if mono: vals*=2
        if len(vals)!=2:raise ValueError('stereo output required')
        out.extend(struct.pack('<hh',*vals))
    return bytes(out)
def wav(pcm):
    assert len(pcm)%4==0 and len(pcm)+36<=0xffffffff
    return struct.pack('<4sI4s4sIHHIIHH4sI',b'RIFF',len(pcm)+36,b'WAVE',b'fmt ',16,1,2,RATE,176400,4,16,b'data',len(pcm))+pcm
def pcm_from_wav(data):
    assert len(data)>=44 and data[:44]==wav(data[44:])[:44],'noncanonical WAV'
    return data[44:]

