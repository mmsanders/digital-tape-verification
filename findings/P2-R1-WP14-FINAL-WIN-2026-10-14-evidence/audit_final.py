from pathlib import Path
import argparse, datetime, hashlib, json, struct, zipfile

parser=argparse.ArgumentParser(description='Offline audit of original Windows witness; no device access or Product execution')
parser.add_argument('--archive', type=Path, default=Path(__file__).parent/'final-win-3600.zip')
parser.add_argument('--out', type=Path)
args=parser.parse_args()
archive=args.archive
members={name: b for name,b in [(i.filename,zipfile.ZipFile(archive).read(i)) for i in zipfile.ZipFile(archive).infolist()]}
root=Path('final-win-3600')
def txt(p):
    b=members[p.as_posix()]
    return b.decode('utf-16') if b[:2] in (bytes([255,254]),bytes([254,255])) else b.decode('utf-8-sig')
def j(n): return json.loads(txt(root/n))
pattern=b''.join(struct.pack('<hh',i*251-16000,15000-i*239) for i in range(128))
frames=3600*44100; data=frames*4
h=hashlib.sha256(struct.pack('<4sI4s4sIHHIIHH4sI',b'RIFF',36+data,b'WAVE',b'fmt ',16,1,2,44100,176400,4,16,b'data',data))
page=pattern*2048; pages,tail=divmod(data,len(page))
for _ in range(pages): h.update(page)
h.update(page[:tail]); expected=h.hexdigest()
assert expected=='c7369c6fdcb476fcc7f6a9d68aaab276f68a4d316ffb595faabb736e6046495d'
inputs=j('inputs.json')
assert inputs[0]['sha256'].lower()=='82798af2899e9364b9c9bfaa2021daf6cc51ccd0c6562598d50e0a86944bb7a9' and inputs[0]['bytes']==435533
assert inputs[1]['sha256'].lower()==expected and inputs[1]['bytes']==data+44
assert len(j('after-wavs.json'))==2
assert all(x['sha256'].lower()==expected and x['bytes']==data+44 for x in j('after-wavs.json'))
commands=[]; last=None
device=chr(92)*2+'.'+chr(92)+'PhysicalDrive1'
for stem in ['provision','load','after-verify','after-A','after-B']:
    x=j(stem+'-command.json')
    assert x['exit']==0 and int(txt(root/(stem+'-exit.txt')))==0
    assert float(txt(root/(stem+'-seconds.txt')))==x['seconds']
    assert x['args'][1]==device
    start=datetime.datetime.fromisoformat(x['started_utc'].replace('Z','+00:00'))
    end=datetime.datetime.fromisoformat(x['ended_utc'].replace('Z','+00:00'))
    assert end>=start and x['seconds']>0 and (last is None or start>=last)
    last=end
    commands.append({'stem':stem,**x,'wall_seconds_from_utc':(end-start).total_seconds(),'stamp_minus_stopwatch_seconds':(end-start).total_seconds()-x['seconds']})
assert txt(root/'after-verify.txt').strip()=='OK'
assert '155048 flushes via FlushFileBuffers' in txt(root/'load.txt')
assert 'uuid f066c44a0ff84f51d898a83f1cf678cf' in txt(root/'provision.txt')
readme=(chr(13)+chr(10)).join(['This is a Digital Tape cartridge.','Label: PNY-C60','Please do not format or erase this card on a computer.','Use the Digital Tape app to load music onto it.','']).encode()
assert len(readme)==156
result={'verdict':'PASS bounded Windows final success/A9 observations; full WP14 HELD','archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'canonical_c60_computed_sha256':expected,'canonical_frames':frames,'canonical_bytes':data+44,'canonical_readme_expected_sha256':hashlib.sha256(readme).hexdigest(),'load_seconds':j('load-command.json')['seconds'],'payload_decimal_MB_s':data/j('load-command.json')['seconds']/1e6,'commands':commands,'missing':['final raw README.TXT bytes','physical native A6 traces Mac and Windows'],'limits':['A/B output blobs not supplied; byte identity judged from contemporaneous recorded SHA256 and lengths, no claimed local sample comparison','reader serial is not CID; PNY Elite-X64GB witness only; no media/atomicity qualification']}
with zipfile.ZipFile(archive) as z:
    result['inventory']=[{'path':i.filename,'bytes':i.file_size,'sha256':hashlib.sha256(z.read(i)).hexdigest()} for i in z.infolist()]
if args.out: args.out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['inventory','commands']},indent=2))
