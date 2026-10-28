"""353 bounded retained-shape reference decoder; NOT an A6 checker or live reader."""
import re,struct,uuid,xml.etree.ElementTree as E
NS='http://schemas.microsoft.com/win/2004/08/events/event'
TR='http://schemas.microsoft.com/win/2004/08/events/trace'
SESSION='9e814aad-3204-11d2-9a82-006008a86939'
HEADER='68fdd900-4a3e-11d1-84f4-0000f80464e3'
FILE='90cbdc39-4a3e-11d1-84f4-0000f80464e3'
THREAD='3d6fa8d1-fe05-11d0-9dda-00c04fd7ba7c'
PROCESS='3d6fa8d0-fe05-11d0-9dda-00c04fd7ba7c'
DISK='3d6fa8d4-fe05-11d0-9dda-00c04fd7ba7c'
SPLIT='d837ca92-12b9-44a5-ad6a-3a65b3578aa8'
CLASSES={HEADER,FILE,THREAD,PROCESS,DISK,SPLIT}
class Stop(ValueError):pass
def need(x,why):
    if not x:raise Stop('STOP_LAYOUT_UNSUPPORTED: '+why)
def number(x,bits=64):
    need(isinstance(x,str) and re.fullmatch(r'(?:[0-9]+|0[xX][0-9a-fA-F]+)',x.strip()),'malformed unsigned numeric field')
    s=x.strip();v=int(s,16 if s.lower().startswith('0x') else 10);need(v<2**bits,'numeric overflow');return v
def guid(x):
    try:return str(uuid.UUID(x.strip('{}')))
    except (ValueError,AttributeError):raise Stop('STOP_LAYOUT_UNSUPPORTED: malformed/missing class GUID')
def one(e,path):
    xs=e.findall(path);need(len(xs)==1,'missing/duplicate '+path);return xs[0]
def read_event(e):
    need(e.tag=='{'+NS+'}Event','wrong XML export namespace')
    system=one(e,'{'+NS+'}System');provider=guid(one(system,'{'+NS+'}Provider').get('Guid'))
    eg=e.findall('{'+TR+'}ExtendedTracingInfo/{'+TR+'}EventGuid')
    need(len(eg)<=1,'duplicate EventGuid')
    need(eg or provider!=SESSION,'kernel-session record missing authoritative EventGuid')
    cls=guid(eg[0].text) if eg else provider
    need(cls in CLASSES,'unknown required class')
    need(provider not in CLASSES or provider==cls,'conflicting known class identities')
    need(provider in CLASSES or provider==SESSION,'unsupported provider export')
    version=number(one(system,'{'+NS+'}Version').text,8);opcode=number(one(system,'{'+NS+'}Opcode').text,8)
    execution=one(system,'{'+NS+'}Execution');tid=number(execution.get('ThreadID'),32)
    data={}
    for x in e.findall('{'+NS+'}EventData/{'+NS+'}Data'):
        key=x.get('Name');need(key and key not in data,'missing/duplicate field name');data[key]=(x.text or '').strip()
    errs=e.findall('{'+NS+'}ProcessingErrorData');payload=None
    if errs:
        need(len(errs)==1 and not data,'mixed raw and named export')
        need(number(one(errs[0],'{'+NS+'}ErrorCode').text)==15005,'unknown processing error')
        raw=one(errs[0],'{'+NS+'}EventPayload').text
        need(isinstance(raw,str) and re.fullmatch(r'(?:[0-9A-Fa-f]{2})+',raw.strip()),'missing/malformed raw payload')
        payload=bytes.fromhex(raw.strip())
    return dict(cls=cls,version=version,opcode=opcode,header_tid=tid,data=data,payload=payload)
def header(e):
    r=read_event(e);need((r['cls'],r['version'],r['opcode'])==(HEADER,2,0) and r['payload'] is None,'unsupported header tuple/export')
    d=r['data']
    keys=['BufferSize','PointerSize','EventsLost','BuffersLost','BuffersWritten','LogFileMode','StartTime','EndTime','ProviderVersion']
    need(all(k in d for k in keys),'missing header contract field')
    vals={k:number(d[k],64 if k in ['StartTime','EndTime'] else 32) for k in keys}
    need(vals['PointerSize']==8,'unsupported pointer width; never infer from OS')
    need(vals['StartTime']<=vals['EndTime'],'header time order')
    # Loss is retained; this decoder never produces an absence/lifetime verdict.
    return vals
def decode(e,context):
    need(type(context) is dict and context.get('PointerSize')==8,'missing qualified trace-header context')
    r=read_event(e);b=r['payload'];key=(r['cls'],r['version'],r['opcode'])
    if r['cls']==HEADER:return dict(kind='header',fields=header(e))
    if r['cls']==FILE and r['version']==3 and r['opcode'] in [67,68]:
        need(b is not None and len(b) in [44,48],'FileIo v3 raw length/export')
        off,irp,fo,fk,tid,size,flags=struct.unpack_from('<QQQQIII',b)
        need(tid==r['header_tid'],'FileIo TTID/header ThreadID mismatch')
        need(irp and fo and fk and tid and size,'zero required identity/size')
        return dict(kind='FileIoReadWrite',opcode=r['opcode'],Offset=off,IrpPtr=irp,FileObject=fo,FileKey=fk,TTID=tid,IoSize=size,IoFlags=flags,uninterpreted_tail=b[44:].hex())
    if r['cls']==THREAD and r['version']==3 and r['opcode'] in [1,2,3,4]:
        need(b is not None and len(b) in [72,74],'Thread v3 raw length/export')
        need(len(b)==72 or b[72:]==b'\0\0','unsupported Thread name tail')
        pid,tid=struct.unpack_from('<II',b);need(pid and tid,'zero Thread payload process/thread')
        # Header IDs can describe the creator/current thread, not this new thread.
        # Only payload ProcessId/TThreadId define this lifecycle record.
        pointers=struct.unpack_from('<7Q',b,8);tag=struct.unpack_from('<I',b,64)[0]
        return dict(kind='Thread',opcode=r['opcode'],ProcessId=pid,TThreadId=tid,pointers=list(pointers),SubProcessTag=tag,priorities_flags=list(b[68:72]),name_tail=b[72:].hex())
    if key==(FILE,3,76):
        need(b is None and set(r['data'])=={'IrpPtr','ExtraInfo','NtStatus'},'OpEnd v3 named field/export set')
        out={k:number(v,32 if k=='NtStatus' else 64) for k,v in r['data'].items()};need(out['IrpPtr']>0,'zero OpEnd identity')
        return dict(kind='OpEnd',**out)
    raise Stop('STOP_LAYOUT_UNSUPPORTED: tuple/export not in partial353 matrix')
