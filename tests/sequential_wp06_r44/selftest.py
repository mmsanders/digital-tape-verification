#!/usr/bin/env python3
"""Synthetic protocol probes, including five deliberately bad observations."""
import copy
import struct
import zlib

from oracle import BLOCK, DEGRADED_CALLS, REFUSALS, SLOTS, cases, check, digest_plan

N = 25000


def superblock(generation=7, high=3, uuid=bytes(range(16))):
    b = bytearray(BLOCK)
    b[:8] = b"TAPEFS\0\x01"
    struct.pack_into("<HHI", b, 8, 1, 0, generation)
    b[20:36] = uuid
    struct.pack_into("<I", b, 56, high)
    struct.pack_into("<I", b, 508, zlib.crc32(b[:508]))
    return b.hex()


def slot(side, seq, runs=()):
    h = bytearray(BLOCK)
    h[:8] = b"TAPEIDX\x01"
    struct.pack_into("<IB3xIQ", h, 8, seq, side, len(runs), sum(x[2] for x in runs))
    e = b"".join(struct.pack("<III", *r) for r in runs)
    struct.pack_into("<I", h, 60, zlib.crc32(h[:60] + e))
    return {"header": h.hex(), "entries": e.hex()}


def blank():
    return {"header": bytes(BLOCK).hex(), "entries": ""}


def base():
    s = superblock()
    return {"primary": s, "mirror": s, "A0": slot(0, 10, [(0, 0, 17)]),
            "A1": blank(), "B0": slot(1, 20, [(1, 0, 31)]), "B1": blank()}


def observation(case):
    o = {"schema": "wp06-r44-v1", "case": case.id, "block_count": N,
         "calls": [], "events": [], "snapshots": {}}
    def c(step, fn, result="TAPE_OK", **extra):
        o["calls"].append({"step": step, "fn": fn, "result": result, **extra})
    def e(step, op, **extra):
        o["events"].append({"step": step, "op": op, "ordinal": len(o["events"]) + 1, **extra})
    if case.family == "repair":
        s = base()
        target = "primary" if "primary" in case.variant else "mirror"
        source = "mirror" if target == "primary" else "primary"
        if "invalid" in case.variant:
            s[target] = bytes(BLOCK).hex()
        else:
            s[target] = superblock(generation=6)
        o["snapshots"]["before"] = copy.deepcopy(s)
        for lba in (0, N - 1, *SLOTS.values()):
            e("mount", "read", lba=lba)
        e("mount", "write", phase=4, lba=0 if target == "primary" else N - 1,
          result="error" if case.expected == "write" else "ok")
        if case.expected != "write":
            e("mount", "flush", phase=4, result="error" if case.expected == "flush" else "ok")
        c("mount", "tape_mount", needs_repair=case.expected != "success", candidate=source)
        if case.expected == "success":
            s[target] = s[source]
        o["snapshots"]["after_mount"] = copy.deepcopy(s)
        if case.expected != "success":
            e("retry", "write", phase=4, lba=0 if target == "primary" else N - 1)
            e("retry", "flush", phase=4)
            s[target] = s[source]
        c("retry", "tape_mount", needs_repair=False)
        o["snapshots"]["after_retry"] = copy.deepcopy(s)
    elif case.family == "degraded":
        s = base()
        if case.variant == "invalid":
            s["B0"] = blank()
        else:
            s["B1"] = slot(1, 20, [(1, 1, 31)])
        o["snapshots"]["before"] = copy.deepcopy(s)
        if case.expected == "mount_B":
            c("probe", "tape_mount", "TAPE_ERR_INCONSISTENT")
            return o
        c("mount", "tape_mount", side_b_valid=False, free_next=3)
        op = case.expected
        fn = {"set_side_A": "tape_set_side", "set_side_B": "tape_set_side",
              "status_info_tell": "tape_get_info", "dup_source": "tape_dup"}.get(op, "tape_" + op)
        c("exercise", fn, REFUSALS.get(op, "TAPE_OK"), **({"side_b_valid": True} if op == "reset_b" else {}))
        if op == "reset_b":
            seq = 11 if case.variant == "invalid" else 21
            s["B0"] = slot(1, seq, [(0, 0, 17)])
            o["snapshots"]["after_reset"] = copy.deepcopy(s)
            o["snapshots"]["after_remount"] = copy.deepcopy(s)
            c("remount", "tape_mount")
            c("switch", "tape_set_side", side="B")
    elif case.family == "roundtrip":
        s = base()
        s["A0"] = slot(0, 1)
        s["B0"] = slot(1, 2)
        o["snapshots"]["after_format"] = copy.deepcopy(s)
        c("format", "tape_format")
        c("mount1", "tape_mount")
        if case.variant != "empty-commit":
            runs = ([(i // 131072, i % 131072, 1) for i in range(4096)]
                    if case.variant == "max-entries" else
                    [(i // 131072, i % 131072, 1) for i in range(43)]
                    if case.variant == "entry-block-boundary" else
                    [(0, 0, 1 if case.variant == "one-frame" else 131073)])
            s["B1"] = slot(1, 3, runs)
            count = 97 if case.variant == "max-entries" else 3 if case.variant == "entry-block-boundary" else 2
            for i in range(count - 1):
                e("commit", "write", lba=393 + i)
            e("commit", "flush")
            e("commit", "write", lba=392)
            e("commit", "flush")
            c("commit", "tape_commit", total_frames=sum(r[2] for r in runs))
            selected = "B1"
        else:
            c("commit", "tape_commit")
            selected = "B0"
        c("unmount", "tape_unmount")
        c("mount2", "tape_mount", selected_b=selected, uuid=bytes(range(16)).hex())
        o["snapshots"]["after_remount"] = copy.deepcopy(s)
    else:
        s = base()
        s["mirror"] = superblock(generation=6)
        o["snapshots"]["before"] = copy.deepcopy(s)
        o["snapshots"]["after_mount"] = copy.deepcopy(s)
        c("mount", "tape_mount", case.expected)
    return o


def run():
    plan = cases()
    for case in plan:
        check(case, observation(case))
    by_id = {c.id: c for c in plan}
    controls = [
        ("repair-invalid-primary-write", lambda o: o["events"].insert(0, {"step":"mount", "op":"write", "lba":0, "ordinal":0, "phase":3})),
        ("degraded-divergent-reset_b", lambda o: o["snapshots"]["after_remount"].update(B0=blank())),
        ("roundtrip-one-frame", lambda o: o["events"].pop()),
        ("roundtrip-max-entries", lambda o: o["events"].insert(0, {"step":"commit", "op":"write", "lba":394, "ordinal":0})),
        ("refusal-bad-A-with-partner", lambda o: o["events"].append({"step":"mount", "op":"write", "lba":0, "ordinal":1})),
    ]
    for key, mutate in controls:
        obs = observation(by_id[key])
        mutate(obs)
        try:
            check(by_id[key], obs)
        except AssertionError:
            pass
        else:
            raise AssertionError("red control survived: " + key)
    print("PASS", len(plan), "positive synthetic cases;", len(controls),
          "red controls killed; plan", digest_plan())


if __name__ == "__main__":
    run()
