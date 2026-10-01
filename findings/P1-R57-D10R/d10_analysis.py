#!/usr/bin/env python3
"""Exhaustive one- and two-interruption analysis of tapefs §9.5 raw-destination classification,
DRAFT-9 rule vs DRAFT-10 (V10-001) rule, for Verification #133. Duplicate transaction; format is
analogous for the superblock-relevant writes. Usage: d10_analysis.py <draft9|draft10> [--two]
"""
from __future__ import annotations

import collections
import struct
import sys

import model as M

B = M.B
FRESH = B.FRESH_DUP_UUID
RULE = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].startswith("draft") else "draft9"
TWO = "--two" in sys.argv
SHARED = 12  # magic + version_major + version_minor: identical in old and fresh superblocks


def is_zero(b):
    return not any(b)


def dup_ops(img):
    """tapefs §9.5 step order, classification by RULE."""
    p, m = img["P"], img["M"]
    vp, vm = M.sb_valid(p), M.sb_valid(m)
    ops = []
    if vp or vm:
        return M.dup_ops(img)                     # valid-copy paths are unchanged by V10-001
    if RULE == "draft10" and not (is_zero(p) and is_zero(m)):
        ops += [("w", "M", M.ZERO), ("f",), ("w", "P", M.ZERO), ("f",)]   # residue zeroing
    return ops + M.dup_ops({**img, "P": M.ZERO, "M": M.ZERO})            # then the blank path


OLD = M.OLD_SB
EXH_P = B.superblock(generation=0xFFFFFFFD, uuid=M.OLD_UUID, high=1)
EXH_M_LOW = B.superblock(generation=0xFFFFFFFC, uuid=M.OLD_UUID, high=1)
torn_tmpl = B.wip_template(OLD, existing_generation=7)[:100] + OLD[100:]
FOREIGN = bytes((i * 89 + 7) & 0xFF for i in range(512))
SHAPES = {name: (s.primary, s.mirror) for name, s in B.raw_shapes().items()}
SHAPES.update({
    "blank": (M.ZERO, M.ZERO),
    # exhaustion with the MIRROR as the selected candidate (primary invalid): V6-008 shape at the boundary
    "exhaustion_mirror_only": (M.ZERO, EXH_P),
    "exhaustion_mirror_candidate": (EXH_M_LOW, EXH_P),
    "residue_primary_torn": (torn_tmpl, M.ZERO),      # V10 shape (b)
    "residue_mirror_torn": (M.ZERO, torn_tmpl),       # V10 shape (b), mirror side
    "residue_foreign": (FOREIGN, FOREIGN[::-1]),      # V10 shape (c)
    "residue_ff_erased": (b"\xff" * 512, b"\xff" * 512),
})


def base(shape):
    p, m = SHAPES[shape]
    return M.cartridge(p, m) if shape != "blank" else {**M.cartridge(M.ZERO, M.ZERO), "C0": M.ZERO}


NEW_A0 = M.index_blocks(0, 1, [(0, 0, 128)])[0]


def outcome(img):
    c = M.classify(img, "A", True)
    if c["result"] != ("TAPE_OK",):
        return c["result"][0], None
    return "TAPE_OK", c["uuid"]


def violation(img, base_img):
    """Mounts under a non-fresh identity while the copied A0 index is durable (silent substitution),
    or mounts under an identity the destination never had valid before the operation."""
    res, uuid = outcome(img)
    if res != "TAPE_OK" or uuid == FRESH.hex():
        return None
    if img["A0h"] == NEW_A0:
        return "previous identity over the copied indices"
    if not (M.sb_valid(base_img["P"]) or M.sb_valid(base_img["M"])):
        return "a destination with no valid superblock mounted"
    return None


def states(start, ops):
    for mode, inject in M.injections(ops):
        for img in M.possible_images(start, ops, inject, mode):
            yield mode, inject, img


def main():
    report = collections.OrderedDict()
    for shape in SHAPES:
        start = base(shape)
        ops = dup_ops(start)
        one = collections.Counter()
        viol1, viol2, seen, two_checked = [], [], {}, 0
        for mode, inject, img in states(start, ops):
            res, uuid = outcome(img)
            kind = None if uuid is None else ("fresh" if uuid == FRESH.hex() else "previous")
            one[(res, kind)] += 1
            v = violation(img, start)
            if v:
                viol1.append((mode, inject, v))
            key = (img["P"], img["M"], img["A0h"])
            seen.setdefault(key, img)
        if TWO:
            for img in seen.values():
                rops = dup_ops(img)
                sb_writes = [i for i, o in enumerate([o for o in rops if o[0] == "w"]) if
                             [o for o in rops if o[0] == "w"][i][1] in ("P", "M")]
                for mode in ("flush_required", "write_through"):
                    for k in sb_writes:
                        for landed in range(513):
                            for img2 in M.possible_images(img, rops, ("write", k, landed), mode):
                                two_checked += 1
                                v = violation(img2, start)
                                if v:
                                    viol2.append((mode, k, landed, v, M.classify(img2, "A", True).get("uuid")))
        report[shape] = (dict(one), viol1, viol2, len(seen), two_checked)
        print(f"{RULE} {shape}: one-interruption outcomes {sorted(one.items(), key=str)}; "
              f"one-int violations {len(viol1)}; distinct first states {len(seen)}; "
              f"two-int images {two_checked}; two-int violations {len(viol2)}", flush=True)
        if viol2:
            land = collections.Counter((v[0], v[1], v[2]) for v in viol2)
            print("   two-int violations by (mode, sb write ordinal, landed):", sorted(land)[:6], "...",
                  "total", len(viol2), flush=True)
    return report


if __name__ == "__main__":
    main()
