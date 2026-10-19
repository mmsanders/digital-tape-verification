"""Validate compact native facts; preserve the full-checker stop."""
import copy,json,struct
from pathlib import Path
HERE=Path(__file__).resolve().parent
F='90cbdc39-4a3e-11d1-84f4-0000f80464e3';D='3d6fa8d4-fe05-11d0-9dda-00c04fd7ba7c'
def num(v):return int(v,16)if str(v).lower().startswith('0x')else int(v)
def check(j):
    assert j['events']==948634 and j['xml_sha256']=='69a81ab6ca7f8aaf7d533b511c496c048bd4c11620999e0159d5898c6fe4ff98'
    r={x['n']:x for x in j['records']};assert len(r)==51
    assert r[1]['data']['EventsLost']==r[1]['data']['BuffersLost']=='0'
    targetkey=0xffffa1861bf99700;logkey=0xffffa18609084d30
    for start,end in[(90388,90461),(300079,300084)]:
        a,b=r[start],r[end];assert a['guid']==b['guid']==F and(a['opcode'],b['opcode'])==(67,76)
        raw=bytes.fromhex(a['payload']);off,irp,fo,fk,tid,size,flags=struct.unpack_from('<QQQQIII',raw)
        assert(off,fk,tid,size)==(62537072128,targetkey,22440,512)
        assert len(raw)==48 and num(a['execution']['ThreadID'])==tid
        assert num(b['data']['IrpPtr'])==irp and num(b['data']['NtStatus'])==0 and num(b['data']['ExtraInfo'])==512
    exitrow=r[480405];assert num(exitrow['data']['ProcessId'])==30236 and num(exitrow['data']['ExitStatus'])==0
    assert 'PhysicalDrive1'in exitrow['data']['CommandLine']
    names=[x for x in r.values()if x['guid']==F and x['opcode']in(0,32,35,36)and num(x['data'].get('FileObject','0'))==logkey]
    assert names and all(x['data']['FileName']==r'\Device\HarddiskVolume3\$LogFile'for x in names)
    for n,off,size in[(480422,16384,4096),(480466,81920,8192)]:
        a=r[n];assert a['guid']==F and a['opcode']==68
        fields=struct.unpack_from('<QQQQIII',bytes.fromhex(a['payload']))
        assert(fields[0],fields[3],fields[4],fields[5])==(off,logkey,22440,size)
        assert exitrow['time']<a['time']
    for n,size in[(480439,4096),(480483,8192)]:
        a=r[n];assert a['guid']==D and a['opcode']==11
        assert num(a['data']['DiskNumber'])==0
        assert num(a['data']['FileObject'])==logkey and num(a['data']['TransferSize'])==size
        assert exitrow['time']<a['time']
    result=json.loads((HERE/'CHECKER-RESULT.json').read_text())
    assert result['verdict']=='FAIL'and len(result['fail'])==1 and not result['held']
    assert result['target_calls']==dict(read=77556,write=0,flush=0)
    assert result['identity']['target_kind']=='disk'and result['identity']['target_key_set_complete']
    assert not result['identity']['writes_unresolved']
    assert {x['n']for x in result['identity']['post_exit']['remaining']}=={480422,480439,480466,480483}
if __name__=='__main__':
    j=json.loads((HERE/'NATIVE-EXCERPT.json').read_text());check(j)
    for case in('short-native-return','card-disk-write'):
        bad=copy.deepcopy(j);r={x['n']:x for x in bad['records']}
        if case=='short-native-return':r[90461]['data']['ExtraInfo']='0x1ff'
        else:r[480439]['data']['DiskNumber']='1'
        try:check(bad)
        except AssertionError:continue
        raise AssertionError('Causal negative control escaped: '+case)
    print('PASS compact native facts and two causal controls; full checker FAIL and physical A6 HELD preserved')
