"""Independent image-vs-disk and teardown attribution controls. SYNTHETIC only.
Generate explicit native XML observations; never execute the stand-in binary.
Checker is an argument, outside this immutable publication.
"""
import argparse,hashlib,json,subprocess,sys,tempfile
from pathlib import Path
G={'p':'3d6fa8d0-fe05-11d0-9dda-00c04fd7ba7c','t':'3d6fa8d1-fe05-11d0-9dda-00c04fd7ba7c','f':'90cbdc39-4a3e-11d1-84f4-0000f80464e3','d':'3d6fa8d4-fe05-11d1-9dda-00c04fd7ba7c','h':'68fdd900-4a3e-11d1-84f4-0000f80464e3'}
# DiskIo GUID is the documented classic DiskIo class, same as earlier verifier fixtures.
G['d']='3d6fa8d4-fe05-11d0-9dda-00c04fd7ba7c'
def event(k,op,n,**data):
 fields=''.join('<Data Name="'+a+'">'+str(b)+'</Data>' for a,b in data.items())
 return '<Event><System><Provider Guid="{'+G[k]+'}"/><Opcode>'+str(op)+'</Opcode><TimeCreated SystemTime="2026-10-14T18:00:%02d.0000000Z"/></System><EventData>'%n+fields+'</EventData></Event>'
def corpus():
 e=event
 start=[e('h',0,0,EventsLost=0,BuffersLost=0,PointerSize=8),e('p',1,1,ProcessId=4242,ImageFileName='tapectl.exe',CommandLine='tapectl.exe verify rehearsal.img'),e('t',1,2,ProcessId=4242,TThreadId=5000),e('f',64,3,IrpPtr='0xA1',TTID=5000,FileObject='0xF1',FileKey='0xE1',CreateOptions='0x1000020',ShareAccess=3,OpenPath='rehearsal.img'),e('f',67,4,Offset=4296015360,IrpPtr='0xB2',FileObject='0xF1',FileKey='0xE1',TTID=5000,IoSize=512,IoFlags=0),e('f',76,5,IrpPtr='0xB2',ExtraInfo=512,NtStatus=0)]
 other=e('f',64,6,IrpPtr='0xA3',TTID=5000,FileObject='0xF2',FileKey='0xE2',CreateOptions='0x1000020',ShareAccess=3,OpenPath='verify-out.txt')
 write=lambda n,fo='0xF2',fk='0xE2':e('f',68,n,Offset=0,IrpPtr='0xD1',FileObject=fo,FileKey=fk,TTID=5000,IoSize=3,IoFlags=0)
 disk=lambda n:e('d',11,n,DiskNumber=0,IrpFlags='0x60043',TransferSize=4096,ByteOffset=123456,IssuingThreadId=5000)
 end=[e('t',2,10,ProcessId=4242,TThreadId=5000),e('p',2,11,ProcessId=4242,ImageFileName='tapectl.exe')]
 close=lambda n,fo='0xF2',fk='0xE2':e('f',66,n,TTID=5000,FileObject=fo,FileKey=fk)
 sets={
 'image-baseline':('PASS',start+end,'rehearsal.img'),
 'image-stdout-write-backing-disk':('PASS',start+[other,write(7),disk(8)]+end,'rehearsal.img'),
 'image-known-foreign-close-after-exit':('PASS',start+[other]+end+[close(12)],'rehearsal.img'),
 'image-target-write':('NOT_PASS',start+[write(7,'0xF1','0xE1')]+end,'rehearsal.img'),
 'image-invalid-object-write':('NOT_PASS',start+[write(7,'0','0xE2')]+end,'rehearsal.img'),
 'image-unknown-key-write':('NOT_PASS',start+[write(7,'0xF9','0')]+end,'rehearsal.img'),
 'image-unknown-post-exit-write':('NOT_PASS',start+end+[write(12,'0xF9','0')],'rehearsal.img'),
 'image-target-post-exit-write':('NOT_PASS',start+end+[write(12,'0xF1','0xE1')],'rehearsal.img'),
 'image-target-post-exit-read':('NOT_PASS',start+end+[e('f',67,12,Offset=4296015360,IrpPtr='0xB9',FileObject='0xF1',FileKey='0xE1',TTID=5000,IoSize=512,IoFlags=0)],'rehearsal.img'),
 'image-foreign-object-target-key-write':('NOT_PASS',start+[other,write(7,'0xF2','0xE1')]+end,'rehearsal.img'),
 'physical-disk-write':('NOT_PASS',start+[disk(8)]+end,r'\\.\PhysicalDrive0'),
 'image-loss':('NOT_PASS',[s.replace('Name="EventsLost">0<','Name="EventsLost">1<') for s in start]+end,'rehearsal.img'),
 }
 physical=[s.replace('rehearsal.img',r'\\.\PhysicalDrive0' if 'CommandLine' in s else r'\Device\Harddisk0\DR0') for s in start]
 sets['physical-baseline']=('PASS',physical+end,r'\\.\PhysicalDrive0')
 sets['physical-disk-write']=('NOT_PASS',physical+[disk(8)]+end,r'\\.\PhysicalDrive0')
 return sets
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--checker',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();res={}
 with tempfile.TemporaryDirectory() as td:
  d=Path(td);exe=d/'tapectl.exe';exe.write_bytes(b'SYNTHETIC VERIFICATION STAND-IN: DO NOT EXECUTE\n');h=hashlib.sha256(exe.read_bytes()).hexdigest()
  for name,b in [('diag',''),('geo','4296015872\n'),('stdout','OK\n'),('exits','wpr-start 0\nwpr-stop 0\ntracerpt 0\n')]: (d/name).write_text(b)
  for id,(want,events,target) in corpus().items():
   (d/'geo').write_text('Number : 0\nSize : 4296015872\nLogicalSectorSize : 512\n' if id.startswith('physical-') else '4296015872\n')
   raw=('<Events>'+''.join(events)+'</Events>').encode();(d/'trace.xml').write_bytes(raw)
   args=[sys.executable,'-B',str(a.checker.resolve()),'--format','etw-xml','--trace',str(d/'trace.xml'),'--pid','4242','--capacity','4296015872','--target',target,'--disk','0','--geometry',str(d/'geo'),'--exe',str(exe),'--sha256',h,'--stdout',str(d/'stdout'),'--tracer-log',str(d/'exits'),'--exit-code','0','--diagnostics',str(d/'diag')]
   r=subprocess.run(args,capture_output=True,text=True)
   assert r.stdout,(id,r.stderr)
   got=json.loads(r.stdout)
   res[id]={'expected':want,'verdict':got['verdict'],'matches':got['verdict']=='PASS' if want=='PASS' else got['verdict']!='PASS','trace_sha256':hashlib.sha256(raw).hexdigest(),'fail':got.get('fail'),'held':got.get('held')}
 a.out.write_text(json.dumps(res,indent=2)+'\n');print(json.dumps({k:(v['expected'],v['verdict'],v['matches']) for k,v in res.items()},indent=1))
