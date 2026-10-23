"""Independent no-card flow predicates; normalized facts require original raw review."""
import argparse
import copy
import importlib.util
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parent.parent
def module(name,file):
    spec=importlib.util.spec_from_file_location(name,ROOT/'wp15_app1a_r1'/file)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
oracle=module('flow_oracle','oracle.py');shell=module('flow_shell','shell_oracle.py')
PIN='3895f3f356c91b8a9fe870c33694da64bf2765df308bef118d657c1be4bb9a20'
LABELS=[('','A'),('','x'*32),('x'*32,'y'),('','é'*16),('é'*16,'x')]


def qualify(r,candidate):
    assert re.fullmatch('[0-9a-f]{40}',candidate) and r['source_head']==candidate
    assert r['raw_refs'] and not r['make_enabled'] and r['lists']==[] and not r['elevated']
    assert r['scope'] in ['backend-real-child','actual-ui']
    for x in r['labels']:
        assert x['after']==oracle.label_append(x['before'],x['addition'])
    assert {(x['before'],x['addition']) for x in r['labels']}==set(LABELS)
    assert len(r['invalid_drops'])==2
    for drop in r['invalid_drops']:
        shell.atomic_drop(drop['before'],drop['after'],drop['gesture'])
        assert any(x['kind']!='folder' for x in drop['gesture'])
    assert {tuple(x['kind'] for x in d['gesture']) for d in r['invalid_drops']}=={('file',),('folder','file')}
    order=r['folder_order'];assert order['raw_refs'] and order['gestures']==[['A'],['B','C']]
    assert order['accepted']==['A','B','C'] and order['component']=='production drop/state methods; no GUI claim'
    for x in r['checks']:
        assert x['child']['tool']=='ingest' and x['child']['actual_executable_sha256']==PIN
        shell.child(x['child'])
        assert x['observed_checking'] and x['current_generation'] and x['raw_refs']
        if x['case']=='positive':
            assert x['exit']==0 and x['pair_present'] and x['total_frames']==88200 and x['capacity_frames']==158760000
            assert x['bar_frames']==x['total_frames'] and x['state']=='Ready'
        elif x['case']=='empty':
            assert x['exit']==2 and x['refusal']=='FOLDER_EMPTY' and not x['pair_present'] and x['state']=='Problem'
            assert x['message_category']=='folder-nonmusic' and x['details_raw_stderr']
        else: raise AssertionError('unissued check')
    assert len(r['checks'])==2 and [x['case'] for x in r['checks']]==['positive','empty']
    if r['scope']=='actual-ui':
        assert r['real_input_tool']=='computer-use' and r['ui_actions']
        assert all(x['actual_input'] and x['before_raw'] and x['after_raw'] for x in r['ui_actions'])
        assert r['positive_folder_gesture_observed'] and r['refusal_gesture_observed']
        assert r['page_readiness_raw'] and r['blank_window_classification_raw']
        return 'ONLY raw-reviewed actual UI actions eligible; no wholeAPP/native acceptance'
    assert not r['ui_actions']
    return 'BACKEND REAL-CHILD ONLY; UI unexecuted'


def selftest():
    # Existing label predicates; no synthetic fake child or UI launches.
    for before,addition,want in [('', 'A','A'),('a'*32,'b','a'*32),('é'*16,'x','é'*16),('abc','\0','abc')]:
        assert oracle.label_append(before,addition)==want
    b=dict(accepted_drops=['A'],child_count=1)
    a=dict(accepted_drops=['A'],child_count=1,app_event='DROP_NOT_FOLDER')
    gesture=[dict(kind='folder'),dict(kind='file')]
    shell.atomic_drop(b,a,gesture)
    for key,value in [('accepted_drops',['A','bad']),('child_count',2),('app_event','NONE')]:
        q=copy.deepcopy(a);q[key]=value
        try: shell.atomic_drop(b,q,gesture)
        except AssertionError:continue
        raise AssertionError('Invalid drop mutation survived')
    assert not shell.success(0,False,True) and not shell.success(1,True,True)
    print('PASS reused UTF8/atomic-drop/pair causal controls; ZERO Product/UI execution')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path);p.add_argument('--candidate');a=p.parse_args()
    if a.input: print(qualify(json.loads(a.input.read_text(encoding='utf-8-sig')),a.candidate))
    else:selftest()
