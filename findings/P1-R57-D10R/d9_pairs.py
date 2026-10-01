#!/usr/bin/env python3
"""Exact DRAFT-9 resurrection pairs: fallback's last zero torn at L1, DRAFT-9 re-run (blank path, no
barrier), a fresh superblock write torn at L2. Reports which copy and which (L1, L2) resurrect."""
import collections

import model as M
import d10_analysis as A

A.RULE = "draft9"
for shape in ("exhaustion_candidate", "exhaustion_equal_divergent", "exhaustion_mirror_only",
              "exhaustion_mirror_candidate"):
    start = A.base(shape)
    ops = A.dup_ops(start)
    writes = [o for o in ops if o[0] == "w"]
    last_zero = 1                               # the fallback's second zero write (write ordinal 1)
    copy_zeroed_last = writes[last_zero][1]
    pairs = collections.Counter()
    for mode in ("flush_required", "write_through"):
        for l1 in range(1, 512):
            for img in M.possible_images(start, ops, ("write", last_zero, l1), mode):
                rops = A.dup_ops(img)
                rw = [o for o in rops if o[0] == "w"]
                for k, o in enumerate(rw):
                    if o[1] not in ("P", "M"):
                        continue
                    for l2 in range(1, 512):
                        for img2 in M.possible_images(img, rops, ("write", k, l2), mode):
                            if A.violation(img2, start):
                                pairs[(mode, o[1], l1, l2)] += 1
    by = collections.defaultdict(list)
    for (mode, copy, l1, l2) in pairs:
        by[(mode, copy)].append((l1, l2))
    print(shape, "last fallback zero hits", copy_zeroed_last)
    for key, v in sorted(by.items()):
        l1s = sorted({a for a, _ in v})
        print("  ", key, "pairs", len(v), "L1 range", (l1s[0], l1s[-1]),
              "L2 for L1=1:", sorted(b for a, b in v if a == 1)[:3], "...", max(b for a, b in v if a == 1),
              "| every pair has L1<=L2<=12:", all(1 <= a <= b <= 12 for a, b in v))
