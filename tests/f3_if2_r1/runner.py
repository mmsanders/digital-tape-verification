"""CLI bindings for declared F3-IF/2; selftest is fixture/predicate readiness only."""
import argparse,copy,json,os,subprocess,sys
from pathlib import Path
from support import *
from vectors import timing,bundles
from build_vectors import inspect_cases,build_record_cases
from run import agrees as wire_agrees,line as wire_line

def bundle_agrees(r,c,m,raw):
 try:
  report_keys(r)
  if r['overall']!=c['overall'] or r['manifest_sha256']!=SHA(raw):return False
  if c['f3'] is not None and r['criteria']['F3']['state']!=c['f3']:return False
  if c['reason'] and c['reason'] not in json.dumps(r):return False
  states={o['id']:o['state'] for o in r['observations']}
  if any(states.get(k)!=v for k,v in c['observations'].items()):return False
  physical=m['session']['kind']=='physical' and any(o['provenance']=='actual' for o in m['observations'])
  return r['physical_run'] is physical
 except (AssertionError,KeyError,TypeError):return False

def invoke(script,args,env=None):
 args=list(map(str,args));target=Path(args[args.index('--out')+1]).resolve();root=target.parent
 guard=Path(__file__).with_name('guard.py').resolve();mode='git' if '--describe' in args else 'offline'
 q=subprocess.run([sys.executable,'-B',str(guard),str(script.resolve()),str(root),str(target),mode,*args],capture_output=True,text=True,env=env)
 if 'AUDIT_VIOLATION' in q.stderr:q.returncode=125
 return q

def inspector_run(tool,out):
 result=[]
 for c in inspect_cases():
  d=out/c['name'];d.mkdir();h,e,b=artifact(c['control']);h,e,b=c['edit'](h,e,b);(d/'firmware.hex').write_bytes(h);(d/'firmware.elf').write_bytes(e);(d/'build.json').write_text(json.dumps(b));rpath=d/'report.json'
  q=invoke(tool,['--hex',d/'firmware.hex','--elf',d/'firmware.elf','--build-json',d/'build.json','--out',rpath])
  try:
   r=json.loads(rpath.read_text());good=set(r)=={'schema','state','reasons','env','inject_us','hex_sha256','elf_sha256','marker','seam_symbol_present','accepted'} and r['schema']=='digital-tape/fw-build-inspect/1' and r['state']==c['state'] and r['accepted'] is False and all(x in r['reasons'] for x in c['reasons']) and r['reasons']==sorted(set(r['reasons'])) and q.returncode==(0 if c['state']=='CONSISTENT' else 2)
   if c['state']=='CONSISTENT':good=good and r['hex_sha256']==SHA(h) and r['elf_sha256']==SHA(e) and r['seam_symbol_present'] is c['control'] and r['marker']=={k:b[k] for k in ('id','commit','dirty','env','inject_us')}
   if any(reason in c['reasons'] for reason in ('marker_missing','marker_duplicate')):good=good and r['marker'] is None
  except (OSError,ValueError,KeyError):r={};good=False
  result.append(dict(case=c['name'],passed=bool(good) and 'Traceback' not in q.stderr,exit=q.returncode,report=r))
 existing=out/'production-no-seam'/'report.json';before=existing.read_bytes() if existing.exists() else b''
 if existing.exists():
  d=existing.parent;q=invoke(tool,['--hex',d/'firmware.hex','--elf',d/'firmware.elf','--build-json',d/'build.json','--out',existing]);result.append(dict(case='inspector-exclusive-output',passed=q.returncode==64 and existing.read_bytes()==before))
 return result

