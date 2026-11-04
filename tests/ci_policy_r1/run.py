"""V390 independent CI-policy review checks. Requires PyYAML (BaseLoader)."""
import argparse,copy,hashlib,importlib.util,json,os,subprocess,sys
from pathlib import Path
import yaml

def read(p):return yaml.load(p.read_text(encoding='utf-8'),Loader=yaml.BaseLoader)
def needs(job):
 n=job.get('needs',[]);return [n] if isinstance(n,str) else n

def structural(ci,manual,base):
 jobs=ci['jobs'];old=base['jobs'];fail=[]
 def check(name,ok):
  if not ok:fail.append(name)
 for lane in ('cheap','regression','qualification'):
  check(lane+'-nonempty-always',bool(needs(jobs[lane])) and 'always()' in jobs[lane].get('if',''))
 def reachable(name):
  seen=set();todo=[name]
  while todo:
   n=todo.pop()
   if n in seen:continue
   seen.add(n);todo.extend(needs(jobs.get(n,{})))
  return seen
 normal=set().union(*(reachable(n) for n in ('cheap','regression','qualification')))
 check('normal-no-macos',all('macos' not in str(jobs[n].get('runs-on','')).lower() and
   all('macos' not in str(x.get('runner','')).lower() for x in jobs[n].get('strategy',{}).get('matrix',{}).get('include',[])) for n in normal if n in jobs))
 check('supported-package-legs',{x['platform'] for x in jobs['wp14-package']['strategy']['matrix']['include']}=={'linux','windows'})
 check('supported-mandatory-members',{'wp14-linux-device','wp14-windows','golden'}<=set(needs(jobs['regression'])) and {'wp14-package','wp14-package-identity'}<=set(needs(jobs['qualification'])))
 check('manual-dispatch-only',set(manual['on'])=={'workflow_dispatch'})
 mj=manual['jobs'];check('manual-three-platforms',{x['platform'] for x in mj['wp14-package']['strategy']['matrix']['include']}=={'linux','macos','windows'})
 check('manual-commands-preserved',all(mj[n]['steps']==old[n]['steps'] for n in ('wp14-macos','wp14-package','wp14-package-census')))
 check('supported-package-commands-preserved',jobs['wp14-package']['steps']==old['wp14-package']['steps'])
 # Required artifact/census checks are broader than the deferred macOS leg.
 # Native execution validates local files before upload; that does not replace
 # the removed downloaded-artifact census and retained-byte authentication.
 check('supported-retained-census-required',any('census.py' in str(jobs.get(n,{}).get('steps',[])) for n in normal))
 return sorted(fail)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--product',type=Path,required=True);ap.add_argument('--base',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--record-known-finding',action='store_true');a=ap.parse_args()
 root=a.product.resolve();ci=read(root/'.github/workflows/ci.yml');manual=read(root/'.github/workflows/wp14-macos-manual.yml');base=read(a.base/'.github/workflows/ci.yml')
 failed=structural(ci,manual,base);controls=[]
 for name,mutate,want in [
  ('normal-macos',lambda c,m:c['jobs']['wp14-package']['strategy']['matrix']['include'].append(dict(platform='macos',runner='macos-latest')),'normal-no-macos'),
  ('empty-regression',lambda c,m:c['jobs']['regression'].update(needs=[]),'regression-nonempty-always'),
  ('missing-windows',lambda c,m:c['jobs']['regression']['needs'].remove('wp14-windows'),'supported-mandatory-members'),
  ('automatic-manual',lambda c,m:m['on'].update(pull_request={}), 'manual-dispatch-only'),
  ('manual-command-drift',lambda c,m:m['jobs']['wp14-macos']['steps'].append(dict(run='true')),'manual-commands-preserved')]:
  c,m=copy.deepcopy(ci),copy.deepcopy(manual);mutate(c,m);assert want in structural(c,m,base);controls.append(name)
 # Exercise the actual lane-verdict executable using membership from a separate
 # YAML parser. Every selected lane must reject failure/cancel/missing/skip.
 runtime=[]
 for lane in ('cheap','regression','qualification'):
  members=needs(ci['jobs'][lane]);members=[n for n in members if lane=='cheap' or n!='changes']
  for variant in ('success','failure','cancelled','missing','skipped','uncertain-success','uncertain-skipped'):
   results={n:dict(result='success') for n in members};results.setdefault('changes',dict(result='success'));n=next(n for n in members if n!='changes')
   if variant=='missing':del results[n]
   elif variant in ('failure','cancelled','skipped'):results[n]['result']=variant
   elif variant=='uncertain-skipped':results[n]['result']='skipped'
   env=dict(os.environ,LANE=lane,NEEDS=json.dumps(results),DOCS_ONLY='' if variant.startswith('uncertain') else 'false',QUALIFY='' if variant.startswith('uncertain') else 'true',QUALIFY_JOBS=',')
   p=subprocess.run([sys.executable,'-B',str(root/'tools/ci/lane-verdict.py')],env=env,capture_output=True,text=True)
   want=0 if variant in ('success','uncertain-success') else 1
   runtime.append(dict(case=lane+'-'+variant,exit=p.returncode,expected=want,passed=p.returncode==want))
 assert all(x['passed'] for x in runtime),runtime
 # Independently drive the actual selector's CLI for uncertainty and full events.
 selectors=[]
 for paths,event in [('', 'pull_request'),('???','push'),('docs/STATUS.md','schedule'),('engine/src/tape.c','pull_request')]:
  with __import__('tempfile').TemporaryDirectory() as d:
   output=Path(d)/'outputs';env=dict(os.environ,EVENT=event,LABELS='',GITHUB_OUTPUT=str(output))
   p=subprocess.run([sys.executable,'-B',str(root/'tools/ci/classify-changes.py')],input=paths,capture_output=True,text=True,env=env)
   text=output.read_text() if output.exists() else '';ok=p.returncode==0 and 'docs_only=false' in text and 'qualify=true' in text
   selectors.append(dict(path=paths,event=event,passed=ok,outputs=text))
 assert all(x['passed'] for x in selectors)
 hashes={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in ['.github/workflows/ci.yml','.github/workflows/wp14-macos-manual.yml','.github/workflows/wp14-release.yml','tools/ci/verify-change-classifier.py']}
 if a.record_known_finding:
  expected=json.loads((Path(__file__).parent/'ORIGINAL-HASHES.json').read_text());assert hashes==expected
 ok=failed==['supported-retained-census-required'] if a.record_known_finding else not failed
 result=dict(failed=failed,structural_controls=controls,lane_cli=runtime,selector_cli=selectors,hashes=hashes,harness_success=ok,clearance=False,mode='original-HOLD-reproduction' if a.record_known_finding else 'strict-policy-review')
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(failed=failed,lane_cases=len(runtime),selector_cases=len(selectors),controls=len(controls),harness_success=ok)));return 0 if ok else 1
if __name__=='__main__':raise SystemExit(main())
