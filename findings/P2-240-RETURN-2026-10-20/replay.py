"""Independent raw replay of frozen ordinary-file boundary returns; no Product run."""
import argparse,copy,hashlib,io,json,pathlib,re,struct,sys,zipfile
from decimal import Decimal
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--artifact',type=pathlib.Path,required=True)
ap.add_argument('--out',type=pathlib.Path,required=True);a=ap.parse_args()
sha=lambda b:hashlib.sha256(b).hexdigest()
outer=a.artifact.read_bytes()
assert len(outer)==480262 and sha(outer)=='15f689dfcc9c473789d75eab4902eed5492ca5ce91b332bef408db5c551fdea5'
oz=zipfile.ZipFile(io.BytesIO(outer));raw=oz.read('_temp/software500-exact-return.zip')
assert len(raw)==297029 and sha(raw)=='108ad9bfe7036605e0405e52c46f9065fb6028244bb953b276f694d3faa0476c'
z=zipfile.ZipFile(io.BytesIO(raw));names=z.namelist()
assert len(names)==len(set(names))==260
assert all(not n.startswith('/') and '..' not in pathlib.PurePosixPath(n).parts and '\\' not in n for n in names)
inv=json.loads(z.read('FILES.json'));assert set(inv)==set(names)-{'FILES.json'}
for n,p in inv.items():
 b=z.read(n);assert len(b)==p['bytes'] and sha(b)==p['sha256'],n
for n in names:
 outername='_temp/software500-raw/'+n
 assert oz.read(outername)==z.read(n),n
sys.path.insert(0,str(ROOT/'tests/wp16_join_boundary_r1'))
import cases
sys.path.insert(0,str(ROOT/'tests/wp16_ingest_stage1'))
import model
assert sha((ROOT/'tests/wp16_ingest_stage1/model.py').read_bytes())=='4dfc0d0987eea047968db046e088e4124dcc55ca47a618f66fa51ea9cea1e9d9'
build='Digital-Tape/Digital-Tape/shipping-build/'
assert sha(oz.read(build+'Cargo.lock'))=='6e8d14c97dc59d4e627e68f37d6647c45e7f6d52de5e3c51653239993ad0f864'
assert b'rustc 1.97.0' in oz.read(build+'rustc.txt')
assert b'User time (seconds): 25.03' in oz.read(build+'build-time.txt')
assert b'System time (seconds): 2.19' in oz.read(build+'build-time.txt')
assert b'Exit status: 0' in oz.read(build+'build-time.txt')
rows=cases.corpus();frozen=[cases.facts(c) for c in rows]
assert frozen==json.loads((ROOT/'tests/wp16_join_boundary_r1/MANIFEST.json').read_bytes())
assert json.loads(z.read('MANIFEST.json'))==frozen
assert z.read('REFERENCE.json')==(ROOT/'tests/wp16_join_boundary_r1/REFERENCE.json').read_bytes()
ledger=json.loads(z.read('LEDGER.json'));assert len(ledger)==17
assert [r['name'] for r in ledger]==[c['name'] for c in rows][1:]
assert not any(n.startswith('endpoint-1/') for n in names)
version=z.read('version.stdout').decode().strip()
assert version=='ingest 0.1.1 INGEST-1 arithmetic-profile INGEST1-AP4'
assert z.read('version.stderr')==b''
seen_pcm={};results=[];source_count=0;gain_zero_exact=0;attenuated=0

