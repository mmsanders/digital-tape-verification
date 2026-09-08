#!/usr/bin/env python3
"""Mutation test for VT8-001 oracle; not an engine."""
import copy,struct,zlib
from oracle import *
def expect_fail(c,p,e,label):
    x=check(c,p,e)
    if not x:raise AssertionError('mutation escaped: '+label)
    print('CAUGHT',label,'=>',x[0])
def main():
    rb,rec=make_cases()
    for c in (rb,rec):
        p,e=synth_post(c); x=check(c,p,e)
        if x:raise AssertionError((c.id,x))
        print('PASS conforming',c.id)
    p,e=synth_post(rb); s=list(p.slots); s[2]=idx(1,[(0,0,128)],501); expect_fail(rb,Media(p.blocks,p.primary,p.mirror,tuple(s)),e,'reset live-only sequence base')
    p,e=synth_post(rb); e=copy.deepcopy(e); e.insert(1,{'phase':'reset_b','op':'write','lba':LBA_CHUNK_BASE+2*1024,'count':1}); expect_fail(rb,p,e,'reset chunk write')
    p,e=synth_post(rec); s=list(p.slots); s[3]=idx(1,[(0,0,128),(3,0,128)],21); expect_fail(rec,Media(p.blocks,p.primary,p.mirror,tuple(s)),e,'record live-only sequence base')
    p,e=synth_post(rec); e=copy.deepcopy(e); e[0]['lba']=LBA_CHUNK_BASE+2*1024; expect_fail(rec,p,e,'record allocation below H/free_next')
    p,e=synth_post(rec); b=bytearray(p.primary); struct.pack_into('<I',b,12,8); struct.pack_into('<I',b,508,zlib.crc32(b[:508])); bad=bytes(b); expect_fail(rec,Media(p.blocks,bad,bad,p.slots),e,'record sb_generation increment')
    p,e=synth_post(rec); s=list(p.slots); s[3]=idx(1,[(0,0,128),(0,64,128)],701); expect_fail(rec,Media(p.blocks,p.primary,p.mirror,tuple(s)),e,'record overlapping committed index')
    print('SELFTEST PASS: 2 conforming + 6 required mutations')
if __name__=='__main__':main()
