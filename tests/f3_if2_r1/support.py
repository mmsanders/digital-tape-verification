"""Independent generated artifacts for public F3-IF/2; never target firmware."""
import copy,hashlib,importlib.util,json,struct,sys
from pathlib import Path
OLD=Path(__file__).resolve().parents[1]/'f3_wake_if1_r1';sys.path.insert(0,str(OLD))
import checker_cases as if1
from cases import scenario as old_scenario
SHA=lambda b:hashlib.sha256(b).hexdigest()

def elf32(symbol=False):
 # ELF32 little endian ARM ET_REL: null, .text, .strtab, .symtab, .shstrtab.
 shnames=b'\0.text\0.strtab\0.symtab\0.shstrtab\0';strings=b'\0'+(b'fw_wake_inject\0' if symbol else b'ordinary_function\0')
 text=b'\x00\xbf';syms=b'\0'*16+struct.pack('<IIIBBH',1,0,len(text),0x12,0,1)
 raw=bytearray(b'\0'*52);sections=[]
 for data in (text,strings,syms,shnames):
  while len(raw)%4:raw+=b'\0'
  sections.append((len(raw),len(data)));raw+=data
 while len(raw)%4:raw+=b'\0'
 shoff=len(raw);raw+=b'\0'*40
 for name,typ,index,link,info,align,entsize in [('.text',1,0,0,0,2,0),('.strtab',3,1,0,0,1,0),('.symtab',2,2,2,1,4,16),('.shstrtab',3,3,0,0,1,0)]:
  off,size=sections[index];raw+=struct.pack('<10I',shnames.index(name.encode()),typ,6 if name=='.text' else 0,0,off,size,link,info,align,entsize)
 ident=b'\x7fELF'+bytes([1,1,1,0])+b'\0'*8
 raw[:52]=struct.pack('<16sHHIIIIIHHHHHH',ident,1,40,1,0,0,shoff,0,52,0,0,40,5,4)
 return bytes(raw)

def artifact(control=False,marker_count=1,symbol=None):
 id=('b' if control else 'a')*32;env='teensy41_ctl_wake150' if control else 'teensy41';inject=150000 if control else 0
 marker=f'DTBUILD id={id} commit={if1.COMMIT} dirty=0 env={env} inject_us={inject}'.encode()
 image=if1.intel(b'SYNTHETIC NOT FLASHABLE\0'+(marker+b'\0')*marker_count);elf=elf32(control if symbol is None else symbol)
 build=dict(schema='digital-tape/fw-build/1',id=id,commit=if1.COMMIT,dirty=0,env=env,inject_us=inject,engine_tree='d96b4245e04d74078f8938744b1394c3018516f7',toolchain=copy.deepcopy(if1.PINS),firmware_hex_sha256=SHA(image),firmware_elf_sha256=SHA(elf))
 return image,elf,build

def bundle(control=True):
 m,f=if1.fixture(provenance='simulated',session='simulation')
 image,elf,build=artifact();f.update({'firmware.hex':image,'firmware.elf':elf,'build.json':json.dumps(build).encode()});m['candidate']['firmware_hex_sha256']=SHA(image)
 if control:
  cm,cf=if1.fixture(kind='control_wake150',elapsed=150000,provenance='simulated',session='simulation');image,elf,b=artifact(True)
  prefix='builds/control/';f.update({prefix+'firmware.hex':image,prefix+'firmware.elf':elf,prefix+'build.json':json.dumps(b).encode()})
  f['control.log']=cf['capture.log'].replace(if1.ID.encode(),b['id'].encode());ob=dict(cm['observations'][0],id='SYNTHETIC-CONTROL',sequence=2,capture='control.log',build=prefix);m['observations'].append(ob)
 return m,f

def materialize(d,m,f):
 d.mkdir(parents=True,exist_ok=False)
 for key,raw in f.items():
  p=d/key;assert d.resolve() in p.resolve().parents;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
 m['files']=[dict(path=k,sha256=SHA(raw),bytes=len(raw)) for k,raw in sorted(f.items())];(d/'manifest.json').write_text(json.dumps(m),encoding='utf-8')

def report_keys(r):
 assert set(r)=={'schema','checker','manifest_sha256','accepted','physical_run','overall','criteria','observations'}
 assert r['schema']=='digital-tape/f3-report/1' and r['checker']==dict(name='f3_evidence.py',interface='F3-IF/2') and r['accepted'] is False
 assert set(r['criteria'])=={'F3','F4'}
 assert r['criteria']['F4']==dict(state='NOT_RUN',reasons=['f4_deferred'],target_met=None)
 for c in r['criteria'].values():assert set(c)=={'state','reasons','target_met'} and c['reasons']==sorted(set(c['reasons']))
 for ob in r['observations']:
  assert set(ob)=={'id','sequence','kind','provenance','build_id','state','reasons','elapsed_us','target_met','superseded_by'}
  assert ob['reasons']==sorted(set(ob['reasons']))
 assert [o['sequence'] for o in r['observations']]==sorted(o['sequence'] for o in r['observations'])
 return True
