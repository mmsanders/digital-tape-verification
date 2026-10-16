"""Bounded evidence inspection; NO receipts, candidate execution or acceptance.

Usage: python3 -B inspect_return.py ZIP_DIRECTORY --sources SOURCES.json --out REPORT
Reads authenticated ZIPs without extracting multi-GiB WAVs. Uses the original
independently published package predicates; never imports Product code.
"""
import argparse,collections,hashlib,json,struct,sys,zipfile
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tests/wp16_ingest_stage1'))
import cases,filter_bounds,model,qualification

HEAD='92a5eb809a282bcae7330b44c12059a1166cdcd7'
PACKS={
 'linux':(12026439092,148196277,'10f4f2a64726f35b425e6992f482fbbe862f0455981ea50496323eecde25f92d'),
 'mac':(12029137547,153061970,'a0b9aec7b5f6a98bd4e4234699b732d38f5c15521444dd745a9efd0c5114cb30'),
 'windows-server':(12027701356,208588468,'52d917b2d213f2d5aec19a240982d30db6e5299b3713ad12a1feaad3be98751f'),
}

def digest_file(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        while block:=f.read(1024*1024):h.update(block)
    return h.hexdigest()

def run(root,sources):
    assert digest_file(sources)=='19b8a56f67a4a4a0d0a63e63635d7d64c6835b2eb4620a23ade5a33be17f41ea'
    facts=json.loads(sources.read_text(encoding='utf-8'));catalog={c['id']:c for c in cases.expand(facts)}
    reports={};outputs={}
    for label,(artifact,size,sha) in PACKS.items():
        path=root/(label+'.zip');assert path.stat().st_size==size and digest_file(path)==sha,label
        with zipfile.ZipFile(path) as z:
            idx=json.loads(z.read('INDEX.json'));assert idx['candidate_sha']==HEAD and idx['profile']=='INGEST1-AP4'
            assert set(idx['cases'])==set(catalog)
            exits=collections.Counter();observers=collections.Counter();unavailable={};out={};bytes_read=0;calibration=[];incomplete={};controls={};normalized_failures={}
            for id,member in idx['cases'].items():
                r=json.loads(z.read(member));exits[str(r['exit'])]+=1
                native=json.loads(z.read(r['native_record']));observers[native.get('observer')]+=1
                assert model.digest(z.read(r['raw_trace']))==native['raw_trace_sha256'],(label,id,'trace hash')
                if not native['complete']:incomplete[id]=native.get('integrity')
                checked=dict(native,raw_review='PASS') # predicate diagnostic only; NOT a raw-review receipt
                import audit
                try:audit.transaction(checked)
                except Exception as e:normalized_failures[id]=str(e)
                if 'unavailable' in r:
                    unavailable[id]=r['unavailable'];continue
                expected=catalog[id]['expected_exit'];code=r['exit']
                assert expected is None or code==expected or isinstance(expected,list) and code in expected,(label,id,'exit')
                if 'wav' not in r:continue
                raw=z.read(r['manifest']);m=json.loads(raw);frames=m['total_frames'];info=z.getinfo(r['wav'])
                assert raw==model.canonical(m),(label,id,'canonical manifest')
                h=hashlib.sha256()
                with z.open(r['wav']) as f:
                    first=f.read(44);h.update(first)
                    assert first==struct.pack('<4sI4s4sIHHIIHH4sI',b'RIFF',36+4*frames,b'WAVE',b'fmt ',16,1,2,44100,176400,4,16,b'data',4*frames),(label,id,'WAV header')
                    assert info.file_size==44+4*frames
                    while block:=f.read(1024*1024):
                        h.update(block)
                        if id=='capacity/riff-largest-legal':assert block==bytes(len(block)),(label,id,'nonzero silent payload')
                wav_sha=h.hexdigest();assert wav_sha==m['wav_sha256'],(label,id,'WAV hash binding')
                out[id]={'wav':wav_sha,'manifest':model.digest(raw)};bytes_read+=info.file_size
                if id.startswith('asset/qual-'):
                    fact=facts[id[6:]];qualification.check(fact,m['sources'][0]);calibration.append(id)
            config=z.read('config.json');platform=z.read(idx['platform_file'])
            assert model.digest(config)==idx['config_sha256']
            assert model.digest(platform)==idx['platform_sha256']
            st=json.loads(z.read('observer-selftest/result.json'))
            assert model.digest(z.read('observer-selftest/'+st['trace']))==st['trace_sha256']
            for k,v in st['false_pass_controls'].items():
                raw=z.read('observer-selftest/'+v['file']);assert model.digest(raw)==v['sha256']
                controls[k]={'raw_sha256':v['sha256'],'reported_rejected':v['rejected'],'raw_bytes':len(raw)}
            profile_raw=z.read(idx['profile_file']);profile=json.loads(profile_raw);bounds=[]
            if label=='linux':
                for rate,desc in profile['resamplers'].items():
                    coefficients=z.read(desc['coefficients_file'])
                    assert model.digest(coefficients)==desc['coefficients_sha256']
                    bounds.append(filter_bounds.certify(np.frombuffer(coefficients,dtype='<f8'),int(rate)))
            reports[label]={
                'artifact_id':artifact,'zip_sha256':sha,'zip_bytes':size,
                'index':{k:v for k,v in idx.items() if k!='cases'},
                'case_records':len(idx['cases']),'exit_counts':dict(exits),'observers':dict(observers),
                'unavailable':unavailable,'incomplete_native_records':incomplete,'normalized_predicate_failures_NO_receipts':normalized_failures,'control_hash_bindings':controls,'wav_manifest_pairs':len(out),'actual_wav_bytes_read':bytes_read,
                'output_inventory_sha256':model.digest(model.canonical(out)),
                'profile_sha256':model.digest(profile_raw),'independent_input_calibrations':len(calibration),
                'largest_legal_actual_zero_wav_bytes':z.getinfo(json.loads(z.read(idx['cases']['capacity/riff-largest-legal']))['wav']).file_size,
                'declared_FIR_continuous_band_certificates':bounds,
                'observer_selftest':json.loads(z.read('observer-selftest/result.json')),
            };outputs[label]=out
            print(label,len(out),'actual WAV/manifest pairs checked',flush=True)
    comparisons={}
    for label in ('mac','windows-server'):
        a,b=outputs['linux'],outputs[label]
        comparisons[label]={
            'missing':sorted(a.keys()-b.keys()),'extra':sorted(b.keys()-a.keys()),
            'different':sorted(id for id in a.keys()&b.keys() if a[id]!=b[id]),
        }
    return {'candidate':HEAD,'disposition':'HELD; bounded inspection, NO independent acceptance/receipts',
            'platforms':reports,'observed_output_identity':comparisons,
            'scope':'ZIP/census/exit/trace hash/header/canonical manifest/full WAV bytes/metadata binding/largest zero payload/cross-runner identity, thirty published input calibration points and declared FIR bounds only; no complete numeric/native/shipping equivalence disposition'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--sources',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    result=run(a.root,a.sources);a.out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(result['disposition'])
