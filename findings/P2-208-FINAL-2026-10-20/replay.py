"""Authenticate only new producer observations; no unchanged campaign replay."""
import argparse, hashlib, importlib.util, json, subprocess, urllib.request, zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
HEAD='1ad813d86d094a3702a03e3b2e602c221855a9ca'

def run(directory, out, release=None):
    directory.mkdir(parents=True,exist_ok=True)
    s=importlib.util.spec_from_file_location('old_replay',HERE.parent/'P2-208-R2-2026-10-19/replay.py')
    old=importlib.util.module_from_spec(s);s.loader.exec_module(old);old.SOURCE=HEAD
    results=[]
    for pin in json.loads((HERE/'INPUTS.json').read_text()):
        p=directory/(pin['name']+'.zip')
        if not p.exists():
            if release:
                with urllib.request.urlopen(release.rstrip('/')+'/'+p.name,timeout=60)as r,p.open('wb')as f:
                    while b:=r.read(1024*1024):f.write(b)
            else:
                with p.open('wb')as f:subprocess.run(['gh','api',f"repos/mmsanders/Digital-Tape/actions/artifacts/{pin['id']}/zip"],stdout=f,check=True)
        assert p.stat().st_size==pin['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==pin['sha256']
        dst=directory/pin['name'];dst.mkdir(exist_ok=True)
        with zipfile.ZipFile(p)as z:
            for i in z.infolist():assert not Path(i.filename).is_absolute()and'..'not in Path(i.filename).parts and(i.external_attr>>16)&0o170000!=0o120000
            z.extractall(dst)
        states={};rows=[]
        for path in sorted((dst/'controls').glob('*.json')):
            j,r=old.check_controls(path);states[j['state']]=j;rows.extend(r)
        assert states
        rec=dict(pin,rows=rows)
        if pin['name']=='cards-linux':
            j=states['dm-mounted'];r={(x['producer'],x['case']):x for x in j['rows']}
            good=old.disks(r['new','none']);baseline=old.disks(r['old','none'])
            assert good['/dev/loop0']['n_mounted']==1 and baseline['/dev/loop0']['n_mounted']==0
            assert next(p for p in good['/dev/loop0']['parts']if p['index']==1)['mounted']==1
            for case in ['denied','readdir','stack','enoent']:
                disks=old.disks(r['new',case]);assert len(disks)==len(good)
                assert all(d['n_mounted']==-1 and d['verdict']=='unprobed'for d in disks.values())
                assert next(p for p in disks['/dev/loop0']['parts']if p['index']==1)['mounted']==-1
            assert all(d['holds_os']==-1 for d in old.disks(r['new','denied']).values())
            plain={x['case']:x for x in states['plain']['rows']if x['producer']=='new'}
            assert old.disks(plain['none'])==old.disks(plain['readdir'])
            assert all(d['n_mounted']==-1 for d in old.disks(plain['denied']).values())
            rec['judgment']='final submitted EACCES/incomplete walk/whole-device ENOENT controls pass; plain readdir is non-triggering; known partition/listing neighbours carry with exact-source reproduction'
        elif pin['name']=='cards-macos':
            r={x['case']:x for x in states['image-mounted']['rows']}
            assert old.disks(r['none'])==old.disks(r['protocol'])
            rec['judgment']='unchanged platform carried; protocol row remains NON-CAUSAL'
        else:rec['judgment']='unchanged Windows producer controls carried; hosted Server only'
        results.append(rec)
    out.write_text(json.dumps(results,indent=2)+'\n')
    print('PASS three ZIP hashes and exact-head producer observations; bounded final control replay; other S2/base/native scope separate')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--artifacts',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--release')
    a=p.parse_args();run(a.artifacts,a.out,a.release)
