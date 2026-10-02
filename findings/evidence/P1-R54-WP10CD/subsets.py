"""Which permitted durable image each crash case landed in (none / all / mixed pending kept)."""
import sys, json, gzip, collections
sys.path.insert(0, ".")
import oracle as O, model as M
tally = collections.Counter()
for case, line in zip(O.iter_cases(), gzip.open(sys.argv[1], "rt")):
    if case["row"] == 3:
        continue
    obs = json.loads(line)
    if case["row"] == 1:
        base = M.cartridge(*M.REPAIR_SHAPES[case["shape"]]); ops = M.repair_ops(base)
    else:
        base = M.rerun_destination(case["shape"]); ops = M.dup_ops(base)
    imgs = M.possible_images(base, ops, tuple(case["inject"]), case["mode"])
    digs = [M.digest(i) for i in imgs]
    n = len(imgs)
    if n == 1:
        k = "single"
    else:
        pos = digs.index(obs["durable_sha256"]) if obs["durable_sha256"] in digs else -1
        k = "none-kept" if pos == 0 else "all-kept" if pos == n - 1 else "mixed" if pos > 0 else "NOT-PERMITTED"
    tally[(case["row"], case["mode"], k)] += 1
for k in sorted(tally): print(k, tally[k])
