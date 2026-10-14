"""Reproduce the saved green baseline and missing-correlation false PASS.

Success of this script confirms the defect; it does not accept the method.
"""
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
os.chdir(HERE)
saved = json.loads((HERE / 'independent-controls/results.json').read_text())
for name, observation in saved.items():
    command = [sys.executable, str(HERE / 'a6check.py')] + observation['command'][2:]
    result = subprocess.run(command, capture_output=True, text=True)
    parsed = json.loads(result.stdout)
    assert result.returncode == observation['exit'] == 0, (name, result.stderr)
    assert parsed == observation['result'], (name, parsed)
    assert parsed['verdict'] == 'PASS'
    print(name + ': reproduced PASS0' + (' (defect)' if name != 'baseline' else ' (positive)'))
