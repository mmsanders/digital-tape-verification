"""Qualify the test protocol using controlled observations, not candidate firmware."""
import json,shlex,subprocess,sys,tempfile
from pathlib import Path
from wp17 import partition

if len(sys.argv)>1 and sys.argv[1]=='--controlled-adapter':
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'wp14_r1'))
    import oracle
    r=json.load(sys.stdin);path=Path(r['image']);before=path.read_bytes();m=before[:512]
    accepted=not oracle.layout_findings(m,r['sectors'])
    if len(sys.argv)>2 and sys.argv[2]=='blanket-accept':accepted=True
    if not accepted:print(json.dumps(dict(accepted=False)));sys.exit()
    start=oracle.P2_START;blocks=r['sectors']-start
    reads=[before[start*512:(start+1)*512].hex(),before[-512:].hex()]
    pos=start+1
    if len(sys.argv)>2 and sys.argv[2]=='wrong-offset':pos=1
    with path.open('r+b')as f:f.seek(pos*512);f.write(bytes.fromhex('a5'*512))
    print(json.dumps(dict(accepted=True,start=start,blocks=blocks,read_hex=reads,write_absolute_lba=[pos],out_of_range_refused=True)))
else:
    adapter=shlex.quote(sys.executable)+' '+shlex.quote(str(Path(__file__).resolve()))+' --controlled-adapter'
    with tempfile.TemporaryDirectory()as d:
        rows=partition(adapter,Path(d)/'positive');assert len(rows)==12
        for mutant in ('blanket-accept','wrong-offset'):
            try:partition(adapter+' '+mutant,Path(d)/mutant)
            except AssertionError:pass
            else:raise AssertionError('partition method missed '+mutant)
    print(json.dumps(dict(fixture_rows=len(rows),controls=['blanket-accept rejected','wrong-offset rejected'],
                          scope='controlled protocol qualification only; firmware binding untested')))
