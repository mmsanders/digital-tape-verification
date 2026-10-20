"""Fetch only the pinned source material read for232; hashes, not new execution."""
import argparse, concurrent.futures, hashlib, json, zipfile, urllib.request
from pathlib import Path
HERE=Path(__file__).resolve().parent
def fetch(archive,out):
 with zipfile.ZipFile(archive) as z: index=json.loads(z.read('SOURCE-INDEX.json'))
 assert index['candidate']=='b9f430c8c9b33532abf07eea0ed2653310639f2d'
 selected=[f for f in index['files'] if '/src/' in f['path'] and '/vendor/' not in f['path'] or f['path'] in ('host/ingest/vendor/symphonia-bundle-mp3/src/decoder.rs','host/ingest/Cargo.lock','host/ingest/Cargo.toml','docs/WP16-INGEST-CONTRACT.md')]
 def get(f):
  with urllib.request.urlopen('https://raw.githubusercontent.com/mmsanders/Digital-Tape/'+index['candidate']+'/'+f['path'],timeout=30) as q: b=q.read(f['bytes']+1)
  assert len(b)==f['bytes'] and hashlib.sha256(b).hexdigest()==f['sha256']
  assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==f['blob']
  p=out/f['path'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
  return f
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool: pins=list(pool.map(get,selected))
 result=dict(candidate=index['candidate'],files=pins,scope='source bytes reviewed; no compilation or production witness')
 (out/'SOURCE-PINS.json').write_text(json.dumps(result,indent=2)+'\n')
 print('Authenticated source files',len(pins));return result
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--archive',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 # replay.py authenticates the complete input archive first; standalone also binds it.
 from replay import ARCHIVE_SHA,ARCHIVE_SIZE,sha
 raw=a.archive.read_bytes();assert len(raw)==ARCHIVE_SIZE and sha(raw)==ARCHIVE_SHA
 fetch(a.archive,a.out)
