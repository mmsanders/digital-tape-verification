"""Stream the original complete ETW XML; publish only bounded anonymous identity facts."""
import argparse,hashlib,json,struct,xml.etree.ElementTree as E
from pathlib import Path
import supplement
F='90cbdc39-4a3e-11d1-84f4-0000f80464e3';D='3d6fa8d4-fe05-11d0-9dda-00c04fd7ba7c'
KEY=0xffffa18609084d30
FILE_REQUESTS={0xffffa18627895918,0xffffa1863e7e99d8}
DISK_REQUEST=0xffffa1861c4eb010
def num(v):
 try:return int(v,16) if str(v).lower().startswith('0x') else int(v)
 except (TypeError,ValueError):return None
def run(xml,out):
 with xml.open('rb') as stream:digest=hashlib.file_digest(stream,'sha256').hexdigest()
 assert digest=='69a81ab6ca7f8aaf7d533b511c496c048bd4c11620999e0159d5898c6fe4ff98'
 n=0;file_rows=[];disk_rows=[];names=set();explicit_bridges=[];payload_bridges=[];request_facts=[]
 it=E.iterparse(xml,events=('start','end'));_,root=next(it)
 for kind,e in it:
  if kind!='end' or e.tag.rsplit('}',1)[-1]!='Event':continue
  n+=1;d={};s={}
  for c in e.iter():
   tag=c.tag.rsplit('}',1)[-1]
   if tag=='EventGuid':s['guid']=(c.text or '').strip('{}').lower()
   elif tag=='Opcode' and (c.text or '').strip().isdigit():s.setdefault('opcode',int(c.text))
   elif tag=='Version' and (c.text or '').strip().isdigit():s.setdefault('version',int(c.text))
   elif tag=='TimeCreated':s['time']=c.get('SystemTime')
   elif tag=='EventPayload':s['payload']=(c.text or '').strip()
   elif tag=='Data' and c.get('Name'):d[c.get('Name')]=(c.text or '').strip()
  g=s.get('guid');op=s.get('opcode');raw=bytes.fromhex(s.get('payload',''))
  pointers={num(v) for v in d.values()}
  for req in FILE_REQUESTS:
   if req in pointers and DISK_REQUEST in pointers:explicit_bridges.append(n)
   if struct.pack('<Q',req) in raw and struct.pack('<Q',DISK_REQUEST) in raw:payload_bridges.append(n)
  if g==F:
   if op in(0,32,35,36) and num(d.get('FileObject'))==KEY:names.add(d.get('FileName',''))
   if op==68 and s.get('version')==3 and len(raw)>=44:
    off,irp,obj,key,tid,size,flags=struct.unpack_from('<QQQQIII',raw)
    if key==KEY:file_rows.append(dict(n=n,layer='file',op='write',key=key,request=irp,object=obj,bytes=size,offset=off,time=s['time'],tid=tid))
  if g==D and op==11 and num(d.get('FileObject'))==KEY:
   disk_rows.append(dict(n=n,layer='disk',op='write',key=KEY,request=num(d.get('Irp')),disk=num(d.get('DiskNumber')),bytes=num(d.get('TransferSize')),offset=num(d.get('ByteOffset')),time=s['time'],tid=num(d.get('IssuingThreadId'))))
  root.remove(e);e.clear()
 assert n==948634
 file_selected=[r for r in file_rows if r['n'] in(480422,480466)]
 disk_selected=[r for r in disk_rows if r['n'] in(480439,480483)]
 assert len(file_selected)==len(disk_selected)==2
 audit=[]
 for f,d in zip(file_selected,disk_selected):
  assert f['key']==d['key'] and f['bytes']==d['bytes'] and d['disk']==0
  audit.append({'file_record':f['n'],'disk_record':d['n'],'file_request':hex(f['request']),'disk_request':hex(d['request']),
      'request_equal':f['request']==d['request'],'file_offset':f['offset'],'disk_offset':d['offset'],'offset_delta':d['offset']-f['offset'],
      'bytes':f['bytes'],'disk':d['disk'],'same_key_disk_writes_in_complete_capture':len(disk_rows),
      'same_key_size_disk_candidates':sum(r['bytes']==f['bytes'] for r in disk_rows),
      'same_request_size_disk_matches':sum(r['request']==f['request'] and r['bytes']==f['bytes'] for r in disk_rows)})
 sample=supplement.baseline()
 sample['remaining']=[]
 for i,f in enumerate(file_selected):
  sample['remaining'].append(dict(f,time=i*10,same_offset_coordinate=False))
 for i,d in enumerate(disk_selected):sample['remaining'].append(dict(d,time=i*10+1))
 sample['ambiguous_keys']=len(names)!=1
 result={'xml_sha256':digest,'events_streamed':n,'controls_publication':'b0eddaaab3fa32e8902fa7fe93446983c29025fa',
      'old_checker_verdict':'FAIL','amended_method':supplement.judge(sample),
      'native_identity_audit':audit,'all_logkey_file_writes':len(file_rows),'all_logkey_disk_writes':len(disk_rows),
      'distinct_logkey_names':len(names),'records_with_both_request_ids_in_named_fields':explicit_bridges,
      'records_with_both_request_ids_in_payload':payload_bridges,
      'limit':'Key/size/time and constant offset delta are observations, not independent request/extent translation proof. Raw identity scan does not independently decode every other provider schema.'}
 assert not explicit_bridges and not payload_bridges
 assert result['amended_method']['verdict']=='HELD' and not result['amended_method']['excluded']
 out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('xml',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args();run(a.xml,a.out)
