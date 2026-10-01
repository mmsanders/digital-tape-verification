#!/usr/bin/env python3
"""Verification #136, Ask 2: map every DRAFT-10 dup crash state onto the r2 tapefs §9.5 crash table.

For each starting destination (the 14 #133 shapes, then every distinct one-interruption durable state as
the destination of a re-run) the run's path is planned from raw bytes (template / fallback / residue /
blank, tapefs §9.5 item 5 r2). Each injection's phase selects the applicable table rows; the classifier's
outcome must lie in their permitted union. Observed outcome sets per (path, phase) expose over-permission.
Re-runs are deduplicated on (primary, mirror, A0 header) and injected at every superblock write and flush
(steps 2-3 never write a superblock, so their outcome is fixed by the superblock state step 1 leaves).
"""
import collections

import model as M
import d10_analysis as A

A.RULE = "draft10"
FRESH = M.B.FRESH_DUP_UUID.hex()


def path_of(img):
    p, m = img["P"], img["M"]
    vp, vm = M.sb_valid(p), M.sb_valid(m)
    if vp or vm:
        top = max(M.gen(x) for x, v in ((p, vp), (m, vm)) if v)
        eqdiv = vp and vm and M.gen(p) == M.gen(m) and p != m
        return ("fallback" if top >= 0xFFFFFFFD else "template"), eqdiv
    return ("blank" if not any(p) and not any(m) else "residue"), False


def phases(ops, path):
    names = []
    writes = [o for o in ops if o[0] == "w"]
    n_step1 = 2 if path in ("template", "fallback", "residue") else 0
    for k, o in enumerate(writes):
        if k < n_step1:
            names.append("step1_first" if k == 0 else "step1_last")
        elif k == len(writes) - 2:
            names.append("step4_mirror")
        elif k == len(writes) - 1:
            names.append("step4_primary")
        else:
            names.append("step23")
    return names


def phase_of(inject, ops, path):
    names = phases(ops, path)
    if inject[0] == "write":
        return names[inject[1]]
    # a flush belongs to the write it follows
    wk = fk = 0
    last = None
    for o in ops:
        if o[0] == "w":
            last = names[wk]
            wk += 1
        else:
            if fk == inject[1]:
                return last if last != "step4_primary" else "after4"
            fk += 1
    raise AssertionError


def category(img, start, start_res):
    """Every table label the outcome satisfies (an outcome can be 'unchanged' and 'INCOMPLETE' at once)."""
    c = M.classify(img, "A", True)
    r = c["result"]
    labels = set()
    if r != ("TAPE_OK",) and set(r) <= {"TAPE_ERR_BAD_MAGIC", "TAPE_ERR_CRC"}:
        labels.add("unmountable:" + "/".join(r))
    if r == ("TAPE_OK",) and c["uuid"] == FRESH:
        labels.add("completed")
    if (r, c.get("uuid")) == start_res:
        labels.add("unchanged")
    if r == ("TAPE_OK",) and M.sb_valid(start["P"]) and c["uuid"] == start["P"][20:36].hex():
        labels.add("surviving_primary")
    if r == ("TAPE_ERR_INCOMPLETE",):
        labels.add("TAPE_ERR_INCOMPLETE")
    return frozenset(labels) or frozenset({r[0] if r != ("TAPE_OK",) else "OK-other:" + c["uuid"][:8]})


UNM = {"unmountable:TAPE_ERR_BAD_MAGIC", "unmountable:TAPE_ERR_BAD_MAGIC/TAPE_ERR_CRC"}
# r2 §9.5 rows, by (path, eq-div, phase) -> permitted categories (row ids in comments)
PERMIT = {
    ("template", False, "step1_first"): {"unchanged", "TAPE_ERR_INCOMPLETE"},                 # R3
    ("template", True, "step1_first"): {"unchanged", "surviving_primary", "TAPE_ERR_INCOMPLETE"},  # R5, R6
    ("template", None, "step1_last"): {"TAPE_ERR_INCOMPLETE"},                                # R4, R6
    ("template", None, "step23"): {"TAPE_ERR_INCOMPLETE"},                                    # R7
    ("template", None, "step4_mirror"): {"TAPE_ERR_INCOMPLETE"},                              # R8
    ("template", None, "step4_primary"): {"TAPE_ERR_INCOMPLETE", "completed"},                # R9
    ("template", None, "after4"): {"TAPE_ERR_INCOMPLETE", "completed"},                       # R9, R19
    ("fallback", False, "step1_first"): {"unchanged"},                                        # R3 (first half), R10
    ("fallback", True, "step1_first"): {"unchanged", "surviving_primary"},                    # R11, R12
    ("fallback", False, "step1_last"): {"unchanged"} | UNM,                                   # R10, R13, R14
    ("fallback", True, "step1_last"): {"surviving_primary"} | UNM,                            # R12, R13, R14
    ("residue", None, "step1_first"): UNM,                                                    # R15
    ("residue", None, "step1_last"): UNM,                                                     # R15
}
for path in ("fallback", "residue", "blank"):                                                 # R14/R15 -> R16..R19
    PERMIT[(path, None, "step23")] = UNM
    PERMIT[(path, None, "step4_mirror")] = UNM | {"completed"}                                # R17
    PERMIT[(path, None, "step4_primary")] = {"completed"}                                     # R18
    PERMIT[(path, None, "after4")] = {"completed"}                                            # R19


def permitted(path, eqdiv, phase):
    return PERMIT.get((path, eqdiv, phase)) or PERMIT[(path, None, phase)]


def run(start, label, observed, bad, sb_only=False):
    path, eqdiv = path_of(start)
    ops = A.dup_ops(start)
    r0 = M.classify(start, "A", True)
    start_res = (r0["result"], r0.get("uuid"))
    n = 0
    for mode, inject in M.injections(ops):
        ph = phase_of(inject, ops, path)
        if sb_only and ph in ("step23",):
            continue                      # step 2-3 writes never touch a superblock (see docstring)
        allowed = permitted(path, eqdiv, ph)
        for img in M.possible_images(start, ops, inject, mode):
            cat = category(img, start, start_res)
            observed[(path, eqdiv if path in ("template", "fallback") else None, ph)].update(cat & allowed or cat)
            n += 1
            if not (cat & allowed):
                bad.append((label, path, eqdiv, ph, mode, inject, cat))
    return n


def main():
    observed = collections.defaultdict(set)
    bad = []
    one = two = 0
    starts = {}
    for shape in A.SHAPES:
        start = A.base(shape)
        one += run(start, shape, observed, bad)
        ops = A.dup_ops(start)
        for mode, inject in M.injections(ops):
            for img in M.possible_images(start, ops, inject, mode):
                starts.setdefault((img["P"], img["M"], img["A0h"]), img)
    print(f"one-interruption states mapped: {one}; violations so far: {len(bad)}", flush=True)
    for i, img in enumerate(starts.values()):
        two += run(img, f"rerun#{i}", observed, bad, sb_only=True)
    print(f"re-run starts: {len(starts)}; second-interruption states mapped: {two}; total violations: {len(bad)}")
    for b in bad[:10]:
        print("  VIOLATION", b)
    print("observed outcomes per (path, eq-div, phase) vs permitted:")
    for key in sorted(observed, key=str):
        path, eqdiv, ph = key
        allowed = permitted(path, eqdiv, ph)
        unused = sorted(allowed - observed[key])
        print(f"  {key}: observed {sorted(observed[key])}" + (f" | permitted but never observed {unused}" if unused else ""))


if __name__ == "__main__":
    main()
