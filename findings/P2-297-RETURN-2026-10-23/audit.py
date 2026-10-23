"""Offline exact551 carrier authentication. No Cargo or Product runtime."""
import argparse
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import tomllib

BASE='bf2381c9c187c14ce65cc501b13f9eb512c99693'
ORIGINAL='cd996a2e91fbbc6daca520438fef5f6c79dc94b5'
FILES={'children.rs','drops.rs','ingest_job.rs','jobdir.rs','label.rs','lib.rs','state.rs'}

def audit(p,v,head):
    def command(*args):return subprocess.check_output(['git','-C',str(p),*args])
    def data(path,ref=head):return command('show',ref+':'+path)
    subprocess.run(['git','-C',str(p),'merge-base','--is-ancestor',BASE,head],check=True)
    changed=set(command('diff','--name-only',BASE,head).decode().splitlines())
    allowed={'.github/workflows/backend-component.yml','docs/REVIEW/software546/COMPONENT-BLOBS.json',
             'host/app/tests/lifecycle_adapter.rs',*(f'host/app/src/{name}' for name in FILES),
             *(f'host/app/backend-component/{name}' for name in ['.gitignore','Cargo.toml','Cargo.lock','README.md'])}
    assert changed==allowed
    cross=json.loads(data('docs/REVIEW/software546/COMPONENT-BLOBS.json'))
    assert cross['disposed_candidate']==ORIGINAL and cross['independent_report']=='82f31d4820d113ee67d6a6807b4e0d9b18b11bdd'
    assert {e[0] for e in cross['source_blobs']}==FILES
    for name,known in cross['source_blobs']:
        path='host/app/src/'+name
        assert data(path)==data(path,ORIGINAL)
        assert command('rev-parse',head+':'+path).decode().strip()==known
    for name in ['report.rs','messages.rs']:
        path='host/app/src/'+name
        assert data(path)==data(path,BASE)==data(path,ORIGINAL)
    assert data('host/app/tests/lifecycle_adapter.rs')==data('host/app/tests/lifecycle_adapter.rs',ORIGINAL)
    entries=set(command('ls-tree','-r','--name-only',head,'host/app').decode().splitlines())
    assert not any(x in entries for x in ['host/app/src/main.rs','host/app/build.rs','host/app/Cargo.toml','host/app/backend-component/build.rs'])
    spec=importlib.util.spec_from_file_location('carrier',v/'tests/windows_backend_carrier_r1/wrapper.py')
    checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
    checker.wrapper(data('host/app/src/lib.rs').decode())
    m=tomllib.loads(data('host/app/backend-component/Cargo.toml').decode())
    checker.manifest(m)
    assert m['lib']['path']=='../src/lib.rs'
    assert m['example']==[dict(name='lifecycle_adapter',path='../tests/lifecycle_adapter.rs')]
    assert m.get('workspace')=={} and m['profile']['release']==dict(panic='abort',**{'overflow-checks':True})
    old=tomllib.loads(data('host/app/Cargo.lock',ORIGINAL).decode())
    new=tomllib.loads(data('host/app/backend-component/Cargo.lock').decode())
    checker.lock(new['package'],old['package'])
    def edges(package,all_packages):
        result=set()
        for d in package.get('dependencies',[]):
            name,version=re.match(r'([^ ]+)(?: ([0-9][^ ]*))?',d).groups()
            matches=[x for x in all_packages if x['name']==name and (version is None or x['version']==version)]
            assert len(matches)==1
            result.add((matches[0]['name'],matches[0]['version'],matches[0].get('source')))
        return result
    changed_edges=[]
    for package in new['package']:
        prior=next(x for x in old['package'] if x['name']==package['name'] and x['version']==package['version'] and x.get('source')==package.get('source'))
        assert edges(package,new['package'])<=edges(prior,old['package']), 'new lock dependency edge'
        if package.get('dependencies')!=prior.get('dependencies'):changed_edges.append(package['name'])
    readme=data('host/app/backend-component/README.md').decode()
    assert 'does not clear unexercised label/drop/UI functions' in readme
    return dict(candidate=head,base=BASE,accepted_source=ORIGINAL,copied_source_blobs=7,
                existing_parser_blobs=2,exact_adapter=True,changed_paths=sorted(changed),
                external_locked_packages=sum('source' in x for x in new['package']),
                changed_dependency_lists=changed_edges,no_new_dependency_edges=True,
                manifest='PASS',declarations='PASS',scope='mechanical carrier only;286 behavior carried',runtime_executions=0)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--product',type=Path,required=True);p.add_argument('--verification',type=Path,required=True)
    p.add_argument('--head',required=True);p.add_argument('--output',type=Path);a=p.parse_args()
    text=json.dumps(audit(a.product,a.verification,a.head),indent=2)+'\n'
    if a.output:a.output.write_text(text)
    print(text)
