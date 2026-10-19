"""Select original native records for the new physical-capture disposition.

No Product parser import. No events synthesized. The subset is explanatory
evidence, never a substitute complete capture for judging absence of writes.
"""
import argparse,hashlib,json,struct,xml.etree.ElementTree as E
from pathlib import Path
F='90cbdc39-4a3e-11d1-84f4-0000f80464e3';T='3d6fa8d1-fe05-11d0-9dda-00c04fd7ba7c';P='3d6fa8d0-fe05-11d0-9dda-00c04fd7ba7c'
KEYS={0xffffa18609084d30,0xffffa1861bf99700,0xffffa18626d97b90,0xffffa18629102d80}
def num(v):
    try:return int(v,16)if v.lower().startswith('0x')else int(v)
    except (AttributeError,ValueError,TypeError):return None
def run(xml,out):
    assert hashlib.file_digest(xml.open('rb'),'sha256').hexdigest()=='69a81ab6ca7f8aaf7d533b511c496c048bd4c11620999e0159d5898c6fe4ff98'
    rows=[];n=0;it=E.iterparse(xml,events=('start','end'));_,root=next(it)
    for kind,e in it:
        if kind!='end'or e.tag.rsplit('}',1)[-1]!='Event':continue
        n+=1;d={};s={}
        for c in e.iter():
            tag=c.tag.rsplit('}',1)[-1]
            if tag=='EventGuid':s['guid']=(c.text or '').strip('{}').lower()
            elif tag=='Opcode'and(c.text or '').strip().isdigit():s.setdefault('opcode',int(c.text))
            elif tag=='Version'and(c.text or '').strip().isdigit():s.setdefault('version',int(c.text))
            elif tag=='TimeCreated':s['time']=c.get('SystemTime')
            elif tag=='Execution':s['execution']=dict(c.attrib)
            elif tag=='EventPayload':s['payload']=(c.text or '').strip()
            elif tag=='Data'and c.get('Name'):d[c.get('Name')]=(c.text or '').strip()
        g=s.get('guid');op=s.get('opcode');keep=n in(1,90388,300079,480422,480439,480466,480483)
        if g==P and num(d.get('ProcessId'))==30236:keep=True
        if g==T and s.get('payload')and s.get('version')==3:
            b=bytes.fromhex(s['payload'])
            if len(b)>=72 and struct.unpack_from('<I',b)[0]==30236:keep=True
        if g==F:
            if op in(0,32,35,36)and num(d.get('FileObject'))in KEYS:keep=True
            if op==64 and num(d.get('TTID'))==22440:keep=True
            if op==76 and num(d.get('IrpPtr'))in(0xffffa1862798e0f8,0xffffa18617c37c88)and(90388<n<90488 or 300079<n<300179):keep=True
        if keep:rows.append(dict(n=n,**s,data=d))
        root.remove(e);e.clear()
    assert n==948634
    result=dict(xml_sha256='69a81ab6ca7f8aaf7d533b511c496c048bd4c11620999e0159d5898c6fe4ff98',events=n,scope='original selected native records only; absence/lifetime verdict comes from the full exact checker execution',records=rows)
    out.write_text(json.dumps(result,indent=2)+'\n');print('Selected',len(rows),'original records from',n)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('xml',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args();run(a.xml,a.out)
