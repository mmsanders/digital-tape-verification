"""Read-only305 offered partial renderer review. No browser/Product execution."""
import hashlib,json,subprocess,argparse
from pathlib import Path
from html.parser import HTMLParser
HEAD='0c95c45f818fd80836b10ed13fcf443bc4e1c216'
PUB='3395377d5abf37ff32b9b796b492db15664077c7'
IMPORT='391c0cb9686f0d2f56e12aebfbdb01f72bbc8758'
def git(repo,*a):return subprocess.check_output(['git','-C',str(repo),*a])
class Probe(HTMLParser):
    def __init__(self):super().__init__();self.progress=[]
    def handle_starttag(self,t,a):
        if t=='progress':self.progress.append(dict(a))
def audit(p,v):
    get=lambda name:git(p,'show',HEAD+':'+name)
    source=get('host/app/frontend/screen.mjs')
    runtime=json.loads(get('docs/REVIEW/software562/screen-run3/runtime.json'))
    assert hashlib.sha256(source).hexdigest()==runtime['module_sha256']
    assert git(p,'rev-parse',IMPORT+':tests/windows_screen_r1')==git(v,'rev-parse',PUB+':tests/windows_screen_r1')
    subprocess.run(['git','-C',str(p),'merge-base','--is-ancestor',IMPORT,HEAD],check=True)
    assert git(p,'diff','--name-only','c7c6a4a16befcc69923f9fde621aa7c425613411',HEAD,'host','tools')==b''
    obs=json.loads(get('docs/REVIEW/software562/screen-run3/screen-observations.json'))
    dom=json.loads(get('docs/REVIEW/software562/screen-run3/dom.json'))
    mismatch=[]
    for name,row in obs['views'].items():
        assert row['html']==dom[name]
        probe=Probe();probe.feed(dom[name]);assert len(probe.progress)==1
        attrs=probe.progress[0]
        visible='hidden' not in attrs
        actual_indeterminate=visible and 'value' not in attrs
        if visible and row['indeterminate']!=actual_indeterminate:
            mismatch.append(dict(case=name,state=row['state'],claimed_indeterminate=row['indeterminate'],visible_progress=True,value_attribute_present='value' in attrs,html_progress_attributes=attrs))
    assert len(mismatch)==6
    return dict(candidate=HEAD,publication=PUB,module_sha256=runtime['module_sha256'],view_count=len(obs['views']),label_count=len(obs['labels']),finding='P2-305-001',
                mismatches=mismatch,scope='Partial renderer/test-DOM observations ONLY; combined host/copy rows pending306; no clearance',no_Product_or_browser_replay=True,
                observations_sha256=hashlib.sha256(get('docs/REVIEW/software562/screen-run3/screen-observations.json')).hexdigest(),dom_sha256=hashlib.sha256(get('docs/REVIEW/software562/screen-run3/dom.json')).hexdigest())
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--root',type=Path,required=True);a.add_argument('--output',type=Path,required=True);x=a.parse_args()
    r=audit(x.root/'Digital-Tape',x.root/'verification277-local');x.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
