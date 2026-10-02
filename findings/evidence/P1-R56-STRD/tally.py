#!/usr/bin/env python3
"""#131 tally: independent read of Product row-2 raw callbacks and row-1/3 census from retained evidence."""
import gzip, json, sys, collections
CHUNK_STORE_HINT = None
obs = [json.loads(l) for l in gzip.open(sys.argv[1])]
by = collections.Counter(o["row"] for o in obs)
print("rows", dict(by))
for o in obs:
    if o["kind"] == "respool_pass2_run":
        print("mount", o["mount"]); print("calls", o["calls"])
        for e in o["events"]:
            print(" ", e["op"], e.get("lba"), e.get("count"), "data" if "data" in e else "")
        print("mount_B_after", o["mount_B_after"])
r1 = [o for o in obs if o["kind"] == "dup_audio"]
print("row1", [(o.get("frames"), o.get("destination"), o["call"]["result"], o["mount_A"]["info"], o["mount_B"]["info"]) for o in r1])
r3 = [o for o in obs if o["kind"] == "capacity_premise"]
print("row3 raw_before keys", sorted({tuple(sorted(o["raw_before"])) for o in r3}))
print("row3 A0 headers distinct", len({json.dumps(o["raw_before"]["A0"], sort_keys=True) for o in r3}),
      "A1 distinct", len({json.dumps(o["raw_before"]["A1"], sort_keys=True) for o in r3}))
