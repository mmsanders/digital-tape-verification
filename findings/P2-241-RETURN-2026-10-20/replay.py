"""Raw-only independent replay: two faults, no new native invocation/campaign."""
import argparse,collections,copy,gzip,hashlib,importlib.util,io,json,pathlib,re,struct,sys,zipfile
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--artifact',type=pathlib.Path,required=True)
ap.add_argument('--out',type=pathlib.Path,required=True);a=ap.parse_args()
sha=lambda b:hashlib.sha256(b).hexdigest()
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
M=module('frozen_model241',ROOT/'tests/wp10_subset_r1/model.py')
assert hashlib.sha1(b'blob '+str(len((ROOT/'tests/wp10_subset_r1/model.py').read_bytes())).encode()+b'\0'+(ROOT/'tests/wp10_subset_r1/model.py').read_bytes()).hexdigest()=='f44edafd2c81fc58d51afbd46a6a4807e3555f59'
sys.path.insert(0,str(ROOT/'findings/P2-SUBSET-ROWS-2026-10-17'))
J=module('frozen_state241',ROOT/'findings/P2-SUBSET-ROWS-2026-10-17/load_rows.py')
O=module('frozen_fault241',ROOT/'tests/wp10_narrow_supplement_r1/oracle.py')
assert sha((ROOT/'tests/wp10_narrow_supplement_r1/oracle.py').read_bytes())=='61b84674df7b8135478b8c95f841c2f204ecc0b08a56b66f15e6152dd9f383d0'
assert sha((ROOT/'findings/P2-SUBSET-ROWS-2026-10-17/load_rows.py').read_bytes())=='6d0fc32e3055dfa529bf02ca4c98c5353f7f1c8d12d5497e5d25a53d843c1e97'
N=module('frozen_provenance241',ROOT/'tests/wp10_missing_faults_r1/oracle.py')
PLAN=N.PLAN
outer=a.artifact.read_bytes();assert len(outer)==5482797 and sha(outer)=='02389ab47800f889fc5a7cc842069f6ffe19deb68e641e89bebaf8039b3bf6ed'
oz=zipfile.ZipFile(io.BytesIO(outer));raw=oz.read('_temp/software501-exact-return.zip')
assert len(raw)==3370251 and sha(raw)=='eb7fcf40f00e3ad0201657ccae88016b8705b6ca0877d496fe6dbf1b16730db7'
z=zipfile.ZipFile(io.BytesIO(raw));names=z.namelist();assert len(names)==len(set(names))==4438
assert all(not n.startswith('/') and '..' not in pathlib.PurePosixPath(n).parts and '\\' not in n for n in names)
files={n:z.read(n) for n in names};inv=json.loads(files['FILES.json'])
assert set(inv)==set(names)-{'FILES.json'}
for n,p in inv.items():assert len(files[n])==p['bytes'] and sha(files[n])==p['sha256'],n
for n in names:assert oz.read('_temp/software501-raw/'+n)==files[n]
get=lambda n:json.loads(files[n])
initial=gzip.decompress(files['initial.img.gz']);assert len(initial)==33554432 and sha(initial)==PLAN['initial_sha256']
voice=files['source.wav'];assert sha(voice)==PLAN['source_wav_sha256']
assert files['pcm/'+sha(voice)+'.wav']==voice
empty=J.wav(b'');assert files['pcm/'+sha(empty)+'.wav']==empty
baseline=[json.loads(l) for l in files['original-baseline.jsonl'].splitlines()]
assert sha(files['original-baseline.jsonl'])==PLAN['original_complete_trace_sha256'] and len(baseline)==405
catalog=json.loads((ROOT/'tests/wp10_missing_faults_r1/BASELINE.json').read_bytes())
prefix=b'';barriers=[]
for i,(e,c) in enumerate(zip(baseline,catalog)):
 assert c['trace_index']==i and c['successful_prefix_sha256']==sha(prefix) and c['prior_successful_barriers']==barriers
 if e['t']=='W':assert c['ordinal']==e['call'] and c['lba']==e['lba'] and c['payload_sha256']==sha(bytes.fromhex(e['hex']))
 else:assert c['ordinal']==e['ord'];barriers.append(e['ord'])
 prefix+=json.dumps(e,sort_keys=True).encode()+b'\n'

