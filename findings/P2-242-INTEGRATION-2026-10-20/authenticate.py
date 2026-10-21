"""Authenticate carried Git identities/ancestry only; no Product execution."""
import json,pathlib,urllib.request,hashlib,os
p=json.loads(pathlib.Path(__file__).with_name('PINS.json').read_text())
def get(url):
 h={'Accept':'application/vnd.github+json','User-Agent':'Verification242-independent-carry'}
 if os.environ.get('GH_TOKEN') and url.startswith('https://api.github.com/'):h['Authorization']='Bearer '+os.environ['GH_TOKEN']
 return urllib.request.urlopen(urllib.request.Request(url,headers=h),timeout=45).read()
def api(path):return json.loads(get('https://api.github.com/repos/mmsanders/Digital-Tape/'+path))
def tree(ref):return {x['path']:x['sha'] for x in api('git/trees/'+ref+'?recursive=1')['tree']}
a=tree(p['candidate']);b=tree(p['corrected459'])
assert all(a[k]==b[k]==v for k,v in p['trees'].items())
assert a[p['spec']['path']]==p['spec']['blob']
for ref in [p['corrected459'],p['product_input_main']]:
 c=api('compare/'+ref+'...'+p['candidate'])
 assert c['merge_base_commit']['sha']==ref and c['status'] in ('ahead','identical')
for r in p['evidence_reports']:
 raw=get('https://raw.githubusercontent.com/mmsanders/digital-tape-verification/'+p['verification_input']+'/'+r['path'])
 assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==r['blob']
assert p['new_product_execution']==p['observer_retry']==0
print('PASS exact source/test/engine ancestry and5 carried-report identities; HOLD remains, no integration permission')
