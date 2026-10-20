"""Independent native publication/flush proof and Windows global-CSV reconciliation.

No Product parser import. Does not issue blanket native absence/source-pass receipts.
Never prints or retains Process Start environment blocks in its result.
"""
import argparse,collections,csv,gzip,hashlib,io,json,re,tempfile,zipfile
from pathlib import Path

def digest(b):return hashlib.sha256(b).hexdigest()
def canonical_row(e):return json.dumps(e,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def norm(s):return re.sub(r'[\\/]+','/',s).casefold()

def linux_proof(raw,n):
    lines=raw.decode().splitlines();publications=[]
    for i,l in enumerate(lines):
        if 'renameat2(' not in l or not l.rstrip().endswith('= 0'):continue
        paths=re.findall(r'"([^"\\]*(?:\\.[^"\\]*)*)"',l)
        assert len(paths)==2 and 'RENAME_NOREPLACE' in l
        src,dest=paths;expected=n['argv'][n['argv'].index('--out')+1]
        assert dest==expected and src!=dest and '.ingest-stage-' in src.rsplit('/',1)[1] and src.rsplit('/',1)[0]==dest.rsplit('/',1)[0]
        for name in ('audio.wav','manifest.json'):
            path=src+'/'+name
            opens=[j for j,s in enumerate(lines[:i]) if 'openat(' in s and '"'+path+'"' in s and 'O_EXCL' in s and 'O_CREAT' in s and re.search(r'= \d+<',s)]
            flush=[j for j,s in enumerate(lines[:i]) if 'fsync(' in s and '<'+path+'>' in s and s.rstrip().endswith('= 0')]
            closes=[j for j,s in enumerate(lines[:i]) if 'close(' in s and '<'+path+'>' in s and s.rstrip().endswith('= 0')]
            assert opens and flush and closes and min(opens)<max(flush)<max(closes)<i
        assert any('mkdir("'+src+'"' in s and s.rstrip().endswith('= 0') for s in lines[:i])
        publications.append({'line':i,'source':src,'destination':dest,'no_replace':True})
    claimed=sum(e['op']=='publish_dir_noreplace' for e in n['events'])
    assert len(publications)==claimed
    return publications

def windows_proof(rows,n):
    pubs=[]
    for i,e in enumerate(rows):
        if e['Operation']!='SetRenameInformationFile' or e['Result']!='SUCCESS':continue
        src=norm(e['Path']);detail=e['Detail']
        assert 'ReplaceIfExists: False' in detail
        dest=norm(detail.split('FileName: ',1)[1]);expected=norm(n['argv'][n['argv'].index('--out')+1])
        assert dest==expected and src!=dest and '.ingest-stage-' in src.rsplit('/',1)[1] and src.rsplit('/',1)[0]==dest.rsplit('/',1)[0]
        creates=[j for j,x in enumerate(rows[:i]) if x['Operation']=='CreateFile' and x['Result']=='SUCCESS' and norm(x['Path'])==src and 'Disposition: Create,' in x['Detail'] and 'Options: Directory' in x['Detail']]
        assert creates
        for name in ('audio.wav','manifest.json'):
            path=src+'/'+name
            opens=[j for j,x in enumerate(rows[:i]) if x['Operation']=='CreateFile' and x['Result']=='SUCCESS' and norm(x['Path'])==path and 'Disposition: Create,' in x['Detail'] and 'Generic Write' in x['Detail']]
            flush=[j for j,x in enumerate(rows[:i]) if x['Operation']=='FlushBuffersFile' and x['Result']=='SUCCESS' and norm(x['Path'])==path]
            closes=[j for j,x in enumerate(rows[:i]) if x['Operation']=='CloseFile' and x['Result']=='SUCCESS' and norm(x['Path'])==path]
            assert opens and flush and closes and min(opens)<max(flush)<max(closes)<i
        pubs.append({'index':int(e['Index']),'source':src,'destination':dest,'no_replace':True})
    assert len(pubs)==sum(e['op']=='publish_dir_noreplace' for e in n['events'])
    return pubs

def run(root):
    result={'scope':'Actual native publication/flush-close properties and full Windows CSV row reconciliation only; full absence/source-per-pass/shipping-exhaustion receipts remain separate.','platforms':{}}
    for label in ('linux','windows-server'):
        with zipfile.ZipFile(root/(label+'.zip')) as z:
            index=json.loads(z.read('INDEX.json'));stats=collections.Counter();proofs={};global_rows={};seen=set()
            if label=='windows-server':
                with tempfile.TemporaryFile() as tmp:
                    h=hashlib.sha256()
                    with gzip.GzipFile(fileobj=z.open('observer-session/session.csv.gz')) as f:
                        while b:=f.read(1<<20):h.update(b);tmp.write(b)
                    assert h.hexdigest()==z.read('observer-session/session.csv.sha256').decode().strip()
                    tmp.seek(0);text=io.TextIOWrapper(tmp,encoding='utf-8-sig',newline='')
                    for k,e in enumerate(csv.DictReader(text)):
                        assert k not in global_rows;global_rows[k]=digest(canonical_row(e))
                    text.detach()
                stats['global_CSV_records']=len(global_rows)
                assert max(global_rows)-min(global_rows)+1==len(global_rows)
                partition=json.loads(z.read('observer-session/partition.json'))
                assert partition['records']==len(global_rows) and partition['multiply_owned']==partition['unowned_count']==0
                owners={norm(k):v for k,v in partition['owners'].items()}
            tasks=[]
            for id,member in index['cases'].items():
                r=json.loads(z.read(member));tasks.append((id,r['native_record'],r['raw_trace']))
                for j,c in enumerate(r.get('comparisons',[])):tasks.append((id+'/comparison/'+str(j),c['native_record'],c['raw_trace']))
            for id,np,rp in tasks:
                n=json.loads(z.read(np));raw=z.read(rp);assert digest(raw)==n['raw_trace_sha256'] and n['binary_sha256']==index['binary_sha256']
                if label=='linux':pub=linux_proof(raw,n)
                else:
                    rows=list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'),newline='')))
                    ids=[int(e['Index']) for e in rows];assert ids==sorted(set(ids))
                    assert len(rows)==owners[norm(np)]
                    for e in rows:
                        k=int(e['Index']);body={a:b for a,b in e.items() if a!='Index'};assert global_rows[k]==digest(canonical_row(body));assert k not in seen;seen.add(k)
                    pub=windows_proof(rows,n)
                    stats['individually_bound_CSV_records']+=len(rows)
                stats['native_traces_checked']+=1;stats['publications']+=len(pub);stats['flush_close_pairs_before_publication']+=2*len(pub)
                if pub:proofs[id]={'trace_sha256':n['raw_trace_sha256'],'native_record_sha256':digest(z.read(np)),'publication_count':len(pub)}
            if label=='windows-server':
                probe=list(csv.DictReader(io.StringIO(z.read('observer-selftest/trace.txt').decode('utf-8-sig'),newline='')))
                assert len(probe)==owners[norm('observer-selftest')]
                for e in probe:
                    k=int(e['Index']);body={a:b for a,b in e.items() if a!='Index'};assert global_rows[k]==digest(canonical_row(body)) and k not in seen;seen.add(k)
                stats['selftest_CSV_records']=len(probe)
                # Remaining ownership is explicitly shipping runs, not silently
                # fabricated native source/absence coverage for the observed run.
                remaining=sum(v for k,v in owners.items() if k.startswith('shipping:'))
                assert len(global_rows)-len(seen)==remaining
                stats['remaining_declared_shipping_records']=remaining
                result['global_csv_sha256']=h.hexdigest()
            result['platforms'][label]={'counts':dict(stats),'publication_bindings':proofs}
            print(label,dict(stats),flush=True)
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args();r=run(a.root);a.out.write_text(json.dumps(r,separators=(',',':'))+'\n')
