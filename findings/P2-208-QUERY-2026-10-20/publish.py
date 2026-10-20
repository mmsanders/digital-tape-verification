"""Deterministic new-extension archive; no Product or private evidence inputs."""
import hashlib,json,os,subprocess,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).parent
def run():
 source=os.environ.get('SOURCE_HEAD') or subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
 package=ROOT/'tests/wp15_boundary_query_r1'
 pins=json.loads((package/'pins.json').read_text())
 assert hashlib.sha256((ROOT/'tests/wp15_app1a_r1/oracle.py').read_bytes()).hexdigest()==pins['required_prior_oracle_sha256']=='66ff0af2fe60d9aff50c68376eb0b0fe0a0cbfc40711f8ef9899c124f46d3aa3'
 assert pins['authority_commit']=='d09e5ba772729cb9b3d1c9b38b9052c4cbf77c6e'
 assert hashlib.sha256((package/'spec/WP15-APP-ANNEX.md').read_bytes()).hexdigest()==pins['annex_sha256']=='e01a897ce316f8c54d55fd0ccddd9c5fb52805c3ff16c41078bb34b72001baed'
 manifest=json.loads((package/'FILES.json').read_text())
 actual={p.relative_to(package).as_posix():p for p in package.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='FILES.json'}
 assert set(actual)==set(manifest)
 for name,p in actual.items():assert hashlib.sha256(p.read_bytes()).hexdigest()==manifest[name]
 out=ROOT/'boundary-query-publication';out.mkdir(exist_ok=True)
 archive=out/'wp15-boundary-query-r1.zip'
 with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for p in sorted(list(actual.values())+[package/'FILES.json']):
   info=zipfile.ZipInfo(p.relative_to(ROOT).as_posix(),date_time=(2026,10,20,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
   z.writestr(info,p.read_bytes())
 # PR checkout is a shallow merge; fetch the exact authored head before citing its tree.
 subprocess.run(['git','fetch','--no-tags','--depth=1','origin',source],check=True,capture_output=True)
 for p in list(actual.values())+[package/'FILES.json']:
  rel=p.relative_to(ROOT).as_posix()
  assert subprocess.check_output(['git','show',source+':'+rel])==p.read_bytes(),rel
 tree=subprocess.check_output(['git','rev-parse',source+':tests/wp15_boundary_query_r1'],text=True).strip()
 provenance={'source_commit':source,'package_tree':tree,'archive':archive.name,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'authored_rows':49,'controls':23,'status':'AUTHORED ONLY; no enabled S3 platform'}
 (out/'PROVENANCE.json').write_text(json.dumps(provenance,indent=2)+'\n')
 files=[archive,out/'PROVENANCE.json']
 (out/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in files))
 print(json.dumps(provenance,indent=2))
if __name__=='__main__':run()
