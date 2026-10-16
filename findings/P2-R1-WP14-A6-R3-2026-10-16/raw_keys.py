"""Independently extract raw ETW writes/name lifecycles underlying the residual stop.
No Product parser imports or Windows execution. Reads the original authenticated ZIP.
"""
import argparse,hashlib,json,struct,xml.etree.ElementTree as E,zipfile
from pathlib import Path
F='90cbdc39-4a3e-11d1-84f4-0000f80464e3'
class Reader:
 def __init__(self,f):self.f=f;self.h=hashlib.sha256()
 def read(self,n=-1):b=self.f.read(n);self.h.update(b);return b
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('zip',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 assert hashlib.file_digest(a.zip.open('rb'),'sha256').hexdigest()=='9b23466b502f386bc3c12ac8a6674710d0caf9491358c2c654bb5717d7cbd755'
 rows=[];names=[];n=0
 with zipfile.ZipFile(a.zip) as z,z.open('verify.xml') as src:
  r=Reader(src);it=E.iterparse(r,events=('start','end'));_,root=next(it)
  for kind,e in it:
   if kind!='end' or e.tag.rsplit('}',1)[-1]!='Event':continue
   n+=1;d={};s={}
   for c in e.iter():
    t=c.tag.rsplit('}',1)[-1]
    if t=='EventGuid':s['guid']=(c.text or '').strip('{}').lower()
    elif t=='Opcode' and c.text and c.text.isdigit():s.setdefault('opcode',int(c.text))
    elif t=='Version' and c.text and c.text.isdigit():s.setdefault('version',int(c.text))
    elif t=='TimeCreated':s['time']=c.get('SystemTime')
    elif t=='Execution':s['execution']=dict(c.attrib)
    elif t=='EventPayload':s['payload']=c.text
    elif t=='Data' and c.get('Name'):d[c.get('Name')]=(c.text or '').strip()
   if s.get('guid')==F and s.get('opcode') in (0,32,35,36):
    name=d.get('FileName','')
    if name.lower().endswith(('rehearsal.img','$logfile')):names.append({'n':n,**s,'data':d})
   if n in (124471,124519):
    assert s.get('guid')==F and s.get('opcode')==68 and s.get('version')==3
    b=bytes.fromhex(s['payload']);assert len(b)==48
    off,irp,fo,fk,ttid,size,flags=struct.unpack_from('<QQQQIII',b);assert ttid==int(s['execution']['ThreadID'])
    rows.append({'n':n,**s,'decoded':{'offset':off,'irp':hex(irp),'object':hex(fo),'key':hex(fk),'ttid':ttid,'size':size,'flags':flags,'uninterpreted_tail':b[44:].hex()}})
   root.remove(e);e.clear()
 assert r.h.hexdigest()=='e50da0d54c0ab406e49431ff23f189ce28475670358e19dc4978232899f834d8' and n==1232801 and len(rows)==2
 keyset={x['decoded']['key'].lower() for x in rows};target={x['data'].get('FileObject','').lower() for x in names if x['data'].get('FileName','').lower().endswith('rehearsal.img')}
 for x in rows:
  key=x['decoded']['key'].lower();evidence=[y for y in names if y['data'].get('FileObject','').lower()==key]
  assert evidence and all(y['data']['FileName'].lower().endswith('$logfile') for y in evidence) and key not in target
  x['matching_name_records']=[y['n'] for y in evidence]
 result={'events':n,'xml_sha256':r.h.hexdigest(),'residual_writes':rows,'relevant_key_name_records':names,'target_name_keys':sorted(target),'scope':'raw record decoding and name evidence only; does not infer process ownership after exit or qualify physical I/O'}
 a.out.write_text(json.dumps(result,indent=2)+'\n');print('Two raw post-exit writes name a LogFile key distinct from every captured target name key')
