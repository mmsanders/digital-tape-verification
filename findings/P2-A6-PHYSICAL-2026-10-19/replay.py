"""Replay only the authenticated physical return with the unchanged accepted checker."""
import argparse,hashlib,json,shutil,subprocess,sys,zipfile
from pathlib import Path,PurePosixPath,PureWindowsPath
HERE=Path(__file__).resolve().parent
def text(p):
    b=p.read_bytes();return b.decode('utf-16'if b.startswith((b'\xff\xfe',b'\xfe\xff'))else'utf-8-sig')
def run(packet,checker,work):
    assert packet.stat().st_size==92802476
    assert hashlib.file_digest(packet.open('rb'),'sha256').hexdigest()=='0246c24a96b1de22bad15086aa925def9d2b43bb6ecd13c146a305f914df0bcb'
    assert hashlib.sha256(checker.read_bytes()).hexdigest()=='7cbba051629d56bffd85e715fe34cb909421aa6b105a52c883f383aed10b8d89'
    checker=checker.resolve();work.mkdir(exist_ok=False)
    seen=set();total=0
    with zipfile.ZipFile(packet)as z:
        for i in z.infolist():
            p=PurePosixPath(i.filename.replace('\\','/'))
            assert not p.is_absolute()and'..'not in p.parts and':'not in str(p)
            assert(i.external_attr>>16)&0o170000!=0o120000
            assert str(p).casefold()not in seen;seen.add(str(p).casefold())
            total+=i.file_size;assert total<2*1024**3
            if len(p.parts)!=1 or i.is_dir():continue
            with z.open(i)as src,(work/p.name).open('wb')as dst:shutil.copyfileobj(src,dst)
    manifest=json.loads(text(work/'file-hashes.json'));assert len(manifest)==29
    for r in manifest:
        p=work/PureWindowsPath(r['Path']).name
        assert hashlib.file_digest(p.open('rb'),'sha256').hexdigest()==r['Hash'].lower()
    assert text(work/'verify-pid.txt').strip()=='30236'and text(work/'verify-exit.txt').strip()=='0'
    args=['--format','etw-xml','--trace','verify.xml','--pid','30236','--capacity','62537072640','--geometry','geometry.txt','--target',r'\\.\PhysicalDrive1','--disk','1','--exe','tapectl.exe','--sha256','82798af2899e9364b9c9bfaa2021daf6cc51ccd0c6562598d50e0a86944bb7a9','--stdout','verify-out.txt','--tracer-log','tracer-exits.txt','--exit-code','0']
    for n in ['wpr-start-out.txt','wpr-start-err.txt','wpr-stop-out.txt','wpr-stop-err.txt','tracerpt-out.txt','tracerpt-err.txt']:args+=['--diagnostics',n]
    r=subprocess.run([sys.executable,'-B',str(checker)]+args,cwd=work,capture_output=True,text=True)
    actual=json.loads(r.stdout);assert r.returncode==1 and actual==json.loads((HERE/'CHECKER-RESULT.json').read_text())
    (work/'CHECKER-RESULT.json').write_text(r.stdout);print('Exact unmodified checker FAIL reproduced; physical A6 remains HELD')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--packet',type=Path,required=True);p.add_argument('--checker',type=Path,required=True);p.add_argument('--work',type=Path,required=True);a=p.parse_args();run(a.packet,a.checker,a.work)
