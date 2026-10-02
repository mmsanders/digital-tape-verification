import sys, gzip, json, hashlib, collections
sys.path.insert(0, ".")
import oracle as O
d = sys.argv[1]
g, c = (gzip.decompress(open(f"{d}/{n}.jsonl.gz", "rb").read()) for n in ("gcc", "clang"))
assert g == c, "GCC/Clang diverge"
recs = O.parse_jsonl(g)
print("PASS", len(recs), "vectors under unchanged oracle; GCC==Clang; stream", hashlib.sha256(g).hexdigest())
cen = collections.Counter()
for r in recs:
    bc = r["block_count"]; t = r["trace"]
    m = t[0]["block_events"]; s = [e for x in t if x["fn"] == "tape_service" for e in x["block_events"]]
    cen["block_count=%d" % bc] += 1
    cen["mount reads both sb"] += any(e["lba"] == 0 for e in m) and any(e["lba"] + e["count"] > bc - 1 >= e["lba"] for e in m)
    cen["service reads"] += bool(s)
    cen["writes/flushes"] += sum(e["op"] != "read" for x in t for e in x.get("block_events", []))
    cen["seek/rate/render callbacks"] += sum(len(x["block_events"]) for x in t if x["fn"] in ("tape_seek", "tape_set_rate", "tape_render"))
    cen["service calls"] += sum(x["fn"] == "tape_service" for x in t)
print(dict(cen))
