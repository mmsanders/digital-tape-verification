#!/usr/bin/env python3
"""#130 provenance: structural diff of the accepted record_draft8 evidence (a88850df) against Product main's
retained bundle (c461e9e0). Usage: record_provenance_diff.py ACCEPTED.jsonl PRODUCT_MAIN.jsonl"""
import hashlib, json, sys


def diff(x, y, p=""):
    if isinstance(x, dict) and isinstance(y, dict):
        out = []
        for k in sorted(set(x) | set(y)):
            out += [(p + "." + k, "missing")] if (k not in x or k not in y) else diff(x[k], y[k], p + "." + k)
        return out
    if isinstance(x, list) and isinstance(y, list) and len(x) == len(y):
        return [d for i, (u, v) in enumerate(zip(x, y)) for d in diff(u, v, f"{p}[{i}]")]
    return [] if x == y else [(p, (x, y))]


a, c = sys.argv[1:3]
for f in (a, c):
    print(f, hashlib.sha256(open(f, "rb").read()).hexdigest())
A = [json.loads(l) for l in open(a)]
C = [json.loads(l) for l in open(c)]
print("records", len(A), len(C), "same case order", [r.get("case") for r in A] == [r.get("case") for r in C])
for u, v in zip(A, C):
    for path, vals in diff(u, v):
        print("DIFF", u.get("case"), path, vals)
