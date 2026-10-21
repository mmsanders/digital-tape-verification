"""Authenticate original Software499 bytes and replay frozen comparisons.

No Product executable, codec, audio generation or proof oracle mutation.
The source correspondence judgments in README are manual conditional lemmas.
"""
import argparse, copy, hashlib, json, os, pathlib, sys, urllib.request

HERE=pathlib.Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SOURCE='b9f430c8c9b33532abf07eea0ed2653310639f2d'
CANDIDATE='69075205a31a2cbea4f00e142bc8b65d3437091c'
TESTED='8b689218dc06e68b6b09b6744e3e4f4e54c5ddf2'
ap=argparse.ArgumentParser()
ap.add_argument('--out',type=pathlib.Path,required=True)
ap.add_argument('--offline',type=pathlib.Path)
a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True)

def get(url):
 headers={'User-Agent':'Verification239-independent-replay'}
 if url.startswith('https://api.github.com/') and os.environ.get('GH_TOKEN'):
  headers['Authorization']='Bearer '+os.environ['GH_TOKEN']
 return urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=40).read()
def raw(path):
 if a.offline:
  name=pathlib.Path(path).name
  return (a.offline/'239-return'/('FILES.json' if name=='run1-FILES.json' else name)).read_bytes()
 return get('https://raw.githubusercontent.com/mmsanders/Digital-Tape/'+CANDIDATE+'/'+path)
def blob(b):return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def sha(b):return hashlib.sha256(b).hexdigest()
base='docs/REVIEW/software499/'
inv=raw(base+'run1-FILES.json')
assert blob(inv)=='96824d42155572f805d6e9237187e2824dfc75b3'
files=json.loads(inv);assert len(files)==11
data={}
for name,pin in files.items():
 assert '/' not in name
 b=raw(base+'run1/'+name)
 assert len(b)==pin['bytes'] and sha(b)==pin['sha256'],name
 data[name]=b;(a.out/name).write_bytes(b)
inner=json.loads(data['SHA256SUMS.json'])
stale=[n for n,s in inner.items() if sha(data[n])!=s]
assert stale==['run-time.txt'] and inner['run-time.txt']==sha(b'')
assert sum(x['bytes'] for x in files.values())==41441

sys.path.insert(0,str(ROOT/'tests/wp16_internal_invariants_r1'))
from cases import corpus
from oracle import compare
rows=corpus();assert json.loads(data['stdin.json'])==rows
actual=json.loads(data['actual.json']);compare(rows,actual)
commands=json.loads(data['commands.json']);assert len(commands)==16
by={r['name']:r for r in actual}
keys={'frames':['effective','rate'],'trim':['raw','head','tail'],
 'pcm_count':['bytes','channels','width'],'channels':['left','right','output_samples']}
native=[r for r in rows if r['op'] in keys]
for c,cmd in zip(native,commands):
 assert c['name']==cmd['name'] and cmd['exit']==0 and cmd['stderr_hex']==''
 assert cmd['argv'][0]=='/home/runner/work/_temp/source499/host/ingest/target/debug/examples/invariant_challenges'
 assert cmd['argv'][1:]==[c['op']]+[str(c['args'][k]) for k in keys[c['op']]]
 out=json.loads(bytes.fromhex(cmd['stdout_hex']))
 assert out=={k:v for k,v in by[c['name']].items() if k not in ['name','label']},c['name']
labels={
 'frames':'actual production dsp::output_frames',
 'trim':'actual Decoded::finish guard, impossible empty-plane constructor; not production admission',
 'pcm_count':'actual deinterleave on valid block plus extracted WAV caller divisibility discriminator',
 'channels':'actual quantize plus explicit equal-plane/output-count premise discriminator',
 'append':'proof-model only: block shape/append/raw recurrence',
 'pass_premise':'proof-model only: two explicit deterministic pass premises',
 'convergence':'proof-model only: 32 continuing steps are no ranking certificate'}
for c,r in zip(rows,actual):assert r['label']==labels[c['op']]
assert by['stereo-zip-short']['actual_samples']==4
assert all(by[c['name']]['constructed_empty_planes'] is True for c in rows if c['op']=='trim')
assert by['partial-frame']['caller_divisibility_refusal'] is True
for c in rows:
 if c['op']=='pcm_count' and c['name']!='partial-frame':
  r=by[c['name']];assert r['actual_planes']==c['args']['channels']
  assert r['actual_plane_lengths']==[c['expected']]*c['args']['channels']
for i in range(25):
 bad=copy.deepcopy(actual);v=bad[i]['value']
 bad[i]['value']=False if v is True else True if v is False or v is None else v+1
 try:compare(rows,bad)
 except AssertionError:pass
 else:raise AssertionError('undetected actual-response corruption')

