"""Saved-file reproduction of corrected-method findings, not acceptance."""
from pathlib import Path
import json, subprocess, sys

root=Path(__file__).parent
for row in json.loads((root/'independent-controls.json').read_text()):
    argv=row['argv']
    local=[sys.executable,str(root/'a6check.py')]
    for a in argv[2:]:
        local.append(str(root/Path(a).name) if a.startswith('/workspace/') else a)
    result=subprocess.run(local,capture_output=True,text=True)
    old=json.loads(row['stdout']);new=json.loads(result.stdout)
    for field in ('verdict','fail','held','target_calls','last_sector_reads','exit','tracer_steps','geometry'):
        assert old[field]==new[field],(row['case'],field)
    assert result.returncode==row['returncode'] and result.stderr==row['stderr'],row['case']
    print(row['case'],new['verdict'],'exit',result.returncode)
print('Reproduced green baseline and three false PASS cases; not a method PASS')
