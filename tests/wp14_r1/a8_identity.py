#!/usr/bin/env python3
"""Stage2 Git-object identity checks. Does not open implementation source files."""
import argparse
import json
import subprocess
from pathlib import Path

ENGINE='b80a8e54775c5aabad7bc338a6e30db3596b657b'

def git(repo,*args):
    return subprocess.check_output(['git','-C',str(repo),*args],text=True).strip()

def audit(verification,product,publication,candidate,import_commit,import_path,golden_path):
    published=git(verification,'rev-parse',publication+':tests/wp14_r1')
    imported=git(product,'rev-parse',import_commit+':'+import_path)
    final=git(product,'rev-parse',candidate+':'+import_path)
    assert published==imported==final,'verifier import differs'
    engine=git(product,'rev-parse',candidate+':engine')
    assert engine==ENGINE,'engine changed from pinned normative input'
    golden=git(verification,'rev-parse','6837102116ed94f80b8a6454713ffb1e7c076427:tests/golden')
    actual=git(product,'rev-parse',candidate+':'+golden_path)
    assert golden==actual,'golden bytes changed'
    subprocess.run(['git','-C',str(product),'merge-base','--is-ancestor',import_commit,candidate],check=True)
    return {'kind':'A8-git-identity','publication':publication,'candidate':candidate,
            'import_commit':import_commit,'verifier_tree':published,'engine_tree':engine,
            'golden_tree':golden,'accepted':False,
            'remaining':'authenticate remote refs and full Phase1 replay/CI results; native cases and witnesses'}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for arg in ('verification','product','publication','candidate','import-commit','import-path','golden-path'):
        p.add_argument('--'+arg,required=True)
    a=p.parse_args()
    print(json.dumps(audit(a.verification,a.product,a.publication,a.candidate,a.import_commit,a.import_path,a.golden_path),indent=2))