def metadata_run(tool,out):
 result=[]
 for name,opts,valid in build_record_cases():
  d=out/name;d.mkdir();h,e,b=artifact(opts.get('control',False));(d/'a.hex').write_bytes(h);(d/'a.elf').write_bytes(e);(d/'pins.json').write_text(json.dumps([] if opts.get('bad_toolchain') else if1.PINS));target=d/'build.json'
  args={'id':b['id'],'commit':b['commit'],'dirty':str(b['dirty']),'env':b['env'],'inject-us':str(b['inject_us']),'engine-tree':b['engine_tree']}
  if 'bad_key' in opts:args[opts['bad_key']]=opts['bad_value']
  cli=['--hex',d/'a.hex','--elf',d/'a.elf','--toolchain',d/'pins.json','--out',target]
  for k,v in args.items():cli.extend(['--'+k,v])
  q=invoke(tool,cli);r=json.loads(target.read_text()) if target.exists() else {};good=q.returncode==(0 if valid else 64) and (r==b if valid else not target.exists()) and 'Traceback' not in q.stderr
  result.append(dict(case=name,passed=good,exit=q.returncode))
 d=out/'exact-production-metadata';target=d/'build.json';before=target.read_bytes() if target.exists() else b''
 if target.exists():
  _,_,b=artifact();cli=['--hex',d/'a.hex','--elf',d/'a.elf','--toolchain',d/'pins.json','--out',target]
  for k,v in [('id',b['id']),('commit',b['commit']),('dirty','0'),('env','teensy41'),('inject-us','0'),('engine-tree',b['engine_tree'])]:cli.extend(['--'+k,v])
  q=invoke(tool,cli);result.append(dict(case='metadata-exclusive-output',passed=q.returncode==64 and target.read_bytes()==before))
 return result