pins=json.loads((ROOT/'tests/wp16_internal_invariants_r1/PINS.json').read_bytes())
result=json.loads(data['RESULT.json'])
assert result['source_bindings']==[{'path':f['path'],'sha256':f['sha256']} for f in pins['files']]
if a.offline:
 tree=json.loads((a.offline/'239-review-inputs/source-tree.json').read_bytes())
else:tree=json.loads(get('https://api.github.com/repos/mmsanders/Digital-Tape/git/trees/'+SOURCE+'?recursive=1'))
assert not tree['truncated'] and tree['sha']==SOURCE
entries={r['path']:r for r in tree['tree']}
for f in pins['files']:
 assert entries[f['path']]['sha']==f['blob'] and entries[f['path']]['size']==f['bytes']
assert entries['host/ingest']['sha']==pins['ingest_tree']=='835078995d4e9cc2424f9ea8d6f11304b45f783f'
inputs=json.loads((HERE/'INPUTS.json').read_bytes())
for f in inputs['candidate_files']:
 if f['path'].endswith('run1-FILES.json'):b=inv
 elif a.offline:
  name='software499.yml' if f['path'].startswith('.github/') else pathlib.Path(f['path']).name
  b=(a.offline/'239-review-inputs'/name).read_bytes()
 else:b=get('https://raw.githubusercontent.com/mmsanders/Digital-Tape/'+CANDIDATE+'/'+f['path'])
 assert blob(b)==f['sha'] and len(b)==f['size'],f['path']
audited=['host/ingest/src/'+n+'.rs' for n in ['common','wav','flac','mpeg','aac','dsp','main','convert']]
audited+=['host/ingest/vendor/symphonia-core/src/audio/'+n+'.rs' for n in ['mod','generic','buf']]
pinmap={f['path']:f for f in pins['files']}
for p in audited:
 if a.offline:
  prefix='239-review-inputs' if '/vendor/' in p else '232-return-evidence/source'
  b=(a.offline/prefix/p).read_bytes()
 else:b=get('https://raw.githubusercontent.com/mmsanders/Digital-Tape/'+SOURCE+'/'+p)
 assert sha(b)==pinmap[p]['sha256'] and blob(b)==pinmap[p]['blob'],p
if not a.offline:
 ct=json.loads(get('https://api.github.com/repos/mmsanders/Digital-Tape/git/trees/'+CANDIDATE+'?recursive=1'))
 assert not ct['truncated'];ce={x['path']:x for x in ct['tree']}
 assert ce['tests/wp16_internal_invariants_r1']['sha']==inputs['method_tree']
 assert ce['engine']['sha']==inputs['engine_tree']
 for f in inputs['candidate_files']:assert ce[f['path']]['sha']==f['sha']
 run=json.loads(get('https://api.github.com/repos/mmsanders/Digital-Tape/actions/runs/39553865535'))
 assert run['head_sha']==TESTED and run['conclusion']=='success'
assert result['actual_function_rows']==5 and result['guard_or_shape_discriminators']==11 and result['model_rows']==9
assert result['global_theorem'] is result['admitted_production_witness'] is False
assert result['adapter_sha256']=='ffc0fb2ba11a31ce479c8db01b829d17d75f45efb7984af258352ab2f0de5219'
for n in ['build-time.txt','run-time.txt']:assert b'Exit status: 0' in data[n]
assert b'User time (seconds): 16.44' in data['build-time.txt']
assert b'System time (seconds): 2.58' in data['build-time.txt']
assert b'User time (seconds): 0.05' in data['run-time.txt']
assert b'System time (seconds): 0.01' in data['run-time.txt']
review=dict(candidate=CANDIDATE,tested=TESTED,source=SOURCE,
 raw_files=11,raw_bytes=41441,outer_inventory_blob=blob(inv),
 manually_reviewed_source_file_hashes=len(audited),
 disclosed_stale_inner_entries=stale,source_pin_git_bindings=len(pins['files']),
 frozen_comparisons=25,native_commands=16,production_scalar_rows=5,
 guard_shape_rows=11,proof_model_rows=9,detected_actual_answer_corruptions=25,
 software_build_cpu_seconds=19.02,software_run_cpu_seconds=0.06,
 disposition='bounded scalar/discriminator PASS; manually reviewed conditional count lemmas; global INTERNAL UNPROVED',
 admitted_production_witness=False,integration_permission=False,
 residuals=['MP3/AAC buffer num_planes equals admitted spec channels constructor premise',
 'finite-precision peak-update next-peak/repetition bound',
 '!limited gated loudness-feedback finite ranking bound'])
(a.out/'REVIEW.json').write_text(json.dumps(review,indent=2)+'\n')
print(json.dumps(review,indent=2))
