"""352 correction1: independent oracle replay of retained component bytes only."""
import argparse,base64,hashlib,importlib.util,json,os
from pathlib import Path
V=Path(os.environ.get('VERIFICATION_REPO',Path(__file__).resolve().parents[2]))
sp=importlib.util.spec_from_file_location('cards352',V/'tests/windows_cards_receipts_r1/receipts.py');c=importlib.util.module_from_spec(sp);sp.loader.exec_module(c)
HEAD='7d1fd9791c62bbda09fee5a61a49075428583ae0'
PROBE='56494c967d5134d74e0d6abd2515480e24d15abbaab0551b4d2ba43fda625ae6'
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--evidence',type=Path);p.add_argument('--out',type=Path);p.add_argument('--self-check',action='store_true');a=p.parse_args()
    if a.self_check:
        r=json.loads(Path(__file__).with_name('RESULT.json').read_text());assert r['head']==HEAD and len(r['cases'])==20
        assert sum(x['complete'] for x in r['cases'])==7 and r['incomplete']==13
        assert len(r['faults'])==6 and len(r['external'])==7 and r['product_executions']==0
        print('PASS correction publication integrity; separate actual20-envelope replay recorded, no Product execution');return
    assert a.evidence and a.out
    r=dict(head=HEAD,artifact=12793413199,run=40636090229,scope='retained COMPONENT bytes only',cases=[],faults={},external=[],product_executions=0)
    assert (a.evidence/'probe_child.sha256').read_text().strip()==PROBE
    assert (a.evidence/'probe_child.source-blob').read_text().strip()=='90916b64e93749ec0bd824ec7c0bd60c6b9bd8ea'
    for env in sorted((a.evidence/'raw').glob('*/envelope-*.json')):
        d=env.parent;tag=env.stem.removeprefix('envelope-');f={k:base64.b64decode(v,validate=True) for k,v in json.loads(env.read_text())['files'].items()}
        binding=json.loads((d/f'binding-{tag}.json').read_text());complete=(d/f'expect-{tag}.txt').read_text().strip()=='complete'
        assert binding['sha256']==PROBE and binding['version_label']=='probe612-TEST-ONLY'
        c.validate(f,binding,complete);rows=[json.loads(x) for x in f['records.jsonl'].splitlines()]
        assert rows[0]['data']['source_commit']==HEAD
        r['cases'].append(dict(case=d.name,tag=tag,complete=complete,records_sha256=sha(f['records.jsonl']),envelope_sha256=sha(env.read_bytes())))
        get=lambda kind:[x['data'] for x in rows if x['kind']==kind]
        launch=get('cards-launch');ext=[]
        if d.name=='P1-poll':ext=[(launch[i],d/f'external-poll-{i}.json') for i in range(2)]
        elif (d/f'external-{tag}.json').exists() and launch:ext=[(launch[-1],d/f'external-{tag}.json')]
        for l,path in ext:
            o=json.loads(path.read_text())
            for k in ['pid','os_start_ns','argv','cwd']:assert l[k]==o[k]
            assert o['console_window'] is False
            for b in get('cards-blob'):
                if b['run_id']==l['run_id']:assert sha(f[b['leaf']])==o['sha256'][b['role']]
            r['external'].append(dict(case=d.name,run=l['run_id'],observation_sha256=sha(path.read_bytes())))
        if d.name.startswith('F'):
            assert not complete
            kinds=[x['kind'] for x in rows];reason=rows[-1]['data']['reason']
            if d.name=='F1-read':
                m=get('cards-missing');assert len(m)==1 and m[0]['role']=='stderr'
                assert m[0]['reason']=='injected read failure; 19 bytes read before it, sha256 '+sha(b'PROBE-CARDS-ERR\0\xff\r\n')
                assert not any(b['role']=='stderr' for b in get('cards-blob'))
            elif d.name=='F1-reader':
                m=get('cards-missing');assert len(m)==1 and m[0]['role']=='stdout' and m[0]['reason']=='reader thread failed: injected stdout reader failure; 0 bytes read before it, sha256 '+sha(b'')
                assert not any(b['role']=='stdout' for b in get('cards-blob'))
            elif d.name=='F1-wait':
                assert kinds==['session','cards-contract','cards-admit','cards-launch','incomplete']
                assert 'try_wait failed: injected try_wait failure; wait failed: injected wait failure' in reason
            elif d.name=='F2-guard':
                assert not get('cards-cleanup') and reason.startswith('cards-cleanup-refused:') and reason.endswith('failed the ownership check; nothing was removed')
            elif d.name=='F2-remove':
                x=get('cards-cleanup');assert len(x)==1 and x[0]['attempted'] is True and x[0]['result']=='failed' and 'os error 32' in x[0]['error']
            elif d.name=='F2-partial':
                assert kinds==['session','cards-contract','incomplete'] and reason.startswith('cards-job-partially-created:') and 'control failed: injected create failure' in reason
            else:raise AssertionError('unexpected correction fixture')
            public_reason=reason
            if d.name=='F2-guard':public_reason='cards-cleanup-refused: <run>: <owned-job> failed the ownership check; nothing was removed'
            if d.name=='F2-partial':public_reason='cards-job-partially-created: <owned-job> exists, then control failed: injected create failure after the job directory'
            r['faults'][d.name]=dict(complete=False,last_kind=kinds[-1],reason=public_reason)
    assert len(r['cases'])==20 and sum(x['complete'] for x in r['cases'])==7 and len(r['external'])==7 and len(r['faults'])==6
    r.update(complete=7,incomplete=13,probe_sha256=PROBE,probe_source_blob='90916b64e93749ec0bd824ec7c0bd60c6b9bd8ea',disposition='F352-1/2 corrected within reviewed source/component scope')
    r['artifact_file_manifest']={x.relative_to(a.evidence).as_posix():dict(bytes=x.stat().st_size,sha256=sha(x.read_bytes())) for x in sorted(a.evidence.rglob('*')) if x.is_file()}
    a.out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:r[k] for k in ['head','complete','incomplete','faults','disposition','product_executions']},indent=2))
if __name__=='__main__':main()
