"""Causal faults in actual retained native records after honest positive baselines."""
import argparse,copy,csv,io,json,zipfile
from pathlib import Path
from native_receipts import linux_proof,windows_proof

def run(root):
    out={}
    for label in ('linux','windows-server'):
        with zipfile.ZipFile(root/(label+'.zip')) as z:
            idx=json.loads(z.read('INDEX.json'));r=json.loads(z.read(idx['cases']['asset/ordinary.wav']));n=json.loads(z.read(r['native_record']));raw=z.read(r['raw_trace'])
            if label=='linux':
                assert len(linux_proof(raw,n))==1;out['linux-honest']='PASS'
                bads={'linux-replace-allowed':raw.replace(b'RENAME_NOREPLACE',b'0'),
                      'linux-missing-audio-fsync':b'\n'.join(l for l in raw.splitlines() if not(b'fsync(' in l and b'/audio.wav>' in l))}
                for key,b in bads.items():
                    assert b!=raw
                    try:linux_proof(b,n)
                    except AssertionError:out[key]='REJECTED'
                    else:raise AssertionError(key+' did not go red')
            else:
                rows=list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'),newline='')))
                assert len(windows_proof(rows,n))==1;out['windows-honest']='PASS'
                bad=copy.deepcopy(rows)
                for e in bad:
                    if e['Operation']=='SetRenameInformationFile':e['Detail']=e['Detail'].replace('ReplaceIfExists: False','ReplaceIfExists: True')
                noflush=[e for e in rows if not(e['Operation']=='FlushBuffersFile' and e['Path'].endswith('audio.wav'))]
                for key,b in {'windows-replace-allowed':bad,'windows-missing-audio-flush':noflush}.items():
                    assert b!=rows
                    try:windows_proof(b,n)
                    except AssertionError:out[key]='REJECTED'
                    else:raise AssertionError(key+' did not go red')
                original=list(csv.DictReader(io.StringIO(z.read('observer-selftest/trace.txt').decode(),newline='')))
                original_ids={int(e['Index']) for e in original}
                controls=json.loads(z.read('observer-selftest/result.json'))['false_pass_controls']
                for key,c in controls.items():
                    rows=list(csv.DictReader(io.StringIO(z.read('observer-selftest/'+c['file']).decode(),newline='')))
                    ids={int(e['Index']) for e in rows};assert ids<original_ids
                    out['windows-global-partition-'+key]={'verdict':'REJECTED','actual_missing_global_indices':len(original_ids-ids)}
    return out

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args();r=run(a.root);a.out.write_text(json.dumps(r,indent=2)+'\n');print(r)
