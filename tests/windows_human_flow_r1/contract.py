"""328 human-visible evidence INDEX controls only; never UI, child or collector proof."""
import argparse,copy,json,re
from pathlib import Path
APP='ee4c84acb03655c4fb1344db1548ab283054eabe9caea9c2482b0181b39fa250'
CHILD='3895f3f356c91b8a9fe870c33694da64bf2765df308bef118d657c1be4bb9a20'
WAV='48f1b3c7ce7fe27a90469364f841803087a9d274a4af9a4ec8ee195a2846ac18'
VISUAL=['page','label','file-drop-visible','mixed-drop-visible','music-visible','checking-visible','empty-visible','reset-visible','normal-close-visible']
HELD=['complete-positive-child-chain','empty-child-exit2','zero-new-requests','event-ipc-worker-attribution','published-pair-88200-hashes','owned-cleanup-order']
def template():
    return dict(scope='candidate564 human-visible partial observations only',actor='Michael',actor_kind='human',platform='Windows11 x64',effective_admin=False,app_sha256=APP,child_sha256=CHILD,fixture_sha256=WAV,source_head='266bdcaa760f702d6f685300cc9ca6e4491b6438',session_seconds=None,context_ref=None,authorization_ref=None,collector='NONE',injection=False,direct_cli_substitute=False,held_claims=HELD.copy(),promoted_claims=[],raw={},observations={k:dict(status='UNEXECUTED',refs=[],start=None,end=None,note=None,signed=None,date=None) for k in VISUAL},sentinels=dict(before_ref=None,after_ref=None,unchanged=None),labels_nul='UNEXECUTED: unsupported natural input')
def qualify(r):
    assert r['scope']=='candidate564 human-visible partial observations only'
    assert (r['actor'],r['actor_kind'],r['platform'],r['effective_admin'])==('Michael','human','Windows11 x64',False)
    assert r['app_sha256']==APP and r['child_sha256']==CHILD and r['fixture_sha256']==WAV
    assert r['source_head']=='266bdcaa760f702d6f685300cc9ca6e4491b6438'
    assert r['collector']=='NONE' and r['injection'] is False and r['direct_cli_substitute'] is False
    assert set(r['held_claims'])==set(HELD) and not r['promoted_claims']
    assert set(r['observations'])==set(VISUAL)
    observed=False
    for k,x in r['observations'].items():
        assert x['status'] in ['observed','failed','UNEXECUTED']
        if x['status']=='UNEXECUTED':continue
        observed=True
        assert x['note'] and x['signed']=='Michael' and x['date']
        assert isinstance(x['start'],(int,float)) and isinstance(x['end'],(int,float)) and 0<=x['start']<=x['end']<=r['session_seconds']
        refs=[r['raw'][name] for name in x['refs']];assert refs
        assert any(f['kind'] in ['video','screenshot'] for f in refs)
        for f in refs:
            assert re.fullmatch('[0-9a-f]{64}',f['sha256'])
            assert f['session']=='current564' and f['original_ref'] and f['redaction_map_ref']
    if observed:
        assert 0<r['session_seconds']<=600 and r['context_ref'] and r['authorization_ref']
    return 'INDEX ONLY: inspect private originals/chronology/identity/redaction; full child/IPC/no-request/cleanup claims HELD'
def controls():
    r=template();qualify(r)
    r.update(session_seconds=500,context_ref='SYNTHETIC-context',authorization_ref='SYNTHETIC-authorization')
    r['raw']={'v':dict(kind='video',sha256='a'*64,session='current564',original_ref='SYNTHETIC-original',redaction_map_ref='SYNTHETIC-map')}
    r['observations']['music-visible']=dict(status='observed',refs=['v'],start=100,end=110,note='SYNTHETIC visible 2seconds only',signed='Michael',date='SYNTHETIC')
    qualify(r)
    mutations=[('wrong candidate',lambda b:b.update(app_sha256='0'*64)),('new bundle',lambda b:b.update(source_head='f'*40)),('collector',lambda b:b.update(collector='jobobject')),('injection',lambda b:b.update(injection=True)),('directCLI',lambda b:b.update(direct_cli_substitute=True)),('promoted child',lambda b:b['promoted_claims'].append(HELD[0])),('omitted hold',lambda b:b['held_claims'].pop()),('no image',lambda b:b['raw']['v'].update(kind='typed-boolean')),('stale evidence',lambda b:b['raw']['v'].update(session='old564')),('corrupt hash',lambda b:b['raw']['v'].update(sha256='bad')),('missing original',lambda b:b['raw']['v'].update(original_ref='')),('no signature',lambda b:b['observations']['music-visible'].update(signed=None)),('reversed time',lambda b:b['observations']['music-visible'].update(end=99)),('out of session',lambda b:b['observations']['music-visible'].update(end=501)),('no refs',lambda b:b['observations']['music-visible'].update(refs=[])),('overtime',lambda b:b.update(session_seconds=601))]
    for name,mutate in mutations:
        b=copy.deepcopy(r);mutate(b)
        try:qualify(b)
        except (AssertionError,KeyError,TypeError):continue
        raise AssertionError('negative survived: '+name)
    print('PASS16 human-visible index attribution/corruption/staleness/partial-claim negatives; ZERO Product/UI/collector execution')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--emit',action='store_true');p.add_argument('--input',type=Path);a=p.parse_args()
    if a.emit:print(json.dumps(template(),ensure_ascii=True,indent=2))
    elif a.input:print(qualify(json.loads(a.input.read_text(encoding='utf-8-sig'))))
    else:controls()