def trace(seam):
 result=[];wi=fi=0
 for e in seam['events']:
  if e['kind']=='write':
   assert e['bytes']==512 and e['offset']%512==0 and len(bytes.fromhex(e['data_hex']))==512
   result.append(dict(t='W',id=wi,call=wi,lba=e['offset']//512,ack=e['ok'],phase='op',hex=e['data_hex']));wi+=1
  elif e['kind']=='flush':result.append(dict(t='F',ord=fi,ok=e['success'],phase='op'));fi+=1
 return result

commands={};loads=[];readbacks=0
for n in sorted(n for n in names if n.startswith('commands/') and n.endswith('/PROCESS.json')):
 r=get(n);p=n.rsplit('/',1)[0];argv=r['argv'];cmd=argv[1]
 assert argv[0]=='/home/runner/work/_temp/source501/build/host/tapectl-test'
 assert r['proxy_argv'][1:]==argv[1:]
 syscalls=files[p+'/syscalls.txt'].decode()
 if cmd=='provision':assert r['exit']==0 and r['input_before_sha256'] is None and r['input_after_sha256']==sha(initial);continue
 seam=get(p+'/seam.json');assert seam['argv']==argv[1:] and seam['exit']==r['exit']
 assert seam['build']==PLAN['prior_actual'] and seam['target_kind']=='image' and not seam['target_is_device']
 assert seam['target']==argv[2] and argv[2] in syscalls
 assert r['seam']==p+'/seam.json' and r['syscalls']==p+'/syscalls.txt'
 if cmd=='load':
  assert r['input_before_sha256']==sha(initial)
  assert argv[3]=='/home/runner/work/_temp/source501/tests/golden/src/voice.wav'
  assert re.search(r'openat\([^\n]*"'+re.escape(argv[3])+r'", O_RDONLY\)',syscalls)
  loads.append((r,seam,syscalls,p));continue
 assert cmd in ('verify','dump');readbacks+=1
 assert r['input_before_sha256']==r['input_after_sha256']
 assert seam['writes']==seam['flushes']==0
 assert not any(e['kind'] in ('write','flush') for e in seam['events'])
 binds=[e for e in seam['events'] if e['kind']=='engine_bind']
 mounts=[e for e in seam['events'] if e['kind']=='engine_mount']
 assert binds and mounts and all(e['cold'] and e['result']=='TAPE_OK' for e in mounts)
 if cmd=='verify':assert all(e['write_is_null'] for e in binds)
 else:
  b=files['pcm/'+r['wav_sha256']+'.wav'];assert sha(b)==r['wav_sha256'] and b in (voice,empty)
 key=(r['input_before_sha256'],'verify' if cmd=='verify' else 'dump_'+argv[argv.index('--side')+1],sha(files[p+'/seam.json']))
 commands.setdefault(key,[]).append((r,seam,p))
assert readbacks==825 and len(loads)==3
assert [s['fault'] for r,s,sc,p in loads]==['','write-error:19','write-error:63']
assert trace(loads[0][1])==baseline
positive=get('faults/none/record.json');assert positive['exit']==0 and J.check(positive['post_failure_remount'])=='new/new'
assert positive['op_calls']==353 and positive['op_barriers']==52

def observation(o):
 state=J.check(o);h=o['projection_sha256']
 assert o['fresh_image_per_command'] is True
 for label in ('verify','dump_A','dump_B'):
  q=o[label];key=(h,label,q['seam_trace_sha256']);assert key in commands,(h,label)
  candidates=commands[key]
  for r,seam,p in candidates:
   assert r['exit']==q['exit'] and files[p+'/stdout.bin'].decode()==q['stdout'] and files[p+'/stderr.bin'].decode()==q['stderr']
   assert q['image_sha256_before']==q['image_sha256_after']==h
   assert q['engine']==[e for e in seam['events'] if e['kind'] in ('engine_bind','engine_mount','engine_info')]
   if label!='verify':assert r['wav_sha256']==q['wav_sha256']
 return state
observation(positive['post_failure_remount'])
ledger=get('LEDGER.json');assert [x['coordinate'] for x in ledger]==[dict(kind='write',ordinal=i) for i in (19,63)]
outrows=[];projection_total=0;detect=0
for i,(entry,(command,seam,syscalls,cp)) in enumerate(zip(ledger,loads[1:])):
 row=PLAN['rows'][i];assert entry['coordinate']==dict(kind=row['kind'],ordinal=row['ordinal'])
 rec=get(entry['original_record']);O.host_fault(rec);N.check(entry['provenance'],row)
 assert rec['requested']['ordinal']==row['ordinal'] and rec['actual_input_sha256']==sha(initial)
 assert rec['exit']==command['exit']==1 and sha(files[cp+'/seam.json'])==rec['seam_trace_sha256']
 assert files[cp+'/seam.json']==files['faults/write-'+str(row['ordinal'])+'/seam-trace.json']
 assert rec['stdout']==files[cp+'/stdout.bin'].decode() and rec['stderr']==files[cp+'/stderr.bin'].decode()
 t=trace(seam);assert len(t)==row['trace_index']+1 and t[:-1]==baseline[:row['trace_index']]
 attempt=t[-1];assert not attempt['ack'] and attempt['call']==row['ordinal'] and attempt['lba']==row['lba']
 assert sha(bytes.fromhex(attempt['hex']))==row['payload_sha256']
 failure=re.findall(r'pwrite64\(-1, "([^\n]*)", 512, '+str(row['lba']*512)+r'\) = -1 EBADF[^\n]*',syscalls)
 assert len(failure)==1,'missing exact native -1/EBADF512-byte write'
 # strace uses C octal/control escapes. Decode its full untruncated 512-byte payload.
 encoded=failure[0];assert '...' not in encoded
 def unescape(s):
  out=bytearray();j=0;esc={'n':10,'r':13,'t':9,'b':8,'f':12,'v':11,'a':7,'\\':92,'"':34}
  while j<len(s):
   if s[j]!='\\':out.append(ord(s[j]));j+=1;continue
   j+=1;m=re.match('[0-7]{1,3}',s[j:])
   if m:out.append(int(m[0],8));j+=len(m[0])
   else:out.append(esc[s[j]]);j+=1
  return bytes(out)
 assert unescape(encoded)==bytes.fromhex(attempt['hex'])
 assert [e['ord'] for e in t[:-1] if e['t']=='F' and e['ok']]==row['prior_successful_barriers']
 assert sha(b''.join(json.dumps(e,sort_keys=True).encode()+b'\n' for e in t[:-1]))==row['successful_prefix_sha256']
 dev=M.Device({k:initial[k*512:(k+1)*512] for k in range(len(initial)//512)})
 for e in t:
  if e['t']=='W':dev.write(e['lba'],bytes.fromhex(e['hex']),acknowledged=e['ack'],**({} if e['ack'] else {'visible':[]}))
  else:dev.flush(successful=e['ok'])
 working=b''.join(dev.working.get(k,bytes(512)) for k in range(len(initial)//512))
 after=gzip.decompress(files['faults/write-'+str(row['ordinal'])+'/image-after.img.gz'])
 assert working==after and sha(after)==rec['image_after_sha256']==command['input_after_sha256']==entry['working_reconstruction_sha256']
 assert observation(rec['post_failure_remount'])==entry['working_state']=='empty/empty'
 orders=list(M.exhaustive(dev.events));assert len(orders)==entry['model_orders']==(16 if i==0 else 256)
 assert sha(b''.join(json.dumps(p['landing_order'],sort_keys=True,separators=(',',':')).encode()+b'\n' for p in orders))==entry['model_orders_sha256']
 expected={};first={};selected={}
 durable=b''.join(dev.durable.get(k,bytes(512)) for k in range(len(initial)//512))
 for p in orders:
  image=bytearray(durable)
  for ev in [next(e for e in dev.events if e.id==eid) for eid in p['landing_order']]:image[ev.lba*512:(ev.lba+1)*512]=ev.data
  h=sha(image);expected.setdefault(h,p['landing_order'])
  o=get('projections/'+h+'/observation.json');assert o['projection_sha256']==h
  state=observation(o);first.setdefault(state,[]).append(h)
  if any(e.get('needs_repair') for label in ('verify','dump_A','dump_B') for e in o[label]['engine'] if e['kind']=='engine_info'):selected.setdefault(h,[]).append('needs_repair')
 assert {x['image_sha256']:x['landing_order'] for x in entry['projections']}==expected
 for state,hs in first.items():selected.setdefault(min(hs),[]).append('first '+state)
 assert selected==entry['selected']
 for h in selected:assert sha(gzip.decompress(files['projections/'+h+'/projection.img.gz']))==h
 projection_total+=len(expected)
 # Mutate actual provenance and original allowed-state observations, without native reruns.
 for key,value in [('successful_prefix_sha256','0'*64),('failure_actual_return_bytes',1),('prior_successful_barriers',[])]:
  bad=copy.deepcopy(entry['provenance']);bad[key]=value
  try:N.check(bad,row)
  except AssertionError:detect+=1
  else:raise AssertionError('provenance corruption escaped')
 bad=copy.deepcopy(rec['post_failure_remount']);bad['dump_A']['wav_sha256']=sha(voice);bad['dump_B']['wav_sha256']=sha(empty)
 try:J.check(bad)
 except AssertionError:detect+=1
 else:raise AssertionError('forbidden new/empty state escaped')
 outrows.append(dict(kind='write',ordinal=row['ordinal'],native_error='EBADF',attempted_bytes=512,landed_bytes=0,
  prior_barriers=row['prior_successful_barriers'],state='empty/empty',model_orders=len(orders),projections=len(expected),cpu_seconds=round(entry['actual_cpu_seconds'],6)))
result=get('RESULT.json');assert result['remaining']==PLAN['rows'][2:] and result['executed']==2
assert ledger[0]['actual_cpu_seconds']<=120<ledger[1]['actual_cpu_seconds']
assert result['cpu_seconds_including_600_build_reserve']<7200 and 'stop before next' in result['stop']
review=dict(candidate='cd4fdae796496a47be7756e21a11d9666f94deb2',source=PLAN['prior_actual'],
 artifact=12325916869,outer_sha256=sha(outer),inner_sha256=sha(raw),raw_files=4438,raw_command_records=829,
 readback_command_records=readbacks,positive_complete_events=405,rows=outrows,
 original_model_orders=projection_total,detecting_actual_controls=detect,
 retained_previous_executed=39,new_independently_passed=2,executed_coverage_after_publication=41,
 unexecuted_coordinates=363,selected_unexecuted=23,unselected_unexecuted=340,
 stop_before=dict(kind='write',ordinal=64),cpu_including_build_reserve=result['cpu_seconds_including_600_build_reserve'],
 durable_transport='existing authenticated Actions evidence; specific durable release approval pending',
 overall443_accepted=False,integration_permission=False,
 disposition='two actual coordinate predicates PASS, mandatory estimate stop honored; remaining scope and durable transport HELD')
a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(review,indent=2)+'\n',newline='\n');print(json.dumps(review,indent=2))
