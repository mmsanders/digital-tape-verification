"""Authenticate original Software511 bytes; never run the recorder or Product."""
import argparse,hashlib,importlib.util,io,json,pathlib,re,sys,urllib.request,zipfile
ROOT=pathlib.Path(__file__).resolve().parents[2]
METHOD=ROOT/'tests/evidence_recorder_r1'
def mod(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
oracle=mod('independent252',METHOD/'oracle.py');cases=mod('cases252',METHOD/'cases.py')
sha=lambda b:hashlib.sha256(b).hexdigest()
HEAD='2148a139fc59e71795b269281f152e707a7d61b0'
TESTED='a5dd957c8783eaddb86bc7e576f6abe9b6cb2bd0'
INNER='88638342e902089ccd0e704487d90170655fcd7109af138911dfac1165b4110e'
OUTER='efc2f587f136566bde1f46b6c8cf7557a8fed61d5c76a552822768bb05072a61'
URL='https://raw.githubusercontent.com/mmsanders/Digital-Tape/'+HEAD+'/'
FILES={'recorder.py':('host/evidence-recorder/recorder.py','eb3597ad4ff378d2d140e116b659be467489c03ec77d60f24a2ecb91ccec7cf2'),
 'driver.py':('host/evidence-recorder/run_method.py','560db3b761d86e05bd588d1ed24d621955e901980a674fdcc9b88abf1fbf0a31')}
def fetch(url):
 with urllib.request.urlopen(url,timeout=45) as f:return f.read()
def readzip(raw):
 with zipfile.ZipFile(io.BytesIO(raw)) as z:
  ns=z.namelist();assert len(ns)==len(set(ns))
  assert all(not n.startswith('/') and '..' not in pathlib.PurePosixPath(n).parts and '\\' not in n and ':' not in n for n in ns)
  return {n:z.read(n) for n in ns}
def main():
 p=argparse.ArgumentParser();p.add_argument('--archive',type=pathlib.Path);p.add_argument('--offline',type=pathlib.Path);p.add_argument('--out',type=pathlib.Path,required=True);a=p.parse_args()
 raw=a.archive.read_bytes() if a.archive else fetch(URL+'docs/REVIEW/software511/run1/software511-exact-return.zip')
 if sha(raw)==OUTER:
  outer=readzip(raw);assert len(raw)==352116
  raw=outer['software511-exact-return.zip']
 else:outer=None
 assert sha(raw)==INNER and len(raw)==219659
 f=readzip(raw);assert len(f)==493
 originals={n:b for n,b in f.items() if n!='ARCHIVE-MANIFEST.json'}
 assert json.loads(f['ARCHIVE-MANIFEST.json'])==oracle.inventory(originals)
 oracle.check_archive(raw,originals)
 if outer:
  # Actions' loose-file view omits the hidden marker; the closed inner ZIP retains it.
  assert {n for n in f if 'software511-return/'+n not in outer}=={'owned/.recorder-root'}
  for n,b in f.items():
   if 'software511-return/'+n in outer:assert outer['software511-return/'+n]==b
  assert outer['software511-build/source.txt'].decode().strip()==TESTED
  assert outer['software511-build/run-stderr.txt']==b''
 for local,(path,h) in FILES.items():
  b=(a.offline/'252-return'/local).read_bytes() if a.offline else fetch(URL+path)
  assert sha(b)==h
 j=lambda n:json.loads(f[n])
 def sub(root):return {n[len(root)+1:]:b for n,b in f.items() if n.startswith(root+'/')}
 runtime=j('RUNTIME.json');assert runtime['source']==TESTED and runtime['host_cpu_count']==4
 assert runtime['recorder_sha256']==FILES['recorder.py'][1] and runtime['adapter_sha256']==FILES['driver.py'][1]
 assert abs(runtime['conservative_cpu_seconds_including_build_reserve']-(600+runtime['wall_seconds']*4))<1e-8
 assert runtime['conservative_cpu_seconds_including_build_reserve']<7200
 imported=j('IMPORT.json');assert imported['author']=='72278bde6747c316fa8d4dcf8bd03490b88a38cd' and imported['merge']=='8fbd72c9294178e5017c9dd0ac1a121e4d30ffe5' and imported['tree']=='c370a4e975fe506d884abaacca493cf417e09c5d'
 method={n:(METHOD/n).read_bytes() for n in imported['files']};assert len(method)==9
 assert oracle.inventory(method)==imported['files']
 pins=json.loads(pathlib.Path(__file__).with_name('INPUTS.json').read_text(encoding='utf-8'))
 assert {x['name'] for x in pins['import_files']}==set(method)
 for x in pins['import_files']:
  b=method[x['name']];assert len(b)==x['size'] and hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==x['sha']
 tree=b''.join(b'100644 '+n.encode()+b'\0'+bytes.fromhex(hashlib.sha1(b'blob '+str(len(method[n])).encode()+b'\0'+method[n]).hexdigest()) for n in sorted(method))
 assert hashlib.sha1(b'tree '+str(len(tree)).encode()+b'\0'+tree).hexdigest()==pins['method_tree']
 assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==pins['durable_git_blob']
 rows=j('OBSERVATIONS.json');frozen=cases.corpus();assert len(rows)==32 and {r['name'] for r in rows}=={r['name'] for r in frozen}
 command_roots=sorted({n.rsplit('/',1)[0] for n in f if re.fullmatch(r'commands/\d{4}/launch.json',n)})
 assert command_roots==['commands/'+str(i).zfill(4) for i in range(39)]
 launches={}
 for root in command_roots:
  c=j(root+'/launch.json');t=j(root+'/timing.json');e=j(root+'/exit.json')
  assert c['source']==TESTED and c['pid']>0 and c['parent_pid']>0 and c['argv'][1]=='-B' and c['argv'][2].endswith('/host/evidence-recorder/recorder.py')
  assert type(e['code']) is int
  assert all(type(t[k]) is int and t[k]>=0 for k in ('start_ns','end_ns','duration_ns','cpu_ns'))
  assert t['end_ns']-t['start_ns']==t['duration_ns'] and t['finalized'] is True
  launches[root]=c
 assert len({c['pid'] for c in launches.values()})==39 and len({c['parent_pid'] for c in launches.values()})==1
 child_pids=[];counts={};used=set();mutations=0
 good=next(r for r in rows if r['name']=='complete-text');positive=sub(good['evidence_root']);original_request=j(good['original_request'])
 for row in rows:
  name=row['name'];spec=next(r for r in frozen if r['name']==name);assert row['observed']==spec['expected']
  counts[spec['kind']]=counts.get(spec['kind'],0)+1
  request=j(row['original_request']);assert request['source_commit']==TESTED and request['binary_sha256']==runtime['binary_sha256'] and request['helper_sha256']==sha(method['helper.py'])
  codes=[]
  for root in row['commands']:
   assert root not in used;used.add(root);c=launches[root];codes.append(j(root+'/exit.json')['code'])
   if spec['kind']!='actual-positive-archive-corruption':assert c['argv'][c['argv'].index('--request')+1].endswith('/'+row['original_request'])
  evidence=sub(row['evidence_root'])
  if spec['kind']=='actual-helper':
   assert codes==[0,0];oracle.check_complete(evidence,request);child_pids.append(j(row['evidence_root']+'/launch.json')['pid'])
   before=j('censuses/'+name+'-before.json');after=j('censuses/'+name+'-after.json');assert all(after.get(n)==v for n,v in before.items())
   assert launches[row['commands'][0]]['argv'][3]=='record' and launches[row['commands'][1]]['argv'][3]=='validate'
  elif spec['kind']=='actual-interruption':
   assert len(codes)==1 and codes[0]!=0 and row['evidence_root']=='owned/incomplete/'+name
   assert 'MANIFEST.json' not in evidence and not sub('owned/cases/'+name)
   assert j(row['evidence_root']+'/request.json')==request and sha(evidence['input.bin'])==request['input_sha256']
   launch=j(row['evidence_root']+'/launch.json');child_pids.append(launch['pid'])
   assert launch['argv']==request['argv'] and launch['nonce']==request['nonce']
   h,body=evidence['stdout.bin'].split(b'\n',1);assert json.loads(h)==dict(pid=launch['pid'],nonce=request['nonce'],input_sha256=request['input_sha256'],input_bytes=len(evidence['input.bin']))
   assert body==b'helper-output\n' and evidence['stderr.bin']==b'helper-diagnostic\n'
   before=j('censuses/'+name+'-before.json');after=j('censuses/'+name+'-after.json');assert all(after.get(n)==v for n,v in before.items())
   if name=='producer-killed-after-ready':
    k=j(name+'-kill.json');assert k['target_pid']==launch['pid'] and k['supervisor_pid']==launches[row['commands'][0]]['pid']
    assert k['ready_sha256']==sha(b'READY\n') and bytes.fromhex(k['observed_stdout_hex'])==evidence['stdout.bin'] and bytes.fromhex(k['observed_stderr_hex'])==evidence['stderr.bin']
    assert j(row['evidence_root']+'/exit.json')['code']==-9
   elif name=='recorder-killed-after-ready':
    cr=row['commands'][0];k=j(cr+'/kill-command.json');assert k['actions']==[['Popen.kill',launches[cr]['pid']],['os.kill',launch['pid'],9]]
    assert codes==[-9] and f[cr+'/observed-prefix.bin']==evidence['stdout.bin']
    assert j(cr+'/before-kill.json')['observed']==oracle.inventory(evidence)
   else:assert j(row['evidence_root']+'/exit.json')['code']==0 and j(row['evidence_root']+'/timing.json')['finalized'] is True
  elif spec['kind']=='actual-exclusive-path':
   assert codes==[2] and j('censuses/'+name+'-before.json')==j('censuses/'+name+'-after.json')
   if name=='path-traversal':assert f['sibling-sentinel.bin']==b'preserve sibling\n' and not sub('escape')
  elif spec['kind']=='actual-positive-copy-corruption':
   assert codes==[2];recipe=j('recipes/'+name+'.json');assert recipe['before']==oracle.inventory(positive) and recipe['after']==oracle.inventory(evidence)
   assert recipe['internally_rehashed']==(name!='stale-timing-checksum')
   if name!='stale-timing-checksum':assert json.loads(evidence['MANIFEST.json'])==oracle.inventory({n:b for n,b in evidence.items() if n!='MANIFEST.json'})
   try:oracle.check_complete(evidence,original_request)
   except (AssertionError,KeyError,ValueError):pass
   else:raise AssertionError('actual mutant admitted '+name)
   mutations+=1
  else:
   assert spec['kind']=='actual-positive-archive-corruption' and codes==[2]
   try:oracle.check_archive(f['archive-controls/'+name+'.zip'],positive)
   except (AssertionError,KeyError,ValueError,zipfile.BadZipFile):pass
   else:raise AssertionError('actual archive mutant admitted '+name)
   mutations+=1
 assert len(set(child_pids))==10
 oracle.check_archive(f['archive-controls/original.zip'],positive)
 # The separate good-archive positive is not one of the32 frozen outcome rows.
 extra=set(command_roots)-used;assert len(extra)==1
 cr=extra.pop();assert launches[cr]['argv'][3]=='archive-validate' and j(cr+'/exit.json')['code']==0
 result=dict(candidate=HEAD,tested=TESTED,run=39622114845,artifact=12354982078,inner_sha256=INNER,inner_bytes=219659,original_files=493,inventory_entries=492,frozen_outcomes=32,actual_commands=39,actual_children=10,counts=counts,actual_copy_archive_rejections=mutations,cpu_reservation_seconds=runtime['conservative_cpu_seconds_including_build_reserve'],scope='Linux Python frozen helper protocol; ordinary owned namespace; no arbitrary-program semantics/security/power-loss/native claim',component_disposition='PASS bounded recorder protocol; exact source review and conditional integration boundary in README')
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n');print(json.dumps(result,sort_keys=True))
if __name__=='__main__':main()
