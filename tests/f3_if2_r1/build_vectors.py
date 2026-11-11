"""Independent HEX/ELF and host-build metadata CLI expectations, G4."""
import copy,json,struct
from support import *

def inspect_cases():
 out=[]
 def add(name,control=False,edit=lambda h,e,b:(h,e,b),state='MISMATCH',reasons=()):out.append(dict(name=name,control=control,edit=edit,state=state,reasons=list(reasons)))
 add('production-no-seam',state='CONSISTENT');add('control-seam-present',control=True,state='CONSISTENT')
 add('production-seam-present',edit=lambda h,e,b:(h,elf32(True),dict(b,firmware_elf_sha256=SHA(elf32(True)))),reasons=['seam_present_in_production'])
 add('control-seam-absent',control=True,edit=lambda h,e,b:(h,elf32(False),dict(b,firmware_elf_sha256=SHA(elf32(False)))),reasons=['seam_absent_in_control'])
 add('both-file-hash-mismatches',edit=lambda h,e,b:(h,e,dict(b,firmware_hex_sha256='0'*64,firmware_elf_sha256='0'*64)),reasons=['elf_hash_mismatch','hex_hash_mismatch'])
 add('claimed-control-on-production-negative-control',edit=lambda h,e,b:(h,e,dict(b,env='teensy41_ctl_wake150',inject_us=150000)),reasons=['marker_mismatch','seam_absent_in_control'])
 add('unknown-env',edit=lambda h,e,b:(h,e,dict(b,env='unknown')),reasons=['unknown_env','marker_mismatch'])
 add('production-wrong-inject',edit=lambda h,e,b:(h,e,dict(b,inject_us=1)),reasons=['inject_mismatch','marker_mismatch'])
 add('control-wrong-inject',control=True,edit=lambda h,e,b:(h,e,dict(b,inject_us=149999)),reasons=['inject_mismatch','marker_mismatch'])
 for n,reason in [(0,'marker_missing'),(2,'marker_duplicate')]:
  def edit(h,e,b,n=n):
   nh,_,_=artifact(False,marker_count=n);return nh,e,dict(b,firmware_hex_sha256=SHA(nh))
  add('marker-count-'+str(n),edit=edit,reasons=[reason])
 add('marker-ID-mismatch',edit=lambda h,e,b:(h,e,dict(b,id='c'*32)),reasons=['marker_mismatch'])
 for name,edit in [('bad-magic',lambda e:b'NOPE'+e[4:]),('ELF64-class',lambda e:e[:4]+b'\x02'+e[5:]),('wrong-endian',lambda e:e[:5]+b'\x02'+e[6:]),('truncated-header',lambda e:e[:20]),('out-of-file-section-table',lambda e:e[:32]+struct.pack('<I',0xffffff00)+e[36:])]:
  def mutate(h,e,b,edit=edit):e=edit(e);return h,e,dict(b,firmware_elf_sha256=SHA(e))
  add(name,edit=mutate,state='INVALID',reasons=['elf_malformed'])
 for name,edit in [('bad-hex-text',lambda h:b'NOT HEX\n'),('bad-hex-checksum',lambda h:h[:-3]+b'00\n')]:
  def mutate(h,e,b,edit=edit):h=edit(h);return h,e,dict(b,firmware_hex_sha256=SHA(h))
  add(name,edit=mutate,state='INVALID',reasons=['hex_malformed'])
 def decoy(h,e,b):e+=b'fw_wake_inject\0';return h,e,dict(b,firmware_elf_sha256=SHA(e))
 add('seam-text-outside-symbol-table-is-not-a-symbol',edit=decoy,state='CONSISTENT')
 for typ,data in [(2,b'\x10\x00'),(4,b'\x00\x01')]:
  def ext(h,e,b,typ=typ,data=data):
   r=bytes([2,0,0,typ])+data;prefix=(':'+r.hex().upper()+f'{(-sum(r))&255:02X}'+'\n').encode();h=prefix+h;return h,e,dict(b,firmware_hex_sha256=SHA(h))
  add('Intel-HEX-type-'+str(typ),edit=ext,state='CONSISTENT')
 return out

def build_record_cases():
 out=[('exact-production-metadata',{},True),('exact-control-metadata',dict(control=True),True)]
 for key,value in [('id','BAD'),('commit','xyz'),('dirty','2'),('inject-us','-1'),('engine-tree','wrong')]:out.append(('malformed-'+key,dict(bad_key=key,bad_value=value),False))
 out.append(('wrong-toolchain-shape',dict(bad_toolchain=True),False));return out
