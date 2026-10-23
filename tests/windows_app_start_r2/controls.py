"""Causal context/failure-capture projections; no real child or OS token probe."""
import copy
import json
from pathlib import Path
import tempfile
from child_context import VERSION,capture,oracle
from context import ROUTE,admit


def main():
    good=dict(token_elevated=False,effective_admin=False,tool_route=ROUTE)
    admit(good)
    for key,value in [('token_elevated',True),('effective_admin',True),('tool_route','old-sandbox')]:
        q=copy.deepcopy(good);q[key]=value
        try: admit(q)
        except AssertionError: continue
        raise AssertionError('Invalid context admitted: '+key)
    # Local synthetic files qualify shared capture, not an actual fake process/report seam.
    with tempfile.TemporaryDirectory(prefix='synthetic283-',dir=Path.cwd()) as temp:
        root=Path(temp);nonce='a'*32
        report=root/'synthetic.jsonl';out=root/'stdout';err=root/'stderr';dest=root/'absent'
        records=[dict(t='start',tool='ingest',version=VERSION,nonce=nonce),dict(t='refusal',id='IO_FOLDER',subject='0'),dict(t='end',exit=1)]
        report.write_bytes(('\n'.join(json.dumps(r,separators=(',',':')) for r in records)+'\n').encode())
        out.write_bytes(b'');err.write_bytes(b'synthetic access failure, not an actual child outcome')
        row=dict(exit=1,nonce=nonce,folder_name='Music')
        capture(row,report,dest,out,err)
        assert row['report']['exists'] and row['report']['sha256'] and row['stderr']['bytes']>0
        assert row['parsed_report']['refusal']['id']=='IO_FOLDER'
        assert oracle.message('ingest',1,row['parsed_report'])==('generic',None)
        assert oracle.parse(report.read_bytes(),'ingest',VERSION,'b'*32,1,['Music']) is None
        assert oracle.parse(report.read_bytes(),'ingest','wrong-version',nonce,1,['Music']) is None
        assert not row['dest_exists'] and row['dest_names']==[]
        report.unlink();capture(row,report,dest,out,err)
        assert row['report']['exists'] is False and row['parsed_report'] is None
    print('PASS context rejection / authentic-failure-capture projections; ZERO Product execution or native token probe')


if __name__=='__main__': main()
