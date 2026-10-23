"""Internal ordinary-file session predicates, never native device qualification."""
import argparse
import copy
import json
import importlib.util
from pathlib import Path
import re

PHASES=['provision','load','commit','verify']
spec=importlib.util.spec_from_file_location('wp14_geometry',Path(__file__).resolve().parent.parent/'wp14_r1/oracle.py')
wp14=importlib.util.module_from_spec(spec);spec.loader.exec_module(wp14)


def check(r):
    assert r['scope']=='internal-file-composition' and r['backend']=='ordinary-file'
    assert r['observer']=='compiled-callbacks' and r['raw_refs']
    assert not r['shipping_image_flag'] and not r['shipping_make_enabled'] and not r['elevated']
    assert r['source_unchanged'] and r['foreign_sentinel_unchanged'] and not r['external_io']
    events=r['events'];opens=[e for e in events if e['op']=='authorized-open']
    assert r['required_initial_query_ok'] and r['required_facts_known'] or not opens
    terminal=r['terminal'];case=r['case']
    if case in ['initial-query-failure','unknown-safety','policy-refusal']:
        assert not opens and not any(e['op'] in ['phase','write','flush'] for e in events) and r['exit']!=0
        if case=='initial-query-failure':
            assert not r['required_initial_query_ok']
            assert r['exit']==1 and terminal['id']=='HOST_QUERY_FAILED' and terminal['phase']=='safety' and terminal['op']=='media_query' and terminal['os_error']
        if case=='unknown-safety':assert not r['required_facts_known']
        if case=='policy-refusal':assert r['required_initial_query_ok'] and r['required_facts_known'] and r['policy_facts']['whole'] is False and r['exit']==3 and terminal['id']=='REFUSE_NOT_WHOLE_DEVICE'
        return 'bounded initial fail-closed component'
    assert len(opens)==1 and opens[0]['access']=='readwrite' and opens[0]['ordinary_file']
    sid=opens[0]['session'];file_id=opens[0]['file_id'];seen=[];stop=False;verifying=False
    for e in events[events.index(opens[0])+1:]:
        assert e['op']!='authorized-open', 'reopen forbidden'
        assert e['session']==sid and e['file_id']==file_id
        if e['op']=='close':continue
        assert not stop, 'continued after terminal boundary'
        if e['op']=='phase':
            seen.append(e['phase']);assert seen==PHASES[:len(seen)]
            if e['phase']=='verify':assert e['write_callback_null'];verifying=True
        elif e['op']=='bind-verify':assert e['write_callback_null'];verifying=True
        elif e['op']=='write':assert not verifying
        elif e['op']=='media-change':
            assert e['reason'] in ['changed','removed']
            assert terminal['id']=='CARD_CHANGED' and terminal['phase']==e['phase'] and r['exit']==1
            stop=True
        elif e['op']=='query-failure':
            assert terminal['id']=='HOST_QUERY_FAILED' and terminal['phase']==e['phase'] and terminal['op']=='media_query' and terminal['os_error'] and r['exit']==1
            stop=True
        elif e['op']=='phase-failure':
            assert r['exit']!=0 and seen[-1]==e['phase'];stop=True
        else:assert e['op'] in ['read','flush']
    assert events[-1]['op']=='close' and r['open_attempt_count']==1
    if case=='positive':assert r['exit']==0 and terminal is None and seen==PHASES and verifying
    else:assert stop and not r['normal_output_after_terminal']
    failures=[e for e in events if e['op'] in ['phase-failure','query-failure','media-change']]
    if case.endswith('-failure') and case.split('-')[0] in ['provision','load','verify']:
        assert len(failures)==1 and failures[0]['op']=='phase-failure' and failures[0]['phase']==case.split('-')[0]
    if case in ['media-change','media-remove']:
        assert len(failures)==1 and failures[0]['op']=='media-change' and failures[0]['reason']==('changed' if case=='media-change' else 'removed')
    if case=='query-failure':assert len(failures)==1 and failures[0]['op']=='query-failure'
    # Reference uses the existing separate operations, same input/UUID/epoch/fault.
    assert r['identity_inputs_equal'] and r['composition_exit']==r['baseline_exit']==r['exit']
    assert r['composition_stdout_hex']==r['baseline_stdout_hex']
    assert r['composition_image_sha256']==r['baseline_image_sha256']
    assert len(r['composition_image_sha256'])==64
    return 'ONLY retained ordinary-file component; no native/session/physical acceptance'


