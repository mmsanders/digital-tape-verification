"""Independent byte parser for the submitted DTrace record format.
Checks record completeness, sequence/end records and actual publish/flush closes.
No Product imports, native execution, or blanket absence/acceptance receipt.
"""
import argparse,collections,hashlib,json,re,zipfile
from pathlib import Path
H=re.compile(rb'([RETXS]) (\d+) (\d+) (\d+) (\d+) (\S+)')
R=re.compile(rb' (\w+) ret=(-?\d+) err=(\d+) fd=(-?\d+) a=(-?\d+) l0=(\d+) l1=(\d+)\|')
def parse(data,names):
 rows=[];i=0;bad=[]
 while i<len(data):
  if data[i:i+1] in (b'\n',b'\r'):i+=1;continue
  h=H.match(data,i)
  if not h:bad.append(data[i:i+60].hex());break
  tag,ts,pid,tid,seq,exe=h.groups();r={'tag':tag.decode(),'pid':int(pid),'tid':int(tid),'seq':int(seq),'exe':exe.decode(),'ts':int(ts)};j=h.end()
  if tag==b'R':
   m=R.match(data,j)
   if not m:bad.append('bad syscall fields');break
   call,ret,err,fd,a,n0,n1=m.groups();p=m.end();n0=int(n0);n1=int(n1);q=p+n0+1;end=q+n1
   if data[p+n0:q]!=b'|' or data[end:end+1]!=b'\n':bad.append('bad path framing');break
   r.update(call=call.decode(),ret=int(ret),err=int(err),fd=int(fd),flags=int(a),src=data[p:p+n0],dst=data[q:end]);j=end+1
   if n0>=1023 or n1>=1023:bad.append('truncated path')
  else:
   end=data.find(b'\n',j)
   if end<0:bad.append('truncated final record');break
   r['detail']=data[j:end].decode();j=end+1
  rows.append(r);i=j
 threads=collections.defaultdict(list);root=next((r['pid'] for r in rows if r['exe']==names[0]),None)
 for r in rows:
  if r['exe'] in names:threads[(r['pid'],r['tid'])].append(r)
 contiguous=bool(threads) and all(sorted(r['seq'] for r in v)==list(range(1,len(v)+1)) for v in threads.values())
 ended=bool(threads) and all(max(v,key=lambda r:r['seq'])['tag']=='T' for v in threads.values())
 exits={r['pid'] for r in rows if r['tag']=='X' and r['exe'] in names}
 return rows,{'whole_records':not bad,'sequences':contiguous,'thread_ends':ended,'root_exit':root is not None and root in exits}
def run(path):
 with zipfile.ZipFile(path) as z:
  index=json.loads(z.read('INDEX.json'));out={'cases':0,'publish':0,'flush_close':0,'kills':{},'controls':{},'errors':[]};st=json.loads(z.read('observer-selftest/result.json'))
  baseline,checks=parse(z.read('observer-selftest/'+st['trace']),('probe-parent','probe-child'));assert all(checks.values())
  for name,c in st['false_pass_controls'].items():
   raw=z.read('observer-selftest/'+c['file']);assert hashlib.sha256(raw).hexdigest()==c['sha256']
   rr,ck=parse(raw,('probe-parent','probe-child'));out['controls'][name]={'rejected':not all(ck.values()),'checks':ck};assert not all(ck.values()),name
  for id,p in index['cases'].items():
   rec=json.loads(z.read(p));native=json.loads(z.read(rec['native_record']));data=z.read(rec['raw_trace']);assert hashlib.sha256(data).hexdigest()==native['raw_trace_sha256']
   rows,checks=parse(data,('ingest',));assert all(checks.values()),(id,checks)
   out['cases']+=1;dest=rec['argv'][rec['argv'].index('--out')+1] if '--out' in rec['argv'] else None
   fds={};flushed=set();actual_closed=set()
   for n,r in enumerate(rows):
    if r['tag']!='R' or r['exe']!='ingest':continue
    k=(r['pid'],r['fd']);call=r['call']
    if call.startswith('open') and r['ret']>=0:fds[(r['pid'],r['ret'])]=r['src']
    elif (call.startswith('fsync') or call.startswith('fcntl') and r['flags']==51) and r['ret']==0:flushed.add(k)
    elif call.startswith('close') and r['ret']==0:
     if k in flushed:actual_closed.add((n,fds.get(k)));flushed.remove(k)
     fds.pop(k,None)
   for e in native['events']:
    if e['op']=='publish_dir_noreplace':
     r=rows[e['line']];assert r['tag']=='R' and r['call']=='renameatx_np' and r['ret']==0 and r['err']==0 and r['flags']&4 and not r['flags']&2
     assert r['dst'].decode()==dest and b'.DEST.ingest-stage-' in r['src'];out['publish']+=1
    elif e['op'] in ('audio_flush_close','manifest_flush_close'):
     wanted=e['op'].split('_')[0].encode()+ (b'.wav' if e['op'].startswith('audio') else b'.json')
     assert any(n==e['line'] and p and p.endswith(b'/'+wanted) for n,p in actual_closed),(id,e);out['flush_close']+=1
   if id in ('kill/audio-open','kill/manifest-open','kill/after-publish'):
    out['kills'][id]={'complete_from_raw':True,'dest_after':native['dest_after'],'open_at_exit':native['open_at_exit'],'publish_ops':sum(e['op']=='publish_dir_noreplace' for e in native['events'])}
  out['scope']='Raw recorded publication and flush/close plus per-record integrity on1927 cases; control rejections independently recomputed; no full native/absence/quality receipts'
  return out
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('packet',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args();r=run(a.packet);a.out.write_text(json.dumps(r,indent=2)+'\n');print({k:v for k,v in r.items() if k not in ('controls','scope')})
