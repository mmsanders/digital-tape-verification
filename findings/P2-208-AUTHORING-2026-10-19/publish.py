"""Deterministic compact package/provenance transport. Run after checkout in CI."""
import hashlib,json,os,pathlib,subprocess,zipfile
root=pathlib.Path('tests/wp15_cards_make_r1');out=pathlib.Path('/tmp/publication208');out.mkdir(exist_ok=True)
entries={str(p.relative_to(root)):p.read_bytes()for p in sorted(root.rglob('*'))if p.is_file() and '__pycache__' not in p.parts}
zpath=out/'wp15-cards-make-r1.zip'
with zipfile.ZipFile(zpath,'w',compression=zipfile.ZIP_DEFLATED)as z:
 for name,data in entries.items():
  info=zipfile.ZipInfo('wp15_cards_make_r1/'+name,date_time=(2026,10,19,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;z.writestr(info,data)
sha=hashlib.sha256(zpath.read_bytes()).hexdigest()
manifest=dict(source_commit=os.environ['SOURCE_HEAD'],tree=subprocess.check_output(['git','rev-parse','HEAD:tests/wp15_cards_make_r1'],text=True).strip(),archive_sha256=sha,archive_bytes=zpath.stat().st_size,files={n:dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())for n,b in entries.items()})
(out/'PROVENANCE.json').write_text(json.dumps(manifest,indent=2)+'\n');(out/'SHA256SUMS').write_text(sha+'  wp15-cards-make-r1.zip\n')
print(json.dumps({k:v for k,v in manifest.items()if k!='files'},indent=2))
