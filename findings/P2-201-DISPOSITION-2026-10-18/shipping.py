"""Independent shipping-configuration rebuild of pinned correction, actual Windows Job run."""
from pathlib import Path
import hashlib,json,subprocess,sys,shutil,platform
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tests/wp16_shipping_exhaustion_r1'))
import runner
p=Path('candidate459').resolve();head='50bc4160f6da527da8c684d05264f99815aaa870'
assert subprocess.check_output(['git','-C',str(p),'rev-parse','HEAD']).decode().strip()==head
subprocess.run(['cargo','build','--release','--locked'],cwd=p/'host/ingest',check=True)
b=p/'host/ingest/target/release/ingest.exe';s=runner.sha(b)
sources=Path('sources201').resolve();subprocess.run([sys.executable,'-B','tests/wp16_ingest_stage1/asset.py','--destination',str(sources)],check=True)
out=Path('candidate-results').resolve();r=runner.run(b,s,sources/'assets/ordinary.wav',out,'candidate')
(out/'BUILD.json').write_text(json.dumps(dict(head=head,binary_sha256=s,build='cargo build --release --locked',configuration='shipping; no observe feature',version=subprocess.check_output([str(b),'--version'],text=True).strip(),identity='independent source-head rebuild; compare hash to Software separately'),indent=2)+'\n')
shutil.copyfile(b,out/'ingest.exe')
(out/'OS.json').write_text(json.dumps(dict(os=platform.platform()),indent=2)+'\n')
print('actual independent shipping correction PASS',s)
