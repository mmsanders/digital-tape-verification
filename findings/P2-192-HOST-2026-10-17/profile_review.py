"""Library/profile/metadata identity receipt; no Product imports or execution.

The fixed-tree library hash recipe is publicly declared by build.rs. Audio
expectations remain the independently published Stage1 predicates.
"""
import argparse,hashlib,json,struct,tomllib,zipfile
from pathlib import Path

def sha(b):return hashlib.sha256(b).hexdigest()
def tree(root):
    h=hashlib.sha256()
    for p in sorted((p for p in root.rglob('*') if p.is_file()),key=lambda p:p.relative_to(root).as_posix()):
        data=p.read_bytes();h.update(p.relative_to(root).as_posix().encode()+b'\0'+struct.pack('<Q',len(data))+data)
    return h.hexdigest()

def run(source,packet,kit):
    crate=source/'host/ingest';lock=(crate/'Cargo.lock').read_bytes();pkgs=tomllib.loads(lock.decode())['package'];byname={p['name']:p for p in pkgs}
    with zipfile.ZipFile(packet) as z:
        idx=json.loads(z.read('INDEX.json'));config=json.loads(z.read('config.json'));r=json.loads(z.read(idx['cases']['asset/ordinary.wav']));m=json.loads(z.read(r['manifest']))
        assert sha(lock)==config['cargo_lock_sha256'];rows=[]
        for lib in m['libraries']:
            p=byname[lib['name']];assert p['version']==lib['version']
            if lib['source']=='crates.io':actual=p['checksum']
            else:
                assert lib['source']=='vendored-patched' and 'checksum' not in p;actual=tree(crate/'vendor'/lib['name'])
            assert actual==lib['sha256'];rows.append({'library':lib['name'],'version':lib['version'],'sha256':actual,'source':lib['source']})
        profile=z.read(idx['profile_file']);p=json.loads(profile)
        assert all(m[k]==p[pk] for k,pk in [('resampler_profile','resampler'),('meter_profile','meter'),('dither_profile','dither')])
        assert m['build_profile']==p['profile']=='INGEST1-AP4'
        fullfiles=['src/dsp.rs','src/convert.rs','src/main.rs','src/observe.rs','src/publish.rs','src/manifest.rs','build.rs','Cargo.toml','Cargo.lock']
        reviewed={n:sha((crate/n).read_bytes()) for n in fullfiles}
    with zipfile.ZipFile(kit) as z:
        shipping=z.read('ingest.exe');observe=z.read('observe/ingest.exe')
        markers=[b'INGEST_OBSERVE_DIR',b'INGEST_KILL_AT',b'INGEST_FAULT',b'INGEST_PAUSE_AT',b'INGEST_PAUSE_FILE',b'INGEST_HEAP_LIMIT',b'INGEST_OBSERVE_PROBE',b'injected test fault',b'events.jsonl']
        assert not any(x in shipping for x in markers) and all(x in observe for x in markers)
        assert sha(shipping)=='0e1ef2cb4f283eb876f08019222da5d3ac744ec30d49f020a2e87323f31bcac1'
        assert sha(observe)=='97918d4315955d54894918a24d98f7c8e2fdf3d0568634613f77cf4af1f0eaa6'
    return {'candidate':idx['candidate_sha'],'config_sha256':idx['config_sha256'],'profile_sha256':sha(profile),'libraries':rows,'reviewed_source_sha256':reviewed,'windows_shipping_seam_absence':{'shipping_sha256':sha(shipping),'observe_sha256':sha(observe),'positive_and_real_negative_control':'shipping contains none; observation executable contains every marker'},'manual_review_scope':'After complete independent Stage1 authoring: fixed scalar FIR/count/EBU/true-peak/refinement and per-source PRNG paths agree with declared profile; cfg-disabled shipping seam is no-op, test allocator/probes gated to observe; separate math replay checks actual observations. No engine inspection. No claim of shipping exhaustion from observation allocator cap.'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('packet',type=Path);p.add_argument('kit',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args();r=run(a.source,a.packet,a.kit);a.out.write_text(json.dumps(r,indent=2)+'\n');print('libraries',len(r['libraries']),'profile and exact Windows seam controls PASS')
