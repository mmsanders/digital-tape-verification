"""Authenticate narrow returned producer controls and capability observations.
No unchanged39-row/audio/crash campaign replay. These probes are not S3 Product code.
"""
import argparse,hashlib,json,subprocess,urllib.request,zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
SOURCE='38ca66685bfdfa136ae1df810ae037ab10f97c08'

def disks(row):
    return {d['path']:d for d in map(json.loads,row['discover']['stdout'].splitlines())}

def check_controls(path):
    j=json.loads(path.read_text());out=[]
    for r in j['rows']:
        if r['producer']=='new':assert r['source']==SOURCE
        assert len(r['binary_sha256'])==64
        if r['faults']:assert r['kind'].startswith('compiled control')
        else:assert r['kind']=='native observation'
        assert r['cards']['exit']==r['discover']['exit']
        if r['discover']['exit']==0:
            d=disks(r)
            # All submitted native/producer-fault controls are zero-offer fixtures.
            # Unknown required facts dominate refusal, per the published contract.
            unknown=sum(any(x[k]==-1 for k in ['whole','removable_or_sd','virtual','holds_os','n_mounted']) or not x['bytes_known'] for x in d.values())
            assert not any(x['verdict']=='offer' for x in d.values())
            assert json.loads(r['cards']['stdout'])==dict(t='summary',offered=0,unprobed=unknown)
        else:
            assert r['cards']['exit']==1 and not r['cards']['stdout']
            assert 'cannot list disks' in r['cards']['stderr']
        out.append(dict(producer=r['producer'],case=r['case'],kind=r['kind'],exit=r['cards']['exit'],stdout=r['cards']['stdout']))
    return j,out

def replay(directory,output,release=None):
    directory.mkdir(parents=True,exist_ok=True);results=[]
    for p in json.loads((HERE/'INPUTS.json').read_text()):
        archive=directory/(p['name']+'.zip')
        if not archive.exists():
            if release:
                with urllib.request.urlopen(release.rstrip('/')+'/'+archive.name,timeout=60) as r,archive.open('wb') as f:
                    while b:=r.read(1024*1024):f.write(b)
            else:
                with archive.open('wb') as f:subprocess.run(['gh','api',f"repos/mmsanders/Digital-Tape/actions/artifacts/{p['id']}/zip"],stdout=f,check=True)
        assert archive.stat().st_size==p['bytes'] and hashlib.sha256(archive.read_bytes()).hexdigest()==p['sha256']
        dst=directory/p['name'];dst.mkdir(exist_ok=True)
        with zipfile.ZipFile(archive) as z:
            for i in z.infolist():assert not Path(i.filename).is_absolute() and '..' not in Path(i.filename).parts and (i.external_attr>>16)&0o170000!=0o120000
            z.extractall(dst)
        record=dict(p)
        if p['name'].startswith('cards-'):
            controls={};rows=[]
            for path in sorted((dst/'controls').glob('*.json')):
                j,r=check_controls(path);controls[j['state']]=j;rows.extend(r)
            assert controls
            if p['name']=='cards-r2-linux':
                j=controls['dm-mounted'];r={(x['producer'],x['case']):x for x in j['rows']}
                new=disks(r['new','none'])['/dev/loop0'];old=disks(r['old','none'])['/dev/loop0']
                assert (new['n_mounted'],old['n_mounted'])==(1,0)
                assert next(x for x in new['parts'] if x['index']==1)['mounted']==1
                assert next(x for x in old['parts'] if x['index']==1)['mounted']==0
                assert len(disks(r['new','stack']))==10
                assert all(x['n_mounted']==-1 for x in disks(r['new','stack']).values())
                record['native_dm_control']='old missing underlying mount; new records it'
            elif p['name']=='cards-r2-macos':
                r={x['case']:x for x in controls['image-mounted']['rows']}
                assert disks(r['none'])==disks(r['protocol'])
                assert all(disks(r['none'])[f'/dev/disk{i}']['removable_or_sd']==-1 for i in range(3))
                record['protocol_row']='NON-CAUSAL; baseline and fault disk facts identical'
            record['rows']=rows
        elif p['name']=='s3-r2-linux':
            c=json.loads((dst/'PROBE-linux.json').read_text())['cases']
            for n in ['same','detach']:
                assert c[n]['query']==c[n]['upgrade'] and c[n]['marker_on_upgrade']=='IMAGE-A'
            assert c['detach']['attach_other_at_same_number']['exit']!=0
            ch=c['changefd'];assert ch['change_fd']=='ok' and ch['seq_changed']
            assert ch['query']['diskseq']!=ch['query_after_change']['diskseq']
            assert 'errno' not in ch['write_mode_upgrade_on_ro_loop']
            assert ch['write_mode_upgrade_on_ro_loop']['diskseq']==ch['query_after_change']['diskseq']
            assert ch['marker_on_upgrade']=='IMAGE-B'
            assert c['reuse']['marker_on_path_open']=='IMAGE-B' and not c['reuse']['seq_equal']
            record['judgment']='bounded same-inode/sequence capability; actual O_RDWR upgrade succeeded after change; no pre-open rejection or automatic final-close clearing proved'
        else:
            c=json.loads((dst/'s3/PROBE-windows.json').read_text())['cases']
            assert [c[n]['upgrades']['ReOpenFile']['error'] for n in ['same-read-query','same-zero-access-query']]==[87,31]
            assert all(c[n]['upgrades']['DuplicateHandle']['error']==5 for n in ['same-read-query','same-zero-access-query'])
            assert c['swap']['held_query_after_swap']['device_number']['error']==55
            assert c['swap']['path_open']['marker']=='IMAGE-B'
            a=json.loads((dst/'s3anc/PROBE-ancestor.json').read_text())['cases']
            assert a['bound']['created'] and a['rename-held']['created']
            assert all(x['exit']!=0 for x in a['rename-held']['during'])
            assert list(a['rename-held']['listing'].values())==[['report.jsonl'],[]]
            assert not a['junction']['created'] and list(a['junction']['listing'].values())==[[]]
            assert a['naive']['created'] and all(x['exit']==0 for x in a['naive']['substitution'])
            assert 'naive-elsewhere' in a['naive']['leaf_final_path']
            record['judgment']='tested device upgrade routes unavailable on Server fixture; relative held-ancestor file route available with causal naive contrast; no S3 or Win11 acceptance'
        results.append(record)
    output.write_text(json.dumps(results,indent=2)+'\n');print('PASS five exact archives, producer control facts and bounded capability/limitation replay')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--artifacts',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--release')
    a=p.parse_args();replay(a.artifacts,a.out,a.release)
