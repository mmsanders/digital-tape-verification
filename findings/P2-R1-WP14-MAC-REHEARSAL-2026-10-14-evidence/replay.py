"""Authenticate and replay native Mac collection failure; no Mach-O execution."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile
import zipfile

HERE=Path(__file__).resolve().parent
archive=HERE/'a6-rh-mac.azesRa.zip'
assert hashlib.sha256(archive.read_bytes()).hexdigest()=='cd7ec2507a6308bf572a15627ae68125e04c13a5974e5ba96830d89812b04c5a'
expected={'tapectl':'e7550d8bedbb0c784fd528c387a87cca2bad8d1b411c39217d25377329bb0beb',
          'a6check.py':'227ceed2f1ca8817447c4103983c72b16a060b1d3323de22c805289b621bd1ef',
          'a6-macos.d':'c9764f11f7894fbe57dc08b0fb6248e70ce244b2f6137a9ee59d057397af7be8'}
with tempfile.TemporaryDirectory() as directory:
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        for member in z.infolist():
            path=PurePosixPath(member.filename)
            assert not path.is_absolute() and '..' not in path.parts
            assert (member.external_attr>>16)&0o170000 != 0o120000
        z.extractall(directory)
    run=Path(directory)/'a6-rh-mac.azesRa'
    for name,want in expected.items():assert hashlib.sha256((run/name).read_bytes()).hexdigest()==want
    before=(run/'hashes-before.txt').read_bytes()
    assert before==(run/'hashes-after.txt').read_bytes()
    assert dict((line.split()[1],line.split()[0]) for line in before.decode().splitlines())==expected
    result=subprocess.run([sys.executable,'a6check.py','--format','dtrace','--trace','verify.trace',
                           '--pid','44532','--capacity','4296015872','--geometry','geometry.txt',
                           '--target','rehearsal.img','--exe','tapectl','--sha256',expected['tapectl'],
                           '--stdout','verify-out.txt','--diagnostics','dtrace-err.txt',
                           '--tracer-log','tracer-exits.txt'],cwd=run,capture_output=True,text=True)
    assert result.returncode==int((HERE/'independent-checker-exit.txt').read_text())==1 and result.stderr==''
    actual=json.loads(result.stdout)
    assert actual==json.loads((run/'checker.json').read_text())
    assert actual==json.loads((HERE/'independent-checker.json').read_text())
    assert actual['verdict']=='FAIL' and actual['last_sector_reads']==[]
    print('Original65,223-byte bundle authenticated; native FAIL1 exactly reproduced; physical A6 remains HELD')
