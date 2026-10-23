"""Finite observation boundaries. Normalized assertions require private raw review.

No Product import; no GUI, child, native API or artifact launch.
"""
import argparse
import copy
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'wp15_app1a_r1'))
import oracle

APP='05bc85626bfeaaa904f9ec52b2208f18e584d5808916a5e561be762eebac02dc'
CHILD='3895f3f356c91b8a9fe870c33694da64bf2765df308bef118d657c1be4bb9a20'
HEAD='45695aa0edb8a757db5074d17c39eda12bcda888'


def classify(r):
    assert r['source_head']==HEAD and r['app_sha256']==APP and r['child_sha256']==CHILD
    assert not r['make_enabled'] and not r['device_work'] and not r['elevated']
    assert r['raw_refs'], 'actual transport refs required, reviewed separately'
    if not r['client_started']:
        return 'BUILD/STAGING ONLY; client launch unexecuted'
    assert r['actual_windows_client'] and r['launch_instance_bound']
    if not r['owned_window_fact']:
        return 'PROCESS ONLY; window not established'
    if not r['graceful_quit'] or r['forced_cleanup']:
        return 'WINDOW FACTS; normal quit not established'
    if not r['actual_ui_actions']:
        return 'WINDOW FACTS AND QUIT; UI controls unexecuted'
    assert all(x['raw_refs'] and x['observed'] for x in r['actual_ui_actions'])
    return 'ONLY listed UI actions eligible for independent raw review'


def selftest():
    r=dict(source_head=HEAD,app_sha256=APP,child_sha256=CHILD,make_enabled=False,
           device_work=False,elevated=False,raw_refs=['SYNTHETIC-not-evidence'],
           client_started=True,actual_windows_client=True,launch_instance_bound=True,
           owned_window_fact=True,graceful_quit=True,forced_cleanup=False,actual_ui_actions=[])
    assert classify(r)=='WINDOW FACTS AND QUIT; UI controls unexecuted'
    for key,value,want in [('client_started',False,'BUILD/STAGING ONLY'),
                           ('owned_window_fact',False,'PROCESS ONLY'),
                           ('graceful_quit',False,'WINDOW FACTS;'),
                           ('forced_cleanup',True,'WINDOW FACTS;')]:
        q=copy.deepcopy(r);q[key]=value;assert classify(q).startswith(want)
    for key,value in [('app_sha256','0'*64),('child_sha256','0'*64),
                      ('actual_windows_client',False),('launch_instance_bound',False),
                      ('make_enabled',True),('device_work',True),('elevated',True),('raw_refs',[])]:
        q=copy.deepcopy(r);q[key]=value
        try:classify(q)
        except AssertionError:continue
        raise AssertionError('false observation survived: '+key)
    # Existing contract fallback: raw stderr never supplies a report ID.
    for exit,pair,want in [(0,False,('generic',None)),(0,True,('success',None)),(1,True,('generic',None)),(2,False,('generic',None))]:
        assert oracle.message('ingest',exit,None,pair)==want
    print('PASS finite launch/UI boundaries:4 scope neighbours,8 detecting controls,4 existing fallback projections; ZERO actual app/child/native execution')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path);a=p.parse_args()
    if a.input:print(classify(json.loads(a.input.read_text(encoding='utf-8-sig'))))
    else:selftest()
