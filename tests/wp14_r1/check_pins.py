#!/usr/bin/env python3
"""Check authenticated input copies without changing authoritative manifest bytes."""
import hashlib
import json
from pathlib import Path

root=Path(__file__).resolve().parent
pins=json.loads((root/'INPUTS.json').read_text())
assert pins['product_commit']=='437283291c944d24a3d574dee0e3f44ba97e1896'
assert pins['sha256']['spec/tapefs-v1.md']=='2a6a9f7b6fe1e5f9e3fe068b3c6460a81256276082bb7e336c01dbf1e9c17eba'
assert pins['sha256']['spec/engine-api.md']=='aa042e41e35b02bf2bb6b3896e59340a947720c27dc5fc52a24d657ccd66b33a'
for path,sha in pins['sha256'].items():
    assert hashlib.sha256((root/path).read_bytes()).hexdigest()==sha,path
print(json.dumps({'input_hashes_verified':len(pins['sha256']),'product_commit':pins['product_commit']}))
