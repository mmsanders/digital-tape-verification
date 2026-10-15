"""Independent INGEST-1 observation predicates. No Product imports/execution."""
import argparse, json, math
from pathlib import Path
import numpy as np
import model as m
import numerics as n

class Failure(AssertionError):
    def __init__(self,gate,detail):self.gate=gate;super().__init__(gate+': '+detail)
def require(ok,gate,detail):
    if not ok:raise Failure(gate,detail)
def close(a,b,tol,gate):
    require((a is None and b is None) or (a is not None and b is not None and abs(float(a)-float(b))<=tol),gate,str((a,b)))
def metric(value):return None if value is None else float(value)

def audio(before,pcm,metadata,*,original=None,mono=False,exact=False):
    """before is observed isolated floating SRC, corroborated by source/quality gates.

    The44100 lossless path uses independent decoded originals, not this observation.
    Six-decimal gain uncertainty is explicitly propagated, never a waveform hash.
    """
    x=np.asarray(before,float);q=np.frombuffer(pcm,dtype='<i2').reshape(-1,2).astype(float)/32768
    require(x.shape==q.shape and np.isfinite(x).all(),'count','isolated input/output dimensions')
    if original is not None:require(np.array_equal(x,original),'conversion','44100 lossless must preserve samples')
    silence=not np.any(x)
    g=metric(metadata['applied_gain_db']);require(g is not None and math.isfinite(g),'gain','finite constant required')
    il=n.loudness(x);ip=n.peak(x);ol=n.loudness(q);op=n.peak(q)
    close(metadata['input_lufs'],il,.1,'meter');close(metadata['input_dbtp'],ip,.1,'meter')
    close(metadata['output_lufs'],ol,.1,'meter');close(metadata['output_dbtp'],op,.1,'meter')
    if silence:
        require(pcm==bytes(len(pcm)) and g==0 and metadata['loudness_status']=='digital_silence' and all(metadata[k] is None for k in ('input_lufs','input_dbtp','output_lufs','output_dbtp')),'silence','whole silence bypass')
        require(metadata['loudness_reason'] is None and not metadata['peak_limited'],'status','silence status')
        return
    require(ip is not None and op is not None,'peak','nonzero requires peak')
    require(op+.1<=-1+1e-6 and float(metadata['output_dbtp'])+.1<=-1+1e-9,'peak','source ceiling/guard')
    ideal=x*10**(g/20)
    uncertainty=np.abs(ideal)*math.expm1(math.log(10)*.00000051/20)
    require(np.all(np.abs(q-ideal)<=1.500001/32768+uncertainty),'constant-gain','PCM not one scalar plus issued TPDF/rounding')
    if mono:require(np.array_equal(q[:,0],q[:,1]),'mono','L/R differ')
    if exact:require(pcm==m.quantize(x,mono=mono),'dither','gain0 dyadic exact xorshift/draw/rounding')
    target=None if il is None else -16-il
    close(metadata['target_gain_db'],target,.000002,'gain')
    start=min(0,-1-ip-.1) if il is None else min(target,-1-ip-.1)
    require(g<=start+.000002,'gain','unlicensed boost/ceiling gain')
    if il is None:
        # Quantization correction may reduce gain very slightly for final ceiling.
        require(abs(g-start)<=.02,'gain','unmeasurable arbitrary attenuation')
    if ol is None:
        require(metadata['loudness_status']=='unmeasurable' and metadata['loudness_reason']==('too_short' if len(x)<17640 else 'gated_out'),'status','undefined loudness reason')
    else:
        require(metadata['loudness_status']=='measured' and metadata['loudness_reason'] is None,'status','finite loudness reason')
        if il is not None and abs(ol+16)>.5:
            require(g<target and op>=-1.13 and metadata['peak_limited'],'target','unjustified under-normalization')
    limited=target is not None and g<target-.000002
    require(metadata['peak_limited']==limited,'status','peak_limited disagrees with gain')

