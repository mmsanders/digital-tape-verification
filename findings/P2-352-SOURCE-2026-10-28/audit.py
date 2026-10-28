"""352 independent original-envelope replay. No Product/child/OS observation execution."""
import argparse,base64,copy,hashlib,importlib.util,json,os
from pathlib import Path
V=Path(os.environ.get('VERIFICATION_REPO',Path(__file__).resolve().parents[2]))
spec=importlib.util.spec_from_file_location('cards352',V/'tests/windows_cards_receipts_r1/receipts.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
def sha(x):return hashlib.sha256(x).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--evidence',type=Path);p.add_argument('--out',type=Path);p.add_argument('--self-check',action='store_true');a=p.parse_args()
    if a.self_check:
        r=json.loads(Path(__file__).with_name('RESULT.json').read_text())
        assert len(r['cases'])==r['original_envelopes']==14
        assert sum(x['complete'] for x in r['cases'])==r['complete']==7 and r['incomplete']==7
        assert len(r['external_comparisons'])==6 and all(x['result']=='PASS' for x in r['external_comparisons'])
        assert len(r['negative_controls'])==2 and r['product_executions']==0
        assert r['disposition'].startswith('SOURCE HELD')
        for f in r['artifact_file_manifest'].values():assert f['bytes']>=0 and len(f['sha256'])==64
        print('PASS publication-integrity check; actual14-envelope replay is separately recorded, no Product execution');return
    assert a.evidence and a.out
    result=dict(scope='retained COMPONENT originals / offline consistency ONLY',product_head='44300ea3b37617075fbff48334b3596bc58b789a',verifier_publication='a4f3138cce76b7675116742d109adb91232d1b00',artifact=12788467739,run=40624193966,cases=[],negative_controls=[],external_comparisons=[])
    probe=(a.evidence/'probe_child.sha256').read_text().strip();source=(a.evidence/'probe_child.source-blob').read_text().strip()
    assert probe=='303fef5b969fb7f7fb7915fd9bc3153b65acd72d288f431f39e36267377746b5'
    assert source=='90916b64e93749ec0bd824ec7c0bd60c6b9bd8ea'
    result.update(probe_sha256=probe,probe_source_blob=source)
    for env in sorted((a.evidence/'raw').glob('*/envelope-*.json')):
        tag=env.stem.removeprefix('envelope-');d=env.parent;f={k:base64.b64decode(v,validate=True) for k,v in json.loads(env.read_text(encoding='utf-8'))['files'].items()}
        binding=json.loads((d/f'binding-{tag}.json').read_text());expect=(d/f'expect-{tag}.txt').read_text().strip()
        assert binding['sha256']==probe and binding['version_label']=='probe612-TEST-ONLY'
        c.validate(f,binding,expect=='complete')
        rows=[json.loads(x) for x in f['records.jsonl'].splitlines()]
        assert rows[0]['data']['source_commit']==result['product_head']
        result['cases'].append(dict(case=d.name,tag=tag,complete=expect=='complete',records_sha256=sha(f['records.jsonl']),envelope_sha256=sha(env.read_bytes()),files=len(f),bytes=sum(map(len,f.values()))))
        launches=[r['data'] for r in rows if r['kind']=='cards-launch']
        exts=[]
        if d.name=='P1-poll':exts=[(launches[i],d/f'external-poll-{i}.json') for i in range(2)]
        elif (d/f'external-{tag}.json').exists() and launches:exts=[(launches[-1],d/f'external-{tag}.json')]
        for launch,path in exts:
            obs=json.loads(path.read_text())
            for k in ['pid','os_start_ns','argv','cwd']:assert launch[k]==obs[k]
            assert obs['console_window'] is False
            for row in rows:
                x=row['data']
                if row['kind']=='cards-blob' and x['run_id']==launch['run_id']:assert sha(f[x['leaf']])==obs['sha256'][x['role']]
            result['external_comparisons'].append(dict(case=d.name,tag=path.stem,run=launch['run_id'],result='PASS'))
        if d.name=='P1-production':
            # Already frozen expectation: a launched normal terminal without an observed
            # exit cannot be made complete. This is an OFFLINE mutation, not an OS failure run.
            r=copy.deepcopy(rows);next(x for x in r if x['kind']=='cards-terminal')['data']['exit']=None
            ff=dict(f);ff['records.jsonl']=c.encode(r)
            try:c.validate(ff,binding,True)
            except AssertionError:result['negative_controls'].append('real positive mutated exit=None/complete=True REJECTED')
            else:raise AssertionError('unobserved terminal promoted')
            # Honest failure is retainable as incomplete; no fabricated OS success needed.
            r[-1]['data'].update(complete=False,reason='MODEL unobserved terminal')
            ff['records.jsonl']=c.encode(r);c.validate(ff,binding,False)
            result['negative_controls'].append('same MODEL explicit incomplete retained')
    assert len(result['cases'])==14 and sum(x['complete'] for x in result['cases'])==7
    result['artifact_file_manifest']={p.relative_to(a.evidence).as_posix():dict(bytes=p.stat().st_size,sha256=sha(p.read_bytes())) for p in sorted(a.evidence.rglob('*')) if p.is_file()}
    result.update(original_envelopes=14,complete=7,incomplete=7,native_runs=0,product_executions=0,disposition='SOURCE HELD: see F352-1/2; envelope consistency is not source clearance')
    a.out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ['original_envelopes','complete','incomplete','external_comparisons','negative_controls','product_executions','disposition']},indent=2))
if __name__=='__main__':main()
