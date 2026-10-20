"""Retained Windows11 evidence only; independent raw CSV checks; no Product imports."""
import argparse,collections,csv,gzip,hashlib,io,json,re,zipfile,copy
from pathlib import Path
import native_receipts as prior
SHA='e6d3f2b9e60e93bc90a7516e66418da301c4c0dc3a306dfea3e1394a81731ff3'
HEAD='50bc4160f6da527da8c684d05264f99815aaa870'
def sha(b):return hashlib.sha256(b).hexdigest()
def norm(s):return re.sub(r'[\\/]+','/',s).casefold()
def rowhash(row):return sha(json.dumps(row,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())
def parse(raw):return list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'),newline='')))
def body(row):return {k:v for k,v in row.items() if k!='Index'}
def probe_checks(rows):
 ops=lambda op:[r for r in rows if r['Operation']==op and r['Result']=='SUCCESS']
 starts=ops('Process Start');exits=ops('Process Exit')
 assert len({r['PID'] for r in starts})>=2
 assert any('probe-child' in r['Process Name'] for r in starts)
 assert any('Exit Status: 0' in r['Detail'] for r in exits)
 probe=[r for r in ops('CreateFile') if r['Path'].endswith('probe.txt')]
 assert len(probe)>=2
 assert any(r['Path'].endswith('created.txt') for r in ops('CreateFile'))
 assert any('Harddisk0' in r['Path'] and r['Operation']=='CreateFile' and r['Result']=='SUCCESS' for r in rows)
 return True
def run(packet,out):
 with packet.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==SHA
 with zipfile.ZipFile(packet) as z:
  assert len(z.namelist())==len(set(z.namelist()))
  assert all('..' not in n.replace('\\','/').split('/') and ':' not in n and not n.startswith(('/','\\')) for n in z.namelist())
  def raw(p):return z.read(p)
  def data(p):return json.loads(raw(p))
  index=data('INDEX.json');assert index['candidate_sha']==HEAD
  for p,k in [('config.json','config_sha256'),('platform.json','platform_sha256')]:assert sha(raw(p))==index[k]
  assert index['shipping_binary_sha256']=='d923613badda95baeb387d5415d5212a5dedb7c5c7144b21874479babd178f5b'
  assert index['binary_sha256']=='d544b6f5c82e653842625080a87ac63cb52353aaeca62494dd5d08eedb844d9a'
  rawcsv=gzip.decompress(raw('observer-session/session.csv.gz'))
  assert sha(rawcsv)==raw('observer-session/session.csv.sha256').decode().strip()
  # All row bodies are hashed; process environments are never copied to output.
  global_hash=[];global_short=[];starts=[];exits={}
  for k,r in enumerate(csv.DictReader(io.StringIO(rawcsv.decode('utf-8-sig'),newline=''))):
   global_hash.append(rowhash(r));global_short.append((r['PID'],r['Operation']))
   if r['Operation']=='Process Start' and r['Result']=='SUCCESS':
    starts.append((k,r['PID'],r['Process Name'],r['Detail'].split(', Environment:',1)[0]))
   if r['Operation']=='Process Exit' and r['Result']=='SUCCESS':exits.setdefault(r['PID'],[]).append((k,r['Detail']))
  del rawcsv
  partition=data('observer-session/partition.json');assert partition['records']==len(global_hash)
  counts=collections.Counter();seen=set();owners={norm(k):v for k,v in partition['owners'].items()}
  bindings=[];shipping_expected={};output_bindings=[];summary_controls={}
  tasks=[]
  for id,member in index['cases'].items():
   record=data(member);tasks.append((id,record['native_record'],record['raw_trace']))
   for j,c in enumerate(record.get('comparisons',[])):tasks.append((id+'/comparison/'+str(j),c['native_record'],c['raw_trace']))
   eq=record.get('shipping_equivalence')
   if eq:
    assert eq['exit']==0 and eq['shipping_binary_sha256']==index['shipping_binary_sha256']
    dest=eq['argv'][eq['argv'].index('--out')+1]
    shipping_expected[norm(dest)]=id
    for name,rpath in [('audio.wav',record['wav']),('manifest.json',record['manifest'])]:
     with z.open(rpath) as f:actual=hashlib.file_digest(f,'sha256').hexdigest()
     assert eq[name]['observe_sha256']==actual and eq[name]['shipping_sha256']==actual,(id,name)
    counts['observed_output_pairs_streamed_and_bound']+=1
    output_bindings.append((id,eq['audio.wav']['observe_sha256'],eq['manifest.json']['observe_sha256']))
  for id,np,rp in tasks:
   n=data(np);trace=raw(rp);assert sha(trace)==n['raw_trace_sha256']
   assert n['binary_sha256']==index['binary_sha256']
   rows=parse(trace);ids=[int(e['Index']) for e in rows];assert ids==sorted(set(ids))
   assert len(rows)==owners[norm(np)]
   for e in rows:
    k=int(e['Index']);assert global_hash[k]==rowhash(body(e)) and k not in seen;seen.add(k)
   pubs=prior.windows_proof(rows,n)
   counts['native_traces']+=1;counts['raw_csv_case_comparison_rows']+=len(rows)
   counts['publications']+=len(pubs);counts['flush_close_pairs']+=2*len(pubs)
   bindings.append((id,sha(trace),sha(raw(np))))
   if id=='asset/ordinary.wav':
    assert len(pubs)==1;bad=copy.deepcopy(rows)
    for e in bad:
     if e['Operation']=='SetRenameInformationFile':e['Detail']=e['Detail'].replace('ReplaceIfExists: False','ReplaceIfExists: True')
    noflush=[e for e in rows if not(e['Operation']=='FlushBuffersFile' and e['Path'].endswith('audio.wav'))]
    for label,b in [('replacement-allowed',bad),('missing-audio-flush',noflush)]:
     try:prior.windows_proof(b,n)
     except AssertionError:summary_controls[label]='REJECTED'
     else:raise AssertionError('native negative escaped '+label)
  probe=parse(raw('observer-selftest/trace.txt'));assert probe_checks(probe)
  pids={e['PID'] for e in probe if e['Operation']=='Process Start'}
  probe_ids={int(e['Index']) for e in probe}
  assert len(probe)==owners[norm('observer-selftest')]
  for e in probe:
   k=int(e['Index']);assert global_hash[k]==rowhash(body(e)) and k not in seen;seen.add(k)
  falsepass={}
  for label,c in data('observer-selftest/result.json')['false_pass_controls'].items():
   b=raw('observer-selftest/'+c['file']);assert sha(b)==c['sha256']
   ids={int(e['Index']) for e in parse(b)}
   assert ids<probe_ids
   falsepass[label]={'independent_rejection':'missing raw global indices','missing_rows':len(probe_ids-ids)}
  # Partition shipping remainder by actual global native process lifetimes.
  shipping_ranges=[];seen_shipping_dest=set()
  for k,pid,pname,detail in starts:
   matches=[(dest,id) for dest,id in shipping_expected.items() if dest in norm(detail)]
   if not matches:continue
   assert len(matches)==1 and pname.casefold()=='ingest.exe'
   dest,id=matches[0];assert dest not in seen_shipping_dest;seen_shipping_dest.add(dest)
   ends=[(at,d) for at,d in exits.get(pid,[]) if at>=k]
   assert ends and 'Exit Status: 0' in ends[0][1]
   # Tail close records may follow exit; stop ownership at the next start of same PID.
   nextstart=min([at for at,p,_,_ in starts if p==pid and at>k] or [len(global_hash)])
   shipping_ranges.append((pid,k,nextstart,id))
  assert len(shipping_ranges)==len(shipping_expected),(len(shipping_ranges),len(shipping_expected))
  shipping_counts=collections.Counter();unowned=[]
  for k,(pid,op) in enumerate(global_short):
   if k in seen:continue
   matches=[id for p,start,end,id in shipping_ranges if p==pid and start<=k<end]
   if len(matches)!=1:unowned.append(k)
   else:shipping_counts[matches[0]]+=1;seen.add(k)
  assert not unowned,('unowned',len(unowned),unowned[:5])
  assert len(seen)==len(global_hash)
  assert sum(shipping_counts.values())==sum(v for k,v in owners.items() if k.startswith('shipping:'))
  counts['global_csv_rows']=len(global_hash);counts['selftest_rows']=len(probe)
  counts['independently_partitioned_shipping_rows']=sum(shipping_counts.values())
  counts['shipping_processes_exit0']=len(shipping_ranges)
  result={'candidate':HEAD,'packet_sha256':SHA,'platform':'Windows11 x64','counts':dict(counts),
   'native_controls':summary_controls,'observer_controls':falsepass,
   'output_pair_binding_census_sha256':sha(json.dumps(sorted(output_bindings),separators=(',',':')).encode()),
   'native_trace_binding_census_sha256':sha(json.dumps(sorted(bindings),separators=(',',':')).encode()),
   'passed_scope':['full global CSV hash and every observed case/comparison/selftest row body','raw no-replace and flush-close order with detecting controls','probe child/create/open/completion positives and four dropped-trace controls','shipping root command destinations/exit0 and unique remaining native ownership','streamed observed WAV/manifest hashes including largest legal; bind recorded shipping hashes'],
   'remaining':['PML binary alignment not independently rederived','failed/zero-access device-open visibility remains bounded','exact downloaded shipping d923613b exhaustion not executed by this observation-only exhaustion row','shipping output bytes removed by collector; equality to recorded shipping digests is transport evidence, not independent readback','no unchanged full audio/numerical campaign replay','no fullWP16/native/APP/S1 integration acceptance']}
  out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('packet',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args();run(a.packet,a.out)
