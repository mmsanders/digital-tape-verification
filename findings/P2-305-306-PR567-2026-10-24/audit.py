"""Read-only exact PR567 disposition audit. No Product/DOM/child execution."""
import argparse, copy, hashlib, json, subprocess, zipfile
from html.parser import HTMLParser
from pathlib import Path

SOURCE = '9cde1f2affecca7f598a102c3dda161cf517bc3c'
HEAD = '26c47d476b46fa9fa36606d641bec70bc170114d'
VMAIN = '63af09b6792d728e3acfb39f331602535b09293d'
MAIN = 'd2213aabbcb9a0d0c10fe5edb6bd3c4606b1acb9'
BASE = 'db0325a9befa333cbc128b24bd2ef3690c48ac08'
RAW = 'docs/REVIEW/software563/run-9cde/'
ARTIFACT = '907403ce948bf65b5f9c01ccb6cab13d7d12175ee4215493cb267edbceda3106'
def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args])
class HTML(HTMLParser):
    def __init__(self):
        super().__init__(); self.progress=[]
    def handle_starttag(self, tag, attrs):
        if tag == 'progress': self.progress.append(dict(attrs))

def audit(p, v, artifact):
    get=lambda name:git(p,'show',HEAD+':'+name)
    read=lambda name:json.loads(get(RAW+name))
    oid=lambda repo, rev, path:git(repo,'rev-parse',rev+':'+path).decode().strip()
    assert git(p,'diff','--name-only',SOURCE,HEAD,'host','tools','tests','.github') == b''
    assert git(p,'diff','--name-only',BASE,MAIN,'host','tools','tests','engine','firmware','docs/WP15-APP-CONTRACT.md','docs/WP15-APP-ANNEX.md') == b''
    imports=[('391c0cb9686f0d2f56e12aebfbdb01f72bbc8758','3395377d5abf37ff32b9b796b492db15664077c7','tests/windows_screen_r1','b83166ec74a60c4be88a6fa9958cdbae8ba86fb2'),
             ('164c9cf923d70403d2fc8b91551567443295bc8a','9f6f9dba46d09474615bf8f03b574f9a72c09d80','tests/windows_bridge_r1','acba2483549e5c9b92419f1f9a9ff350e9641f0b')]
    imported={}
    for imp,pub,path,impl in imports:
        assert oid(p,imp,path)==oid(v,pub,path)==oid(p,HEAD,path)
        assert subprocess.call(['git','-C',str(p),'merge-base','--is-ancestor',imp,impl])==0
        imported[path]=oid(p,HEAD,path)
    for name in ['report.rs','messages.rs','jobdir.rs','children.rs','label.rs']:
        assert oid(p,BASE,'host/app/src/'+name)==oid(p,SOURCE,'host/app/src/'+name)
    assert oid(p,HEAD,'tests/windows_app_jobs_r1')==oid(v,'82f31d48','tests/windows_app_jobs_r1')
    assert oid(v,VMAIN,'tests/windows_screen_r1/contract.py')=='e43d19481051eb82c9d48b9713ca052317d36ef2'
    # Execute ONLY independently published Python predicates over retained JSON.
    modules={}
    for key,path in [('screen','tests/windows_screen_r1/contract.py'),('bridge','tests/windows_bridge_r1/contract.py'),('frames','tests/windows_bridge_r1/frames.py')]:
        # Dependency helpers resolve to verified, unchanged verifier checkout files.
        for helper in ['tests/windows_app_jobs_r1/lifecycle.py','tests/wp15_app1a_r1/oracle.py']:
            assert (v/helper).read_bytes().replace(b'\r\n',b'\n')==git(v,'show',VMAIN+':'+helper)
        ns={'__name__':'independent_'+key,'__file__':str(v/path)}
        exec(compile(git(v,'show',VMAIN+':'+path),'<published '+key+'>','exec'),ns)
        modules[key]=ns
    s,b,f=read('screen-observations.json'),read('bridge-observations.json'),read('frames.json')
    messages=[modules[k]['qualify'](r,SOURCE) for k,r in [('screen',s),('bridge',b),('frames',f)]]
    dom,host,br,raw,binding,fr,runtime=[read(n) for n in ['dom.json','screen-host.json','bridge.json','bridge.raw.json','binding-dom.json','frames.raw.json','runtime.json']]
    assert runtime['module_sha256']==hashlib.sha256(get('host/app/frontend/screen.mjs')).hexdigest() and runtime['errors']==[]
    assert s['drops']==host['drops'] and s['backend_reset']==host['start_over']
    assert s['start_over']['accepted']==host['start_over']['accepted']==[]
    assert host['start_over']['label']==host['start_over']['details']=='' and host['start_over']['frames'] is None
    assert host['start_over']['state']=='Empty' and host['start_over']['make_disabled']
    assert s['live_card_line']==host['live_card_line']=="Finding cards isn't part of this build yet."
    for key in ['mount_calls','label_calls','details_calls','details_text']:
        assert b[key]==binding[key]
    for key in ['request','state_rows','delivery_rows']:
        assert b[key]==br[key]==raw[key]
    for key in br:
        if key not in ['adapter_ref','raw_refs']: assert b[key]==br[key]
    assert raw['empty_before_terminal'] and raw['ui_returned_before_release']
    assert raw['cleanup_trace']==['worker-enter','cancel-request','worker-terminal','remove-owned-job','worker-enter','replacement-worker-start','worker-terminal','completion-delivered','remove-owned-job']
    assert raw['reset_trace']==['worker-enter','invalidate-current','cancel-request','empty-view','worker-terminal','remove-owned-job']
    assert br['lock_probe']==['worker-enter','coordinator-lock-acquired','completion-delivered']
    for key,value in f['rows'].items(): assert fr[key][-1]['snapshot']['total_frames']==value
    for want in modules['screen']['VIEWS']:
        key=want['id']; got=s['views'][key]; assert got['html']==dom[key]
        html=HTML();html.feed(dom[key]);assert len(html.progress)==1
        attrs=html.progress[0]; control=got['native_progress']
        assert control['value_attribute']==attrs.get('value')
        assert control['pseudo_indeterminate']==('value' not in attrs)
        assert got['indeterminate']==(control['visible'] and control['position']==-1)
        attributed=got['input_attribution']['backend']
        if key not in ['making-projection-only','done-projection-only']:
            assert attributed==host['views']['empty' if key=='empty-disabled-discovery' else key]
            assert got['sentence']==(attributed['view']['message'] or ('Checking the music…' if key=='checking' else ''))
            if key!='folders-only': assert got['details']==attributed['details']
        if key in ['folders-only','protected','unusable','folder-content','generic','escaped-name']:
            assert 'hidden' in attrs and not control['visible']
    red=s['negative_control']['actual'];assert red['visible'] and red['position']==-1 and red['metadata']=='false'
    bad=copy.deepcopy(s['views']['generic']);bad['indeterminate']=True
    try: modules['screen']['view'](bad,next(x for x in modules['screen']['VIEWS'] if x['id']=='generic'))
    except AssertionError: pass
    else: raise AssertionError('frozen screen predicate failed to reject retained red control')
    # Independently match every hosted artifact member to its retained Git bytes.
    assert hashlib.sha256(artifact.read_bytes()).hexdigest()==ARTIFACT
    with zipfile.ZipFile(artifact) as z:
        members=[x for x in z.namelist() if not x.endswith('/')]
        assert set(members)=={'bridge.raw.json','bridge.json','frames.raw.json','frames.json','screen-host.json','source-blobs.txt'}
        for name in members: assert z.read(name)==get(RAW+name)
    for line in get(RAW+'source-blobs.txt').decode().splitlines():
        mode,kind,blob,path=line.split();assert kind=='blob' and oid(p,SOURCE,path)==blob
    hashes={name:hashlib.sha256(get(RAW+name)).hexdigest() for name in ['screen-observations.json','dom.json','bridge.raw.json','bridge-observations.json','frames.raw.json','frames.json','screen-host.json','binding-dom.json','runtime.json']}
    return dict(source=SOURCE,evidence=HEAD,current_main=MAIN,verification=VMAIN,imports=imported,qualifiers=messages,
                views=len(s['views']),labels=len(s['labels']),drop_rows=len(s['drops']),frame_sequences=len(f['rows']),
                artifact_sha256=ARTIFACT,artifact_members_matched=6,raw_sha256=hashes,
                result='PASS exact source/component scope; staged production-function and isolated DOM facts only',
                product_execution=False,native_ui=False,real_child_execution=False,launch_admission=False)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--product',type=Path,required=True);ap.add_argument('--verifier',type=Path,required=True);ap.add_argument('--artifact',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    result=audit(a.product,a.verifier,a.artifact)
    a.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(result['result'])
