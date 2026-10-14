"""Replay the twelve published175 faults against the reviewed helper; not native acceptance."""
import json
import os
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent
os.chdir(HERE)
saved=json.loads((HERE/'published-175-replay.json').read_text())
for name,observation in saved.items():
    args=list(observation['command'][2:])
    for flag in ('--trace','--geometry','--exe','--stdout','--diagnostics','--tracer-log'):
        at=args.index(flag)+1
        args[at]=str(HERE/'fixtures/verification-175'/Path(args[at]).name)
    result=subprocess.run([sys.executable,str(HERE/'a6check.py')]+args,capture_output=True,text=True)
    parsed=json.loads(result.stdout)
    assert result.returncode==observation['exit'],(name,result.stderr)
    assert parsed['verdict']==('PASS' if name=='baseline' else 'HELD')
    for field in ('verdict','fail','held','last_sector_reads','target_calls'):
        assert parsed[field]==observation['result'][field],(name,field,parsed)
    for field in ('trace','geometry','exe','stdout','tracer_log'):
        assert parsed['inputs'][field]['sha256']==observation['result']['inputs'][field]['sha256']
    print(name+': reproduced '+parsed['verdict']+str(result.returncode))
