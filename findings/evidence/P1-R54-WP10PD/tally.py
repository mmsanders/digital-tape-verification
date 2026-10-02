import sys, json, gzip, collections
sys.path.insert(0, ".")
import oracle as O, model as M
def tally(lines):
    f = O.new_findings(); fails = collections.Counter(); first = {}
    reasons = collections.Counter(); n = 0
    for case, line in zip(O.iter_cases(), lines):
        n += 1
        try: O.check(case, json.loads(line), f)
        except AssertionError as e:
            k = (case["scenario"], case["kind"]); fails[k] += 1; reasons[str(e)[:60]] += 1
            first.setdefault(k, case)
    return n, sum(fails.values()), dict(fails), dict(reasons), first
for label, path in (("fixed-retained", sys.argv[1]), ("pre-fix-054d27ab", sys.argv[2])):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt") as fh:
        n, bad, fails, reasons, first = tally(l for l in fh if l.strip())
    print(f"== {label}: {n} cases, {bad} fail")
    for k, v in sorted(fails.items()): print("  ", k, v, "first:", first[k].get("inject"), first[k]["index"])
    for k, v in reasons.items(): print("   reason:", v, k)
print("\n== (a) planned empty-source dup trace (model.transaction DUP-EMPTY-BLANK):")
for o in M.transaction("DUP-EMPTY-BLANK"): print("  ", o[0], o[1] if len(o) > 1 else "", f"lba={M.TRACKED[o[1]]}" if len(o) > 1 else "")
with gzip.open(sys.argv[1], "rt") as fh: lines = [l for l in fh if l.strip()]
fam = json.loads(lines[-1]); want = O.sha(O.canonical(O.trace_events(M.transaction("DUP-EMPTY-BLANK"))).encode())
print("empty_family index", fam["index"], "trace", fam["trace_sha256"], "== planned" if fam["trace_sha256"] == want else "!= planned")
print("mount_B", fam["mount_B"]); print("family", json.dumps(fam["family"])); print("call", fam["call"])
for l in lines[-7:-1]:
    o = json.loads(l); print("complete", o["scenario"], o["call"], "trace", o["trace_sha256"] == O.sha(O.canonical(O.trace_events(M.transaction(o["scenario"]))).encode()))
