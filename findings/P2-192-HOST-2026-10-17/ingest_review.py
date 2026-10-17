"""Available offline host receipts, using only frozen Verification predicates.

No Product import/execution and no fabricated blanket receipts. Records each
completed property and every error; native receipt gaps stay separate. Exact
identical math observations on another submitted runner inherit only math facts.
"""
import argparse,collections,functools,hashlib,json,math,re,sys,unicodedata,zipfile
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tests/wp16_ingest_stage1'))
import audit,asset,cases,conversion,model,qualification,relations
PACKS={'linux':'819fb79989978d666132952945a3ac53772d3ed40efbafd6abbcb58a2dc5496c','mac':'abd4e2b328540978eeaf330ee8c4ed002f885ffaab33aa6b0a5794db348ad8bc','windows-server':'70bcbe2043bbf07555b8c0a83a2b041f1de3e11e69464acf3eaff1303ca6d774'}

def run(root,sources,out):
    facts=json.loads((sources/'SOURCES.json').read_text());assert asset.sha_file(sources/'SOURCES.json')=='19b8a56f67a4a4a0d0a63e63635d7d64c6835b2eb4620a23ade5a33be17f41ea'
    catalog={c['id']:c for c in cases.expand(facts)}
    prior=json.loads((ROOT/'findings/P2-R2-WP16-RETURN-R3-2026-10-16/observations.json').read_text())
    result={'candidate':'6126d04050133cacb9a1960a0bc13c9ee93130e5','profile':'INGEST1-AP4','property_counts':{},'failures':{},'evidence':{},'platforms':{},'scope':'Offline property-specific review; not full native/shipping/meter-math receipts or overall acceptance.'}
    done=collections.Counter();fail={};observations={};outputs={};math_cache={}
    @functools.lru_cache(16)
    def decoded(a):return conversion.decoded(sources,facts[a])
    @functools.lru_cache(32)
    def expected(a):
        f=facts[a];x=decoded(a)
        return x if f['input_rate']==44100 else conversion.fir(x,f['input_rate'],filters[str(f['input_rate'])])
    def attempt(key,fn):
        try:fn();done[key.split(':',1)[0]]+=1;return True
        except Exception as e:fail[key]={'type':type(e).__name__,'error':str(e)};return False
    def save():
        result['property_counts']=dict(done);result['failures']=fail;result['math_case_results']=observations
        out.write_text(json.dumps(result,separators=(',',':'))+'\n')
    for label,want in PACKS.items():
        zp=root/(label+'.zip');assert asset.sha_file(zp)==want
        with zipfile.ZipFile(zp) as z:
            idx=json.loads(z.read('INDEX.json'));assert idx['candidate_sha']==result['candidate'] and idx['profile']==result['profile']
            assert set(idx['cases'])==set(catalog)
            profile=json.loads(z.read(idx['profile_file']));profile_sha=model.digest(z.read(idx['profile_file']))
            result['platforms'][label]={'zip_sha256':want,'platform':idx['platform'],'config_sha256':idx['config_sha256'],'binary_sha256':idx['binary_sha256'],'shipping_binary_sha256':idx['shipping_binary_sha256'],'profile_sha256':profile_sha,'equal_math_cases':0,'different_math_cases':0,'summary_counts':0,'comparisons':0,'shipping_claims_bound_to_observe':0}
            filters={}
            for rate,d in profile['resamplers'].items():
                b=z.read(d['coefficients_file']);assert model.digest(b)==d['coefficients_sha256']
                filters[rate]=dict(d,coefficients=np.frombuffer(b,dtype='<f8'))
            if label=='linux':
                assert len(prior['platforms']['linux']['declared_FIR_continuous_band_certificates'])==14
                result['carried_FIR_certificates']={'count':14,'basis':'same authenticated ZIP/profile/coefficient bytes as PR190; existing independent continuous-band certificates, no repeated calculation'}
            for id,member in idx['cases'].items():
                c=catalog[id];r=json.loads(z.read(member));n=json.loads(z.read(r['native_record']));code=r['exit']
                assert r['config_sha256']==idx['config_sha256'] and model.digest(z.read(r['raw_trace']))==n['raw_trace_sha256']
                stdout=z.read(r['stdout_file']).decode(r.get('stdout_encoding','utf-8'));stderr=unicodedata.normalize('NFC',z.read(r['stderr_file']).decode(r.get('stderr_encoding','utf-8')))
                if code==2:
                    def refusal():
                        assert stderr.strip()
                        if id.startswith(('asset/','adr180/neighbour/')) or id=='trim/outside-neighbour':
                            bad=[e for f in c['folders'] for e in f if facts[e['asset']].get('refuse')]
                            if not bad:bad=[e for f in c['folders'] for e in f]
                            assert any(e['name'] in stderr for e in bad),'source name missing'
                        if id.startswith('zero/') or id in ('asset/zero-192-n1.wav','asset/zero-192-n2.wav'):assert 'too short' in stderr.lower()
                        if id in ('capacity/one-over','capacity/gap-one-over'):assert '1' in stderr and '00:01' in stderr
                    attempt('refusal:'+label+':'+id,refusal)
                if 'wav' not in r:continue
                mraw=z.read(r['manifest']);m=json.loads(mraw)
                count={'peak_limited':sum(s['peak_limited'] for s in m['sources']),'unmeasurable':sum(s['loudness_status']=='unmeasurable' for s in m['sources']),'gapless_unknown':sum(s['gapless_status']=='gapless_unknown' for s in m['sources'])}
                assert r['summary']==count
                # Actual stdout, not the separately asserted summary object.
                def summary():
                    for key,v in count.items():
                        values=re.findall(r'\b'+re.escape(key.replace('_','-'))+r'\s+(\d+)\b',stdout)
                        assert values==[str(v)],(label,id,'actual stdout count',key,values)
                if attempt('summary:'+label+':'+id,summary):result['platforms'][label]['summary_counts']+=1
                eq=r.get('shipping_equivalence')
                if eq:
                    assert eq['shipping_binary_sha256']==idx['shipping_binary_sha256'] and eq['exit']==0
                    for name,data in (('audio.wav',None),('manifest.json',mraw)):
                        h=m['wav_sha256'] if name=='audio.wav' else model.digest(data)
                        assert eq[name]['observe_sha256']==eq[name]['shipping_sha256']==h
                    result['platforms'][label]['shipping_claims_bound_to_observe']+=1
                if id=='capacity/riff-largest-legal':continue # exact full payload/header/manifest already authenticated in PR190
                if r.get('comparisons'):
                    base_output=(mraw,model.pcm_from_wav(z.read(r['wav'])))
                    for num,o in enumerate(r['comparisons']):
                        other=(z.read(o['manifest']),model.pcm_from_wav(z.read(o['wav'])))
                        native=json.loads(z.read(o['native_record']));assert native['raw_trace_sha256']==model.digest(z.read(o['raw_trace']))
                        if o['mode']=='standalone-versus-batch':attempt('comparison:'+label+':'+id+':'+str(num),lambda:relations.standalone(other,[base_output]))
                        else:attempt('comparison:'+label+':'+id+':'+str(num),lambda:relations.pair(base_output,other,o['mode']))
                        result['platforms'][label]['comparisons']+=1
                before_hashes=[model.digest(z.read(p)) for p in r['before']]
                math_identity=(model.digest(mraw),m['wav_sha256'],tuple(before_hashes),profile_sha,r['joined_dbtp'])
                if label!='linux' and math_identity==math_cache.get(id):
                    result['platforms'][label]['equal_math_cases']+=1;continue
                if label!='linux':result['platforms'][label]['different_math_cases']+=1
                else:math_cache[id]=math_identity
                pcm=model.pcm_from_wav(z.read(r['wav']));outputs[id]=(mraw,pcm)
                ordered=[];names=[]
                for f in c['folders']:
                    g=sorted(f,key=lambda e:model.name_key(e['name']));names.append([e['name'] for e in g]);ordered+=g
                fs=[dict(facts[e['asset']],source_sha256=facts[e['asset']]['sha256']) for e in ordered]
                manifest_ok=attempt('manifest:'+label+':'+id,lambda:audit.manifest(mraw,pcm,fs,names,c['seconds']))
                observations[label+':'+id]={'record':model.digest(z.read(member)),'manifest':model.digest(mraw),'pcm':model.digest(pcm),'before':before_hashes,'checks':[]}
                checks=observations[label+':'+id]['checks']
                if manifest_ok:checks.append('manifest')
                for pos,(e,f,s) in enumerate(zip(ordered,fs,m['sources'])):
                    a=e['asset'];b=np.frombuffer(z.read(r['before'][pos]),dtype='<f8').reshape(-1,2)
                    try:
                        assert asset.sha_file(sources/f['path'])==f['sha256'];x=decoded(a);y=expected(a)
                    except Exception as error:
                        fail['decode:'+label+':'+id+':'+str(pos)]={'type':type(error).__name__,'error':str(error)};continue
                    if attempt('conversion:'+label+':'+id+':'+str(pos),lambda:conversion.compare(b,y,bool(f.get('lossy')),source_scale=float(np.max(abs(x),initial=0)))):checks.append('conversion:'+str(pos))
                    chunk=pcm[4*s['start_frame']:4*(s['start_frame']+s['output_frames'])]
                    if attempt('audio:'+label+':'+id+':'+str(pos),lambda:audit.audio(b,chunk,s,original=x if f['input_rate']==44100 and not f.get('lossy') else None,mono=f['input_channels']==1,exact=a.startswith('dither-'),digital_source=not np.any(x))):checks.append('audio:'+str(pos))
                    if f.get('family')=='endpoint':attempt('latency:'+label+':'+id+':'+str(pos),lambda:audit.latency(b,x,f['input_rate']))
                    if f.get('family')=='src-quality':attempt('quality:'+label+':'+id+':'+str(pos),lambda:audit.quality(b,f['input_rate'],f['frequency'],f['amplitude'],f['window_output_frames']))
                    attempt('qualification:'+label+':'+id+':'+str(pos),lambda:qualification.check(f,s))
                if attempt('joined:'+label+':'+id,lambda:audit.joined(pcm,r['joined_dbtp'])):checks.append('joined')
                attempt('repeated-sources:'+label+':'+id,lambda:relations.repeated_sources(mraw,pcm))
                if len(observations)%25==0:save();print(label,id,'checked',len(observations),'errors',len(fail),flush=True)
            if label=='linux':
                for id in ('joins/sources','joins/folder-gaps','trim/repeated-mp3','trim/repeated-bmff'):
                    c=catalog[id];individual=[outputs['asset/'+e['asset']] for f in c['folders'] for e in f]
                    attempt('standalone:'+id,lambda:relations.standalone(outputs[id],individual))
            save()
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--sources',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();r=run(a.root,a.sources,a.out);print('completed',r['property_counts'],'failures',len(r['failures']))
