import sys, gzip, json, copy
sys.path.insert(0, ".")
import oracle as O
from vectors import vectors
raw = gzip.decompress(open(sys.argv[1] + "/gcc.jsonl.gz", "rb").read())
recs = [json.loads(l) for l in raw.splitlines()]
plan = vectors()
for delta in (+1, -1, +4096):
    killed = 0
    for v, r in zip(plan, recs):
        m = copy.deepcopy(r); m["block_count"] += delta
        try: O.check(v, m)
        except AssertionError as e: killed += 1; why = str(e)
    print(f"block_count{delta:+d}: {killed}/{len(plan)} vectors rejected (e.g. {why})")
