#!/usr/bin/env python3
"""Deterministic synthetic adapter and six killed red controls; never a Product PASS."""
import argparse
import copy
import hashlib
import json
import struct
import zlib
from pathlib import Path

from oracle import INTERVAL, apply, check, edits, pcm


def slot(sequence, length):
    h = bytearray(512)
    h[:8] = b"TAPEIDX\x01"
    struct.pack_into("<IB3xIQ", h, 8, sequence, 1, int(length > 0), length)
    e = struct.pack("<III", 0, 0, length) if length else b""
    struct.pack_into("<I", h, 60, zlib.crc32(h[:60] + e))
    return {"header": h.hex(), "entries": e.hex()}


def make_records():
    timeline = []
    for edit in edits():
        i = edit["id"]
        timeline = apply(timeline, edit)
        obs = {"schema": "wp09-r44-v1", "id": i, "mode": edit["mode"], "at": edit["at"],
               "input_sha256": hashlib.sha256(pcm(edit["frames"])).hexdigest(),
               "accepted": len(edit["frames"]),
               "calls": {k: "TAPE_OK" for k in ("seek", "arm", "feed", "service", "commit")},
               "events": [{"step": "service", "op": "flush", "ordinal": 1},
                          {"step": "commit", "op": "write", "lba": 393 if i % 2 else 265, "ordinal": 2},
                          {"step": "commit", "op": "flush", "ordinal": 3},
                          {"step": "commit", "op": "write", "lba": 392 if i % 2 else 264, "ordinal": 4},
                          {"step": "commit", "op": "flush", "ordinal": 5}]}
        if i % INTERVAL == 0:
            content = pcm(timeline)
            side = "B0" if i % 2 == 0 else "B1"
            obs["checkpoint"] = {"id": i, "after_remount": i % (2 * INTERVAL) == 0,
                                 "render_pcm": content.hex(), "render_block_events": [],
                                 "pcm_sha256": hashlib.sha256(content).hexdigest(),
                                 "raw_index": slot(i + 2, len(timeline)),
                                 "selected_slot": side, "selected_lba": 264 if side == "B0" else 392,
                                 "free_next": 1}
        yield obs


def mutate_at(records, at, fn):
    for record in records:
        if record["id"] == at:
            record = copy.deepcopy(record)
            fn(record)
        yield record


def run():
    result = check(iter(make_records()))
    def wrap_sample(x):
        raw = x["checkpoint"]["render_pcm"]
        x["checkpoint"]["render_pcm"] = ("0080" if raw[:4] != "0080" else "ff7f") + raw[4:]
    def shift_splice(x):
        raw = x["checkpoint"]["render_pcm"]
        x["checkpoint"]["render_pcm"] = raw[8:16] + raw[:8] + raw[16:] if len(raw) >= 16 else raw + "00000000"
    controls = [
        ("dropped suffix", 400, lambda x: x["checkpoint"].update(render_pcm=x["checkpoint"]["render_pcm"][:-8])),
        ("wrapped overdub sample", 800, wrap_sample),
        ("shifted splice boundary", 1200, shift_splice),
        ("stale render digest", 1600, lambda x: x["checkpoint"].update(pcm_sha256="0" * 64)),
        ("final flush reordered", 2000, lambda x: x["events"][-1].update(ordinal=3)),
        ("silent restart", 2400, lambda x: x.update(id=1)),
    ]
    for name, at, fn in controls:
        try:
            check(iter(mutate_at(make_records(), at, fn)))
        except AssertionError:
            pass
        else:
            raise AssertionError("red control survived: " + name)
    return result, len(controls)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit-synthetic", type=Path)
    a = ap.parse_args()
    result, controls = run()
    if a.emit_synthetic:
        if a.emit_synthetic.exists():
            raise SystemExit("refusing to overwrite evidence")
        with a.emit_synthetic.open("x") as out:
            for obj in make_records():
                out.write(json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n")
        result["synthetic_bytes"] = a.emit_synthetic.stat().st_size
        result["synthetic_sha256"] = hashlib.sha256(a.emit_synthetic.read_bytes()).hexdigest()
    print("PASS", result, "red controls killed", controls)


if __name__ == "__main__":
    main()
