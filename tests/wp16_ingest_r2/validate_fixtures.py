"""Authoring decoder crosscheck: exact lossless samples and declared raw counts.
Not candidate acceptance and not a universal lossy waveform golden.
"""
import argparse, concurrent.futures, json
from pathlib import Path
import numpy as np
import fixtures, model

def run(root):
    root=Path(root);facts=json.loads((root/'SOURCES.json').read_text())
    def check(item):
        name,f=item;data=(root/f['path']).read_bytes();assert model.digest(data)==f['sha256'],name
        if f.get('ruling_required'):return {'asset':name,'check':'PENDING_CONTRACT_RULING','finding':f['ruling_required']}
        if f.get('family')=='large-boundary':return {'asset':name,'check':'exact-sparse-PCM-size/hash','frames':f['raw_frames']}
        if f.get('refuse'):return {'asset':name,'check':'hash-only-refusal-fixture'}
        if name.startswith(('zero-192','positive-192','tie-88200')):pass
        x=fixtures.decode(root/f['path'],f['input_channels'],manual=True,ignore_edit=f['container']=='bmff')
        assert len(x)==f['raw_frames'],(name,len(x),f['raw_frames'])
        if f.get('lossy'):return {'asset':name,'check':'raw-count','frames':len(x)}
        if f.get('family'):return {'asset':name,'check':'finite-and-count','frames':len(x)}
        y=fixtures.signal(f['input_rate'],256,f['input_channels'])
        if f['codec']=='pcm' or f['codec']=='flac':y=np.rint(y*2**(f['bits']-1))/2**(f['bits']-1)
        elif f['bits']==32:y=y.astype('f4').astype('f8')
        assert np.array_equal(x,y),(name,float(np.max(abs(x-y))))
        return {'asset':name,'check':'exact-lossless-samples','frames':len(x)}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:return list(pool.map(check,sorted(facts.items())))
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('root');ap.add_argument('--out',required=True);a=ap.parse_args()
    rows=run(a.root);Path(a.out).write_text(json.dumps(rows,indent=2)+'\n');print(len(rows),'fixture hashes/counts checked')
