import sys,pathlib,json,importlib.util,hashlib
import argparse,urllib.request
ap=argparse.ArgumentParser();ap.add_argument('--out',type=pathlib.Path,required=True);ap.add_argument('--offline-sources',type=pathlib.Path);a=ap.parse_args()
receipt=a.out;receipt.mkdir(parents=True,exist_ok=True)
root=pathlib.Path(__file__).resolve().parents[2]
base='https://raw.githubusercontent.com/mmsanders/Digital-Tape/e8437990c28d04ef50e534ecee22d90d621da22e/'
def fetch(p):
 if a.offline_sources:
  if p.startswith('docs/REVIEW/software498/correction1/'):return (receipt/pathlib.Path(p).name).read_bytes()
  return (a.offline_sources/p).read_bytes()
 return urllib.request.urlopen(base+p,timeout=30).read()
manifest=fetch('docs/REVIEW/software498/correction1/SHA256SUMS.json')
assert hashlib.sha1(b'blob '+str(len(manifest)).encode()+b'\0'+manifest).hexdigest()=='1a7438df9e8b526f0da047cbf86f86a2290e5cca'
pins=json.loads(manifest)
assert len(pins)==15
for name,sha in pins.items():
 assert '/' not in name
 b=fetch('docs/REVIEW/software498/correction1/'+name);assert hashlib.sha256(b).hexdigest()==sha,name
 (receipt/name).write_bytes(b)
result=json.loads((receipt/'RESULT.json').read_bytes())
for path,sha in result['sources'].items():
 b=fetch(path);assert hashlib.sha256(b).hexdigest()==sha,path
assert hashlib.sha256((root/'tests/wp15_app1a_r1/oracle.py').read_bytes()).hexdigest()=='66ff0af2fe60d9aff50c68376eb0b0fe0a0cbfc40711f8ef9899c124f46d3aa3' 
sys.path.insert(0,str(root/'tests/wp15_app1a_r1'))
import cases,oracle,parser_runner
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def rows(n):return [json.loads(l) for l in (receipt/n).read_bytes().splitlines()]
app=cases.corpus();stdin=rows('app-stdin.jsonl');got=rows('app-stdout.jsonl')
assert stdin==app;parser_runner.compare(app,got)
q=load('qoracle',root/'tests/wp15_boundary_query_r1/oracle.py')
old=sys.modules['oracle'];sys.modules['oracle']=q
qm=load('qcases',root/'tests/wp15_boundary_query_r1/cases.py');sys.modules['oracle']=old
query=[]
for c in qm.matrix():
 p=q.parse_report(bytes.fromhex(c['report_hex']),c['version'],c['nonce'],c['exit'])
 query.append(dict(name='query-report:'+c['id'],tool='tapectl make',version=c['version'],nonce=c['nonce'],exit=c['exit'],folders=[],pair=False,raw_hex=c['report_hex'],valid=p is not None,message=list(q.message(c['exit'],p))))
assert rows('query-report-stdin.jsonl')==query
parser_runner.compare(query,rows('query-report-stdout.jsonl'))
GENERIC='Something went wrong. Nothing else on your computer was changed.'
MAKE={'make-generic':"The cartridge wasn't finished. Start over and try again.",'card-small':'This card is too small. Use a bigger card.','card-interrupted':'The card was taken out before it was finished. Put it back in and press Make cartridge again.','verify-finding':'Something went wrong writing this card. Press Make cartridge to try again.','music-changed':'The music file changed while the cartridge was being made. Start over and drop the folder again.','card-refused':"This card can't be used right now. Check the card and try again."}
def display(c):
 cat,fact=c['message']
 if cat=='success':return None
 if cat=='generic':return GENERIC
 if cat in MAKE:return MAKE[cat]
 if cat=='overage':
  m,s=divmod(fact,60);parts=[]
  if m:parts.append(str(m)+' min')
  if s or not m:parts.append(str(s)+' s')
  return 'This music is '+' '.join(parts)+' too long for a 60-minute cartridge. Take some songs out and drop the folder again.'
 if cat=='folder-nonmusic':
  i=int(fact.split('/')[0]);return 'The folder "'+c['folders'][i]+'" has something in it that isn\'t music. Use a folder with only songs in it.'
 name=fact.split('/',1)[1] if '/' in fact else c['folders'][int(fact)]
 if cat=='protected':return '"'+name+'" is copy-protected, so it can\'t go on a cartridge. Take it out of the folder.'
 assert cat=='unusable'
 return '"'+name+'" can\'t be used. Take it out of the folder.'
bad=[]
for c,r in zip(app+query,got+rows('query-report-stdout.jsonl')):
 exp=display(c)
 if r['rendered']!=exp:bad.append(dict(name=c['name'],exit=c['exit'],pair=c['pair'],expected_category=c['message'],expected_rendered=exp,actual_rendered=r['rendered']))
out=dict(candidate='e8437990c28d04ef50e534ecee22d90d621da22e',parser_cases=len(app),query_projection_cases=len(query),category_mismatches=0,display_mismatches=bad,scope='independent raw replay; synthetic parser inputs only')
(receipt/'REVIEW.json').write_text(json.dumps(out,indent=2)+'\n')
assert bad==[],bad
assert result['source_commit']=='03d712976fc40fdc85062d48c4666d59cc8a5dca'
assert sum(c['tool']=='ingest' and c['exit']==0 and not c['pair'] for c in app)==21
assert all(r['rendered'] is None for c,r in zip(app,got) if c['message'][0]=='success')
import copy
def judge(rs,gs):
 parser_runner.compare(rs,gs)
 assert all(r['rendered']==display(c) for c,r in zip(rs,gs))
judge(app,got)
mutants=[]
mutants.append(got[:-1])
b=copy.deepcopy(got);b[0]['valid']=not b[0]['valid'];mutants.append(b)
b=copy.deepcopy(got);b[0]['message']=['generic',None];mutants.append(b)
i=next(i for i,c in enumerate(app) if c['name']=='success-needs-pair')
b=copy.deepcopy(got);b[i]['rendered']=None;mutants.append(b)
for b in mutants:
 try:judge(app,b)
 except AssertionError:pass
 else:raise AssertionError('actual-positive mutant escaped')
out['corrected_missing_pair_rows']=21
out['display_rows']=676
out['detecting_actual_row_controls']=4
out['disposition']='bounded exact-head pure parser/message component PASS; integration conditional on current-base required protections'
(receipt/'REVIEW.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
