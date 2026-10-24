"""Read-only P2-305-001 response audit. No browser or Product invocation."""
import argparse,copy,hashlib,json,subprocess
from html.parser import HTMLParser
from pathlib import Path
HEAD='165915e171211d0a530b814139c35c973c4b7c61'
SOURCE='11eb294f6ceb6493cfb0ba068a1b02f3a3429aa2'
PUB='3395377d5abf37ff32b9b796b492db15664077c7'
OLD='0c95c45f818fd80836b10ed13fcf443bc4e1c216'
CASES={'folders-only','protected','unusable','folder-content','generic','escaped-name'}
def git(repo,*a):return subprocess.check_output(['git','-C',str(repo),*a])
class HTML(HTMLParser):
    def __init__(self):super().__init__();self.progress=[]
    def handle_starttag(self,t,a):
        if t=='progress':self.progress.append(dict(a))
def audit(p,v):
    get=lambda name:git(p,'show',HEAD+':'+name)
    assert set(git(p,'diff','--name-only',OLD,SOURCE).decode().splitlines())=={'host/app/frontend/screen.mjs','tools/app/screen-dom.cjs'}
    assert git(p,'diff','--name-only',SOURCE,HEAD,'host','tools')==b''
    assert git(p,'rev-parse',HEAD+':tests/windows_screen_r1')==git(v,'rev-parse',PUB+':tests/windows_screen_r1')
    ns={'__name__':'frozen_screen_contract'}
    exec(compile(git(v,'show',PUB+':tests/windows_screen_r1/contract.py'),'<independent3395377d>','exec'),ns)
    base='docs/REVIEW/software562/correction1/'
    r=json.loads(get(base+'screen-observations.json'));dom=json.loads(get(base+'dom.json'));runtime=json.loads(get(base+'runtime.json'))
    module=hashlib.sha256(get('host/app/frontend/screen.mjs')).hexdigest()
    assert runtime['module_sha256']==module and not runtime['errors'] and r['source_head']==SOURCE
    assert r['evidence_class']=='production component / test DOM' and not r['native_ui'] and not r['make_enabled'] and not r['shipping_test_switch']
    rows={}
    assert set(r['views'])=={x['id'] for x in ns['VIEWS']}
    for want in ns['VIEWS']:
        name=want['id'];got=r['views'][name];assert got['html']==dom[name]
        ns['view'](got,want)
        h=HTML();h.feed(dom[name]);assert len(h.progress)==1
        attrs=h.progress[0];raw=got['native_progress']
        assert raw['value_attribute']==attrs.get('value')
        assert raw['pseudo_indeterminate']==('value' not in attrs)
        assert got['indeterminate']==(raw['visible'] and raw['position']==-1)
        if name in CASES:assert 'hidden' in attrs and raw['visible'] is False and got['indeterminate'] is False
        if name=='checking':assert 'hidden' not in attrs and raw['visible'] and raw['position']==-1 and raw['pseudo_indeterminate']
        if name in ['ready-two-seconds','exact-fit','overage-1','overage-8467200']:assert raw['visible'] and raw['position']==want['ratio'] and not raw['pseudo_indeterminate']
        rows[name]=dict(state=got['state'],indeterminate=got['indeterminate'],visible=raw['visible'],position=raw['position'],value=raw['value_attribute'])
    assert r['labels']==ns['LABELS'] and r['malformed_drop_callbacks']==0 and r['mount_side_effects']==[]
    assert r['drop_transport']=={d['id']:[[x['path'] for x in batch] for batch in d['gestures']] for d in ns['DROPS']}
    control=r['negative_control'];actual=control['actual'];assert actual['visible'] and actual['position']==-1 and actual['pseudo_indeterminate'] and actual['value_attribute'] is None and actual['metadata']=='false'
    bad=copy.deepcopy(r['views']['generic']);bad['html']=control['html'];bad['indeterminate']=actual['visible'] and actual['position']==-1
    try:ns['view'](bad,next(x for x in ns['VIEWS'] if x['id']=='generic'))
    except AssertionError:pass
    else:raise AssertionError('Actual red native-control measurement survived unchanged false predicate')
    assert r['incomplete'] and 'drops' not in r # no fabricated full host-admission return
    return dict(candidate=HEAD,source=SOURCE,publication=PUB,finding='P2-305-001 CLOSED in exact partial renderer',module_sha256=module,
                views=rows,label_rows=8,negative_control_rejected_by_frozen_predicate=True,
                dom_sha256=hashlib.sha256(get(base+'dom.json')).hexdigest(),observations_sha256=hashlib.sha256(get(base+'screen-observations.json')).hexdigest(),
                scope='Partial renderer projection correction ONLY; full305/306 host/copy/admission pending',no_Product_or_browser_replay=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    r=audit(a.root/'Digital-Tape',a.root/'verification277-local');a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
