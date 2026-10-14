"""Reproduce findings against the pinned method under review, not Product acceptance."""
from pathlib import Path
import hashlib, json, subprocess, sys

root=Path(__file__).parent/'method'
records=json.loads((root/'controls.json').read_text())
for record in records:
    argv=record['argv']
    local=[sys.executable,str(root/'a6check.py')]
    for arg in argv[2:]:
        local.append(str(root/Path(arg).name) if arg.startswith('/workspace/') else arg)
    result=subprocess.run(local,capture_output=True,text=True)
    assert result.returncode==record['returncode'],record['case']
    assert json.loads(result.stdout)==json.loads(record['stdout']),record['case']
    assert result.stderr==record['stderr'],record['case']
    print(record['case'],json.loads(result.stdout)['verdict'],'exit',result.returncode)
print('Reproduced two good cases and four false PASS findings; NOT a method acceptance')
