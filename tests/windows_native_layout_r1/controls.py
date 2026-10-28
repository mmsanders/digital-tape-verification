"""Independent finite retained-shape controls; ZERO OS/native/checker execution."""
import copy,hashlib,json,struct,xml.etree.ElementTree as E
from pathlib import Path
import decode as d
HERE=Path(__file__).resolve().parent
raw=(HERE/'native185.xml').read_bytes()
assert hashlib.sha256(raw).hexdigest()=='28a02766f56222e5b699c5d00b79b7319600822f37de46f4d118c38e29636dcb'
events=list(E.fromstring(raw));assert len(events)==5
ctx=d.header(events[0]);positive=[];negative=[]
def xmlpart(e,local):return next(x for x in e.iter() if x.tag.rsplit('}',1)[-1]==local)
def good(name,e,expected):
    got=d.decode(e,ctx)
    for k,v in expected.items():assert got[k]==v,(name,k,got[k],v)
    positive.append(name)
def bad(name,index,mutate,context=None):
    e=copy.deepcopy(events[index]);mutate(e)
    try:d.decode(e,ctx if context is None else context)
    except d.Stop:negative.append(name);return
    raise AssertionError('mutation survived: '+name)
def payload(e,b):xmlpart(e,'EventPayload').text=b.hex()
def remove(e,local):
    for p in e.iter():
        for c in list(p):
            if c.tag.rsplit('}',1)[-1]==local:p.remove(c);return
