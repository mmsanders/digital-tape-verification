"""Independent bounded request-lifetime controls; synthetic, not native acceptance."""
from pathlib import Path
import copy
import json
import subprocess
import sys
import xml.etree.ElementTree as ET

HERE=Path(__file__).resolve().parent
helper=HERE/'a6check.py'
fx=HERE/'fixtures/verification-173'
base=ET.fromstring((fx/'001-xml').read_text())
def opcode(e):return int(e.find('{*}System/{*}Opcode').text)
read=next(e for e in base if opcode(e)==67)
completion=next(e for e in base if opcode(e)==76)
file_guid='{90cbdc39-4a3e-11d1-84f4-0000f80464e3}'

def event(op,number,data):
    e=copy.deepcopy(read)
    e.find('{*}System/{*}Opcode').text=str(op)
    e.find('{*}System/{*}TimeCreated').set('SystemTime','2026-10-14T18:00:01.%07dZ'%number)
    d=e.find('{*}EventData')
    for child in list(d):d.remove(child)
    for name,value in data.items():ET.SubElement(d,'{http://schemas.microsoft.com/win/2004/08/events/event}Data',Name=name).text=str(value)
    return e

args=['--format','etw-xml','--pid','4242','--capacity','62537072640',
      '--target',r'\\.\PhysicalDrive1','--disk','1','--geometry',str(fx/'001-geo'),
      '--exe',str(fx/'stand-in-exe.bin'),'--sha256','525f1d08f6b6f356ce6a48a2a74a828aa3dc1d41fbea6771df9400de191f8732',
      '--stdout',str(fx/'001-out'),'--diagnostics',str(fx/'001-diag'),
      '--tracer-log',str(fx/'001-exits'),'--exit-code','0']
out=HERE/'lifecycle-controls';out.mkdir(exist_ok=True)
observations=[]
for kind in (64,65,66,67,68):
    for previous in range(1,5):
        for resolved_before in range(previous+1):
            # Completion order cannot establish which overlapping request ended;
            # only full resolution BEFORE the mirror read restores identity.
            # Foreign thread's non-read/write requests are still competing IRPs.
            root=copy.deepcopy(base)
            index=list(root).index(next(e for e in root if opcode(e)==67))
            for e in list(root)[index:]:root.remove(e)
            ticks=2000
            for i in range(previous):
                if kind==67:
                    data={'IrpPtr':'0xB2','FileObject':'0xF1','TTID':'0x1388','Offset':0,'IoSize':512}
                else:
                    data={'IrpPtr':'0xB2','FileObject':'0xF9','TTID':'777','OpenPath':r'C:\helper.img','Offset':0,'IoSize':512}
                root.append(event(kind,ticks,data));ticks+=100
            for i in range(resolved_before):
                root.append(event(76,ticks,{'IrpPtr':'0xB2','NtStatus':'0x0','ExtraInfo':512}));ticks+=100
            root.append(event(67,ticks,{'IrpPtr':'0xB2','FileObject':'0xF1','TTID':'0x1388','Offset':62537072128,'IoSize':512}));ticks+=100
            for i in range(previous-resolved_before+1):
                root.append(event(76,ticks,{'IrpPtr':'0xB2','NtStatus':'0x0','ExtraInfo':512}));ticks+=100
            name='%d-%d-%d'%(kind,previous,resolved_before)
            path=out/(name+'.xml');path.write_bytes(ET.tostring(root,encoding='utf-8'))
            result=subprocess.run([sys.executable,str(helper),'--trace',str(path)]+args,capture_output=True,text=True)
            observation=json.loads(result.stdout)
            want='PASS' if resolved_before==previous else 'HELD'
            assert observation['verdict']==want,(name,want,observation)
            assert result.returncode==(0 if want=='PASS' else 3)
            if want=='HELD':assert any('overlapping' in reason for reason in observation['held'])
            observations.append({'case':name,'expected':want,'exit':result.returncode,'result':observation})
(out/'results.json').write_text(json.dumps(observations,indent=2)+'\n')
print(len(observations),'synthetic lifecycle controls passed; no native acceptance')
