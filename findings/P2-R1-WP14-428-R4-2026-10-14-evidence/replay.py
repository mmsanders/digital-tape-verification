"""Reproduce saved control judgments, not native or Product acceptance."""
from pathlib import Path
import json
import os
import subprocess
import sys

HERE=Path(__file__).resolve().parent
os.chdir(HERE)
for collection in ['additional-controls/results.json','published-control-replay.json']:
    saved=json.loads((HERE/collection).read_text())
    for name,observation in saved.items():
        args=list(observation['command'][2:])
        for flag in ('--trace','--geometry','--exe','--stdout','--diagnostics','--tracer-log'):
            at=args.index(flag)+1
            if collection=='published-control-replay.json':
                args[at]=str(HERE/'fixtures/verification-173'/Path(args[at]).name)
        result=subprocess.run([sys.executable,str(HERE/'a6check.py')]+args,capture_output=True,text=True)
        parsed=json.loads(result.stdout)
        assert result.returncode==observation['exit'],(name,result.stderr)
        for field in ('verdict','fail','held','last_sector_reads','target_calls'):
            assert parsed[field]==observation['result'][field],(name,field,parsed)
        for field in ('trace','geometry','exe','stdout','tracer_log'):
            assert parsed['inputs'][field]['sha256']==observation['result']['inputs'][field]['sha256']
        print(name+': reproduced '+parsed['verdict']+str(result.returncode))