def describe_run(tool,out):
 repo=out/'repo';repo.mkdir();(repo/'tracked.txt').write_text('SYNTHETIC GIT FIXTURE');(repo/'firmware/bench').mkdir(parents=True);(repo/'firmware/bench/source.txt').write_text('SYNTHETIC');
 def git(*a):return subprocess.check_output(['git','-c','commit.gpgsign=false','-c','core.hooksPath='+str((out/'no-hooks').resolve()),'-C',str(repo),*a],stderr=subprocess.DEVNULL).decode().strip()
 (out/'no-hooks').mkdir();git('init');git('add','.');git('-c','user.name=Verification fixture','-c','user.email=fixture@example.invalid','commit','-m','synthetic fixture');commit=git('rev-parse','HEAD');obs=[]
 for name,edit,dirty in [('clean',lambda:None,0),('pio-only-ignored',lambda:((repo/'firmware/bench/.pio').mkdir(parents=True),(repo/'firmware/bench/.pio/cache').write_text('ignored')),0),('outside-pio-untracked',lambda:(repo/'other.txt').write_text('dirty'),1),('tracked-edit',lambda:(repo/'tracked.txt').write_text('modified'),1)]:
  edit();target=out/(name+'.json');q=invoke(tool,['--describe','--repo',repo,'--out',target]);r=json.loads(target.read_text()) if target.exists() else {};obs.append(dict(case='describe-'+name,passed=q.returncode==0 and r==dict(commit=commit,dirty=dirty),exit=q.returncode))
 d=out/'not-a-repo';d.mkdir();q=invoke(tool,['--describe','--repo',d,'--out',out/'bad.json'],env=dict(os.environ,GIT_CEILING_DIRECTORIES=str(d.parent.resolve())));obs.append(dict(case='describe-not-repo',passed=q.returncode==3,exit=q.returncode))
 existing=out/'clean.json';before=existing.read_bytes() if existing.exists() else b''
 if existing.exists():
  q=invoke(tool,['--describe','--repo',repo,'--out',existing]);obs.append(dict(case='describe-exclusive-output',passed=q.returncode==64 and existing.read_bytes()==before))
 return obs

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--selftest',action='store_true');ap.add_argument('--host',type=Path);ap.add_argument('--checker',type=Path);ap.add_argument('--inspector',type=Path);ap.add_argument('--build-record',type=Path);ap.add_argument('--build-id',type=Path);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();assert a.selftest or any([a.host,a.checker,a.inspector,a.build_record,a.build_id]);a.out.mkdir(parents=True,exist_ok=False);obs=[]
 if a.selftest or a.host:
  for c in timing():
   if a.selftest:
    good=True if c['usage'] else wire_agrees(wire_line(c['wanted']),c['wanted'])
   else:
    path=a.out/'scenario.json';path.write_text(json.dumps(c['input']));q=subprocess.run([str(a.host.resolve()),'wake-sim',str(path.resolve())],capture_output=True)
    good=q.returncode==64 and not q.stdout if c['usage'] else q.returncode==0 and wire_agrees(q.stdout,c['wanted'])
   obs.append(dict(case='G3-'+c['name'],passed=bool(good)))
 if a.selftest or a.checker:
  for c in bundles():
   m,f=bundle(c['control']);c['edit'](m,f);d=a.out/('G12-'+c['name']);materialize(d,m,f);raw=(d/'manifest.json').read_bytes()
   if a.selftest:good=all(SHA((d/x['path']).read_bytes())==x['sha256'] for x in m['files'])
   else:
    rpath=a.out/(c['name']+'.json');q=invoke(a.checker,['--offline',d,'--out',rpath]);r=json.loads(rpath.read_text()) if rpath.exists() else {};good=q.returncode==c['exit'] and bundle_agrees(r,c,m,raw) and 'Traceback' not in q.stderr
   obs.append(dict(case='G12-'+c['name'],passed=bool(good)))
 if a.selftest:
  for c in inspect_cases():
   d=a.out/('G4-'+c['name']);d.mkdir();h,e,b=artifact(c['control']);h,e,b=c['edit'](h,e,b);(d/'firmware.hex').write_bytes(h);(d/'firmware.elf').write_bytes(e);(d/'build.json').write_text(json.dumps(b));obs.append(dict(case='G4-'+c['name'],passed=True))
 else:
  for tool,fn,name in [(a.inspector,inspector_run,'inspector'),(a.build_record,metadata_run,'metadata'),(a.build_id,describe_run,'describe')]:
   if tool:d=a.out/name;d.mkdir();obs.extend(fn(tool,d))
 # The report predicate must reject erased control observations and altered flags/layout.
 if a.selftest:
  c=bundles()[0];m,f=bundle();raw=b'SYNTHETIC MANIFEST PREDICATE';r=dict(schema='digital-tape/f3-report/1',checker=dict(name='f3_evidence.py',interface='F3-IF/2'),manifest_sha256=SHA(raw),accepted=False,physical_run=False,overall='CONTROL_DETECTED',criteria=dict(F3=dict(state='CONSISTENT',reasons=['simulated_not_physical'],target_met=True),F4=dict(state='NOT_RUN',reasons=['f4_deferred'],target_met=None)),observations=[dict(id=o['id'],sequence=o['sequence'],kind=o['kind'],provenance=o['provenance'],build_id=('b' if i else 'a')*32,state='CONTROL_DETECTED' if i else 'CONSISTENT',reasons=[] if i else ['simulated_not_physical'],elapsed_us=150000 if i else 99000,target_met=False if i else True,superseded_by=None) for i,o in enumerate(m['observations'])])
  assert bundle_agrees(r,c,m,raw)
  changes=[lambda x:x.update(accepted=True),lambda x:x.update(overall='CONSISTENT'),lambda x:x.update(observations=[]),lambda x:x.update(extra=1),lambda x:x['observations'].reverse(),lambda x:x['criteria']['F4'].update(state='CONSISTENT')]
  for change in changes:
   bad=copy.deepcopy(r);change(bad);assert not bundle_agrees(bad,c,m,raw)
 # Detect inert success/state erasure and bad rounding with the public predicates.
 positives=[c for c in timing() if not c['usage']];assert any(not wire_agrees(wire_line(dict(c['wanted'],status='ok',elapsed_us='0')),c['wanted']) for c in positives)
 assert any(c['exit']==2 for c in bundles()) and any(c['state']!='CONSISTENT' for c in inspect_cases())
 result=dict(report_controls_detected=6,mode='fixture-and-wire-predicate-selftest' if a.selftest else 'actual-declared-IF2-CLI',cases=obs,passed=all(c['passed'] for c in obs),counts=dict(timing=len(timing()),bundle=len(bundles()),inspector=len(inspect_cases()),metadata=len(build_record_cases()),describe=5,exclusive_outputs=3),candidate_executed=not a.selftest,physical_run=False,accepted=False)
 (a.out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='cases'}));return 0 if result['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
