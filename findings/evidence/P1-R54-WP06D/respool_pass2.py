"""F-LIVEB-RESPOOL-FLOOR: show the trace, then inject every conceivable pass 2 into the real
Product observation and require the unchanged oracle to reject each one."""
import sys, json, copy
sys.path.insert(0, ".")
import oracle as O
obs_all = [json.loads(l) for l in open(sys.argv[1])]
obs = next(o for o in obs_all if o["case"] == "F-LIVEB-RESPOOL-FLOOR")
case = next(c for c in O.load_plan()["cases"] if c["id"] == obs["case"])
bc = obs["block_count"]; CB, CBL = O.CHUNK_BASE, 1024
print("block_count", bc, "total_chunks", (bc - 1 - CB) // CBL)
for e in obs["events"]:
    if e["step"] == "exercise" and e["op"] != "read":
        where = ("chunk %d+%d" % divmod(e["lba"] - CB, CBL)) if e.get("lba", 0) >= CB and e.get("lba") != bc - 1 else e.get("lba")
        print("  ", e["ordinal"], e["op"], where, e.get("count", ""))
O.check(case, obs); print("baseline PASS")
last = obs["events"][-1]["ordinal"]
killed = survived = 0
total_chunks = (bc - 1 - CB) // CBL
for start in range(0, total_chunks - 2):
    m = copy.deepcopy(obs)
    ev = m["events"]; n = len(ev)
    for i, ch in enumerate(range(start, start + 3)):
        ev.append({"step": "exercise", "op": "write", "lba": CB + ch * CBL, "count": CBL, "ordinal": n + 1 + i, "result": 0})
    ev.append({"step": "exercise", "op": "flush", "ordinal": n + 4, "result": 0})
    try:
        O.check(case, m); survived += 1; print("SURVIVED pass 2 at", start)
    except AssertionError as e:
        killed += 1; print(f"  pass 2 -> [{start},{start+3}) killed: {e}")
print(f"{killed}/{killed+survived} injected pass-2 destinations rejected")
