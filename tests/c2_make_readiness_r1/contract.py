"""APP-1 §2/§4 readiness. Supersedes S2's global Make-disabled wording.

Expectations come from the issued contract, not Product implementation or private
tests. Old packets retain false for fixtures lacking retained audio.
"""
import argparse,copy,itertools,json
from pathlib import Path

CASES=[]
for count,label,success,audio,mode in itertools.product((0,1,2),(False,True),(False,True),(False,True),('idle','confirm','making')):
    CASES.append(dict(id=f'cards{count}-label{int(label)}-check{int(success)}-audio{int(audio)}-{mode}',
        cards=count,label=label,successful_current_check=success,retained_audio=audio,mode=mode,
        expected_make_enabled=count==1 and label and success and audio and mode=='idle'))

def qualify(rows):
    assert [r['id'] for r in rows]==[c['id'] for c in CASES], 'missing/duplicated/reordered readiness case'
    for c,r in zip(CASES,rows):
        assert type(r['make_enabled']) is bool and r['make_enabled']==c['expected_make_enabled'],c['id']
    return len(rows)

def controls(rows=None):
    rows=rows or [dict(id=c['id'],make_enabled=c['expected_make_enabled']) for c in CASES]
    qualify(rows)
    killed=[]
    for value,name in ((False,'permanently-disabled'),(True,'always-enabled')):
        bad=[dict(r,make_enabled=value) for r in rows]
        try:qualify(bad)
        except AssertionError:killed.append(name)
        else:raise AssertionError(name+' survived')
    for i,c in enumerate(CASES):
        bad=copy.deepcopy(rows);bad[i]['make_enabled']=not c['expected_make_enabled']
        try:qualify(bad)
        except AssertionError:continue
        raise AssertionError('readiness outcome inversion survived')
    assert sum(c['expected_make_enabled'] for c in CASES)==1
    return dict(cases=len(rows),positive_cases=1,negative_cases=len(rows)-1,controls=killed,
                scope='readiness predicates/component snapshots; no native/physical/package acceptance')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--emit',action='store_true');p.add_argument('--input',type=Path);a=p.parse_args()
    if a.emit:print(json.dumps(CASES,indent=2))
    else:print(json.dumps(controls(json.loads(a.input.read_text()) if a.input else None),indent=2))
