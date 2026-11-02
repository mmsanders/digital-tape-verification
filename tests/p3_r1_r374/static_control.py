"""Measure an actual oversized object and pass its size to the acceptance predicate."""
import json,subprocess,sys,tempfile
from pathlib import Path
from wp17 import budget
with tempfile.TemporaryDirectory()as d:
    p=Path(d);(p/'oversized.c').write_text('char oversized_static[204801];\n')
    subprocess.run(['cc','-c',str(p/'oversized.c'),'-o',str(p/'oversized.o')],check=True)
    text=subprocess.check_output(['size','-A',str(p/'oversized.o')],text=True)
    bss=int(next(line.split()[1]for line in text.splitlines()if line.split()and line.split()[0]=='.bss'))
    assert bss==204801
    budget(0,204800,0,0)
    try:budget(0,bss,0,0)
    except AssertionError as e:assert str(e)=='RAM exceeds 200 KiB'
    else:raise AssertionError('measured oversized static did not fail')
    print(json.dumps(dict(bss=bss,positive_boundary=204800,negative_control='REJECTED measured oversized static')))
