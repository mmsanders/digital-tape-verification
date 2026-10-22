"""Original-byte/provenance checks, not an automated proof of source induction."""
import argparse, hashlib, importlib.util, io, json, urllib.request, zipfile
from pathlib import Path
HEAD='84d7ea664d2ba7dddb6da5bae33bdffe1414b541'
SOURCE='b9f430c8c9b33532abf07eea0ed2653310639f2d'
URL='https://raw.githubusercontent.com/mmsanders/Digital-Tape/'+HEAD+'/docs/REVIEW/software526/software526-source-return.zip'
def sha(b): return hashlib.sha256(b).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--archive',type=Path);p.add_argument('--root',type=Path,default=Path('.'));p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 raw=a.archive.read_bytes() if a.archive else urllib.request.urlopen(URL).read()
 assert len(raw)==389287 and sha(raw)=='366e6baca260d5489b461fdff9d1066b33655297fc497ea238de73f92cd44712'
 z=zipfile.ZipFile(io.BytesIO(raw));ns=z.namelist()
 assert len(ns)==len(set(ns))==229 and all(not n.startswith('/') and '..' not in Path(n).parts and '\\' not in n for n in ns)
 f={n:z.read(n) for n in ns};j=lambda n:json.loads(f[n]);inv=j('FILES.json')
 assert len(inv)==228 and set(inv)==set(f)-{'FILES.json'}
 for n,v in inv.items():assert len(f[n])==v['bytes'] and sha(f[n])==v['sha256']
 pins=j('SOURCE-PINS.json');assert pins['source']==SOURCE and len(pins['files'])==44
 for n,v in pins['files'].items():
  b=f['source/'+n];assert len(b)==v['bytes'] and sha(b)==v['sha256']
  assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==v['blob']
 cmds=j('COMMANDS.json');assert len(cmds)==89
 seen_show=set();seen_blob=set()
 for i,c in enumerate(cmds):
  assert c['exit']==0 and c['parent']==5224 and c['end_ns']>=c['start_ns']
  for stream in ('stdout','stderr'):assert sha(f[f'commands/{i}-{stream}.bin'])==c[stream+'_sha256']
  argv=c['argv'];assert argv[0]=='git'
  if i==0:assert argv==['git','ls-tree','-r','--name-only',SOURCE,'host/ingest']
  else:
   assert argv[1] in ('show','rev-parse') and argv[2].startswith(SOURCE+':')
   n=argv[2].split(':',1)[1];assert n in pins['files']
   if argv[1]=='show':assert f[f'commands/{i}-stdout.bin']==f['source/'+n];seen_show.add(n)
   else:assert f[f'commands/{i}-stdout.bin'].decode().strip()==pins['files'][n]['blob'];seen_blob.add(n)
 assert seen_show==seen_blob==set(pins['files'])
 pkg=a.root/'tests/codec_cardinality_r2';s=importlib.util.spec_from_file_location('independent269',pkg/'oracle.py');oracle=importlib.util.module_from_spec(s);s.loader.exec_module(oracle)
 ledger=j('LEDGER.json');assert oracle.check_ledger(ledger)=='LEDGER_SHAPE_ONLY_NOT_SOURCE_PROOF' and len(ledger['nodes'])==46
 for n in ledger['nodes']:
  assert pins['files'][n['path']]['sha256']==n['sha256']
  assert n['last_line']<=len(f['source/'+n['path']].decode().splitlines())
 controls=j('CONTROLS.json');assert len(controls)==16
 false=set()
 for c in controls:
  assert oracle.premise_model(c['input']) is False and c['accepted'] is False
  assert c['input'][c['false_premise']] is False;false.add(c['false_premise'])
 assert len(false)==16
 r=j('RESULT.json');assert r['source']==SOURCE and r['new_decoder_runs']==r['new_codec_builds']==0 and r['source_files']==44
 result=dict(source=SOURCE,evidence_head=HEAD,archive_sha256=sha(raw),members=229,inventory_entries=228,source_files=44,git_receipts=89,ledger_nodes=46,codec_obligations=24,abstract_premise_falsifiers=16,new_decoder_runs=0,new_codec_builds=0,byte_replay='PASS',automated_source_proof=False,manual_disposition={'MP3':'PROVED_CONDITIONAL','AAC':'PROVED_CONDITIONAL','host_cardinality':'PROVED_CONDITIONAL'},global_internal='UNPROVED')
 a.out.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf-8',newline='\n')
 print('PASS original bytes and ledger consistency; manual source proof recorded separately')
if __name__=='__main__':main()