def fixture():
    base=dict(session='logical-file-session-1',file_id='owned-file-id-1')
    def e(op,**kw):return dict(op=op,**base,**kw)
    events=[e('authorized-open',access='readwrite',ordinary_file=True),e('phase',phase='provision'),
            e('write'),e('phase',phase='load'),e('write'),e('phase',phase='commit'),e('flush'),
            e('bind-verify',write_callback_null=True),e('phase',phase='verify',write_callback_null=True),e('read'),e('close')]
    return dict(scope='internal-file-composition',backend='ordinary-file',observer='compiled-callbacks',raw_refs=['SYNTHETIC-not-evidence'],
                shipping_image_flag=False,shipping_make_enabled=False,elevated=False,source_unchanged=True,
                foreign_sentinel_unchanged=True,external_io=False,required_initial_query_ok=True,required_facts_known=True,
                case='positive',events=events,terminal=None,exit=0,open_attempt_count=1,normal_output_after_terminal=False,
                identity_inputs_equal=True,composition_exit=0,baseline_exit=0,composition_stdout_hex='4f4b0a',baseline_stdout_hex='4f4b0a',
                composition_image_sha256='a'*64,baseline_image_sha256='a'*64)


def controls():
    blocks=wp14.minimum_blocks(9)
    assert blocks==6145 and wp14.geometry(9,blocks) and not wp14.geometry(9,blocks-1)
    assert (wp14.P2_START+blocks)*512==20972032
    good=fixture();check(good)
    variants=[]
    q=copy.deepcopy(good);q['events'].insert(4,copy.deepcopy(q['events'][0]));variants.append(q)
    q=copy.deepcopy(good);q['events'][2]['session']='different';variants.append(q)
    q=copy.deepcopy(good);q['events'][8]['write_callback_null']=False;variants.append(q)
    q=copy.deepcopy(good);q['events'].insert(-1,dict(op='write',session='logical-file-session-1',file_id='owned-file-id-1'));variants.append(q)
    q=copy.deepcopy(good);q['composition_image_sha256']='b'*64;variants.append(q)
    q=copy.deepcopy(good);q['required_facts_known']=False;variants.append(q)
    q=copy.deepcopy(good);q['composition_stdout_hex']='';variants.append(q)
    for q in variants:
        try:check(q)
        except AssertionError:continue
        raise AssertionError('false session/equivalence control survived')
    for op,id in [('media-change','CARD_CHANGED'),('query-failure','HOST_QUERY_FAILED')]:
        q=copy.deepcopy(good);event=dict(op=op,session='logical-file-session-1',file_id='owned-file-id-1',phase='load',reason='changed')
        q.update(case=op,exit=1,composition_exit=1,baseline_exit=1,terminal=dict(id=id,phase='load',op='media_query',os_error='SYNTHETIC'))
        q['events']=q['events'][:3]+[event,q['events'][-1]];check(q)
        q['events'].insert(-1,dict(op='read',session='logical-file-session-1',file_id='owned-file-id-1'))
        try:check(q)
        except AssertionError:continue
        raise AssertionError('continued after failure')
    print('PASS internal session/equivalence/query/change causal models; ZERO Product/image/device execution')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path);p.add_argument('--candidate');a=p.parse_args()
    if a.input:
        r=json.loads(a.input.read_text());assert re.fullmatch('[0-9a-f]{40}',a.candidate) and r['source_head']==a.candidate
        assert len(r['rows'])==10 and {x['case'] for x in r['rows']}=={'positive','initial-query-failure','unknown-safety','policy-refusal','provision-failure','load-failure','verify-failure','media-change','media-remove','query-failure'}
        for row in r['rows']:print(check(row))
    else:controls()