def main():
    # Every original is identity-extracted. Four supported records decoded; Create stays
    # outside this intentionally PARTIAL oracle, not relabelled an unknown success.
    assert [d.read_event(e)['opcode'] for e in events]==[0,76,67,64,1]
    good('real185 header',events[0],dict(kind='header'))
    good('real185 named OpEnd',events[1],dict(kind='OpEnd',IrpPtr=0xFFFFA186338BF0F8,ExtraInfo=1,NtStatus=0))
    good('real185 raw Read48',events[2],dict(kind='FileIoReadWrite',Offset=0,IoSize=3496,TTID=27364,IrpPtr=0xFFFFA186338BF0F8,FileObject=0xFFFFA1861B91AB60,FileKey=0xFFFF8B022660EAB0,IoFlags=0x60900,uninterpreted_tail='00000000'))
    good('real185 raw Thread74',events[4],dict(kind='Thread',ProcessId=4596,TThreadId=25552,name_tail='0000'))
    # Independent synthetic shorter variants come from documented fixed bases;
    # these are causal interpretation controls, not new actual observations.
    e=copy.deepcopy(events[2]);b=d.read_event(e)['payload'];payload(e,b[:44]);good('synthetic Read44 fixed base',e,dict(IoSize=3496,uninterpreted_tail=''))
    e=copy.deepcopy(events[4]);b=d.read_event(e)['payload'];payload(e,b[:72]);good('synthetic Thread72 fixed base',e,dict(TThreadId=25552,name_tail=''))
    e=copy.deepcopy(events[2]);xmlpart(e,'Opcode').text='68';good('synthetic Write shares published v3 layout',e,dict(opcode=68))
    for opcode in [2,3,4]:
        e=copy.deepcopy(events[4]);xmlpart(e,'Opcode').text=str(opcode);good('synthetic Thread opcode'+str(opcode),e,dict(opcode=opcode))
    e=copy.deepcopy(events[2]);xmlpart(e,'Provider').set('Guid','{'+d.FILE+'}');good('same known Provider/class accepted',e,dict(kind='FileIoReadWrite'))
    # Thread creator header legitimately differs from subject TThreadId in real185.
    assert d.read_event(events[4])['header_tid']==27364 and d.decode(events[4],ctx)['TThreadId']==25552
    for index in [0,1,2,4]:
        bad('missing EventGuid '+str(index),index,lambda e:remove(e,'EventGuid'))
        bad('conflicting known Provider '+str(index),index,lambda e:xmlpart(e,'Provider').set('Guid','{'+d.DISK+'}'))
    bad('foreign required class',2,lambda e:setattr(xmlpart(e,'EventGuid'),'text','{00000000-0000-0000-0000-000000000001}'))
    bad('missing header context',2,lambda e:None,{})
    bad('pointer4 not OS inferred',2,lambda e:None,{'PointerSize':4})
    for index in [1,2,4]:
        for version in [0,2,4,255]:bad('unsupported version '+str(index)+'/'+str(version),index,lambda e,v=version:setattr(xmlpart(e,'Version'),'text',str(v)))
    for value in ['-1','1.0','garbage','4294967296']:
        bad('header thread numeric '+value,2,lambda e,v=value:xmlpart(e,'Execution').set('ThreadID',v))
    bad('TTID/header mismatch',2,lambda e:xmlpart(e,'Execution').set('ThreadID','1'))
    for index,lengths in [(2,[0,36,43,45,47,49,52]),(4,[0,64,71,73,75,76])]:
        for length in lengths:
            def change(e,n=length):
                b=d.read_event(e)['payload'];payload(e,(b+b'\0'*n)[:n])
            bad('raw length '+str(index)+'/'+str(length),index,change)
    bad('missing payload',2,lambda e:remove(e,'EventPayload'))
    bad('odd hex payload',2,lambda e:setattr(xmlpart(e,'EventPayload'),'text','0'))
    bad('nonhex payload',2,lambda e:setattr(xmlpart(e,'EventPayload'),'text','zz'))
    bad('unknown processing error',2,lambda e:setattr(xmlpart(e,'ErrorCode'),'text','5'))
    bad('Thread nonempty/unqualified name',4,lambda e:payload(e,d.read_event(e)['payload'][:72]+b'A\0'))
    bad('unknown required Create opcode in partial decoder',3,lambda e:None)
    for cls,opcode in [(d.PROCESS,1),(d.DISK,10),(d.DISK,12),(d.DISK,14),(d.SPLIT,32)]:
        def unknown(e,cls=cls,opcode=opcode):
            xmlpart(e,'EventGuid').text='{'+cls+'}';xmlpart(e,'Opcode').text=str(opcode)
        bad('unsupported actual tuple '+cls+'/'+str(opcode),2,unknown)
    for name in ['IrpPtr','ExtraInfo','NtStatus']:
        def change(e,name=name):
            next(x for x in e.iter() if x.get('Name')==name).text='not-a-number'
        bad('malformed OpEnd '+name,1,change)
    bad('zero OpEnd identity',1,lambda e:setattr(next(x for x in e.iter() if x.get('Name')=='IrpPtr'),'text','0'))
    bad('duplicate named data',1,lambda e:xmlpart(e,'EventData').append(copy.deepcopy(next(x for x in e.iter() if x.get('Name')=='IrpPtr'))))
    bad('wrong XML namespace',2,lambda e:setattr(e,'tag','{wrong}Event'))
    for field,value in [('PointerSize','4'),('PointerSize','-1'),('ProviderVersion','bad')]:
        bad('header '+field+'/'+value,0,lambda e,k=field,v=value:setattr(next(x for x in e.iter() if x.get('Name')==k),'text',v))
    def missing_pointer(e):
        p=xmlpart(e,'EventData');p.remove(next(x for x in p if x.get('Name')=='PointerSize'))
    bad('missing header PointerSize',0,missing_pointer)
    bad('OpEnd unknown field',1,lambda e:xmlpart(e,'EventData').append(E.Element('{'+d.NS+'}Data',Name='GuessedResult')))
    # Explicit two field mutations verify offsets rather than merely round-tripping.
    e=copy.deepcopy(events[2]);b=bytearray(d.read_event(e)['payload']);struct.pack_into('<Q',b,0,2**32+512);struct.pack_into('<I',b,36,4096);payload(e,b)
    good('synthetic offset/size byte-position control',e,dict(Offset=2**32+512,IoSize=4096,TTID=27364))
    print(json.dumps(dict(scope='PARTIAL RETAINED-SHAPE DECODER ONLY; full route BLOCKED',positive=len(positive),negative=len(negative),positive_cases=positive,negative_cases=negative,original_events=5,supported_original_events=4,native_executions=0,full_trace_replays=0,blocker='SplitIo32 actual event version/export/length not qualified; no invented lineage'),indent=2))
if __name__=='__main__':main()