def check_case(c,f,r,override=None):
 name=c['name'];prefix=name+'/'
 def read(n):return z.read(prefix+n)
 assert json.loads(read('PROCESS.json'))==r
 assert r['exit']==0 and r['refusal'] is None and r['stages']==[]
 expected_root='/home/runner/work/_temp/software500-raw/'+name
 assert r['argv']==['/home/runner/work/_temp/source500/host/ingest/target/release/ingest',
  '--report',expected_root+'/report.jsonl','--report-nonce',r['nonce'],
  '--out',expected_root+'/published','--length','30']+[expected_root+'/folder'+str(i) for i in range(len(c['folders']))]
 assert re.fullmatch('[0-9a-f]{32}',r['nonce'])
 report=[json.loads(l) for l in read('report.jsonl').splitlines()]
 assert report[0]==dict(t='start',tool='ingest',version=version.removeprefix('ingest '),nonce=r['nonce'])
 assert report[-1]==dict(t='end',exit=0)
 assert all(x['t']=='progress' for x in report[1:-1])
 order={'list':0,'decode':1,'convert':2,'write':3,'publish':4};last=(-1,-1)
 for x in report[1:-1]:
  assert set(x)=={'t','step','done','total'} and type(x['done']) is type(x['total']) is int
  assert 0<=x['done']<=x['total'] and (order[x['step']],x['done'])>=last
  last=(order[x['step']],x['done'])
 assert report[-2]==dict(t='progress',step='publish',done=1,total=1)
 assert read('stderr.bin')==b'' and read('stdout.bin').startswith(b'ingest: wrote ')
 mraw=read('published/manifest.json');m=json.loads(mraw)
 wav=read('published/audio.wav');pcm=wav[44:]
 if override is not None:pcm=override
 assert wav[:44]==model.wav(pcm)[:44]
 source_facts=[];folders=[];chunks=[];exact=limited=0
 for folder in c['folders']:folders.append([f'source{j+1:02d}.wav' for j in range(len(folder))])
 for fact,s in zip(f['sources'],[s for folder in c['folders'] for s in folder]):
  p='folder'+fact['path'];b=read(p)
  assert b==cases.wav(s) and sha(b)==fact['sha256'] and len(b)==fact['bytes']
  source_facts.append(dict(source_sha256=fact['sha256'],input_rate=44100,input_channels=fact['channels'],
   raw_frames=fact['frames'],effective_frames=fact['frames'],trim_head=0,trim_tail=0,trim_evidence='none'))
 model.check_manifest(mraw,pcm,source_facts,folders,30)
 assert m['total_frames']==f['total_frames'] and m['gaps']==f['gaps']
 assert m['build_profile']=='INGEST1-AP4'
 assert {n[len(prefix+'published/'):] for n in names if n.startswith(prefix+'published/')}=={'audio.wav','manifest.json'}
 for fact,source,ms in zip(f['sources'],[s for folder in c['folders'] for s in folder],m['sources']):
  assert ms['container']=='wav' and ms['codec']=='pcm' and ms['codec_profile']=='s16le'
  assert ms['input_lufs'] is ms['output_lufs'] is ms['target_gain_db'] is None
  assert ms['loudness_status']=='unmeasurable' and ms['loudness_reason']=='too_short'
  gain=Decimal(ms['applied_gain_db']);assert gain<=0
  assert Decimal(ms['output_dbtp'])+Decimal('0.1')<=Decimal('-1')
  block=pcm[fact['start_frame']*4:(fact['start_frame']+fact['frames'])*4]
  assert block==read('converted-'+fact['path'].replace('/','-')+'.pcm')
  if fact['channels']==1:assert all(l==rr for l,rr in struct.iter_unpack('<hh',block))
  if gain==0 and ms['peak_limited'] is False:
   # A conditional check of the declared identity/no-boost branch, using the
   # already-published independent exact integer quantizer. Rounded gain alone
   # does not establish that this was the internal full-precision scalar.
   samples=struct.iter_unpack('<h' if fact['channels']==1 else '<hh',cases.wav(source)[44:])
   expected=model.quantize(([v/32768 for v in x] for x in samples),mono=fact['channels']==1)
   assert expected==block;exact+=1
  else:limited+=1
  chunks.append((fact['sha256'],block))
 # Original before/after observations bind unchanged input/sentinel and outputs.
 assert read('foreign-sentinel.txt')==b'Software500 foreign ordinary file; preserve exactly\n'
 for n,pin in r['before'].items():
  b=read(n);assert len(b)==pin['bytes'] and sha(b)==pin['sha256'] and r['after'][n]==pin
 for n,pin in r['after'].items():
  b=read(n);assert len(b)==pin['bytes'] and sha(b)==pin['sha256']
 assert not any('.ingest-stage-' in n for n in names if n.startswith(prefix))
 return chunks,exact,limited

for c,f,r in zip(rows[1:],frozen[1:],ledger):
 chunks,exact,limited=check_case(c,f,r)
 for key,b in chunks:
  if key in seen_pcm:assert seen_pcm[key]==b,'same source reset mismatch'
  seen_pcm[key]=b
 source_count+=len(chunks);gain_zero_exact+=exact;attenuated+=limited
 results.append(dict(name=c['name'],exit=0,sources=len(chunks),frames=f['total_frames']))
# Detect actual-output and report-binding corruption using the same checks.
controls=0
for i in [0,3,5,13]:
 c,f,r=rows[i+1],frozen[i+1],ledger[i]
 bad=bytearray(z.read(c['name']+'/published/audio.wav')[44:]);bad[0]^=1
 try:check_case(c,f,r,bytes(bad))
 except AssertionError:controls+=1
 else:raise AssertionError('actual PCM corruption escaped')
summary=json.loads(z.read('RESULT.json'))
assert summary['executed']==17 and summary['remaining']==['endpoint-1'] and summary['failures']==[]
out=dict(candidate='b9866c77228f4ad3832e0e46083fdc8e5aa76aa6',source=summary['source'],
 artifact=12324892347,outer_sha256=sha(outer),inner_sha256=sha(raw),
 original_files=260,closed_inventory_files=259,scheduled=18,usable_commands=17,
 missing_raw=['endpoint-1'],source_occurrences=source_count,
 zero_gain_branch_exact_quantizer_checks=gain_zero_exact,attenuated_source_slices=attenuated,
 actual_output_corruptions_detected=controls,run_cpu_seconds=round(summary['cpu_seconds'],6),
 first_attempt_conservative_cpu_seconds=60,second_build_cpu_seconds=27.22,
 findings=results,global_witness=False,global_absence_proved=False,integration_permission=False,
 disposition='17-case structural/report/output coverage PASS; full18-case/analytical/durable-transport criteria HELD',
 limitations=['endpoint-1 original raw lost, no credit or rerun',
 'rounded gain and assembled PCM slices do not independently prove full-precision per-source gain/meter execution',
 'independent reference is not a Product f32/local/global/refinement transfer theorem',
 'durable raw release upload awaits destination-specific approval; existing Actions evidence only'])
a.out.parent.mkdir(parents=True,exist_ok=True)
a.out.write_text(json.dumps(out,indent=2)+'\n',newline='\n')
print(json.dumps(out,indent=2))