def quality(before,rate,frequency,amplitude,window=4410):
    x=np.asarray(before,float);require(len(x)>2*window,'src-quality','empty steady-state interval')
    t=np.arange(window,len(x)-window)/44100
    folded=abs((frequency+22050)%44100-22050)
    basis=np.stack((np.sin(2*np.pi*folded*t),np.cos(2*np.pi*folded*t)),axis=1)
    fit=np.linalg.lstsq(basis,x[window:-window],rcond=None)[0]
    response=20*np.log10(np.maximum(np.linalg.norm(fit,axis=0)/amplitude,1e-300))
    if frequency<=min(18000,.4*rate):require(np.all(abs(response)<=.1),'src-quality','passband '+str(response))
    if 22050<=frequency<rate/2:require(np.all(response<=-80),'src-quality','alias '+str(response))
    return response.tolist()

def joined(pcm):
    x=np.frombuffer(pcm,dtype='<i2').reshape(-1,2).astype(float)/32768
    p=n.peak(x);require(p is None or p+.1<=-1+1e-6,'join-peak','unsafe concatenated boundary')

def identity(standalone,batch,repeat):
    require(standalone==batch==repeat,'identity','per-source isolated/batch/repeat differ')

def transaction(record):
    """Normalized native evidence facts; raw trace binding/coverage audited separately.
    Events strictly ordered; sequence gaps/truncation cannot establish absence.
    """
    events=record['events'];names=[e['op'] for e in events]
    require(record['complete'] and record['raw_trace_sha256'] and record['observer_selftest'],'trace','incomplete/unqualified observer')
    require([e['seq'] for e in events]==list(range(len(events))),'trace','event sequence gap')
    require('device_open' not in names and 'preflight_disk_scratch' not in names,'io-scope','device/scratch open')
    scenario=record['scenario'];exit_=record['exit']
    staging=[i for i,k in enumerate(names) if k in ('stage_create','output_open')]
    if scenario=='preflight-refusal':
        require(exit_==2 and not staging and not record['dest_after'] and not record['owned_stage_after'],'preflight','output opened before refusal')
        require(record['diagnostic_ok'],'diagnostic','named plain refusal/overage')
    elif scenario in ('success','concurrent-dest','write-error','kill'):
        require('preflight_complete' in names and 'sources_revalidated' in names,'mutation','source identities not revalidated')
        require(not staging or names.index('preflight_complete')<min(staging),'preflight','stage before complete preflight')
        if scenario=='success':
            require(exit_==0 and record['dest_after']==['audio.wav','manifest.json'] and not record['owned_stage_after'],'pair','missing/extra output or leftover stage')
            require(names.count('publish_dir_noreplace')==1 and 'publish_file' not in names,'pair','publication not one no-replace directory boundary')
            at=names.index('publish_dir_noreplace')
            require(all(names.count(op)==1 and names.index(op)<at for op in ('audio_flush_close','manifest_flush_close')),'pair','files not closed/flushed before publish')
            require(all(e.get('exclusive') and e.get('adjacent') for e in events if e['op']=='stage_create') and names.count('stage_create')==1,'pair','stage not exclusive/adjacent')
        elif scenario=='concurrent-dest':
            require(exit_ in (1,2) and record['competitor_unchanged'] and not record['owned_stage_after'] and 'publish_dir_noreplace' not in names,'pair','concurrent DEST overwritten')
        elif scenario=='write-error':
            require(exit_==1 and not record['dest_after'] and not record['owned_stage_after'] and record['unrelated_unchanged'],'cleanup','ordinary error cleanup')
        else:require((record['dest_after']==['audio.wav','manifest.json'] if 'publish_dir_noreplace' in names else not record['dest_after']) and record['unrelated_unchanged'],'pair','kill left partially published DEST')
    elif scenario=='mutation':
        require(exit_==2 and 'source_mutation_detected' in names and not record['dest_after'],'mutation','mixed source versions')
        require(not record['owned_stage_after'],'cleanup','mutation stage not removed')
    else:raise Failure('trace','unknown scenario')
    require(record['raw_review']=='PASS','trace','native raw trace review required; normalized self-report insufficient')


def manifest(raw,pcm,facts,folders,seconds):
    try:return m.check_manifest(raw,pcm,facts,folders,seconds)
    except (AssertionError,ValueError,KeyError,TypeError) as e:raise Failure('manifest',str(e)) from e

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('observation',type=Path);a=ap.parse_args()
    transaction(json.loads(a.observation.read_text()));print('Native normalized predicates PASS; require bound raw trace review')
