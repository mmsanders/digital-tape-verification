"""Reproduce baseline and remaining uncertainty faults; success is not acceptance."""
from pathlib import Path
import json
import os
import subprocess
import sys

HERE=Path(__file__).resolve().parent
os.chdir(HERE)
saved=json.loads((HERE/'independent-controls/results.json').read_text())
for name,observation in saved.items():
    args=list(observation['command'][2:])
    for flag in ('--geometry','--stdout','--diagnostics','--tracer-log'):
        at=args.index(flag)+1
        suffix={'--geometry':'geo','--stdout':'out','--diagnostics':'diag','--tracer-log':'exits'}[flag]
        args[at]='independent-controls/001-'+suffix
    result=subprocess.run([sys.executable,str(HERE/'a6check.py')]+args,capture_output=True,text=True)
    parsed=json.loads(result.stdout)
    assert result.returncode==observation['exit']==0,(name,result.stderr)
    for field in ('verdict','fail','held','last_sector_reads','target_calls'):
        assert parsed[field]==observation['result'][field],(name,field,parsed)
    for field in ('trace','geometry','exe','stdout','tracer_log'):
        assert parsed['inputs'][field]['sha256']==observation['result']['inputs'][field]['sha256']
    print(name+': reproduced PASS0'+(' (positive)' if name=='baseline' else ' (uncertainty defect)'))
