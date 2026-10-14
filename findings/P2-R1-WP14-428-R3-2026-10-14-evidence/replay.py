"""Reproduce the exact third-correction observations; success is not acceptance."""
import json
import os
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent
os.chdir(HERE)
saved=json.loads((HERE/'independent-controls/results.json').read_text())
expected={'baseline':('PASS',0),'missing-irp':('HELD',3),
          'reuse-after-one-of-two-completions':('PASS',0)}
for name,observation in saved.items():
    result=subprocess.run([sys.executable,str(HERE/'a6check.py')]+observation['command'][2:],
                          capture_output=True,text=True)
    parsed=json.loads(result.stdout)
    assert result.returncode==observation['exit'],(name,result.stderr)
    assert parsed==observation['result'],(name,parsed)
    assert (parsed['verdict'],result.returncode)==expected[name]
    print(name+': reproduced '+parsed['verdict']+str(result.returncode))
