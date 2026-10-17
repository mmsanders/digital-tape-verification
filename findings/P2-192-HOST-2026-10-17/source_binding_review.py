"""Source byte/logical-path identity proof from existing evidence, not inode policy.

Authority contract §7 defines identity by exact bytes and normalized logical path.
Combine actual native open/milestone ordering, independently checked source/output
math, immutable manifest source hashes and the covered hash-comparison pipeline.
No new telemetry requirement is inferred from absent native read payloads.
"""
import argparse,collections,csv,hashlib,importlib.util,io,json,re,sys,unicodedata,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('mac_raw',ROOT/'findings/P2-R2-WP16-RETURN-R3-2026-10-16/mac_native.py');MAC=importlib.util.module_from_spec(spec);spec.loader.exec_module(MAC)

def c_string(s):
    data=bytearray();i=0
    while i<len(s):
        if s[i]!='\\':data.extend(s[i].encode());i+=1;continue
        i+=1
        if s[i] in '01234567':
            m=re.match('[0-7]{1,3}',s[i:]);data.append(int(m[0],8));i+=len(m[0])
        elif s[i]=='x':data.append(int(s[i+1:i+3],16));i+=3
        else:data.extend({'n':b'\n','r':b'\r','t':b'\t','v':b'\v','f':b'\f','b':b'\b','a':b'\a','\\':b'\\','"':b'"'}.get(s[i],s[i].encode()));i+=1
    return data.decode('utf-8')

def norm(s,windows=False):
    s=unicodedata.normalize('NFC',s)
    return re.sub(r'[\\/]+','/',s).casefold() if windows else s

def native(raw,label):
    opened=collections.defaultdict(list);pre=[];revalidated=[]
    if label=='linux':
        for i,l in enumerate(raw.decode().splitlines()):
            if '/.mark/' in l and '-preflight_complete"' in l:pre.append(i)
            if '/.mark/' in l and '-sources_revalidated"' in l:revalidated.append(i)
            if 'openat(' in l and 'O_RDONLY' in l and re.search(r'= \d+<',l):
                m=re.search(r'"((?:\\.|[^"\\])*)"',l)
                if m:opened[norm(c_string(m[1]))].append(i)
    elif label=='mac':
        rows,checks=MAC.parse(raw,('ingest',));assert all(checks.values())
        for i,e in enumerate(rows):
            if e['tag']!='R':continue
            path=e['src'].decode()
            if '/.mark/' in path and path.endswith('-preflight_complete'):pre.append(i)
            if '/.mark/' in path and path.endswith('-sources_revalidated'):revalidated.append(i)
            if e['call'].startswith('open') and e['ret']>=0:opened[norm(path)].append(i)
    else:
        for i,e in enumerate(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'),newline=''))):
            path=norm(e['Path'],True)
            if '/.mark/' in path and path.endswith('-preflight_complete'):pre.append(i)
            if '/.mark/' in path and path.endswith('-sources_revalidated'):revalidated.append(i)
            if e['Operation']=='CreateFile' and e['Result']=='SUCCESS' and 'Generic Read' in e['Detail']:opened[path].append(i)
    return opened,pre,revalidated

def run(root):
    out={'scope':'Source byte/logical-path binding on submitted successful/after-publish observations plus actual mutation refusals, using reviewed compiled three-read/hash pipeline. Not an unissued inode-equality or raw-payload criterion.','platforms':{}}
    for label in ('linux','mac','windows-server'):
        counts=collections.Counter();mutations={};proofs={};failures={}
        with zipfile.ZipFile(root/(label+'.zip')) as z:
            index=json.loads(z.read('INDEX.json'))
            for id,p in index['cases'].items():
                r=json.loads(z.read(p));n=json.loads(z.read(r['native_record']))
                if 'wav' not in r and n['scenario']!='mutation':continue
                raw=z.read(r['raw_trace']);assert hashlib.sha256(raw).hexdigest()==n['raw_trace_sha256']
                if n['scenario']=='mutation':
                    err=z.read(r['stderr_file']).decode(r.get('stderr_encoding','utf-8'))
                    assert r['exit']==2 and 'file changed' in err.lower() and not n['dest_after'] and not n['owned_stage_after']
                    mutations[id]={'exit':2,'raw_trace_sha256':n['raw_trace_sha256'],'no_published_or_owned_stage':True};continue
                m=json.loads(z.read(r['manifest']));opened,pre,revalidated=native(raw,label)
                try:
                    assert pre and revalidated and max(pre)<min(revalidated),(id,'milestone order',pre,revalidated)
                    argv=n['argv'];folders=argv[argv.index('--length')+2:]
                    for s in m['sources']:
                        ordinal,name=s['logical_path'].split('/',1)
                        path=norm(folders[int(ordinal)].rstrip('/\\')+'/'+name,label=='windows-server')
                        at=opened[path]
                        assert len(at)==3 and at[0]<at[1]<min(pre)<=max(pre)<at[2]<min(revalidated),(id,s['logical_path'],len(at),at,pre,revalidated)
                        assert len(s['source_sha256'])==64
                        counts['bound_source_instances']+=1
                    counts['bound_output_cases']+=1
                    proofs[id]=hashlib.sha256(json.dumps([(s['logical_path'],s['source_sha256']) for s in m['sources']],separators=(',',':')).encode()).hexdigest()
                except AssertionError as e:failures[id]=str(e)
            assert mutations
        out['platforms'][label]={'counts':dict(counts),'mutations':mutations,'failures':failures,'source_binding_census_sha256':hashlib.sha256(json.dumps(proofs,sort_keys=True,separators=(',',':')).encode()).hexdigest()}
        print(label,dict(counts),'gaps',len(failures),flush=True)
    return out

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args();r=run(a.root);a.out.write_text(json.dumps(r,indent=2)+'\n')
