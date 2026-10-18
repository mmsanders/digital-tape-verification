"""Windows-only causal control of the exact returned script's summary/ZIP tail.
Synthetic packets, actual pinned summarizer; no Product executable or card access.
Exit zero means the known fail-open defect was reproduced, NOT readiness PASS.
"""
import hashlib,json,pathlib,subprocess,sys,urllib.request
P=pathlib.Path
root=P('verification204-results').resolve();root.mkdir(exist_ok=True)
source='https://raw.githubusercontent.com/mmsanders/Digital-Tape/50bc4160f6da527da8c684d05264f99815aaa870/host/ingest/stage1/'
def fetch(name,sha):
 b=urllib.request.urlopen(source+name).read();assert hashlib.sha256(b).hexdigest()==sha
 (root/name).write_bytes(b);return b.decode()
s=fetch('win11_packet.ps1','9d8506670df30bbbc547c6c5757d9370e152ed55cfa4cd8378bd9e1f1337f502')
fetch('summarize_packet.py','dd18e797210da43021f1bac187bfdeb7b6a5f6ae7e9ae18d3098de8f9cf79f4a')
tail=s[s.index('& $python -B (Join-Path $stage1 "summarize_packet.py")'):]
rows=[]
def quote(p):return "'"+str(p).replace("'","''")+"'"
for name,missing in [('complete',False),('missing-census-record',True)]:
 d=root/name;d.mkdir(exist_ok=True);packet=d/'packet';packet.mkdir(exist_ok=True);pkg=d/'package';pkg.mkdir(exist_ok=True)
 (pkg/'CENSUS.json').write_text(json.dumps({'cases':[{'id':'synthetic','expected_exit':0}]}))
 (packet/'record.json').write_text(json.dumps({'exit':0}))
 index={'cases':{} if missing else {'synthetic':'record.json'},'platform':'synthetic','architecture':'x64','observer':'none','profile':'synthetic','candidate_sha':'synthetic','binary_sha256':'none','config_sha256':'none'}
 (packet/'INDEX.json').write_text(json.dumps(index))
 args=[sys.executable,'-B',str(root/'summarize_packet.py'),str(packet),'--package',str(pkg)]
 child=subprocess.run(args,capture_output=True,text=True)
 pre='$ErrorActionPreference = "Stop"\nfunction Sha($p) { (Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLower() }\n'
 for k,v in [('python',sys.executable),('stage1',root),('packet',packet),('pkg',pkg),('Out',d),('Candidate','50bc4160f6da527da8c684d05264f99815aaa870')]: pre+='$'+k+' = '+quote(v)+'\n'
 script=d/'exact-tail.ps1';script.write_text(pre+tail)
 cmd=['powershell.exe','-NoProfile','-File',str(script)]
 r=subprocess.run(cmd,capture_output=True,text=True)
 (d/'stdout.txt').write_text(r.stdout);(d/'stderr.txt').write_text(r.stderr)
 row={'control':name,'direct_summary_exit':child.returncode,'tail_exit':r.returncode,'packet_created':(d/'ingest-win11-packet-50bc4160f6da.zip').exists(),'send_instruction':'Send this zip' in r.stdout,'command':cmd}
 rows.append(row)
assert rows[0]['direct_summary_exit']==0 and rows[0]['tail_exit']==0 and rows[0]['packet_created']
assert rows[1]['direct_summary_exit']==1 and rows[1]['tail_exit']==0 and rows[1]['packet_created'] and rows[1]['send_instruction']
(root/'RESULT.json').write_text(json.dumps({'scope':'exact original tail, actual pinned summarizer, synthetic packet; Server mechanics only','disposition':'RED: summary failure ignored','controls':rows},indent=2)+'\n')
print(json.dumps(rows,indent=2))
