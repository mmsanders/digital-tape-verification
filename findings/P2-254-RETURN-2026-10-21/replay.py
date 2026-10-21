"""Independent retained-byte review only. No Product process or driver execution."""
import argparse,hashlib,io,json,struct,sys,wave,zipfile,importlib.util,urllib.request
from pathlib import Path
SHA='617b66e29f0679eac60436ffa94edda4f3041ec141c08514d656345ccedca071'
URL='https://github.com/mmsanders/Digital-Tape/releases/download/evidence-software513-2026-10-21/software513-exact-return.zip'
def sha(b):return hashlib.sha256(b).hexdigest()
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 p=argparse.ArgumentParser();p.add_argument('--archive',type=Path);p.add_argument('--actions',type=Path);p.add_argument('--root',type=Path,default=Path('.'));p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 raw=a.archive.read_bytes() if a.archive else urllib.request.urlopen(URL).read();assert len(raw)==1454205 and sha(raw)==SHA
 z=zipfile.ZipFile(io.BytesIO(raw));names=z.namelist();assert len(names)==591 and len(set(names))==591
 assert all(not n.startswith('/') and '..' not in Path(n).parts and '\\' not in n for n in names)
 files={n:z.read(n) for n in names};j=lambda n:json.loads(files[n]); inv=j('FILES.json');assert set(inv)==set(files)-{'FILES.json'}
 for n,f in inv.items():assert len(files[n])==f['bytes'] and sha(files[n])==f['sha256'],n
 if a.actions:
  ar=a.actions.read_bytes();assert len(ar)==2582606 and sha(ar)=='6e3e31bddec246660c426fdcd2b4801b98770bf5c9d50aa9aae5ce79ac0f2da4'
  az=zipfile.ZipFile(io.BytesIO(ar));assert az.read('software513-work/software513-exact-return.zip')==raw
  for n,b in files.items():assert az.read('software513-work/return/'+n)==b
 retained=Path(__file__).with_name('retained');pins=json.loads((retained/'INVENTORY.json').read_bytes())
 for n,h in pins.items():assert sha((retained/n).read_bytes())==h
 source=json.loads((retained/'SOURCE.json').read_bytes())
 for n,f in source['compiled'].items():assert sha((retained/n).read_bytes())==f['sha256']
 # The retained module transformations were reviewed separately as text; no imports.
 assert source['original_modules']['dsp']=='fb77778e7f271f2acb1c385ee9e8235e0752f3f1318caf3e7fddcc410a230ffc'
 modelraw=(retained/'model.py').read_bytes();assert sha(modelraw)=='4dfc0d0987eea047968db046e088e4124dcc55ca47a618f66fa51ea9cea1e9d9'
 # This is our pre-existing, hash-pinned independent integer quantizer, not Software code.
 model={};exec(compile(modelraw,'independent-model','exec'),model)
 oracle=module('coordinates',a.root/'tests/meter_precision_r1/oracle.py');rec=module('recorder_oracle',a.root/'tests/evidence_recorder_r1/oracle.py')
 selected=json.loads((a.root/'tests/meter_precision_r1/SELECTED.json').read_bytes());assert len(selected['cases'])==3
 original_count=0
 for c in selected['cases']:
  for f in c['original_files']:
   b=files['inputs/'+f['path']];assert len(b)==f['bytes'] and sha(b)==f['sha256'];original_count+=1
 observations=j('OBSERVATIONS.json');assert len(observations)==28
 traces={};pids=set()
 for o in observations:
  name=o['name'];prefix='owned/cases/'+name+'/';cf={n[len(prefix):]:b for n,b in files.items() if n.startswith(prefix)}
  request=j('requests/'+name+'.json');assert rec.check_complete(cf,request)=='COMPLETE_EVIDENCE'
  payload=j('requests/'+name+'-payload.json');assert json.loads(cf['input.bin'])==payload
  assert request['source_commit']=='b61da399ec97dcc9892398f522091c32f215ad14'
  dd='domain/'+name+'/';di=j(dd+'MANIFEST.json');assert set(di)=={n[len(dd):] for n in files if n.startswith(dd)}-{'MANIFEST.json'}
  for n,f in di.items():assert sha(files[dd+n])==f['sha256'] and len(files[dd+n])==f['bytes']
  launch=j(dd+'LAUNCH.json');exit=j(dd+'EXIT.json');assert exit['code']==0 and not exit['timeout']
  assert launch['argv']==payload['argv'] and launch['binary_sha256']==payload['binary_sha256']=='a0b506f66d8705cd15da695cec3692c7a98987722c859c7ed5eb58559b9be01d'
  assert launch['source']==payload['source']==source['source'];assert launch['pid'] not in pids;pids.add(launch['pid'])
  for path,h in payload['inputs'].items():assert sha(files[path.split('/return/')[1]])==h
  t=[json.loads(x) for x in files[dd+'trace.jsonl'].splitlines()];assert t[0]['pid']==launch['pid'];traces[name]=t
  assert len(t)==o['events'] and sha(files[dd+'MANIFEST.json'])==o['domain_manifest']
 evals=j('EVALUATIONS.json');assert len(evals)==7184;atmap={};points_count=0;gains=[];attempts=0
 for c in selected['cases']:
  name=c['name'];m=j('inputs/'+name+'/published/manifest.json');wb=files['inputs/'+name+'/published/audio.wav']
  with wave.open(io.BytesIO(wb)) as w:pcm=w.readframes(w.getnframes());frames=w.getnframes();assert w.getnchannels()==2
  boundaries={0,frames}
  for s in m['sources']:boundaries.update((s['start_frame'],s['start_frame']+s['output_frames']))
  lo=-256
  while lo<frames+256:hi=min(lo+2**20,frames+256);boundaries.update((lo,hi));lo=hi
  points=sorted({divmod((b+d)*256+q+r,256) for b in boundaries for d in (-257,-256,-255,-1,0,1,255,256,257) for q in (0,64,128,192) for r in (-63,-1,0,1,63)})
  assert files['inputs/'+name+'-coords.txt'].decode()==''.join(f'{n} {q}\n' for n,q in points)
  for ch in (0,1):
   plane=b''.join(struct.pack('<f',r[ch]/32768) for r in struct.iter_unpack('<hh',pcm));assert files[f'inputs/{name}-channel-{ch}.f32']==plane
   vals=[x for x in traces[f'{name}-channel-{ch}'] if x['kind']=='evaluation'];assert [(x['n0'],x['q']) for x in vals]==points
   for v in vals:
    assert v['grid_le']==v['grid_at_abs_le'];oracle.ieee(v['at_le'],'f32');atmap[name,ch,v['n0'],v['q']]=v['at_le']
   stream=traces[f'{name}-stream-{ch}'];fills=[x for x in stream if x['kind']=='fill'];lo=-256
   for f in fills:
    hi=min(lo+2**20,frames+256);assert f['start']==lo-258 and f['length']==hi-lo+516;lo=hi
   assert lo==frames+256 and stream[-1]['kind']=='stream-result'
  for i,s in enumerate(m['sources']):
   with wave.open(io.BytesIO(files['inputs/'+name+'/folder'+s['logical_path']])) as w:rawpcm=w.readframes(w.getnframes());channels=w.getnchannels();assert w.getframerate()==44100 and w.getsampwidth()==2
   assert s['trim_head']==s['trim_tail']==0 and files[f'inputs/{name}-source-{i}.bin']==rawpcm
   trace=traces[f'{name}-source-{i}'];aa=[x for x in trace if x['kind']=='attempt'];attempts+=len(aa);gain=struct.unpack('<d',bytes.fromhex(aa[-1]['linear_gain_le']))[0];gains.append(gain)
   assert trace[-1]['gain_db_le']==aa[-1]['gain_db_le']
   rows=([v/32768*gain for v in r] for r in struct.iter_unpack('<h' if channels==1 else '<hh',rawpcm));expected=model['quantize'](rows,mono=channels==1)
   assert expected==files[f'domain/{name}-source-{i}/converted.pcm']==files['inputs/'+name+'/converted-'+s['logical_path'].replace('/','-')+'.pcm']
 for e in evals:
  oracle.coordinates(e);n=e['n0'];plane=files[f"inputs/{e['case']}-channel-{e['channel']}.f32"]
  support=b''.join(plane[k*4:k*4+4] if 0<=k<len(plane)//4 else bytes(4) for k in range(n-255,n+257));assert sha(support)==e['support_sha256']
  assert e['at_le']==atmap[e['case'],e['channel'],n,e['q']]
 mutants=j('MUTANTS.json');assert len(mutants)==5
 for bad in mutants[:4]:
  try:oracle.coordinates(bad['observation'])
  except AssertionError:pass
  else:raise AssertionError('mutation survived')
 assert not oracle.bind_gain(mutants[-1]['observation'],'f64',mutants[-1]['original'],'f64')
 assert attempts==18 and len(gains)==16 and sum(x<1 for x in gains)==3
 coeff=files['domain/join-29000-1-channel-0/coefficients.f32'];assert len(coeff)==524288 and sha(coeff)=='e0846717173fa5013e14d37e9ddd0a37e57de55590978b81b6fa6e6aa62ee5b0'
 result=dict(archive_sha256=SHA,closed_members=591,original_selected_files=original_count,complete_recorder_cases=28,actual_native_calls=28,finite_evaluations=7184,source_quantizer_original_equal=16,gain_attempts=18,attenuated_final=3,mutations_rejected=5,verdict='BOUNDED FINITE FACTS PASS; analytical/global transfer remains UNPROVED',residuals=['original hidden-gain provenance','complete noncandidate per-step history','global peak/refinement transfer','numerical per-gate storage receipts absent; source gates only'])
 a.out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result))
if __name__=='__main__':main()
