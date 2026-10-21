"""Source/ledger authentication only; no decoder or seventh-function audit."""
import argparse,hashlib,importlib.util,json,pathlib,re,urllib.request
ROOT=pathlib.Path(__file__).resolve().parents[2];HERE=pathlib.Path(__file__).resolve().parent
SHA=lambda b:hashlib.sha256(b).hexdigest()
BLOB=lambda b:hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
HEAD='ba9459e5cc365c53329753c94b49349f9053b6a7'
RETURN=['LEDGER.json','FUNCTIONS.json','SOURCE-PINS.json','FIXTURES.json','README.md','METHOD-SELFTEST.txt']
def fetch(url):
 with urllib.request.urlopen(url,timeout=45) as f:return f.read()
def main():
 p=argparse.ArgumentParser();p.add_argument('--offline',type=pathlib.Path);p.add_argument('--out',type=pathlib.Path,required=True);a=p.parse_args()
 pins=json.loads((HERE/'INPUTS.json').read_text(encoding='utf-8'));blobs={x['path']:x['blob'] for x in pins['changed_files']}
 raw={}
 for n in RETURN:
  path='docs/REVIEW/software512/'+n
  b=(a.offline/'253-return'/n).read_bytes() if a.offline else fetch('https://raw.githubusercontent.com/mmsanders/Digital-Tape/'+HEAD+'/'+path)
  assert BLOB(b)==blobs[path];raw[n]=b
 sources={}
 for k,pin in pins['source_pins'].items():
  b=(a.offline/'253-return/source'/(k+'.rs')).read_bytes() if a.offline else fetch('https://raw.githubusercontent.com/mmsanders/Digital-Tape/'+pin['source_commit']+'/'+pin['path'])
  assert SHA(b)==pin['sha256'] and BLOB(b)==pin['blob'] and len(b.decode().splitlines())==pin['lines']
  sources[pin['path']]=b
 assert json.loads(raw['SOURCE-PINS.json'])==pins['source_pins']
 functions=json.loads(raw['FUNCTIONS.json']);assert functions==pins['new_functions'] and functions['new_body_count']==functions['limit']==6
 assert [x['name'] for x in functions['new_functions']]==['AudioBuffer::new','MpaDecoder::decode_inner','MpaDecoder::decode_ref','AacDecoder::try_new','AacDecoder::decode_inner','AacDecoder::decode_ref']
 assert functions['unreviewed_needed'] and 'seventh' in functions['stop']
 assert json.loads(raw['FIXTURES.json'])==dict(bindings=[],actual_decoder_executions=0,limit=8)
 method=ROOT/'tests/codec_cardinality_r1';imported={x['name']:(method/x['name']).read_bytes() for x in pins['import_files']};assert len(imported)==7
 for x in pins['import_files']:assert len(imported[x['name']])==x['size'] and BLOB(imported[x['name']])==x['sha']
 tree=b''.join(b'100644 '+n.encode()+b'\0'+bytes.fromhex(BLOB(imported[n])) for n in sorted(imported))
 assert hashlib.sha1(b'tree '+str(len(tree)).encode()+b'\0'+tree).hexdigest()==pins['method_tree']
 obligations={'ADMISSION','ALLOCATION','RENDER','TRANSITION','COPY','CALLER'}
 rows=json.loads(raw['LEDGER.json']);assert len(rows)==12 and {(x['codec'],x['obligation']) for x in rows}=={(c,o) for c in ['MP3','AAC'] for o in obligations}
 spec=importlib.util.spec_from_file_location('cardinality_corpus',method/'corpus.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);controls={x['name'] for x in m.cases()}
 spans=0
 for row in rows:
  assert row['assumptions'] and row['types'] and row['necessary_call_field_edges'] and row['derivation'] and row['residual']
  assert set(row['falsification_controls'])<=controls and 'abstract' in row['control_scope']
  assert row['verdict']==('PROVED' if row['obligation']=='ALLOCATION' else 'RESIDUAL')
  if row['obligation']=='ALLOCATION':assert 'stable count' in row['residual'] and 'conditional constructor' in row['derivation']
  for s in row['sources']:
   b=sources[s['path']];assert BLOB(b)==s['blob'] and SHA(b)==s['sha256'] and s['source_commit']==pins['source']
   assert 1<=s['start_line']<=s['end_line']<=len(b.decode().splitlines());spans+=1
 # Source tokens bind the manually reviewed local edges/residual locations; they
 # are not a mechanized Rust/container/procedure-preservation proof.
 buffer=sources[pins['source_pins']['buffer']['path']].decode()
 for token in ['let num_channels = spec.channels().count();','planes.resize_with(num_channels','AudioBuffer { spec, planes, num_frames: 0, capacity }']:assert token in buffer
 mp3=sources[pins['source_pins']['mp3']['path']].decode();aac=sources[pins['source_pins']['aac']['path']].decode()
 assert 'layer.decode(&mut reader, &header, &mut self.buf)?;' in mp3 and 'self.buf.spec() != &header.spec()' in mp3
 assert 'self.buf.render_uninit(None);' in aac and 'self.decode_ga(&mut bs)?' in aac
 assert raw['METHOD-SELFTEST.txt']==b'PASS: 16 abstract controls; zero decoder executions; source derivations pending\n'
 result=dict(candidate=HEAD,source=pins['source'],method_tree=pins['method_tree'],source_files=7,bound_row_spans=spans,frozen_obligations=12,new_vendor_functions=6,known_fixture_bindings=0,actual_decoder_executions=0,abstract_controls=16,local_conditional_allocation_rows=2,residual_rows=10,mp3_complete_lemma='RESIDUAL',aac_complete_lemma='RESIDUAL',global_INTERNAL='UNPROVED',admitted_counterexample=False,integration_permission=False,disposition='local conditional allocation step accepted; exact six-body transitive-preservation stop')
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n');print(json.dumps(result,sort_keys=True))
if __name__=='__main__':main()
