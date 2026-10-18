"""Independent original/corrected transport controls; synthetic packets only.
No Product executable, Procmon or physical-device operation. Windows Server mechanics.
"""
import hashlib,json,os,pathlib,subprocess,sys,urllib.request
P=pathlib.Path
root=P('verification206-results').resolve();root.mkdir(exist_ok=True)
base='https://raw.githubusercontent.com/mmsanders/Digital-Tape/'
pins=[('original.ps1','50bc4160f6da527da8c684d05264f99815aaa870/host/ingest/stage1/win11_packet.ps1','9d8506670df30bbbc547c6c5757d9370e152ed55cfa4cd8378bd9e1f1337f502'),('corrected.ps1','e1e06fc599177872b4f5d39d46f59c8952d1c108/tools/win11-kit/win11_packet.ps1','74e1af2cb91a3f9b418363941c48a60eee972481a32cbb9af22d8f3060318f9e'),('summarize_packet.py','50bc4160f6da527da8c684d05264f99815aaa870/host/ingest/stage1/summarize_packet.py','dd18e797210da43021f1bac187bfdeb7b6a5f6ae7e9ae18d3098de8f9cf79f4a')]
texts={}
for name,url,sha in pins:
 b=urllib.request.urlopen(base+url,timeout=60).read();assert hashlib.sha256(b).hexdigest()==sha
 (root/name).write_bytes(b);texts[name]=b.decode()
old,new=texts['original.ps1'],texts['corrected.ps1']
# Independently assert that all executable body bytes outside this one guard are unchanged.
start=new.index('$summary = $LASTEXITCODE');end=new.index('\n# 8. One zip to send.',start)
new_without_guard=new[:start]+new[end:]
assert old[old.index('param('):]==new_without_guard[new_without_guard.index('param('):]
assert '-ExecutionPolicy' not in new and 'Bypass' not in new
rows=[]
def quote(v):return "'"+str(v).replace("'","''")+"'"
for variant in ['original','corrected']:
 s=texts[variant+'.ps1'];tail=s[s.index('& $python -B (Join-Path $stage1 "summarize_packet.py")'):]
 sha_helper=next(l for l in s.splitlines() if l.startswith('function Sha('))
 for kind in ['complete','missing-record','exit-mismatch','byte-difference']:
  d=root/(variant+'-'+kind);d.mkdir(exist_ok=True);packet=d/'packet';packet.mkdir(exist_ok=True);pkg=d/'package';pkg.mkdir(exist_ok=True)
  (pkg/'CENSUS.json').write_text(json.dumps({'cases':[{'id':'synthetic','expected_exit':0}]}))
  rec={'exit':1 if kind=='exit-mismatch' else 0}
  if kind=='byte-difference':rec['shipping_equivalence']={'identical':False}
  (packet/'record.json').write_text(json.dumps(rec))
  index={'cases':{} if kind=='missing-record' else {'synthetic':'record.json'},'platform':'synthetic','architecture':'x64','observer':'none','profile':'synthetic','candidate_sha':'synthetic','binary_sha256':'none','config_sha256':'none'}
  (packet/'INDEX.json').write_text(json.dumps(index))
  child=subprocess.run([sys.executable,'-B',str(root/'summarize_packet.py'),str(packet),'--package',str(pkg)],capture_output=True,text=True)
  (d/'direct-summary.stdout').write_text(child.stdout);(d/'direct-summary.stderr').write_text(child.stderr)
  pre='$ErrorActionPreference = "Stop"\n'+sha_helper+'\n'
  for k,v in [('python',sys.executable),('stage1',root),('packet',packet),('pkg',pkg),('Out',d),('Candidate','50bc4160f6da527da8c684d05264f99815aaa870')]:pre+='$'+k+' = '+quote(v)+'\n'
  script=d/'exact-tail.ps1';script.write_text(pre+tail)
  env={k:v for k,v in os.environ.items() if k.upper()!='PSMODULEPATH'}
  cmd=['powershell.exe','-NoProfile','-File',str(script)]
  r=subprocess.run(cmd,capture_output=True,text=True,env=env)
  (d/'stdout.txt').write_text(r.stdout);(d/'stderr.txt').write_text(r.stderr)
  bad=kind!='complete';expected_stop=bad and variant=='corrected'
  row={'script':variant,'case':kind,'summary_exit':child.returncode,'tail_exit':r.returncode,'zip':(d/'ingest-win11-packet-50bc4160f6da.zip').exists(),'send':'Send this zip' in r.stdout,'stopped':'STOPPED: summarize_packet.py exited 1' in r.stdout,'stderr':r.stderr,'command':cmd}
  rows.append(row)
  assert child.returncode==int(bad) and r.returncode==int(expected_stop),row
  assert row['zip']==row['send']==(not expected_stop),row
  assert not r.stderr and (not expected_stop or row['stopped']),row
# Verify the issued stdout/stderr/exit-capture block around an actual native child.
# Only the two already-synthetic complete/missing corrected tails are used.
ready=(P(__file__).resolve().parent/'WINDOWS-READY.md').read_text()
block=ready.split('```powershell')[2].split('```')[0]
wrapper_rows=[]
for kind in ['complete','missing-record']:
 d=root/('corrected-'+kind)
 # The tail already sets its private input variables; extra original script args are inert.
 (d/'win11_packet.ps1').write_bytes((d/'exact-tail.ps1').read_bytes())
 wrapper=d/'issued-capture.ps1'
 wrapper.write_text('$ErrorActionPreference = "Stop"\n$d = '+quote(d)+'\n$work = "synthetic"\n'+block)
 r=subprocess.run(['powershell.exe','-NoProfile','-File',str(wrapper)],capture_output=True,text=True,env=env)
 (d/'wrapper.stdout').write_text(r.stdout);(d/'wrapper.stderr').write_text(r.stderr)
 code=int((d/'collection-exit.txt').read_text(encoding='utf-8-sig').strip())
 stdout=(d/'collection-stdout.txt').read_bytes()
 stderr=(d/'collection-stderr.txt').read_bytes()
 assert code==int(kind!='complete') and r.returncode==code
 assert b'census 1:' in stdout
 assert not stderr
 if code:assert b'STOPPED: summarize_packet.py exited 1' in stdout
 wrapper_rows.append({'case':kind,'native_exit_recorded':code,'outer_exit':r.returncode,'stdout_stderr_preserved':True})
(root/'RESULT.json').write_text(json.dumps({'disposition':'PASS bounded transport corrections','scope':'exact tails, actual pinned summarizer, synthetic records; Windows Server mechanics only','pins':pins,'body_delta':'header plus immediate summary exit guard only','controls':rows,'issued_capture_controls':wrapper_rows},indent=2)+'\n')
print(json.dumps(rows,indent=2))
