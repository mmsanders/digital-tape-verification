"""Verification-authored causal controls on the exact PR #311 Product observations (#107)."""
import base64
import copy
import json
import struct
import sys
import zlib
from pathlib import Path

# usage: python3 P1-R53-WP09D-verif-controls.py <capacity_wp09_r52 dir @87ae5746> <Product observations.jsonl[.gz]>
PACKAGE, OBSERVATIONS = Path(sys.argv[1]), Path(sys.argv[2])
sys.path.insert(0, str(PACKAGE))
import oracle  # noqa: E402  unchanged #99 oracle, commit 87ae5746

_raw = OBSERVATIONS.read_bytes()
if OBSERVATIONS.suffix == ".gz":
    import gzip
    _raw = gzip.decompress(_raw)
obs_all = [json.loads(l) for l in _raw.decode("utf-8").splitlines() if l]
cases = {c.id: c for c in oracle.cases()}


def final(o):
    return o["calls"]["feed_steps"][-1]


def renumber(o):
    for i, e in enumerate(o["events"], 1):
        e["ordinal"] = i


def feed_io(o):
    final(o)["events_from_call"] = 1


def accepted_plus_one(o):
    final(o)["accepted"] += 1


def premature_commit_ok(o):
    o["calls"]["premature_commit"]["result"] = "TAPE_OK"


def allocation_into_live_b(o):
    w = next(e for e in o["events"] if e["step"].startswith("service") and e["op"] == "write")
    w["lba"] = 2048 + 2 * 1024  # chunk 2 holds the live B0 seed run


def missing_commit_flush(o):
    idx = max(i for i, e in enumerate(o["events"]) if e["step"] == "commit" and e["op"] == "flush")
    del o["events"][idx]
    renumber(o)


def pcm_bit_flip_with_spoofed_pass(o):
    r = o["calls"]["render"]
    raw = bytearray(zlib.decompress(base64.b64decode(r["pcm_zlib_b64"])))
    raw[len(raw) // 2] ^= 1
    r["pcm_zlib_b64"] = base64.b64encode(zlib.compress(bytes(raw), 9)).decode()
    o["verdict"] = "PASS"


def stale_free_chunks(o):
    o["calls"]["info_after"]["free_chunks"] = 1


def committed_sequence_5(o):
    h = bytearray(bytes.fromhex(o["raw_after"]["B1"]["header"]))
    e = bytes.fromhex(o["raw_after"]["B1"]["entries"])
    struct.pack_into("<I", h, 8, 5)
    struct.pack_into("<I", h, 60, zlib.crc32(bytes(h[:60]) + e))
    o["raw_after"]["B1"]["header"] = h.hex()


def fixture_generation_edit(o):
    for k in ("primary", "mirror"):
        b = bytearray(bytes.fromhex(o["raw_before"][k]))
        struct.pack_into("<I", b, 12, 8)
        struct.pack_into("<I", b, 508, zlib.crc32(bytes(b[:508])))
        o["raw_before"][k] = b.hex()


CONTROLS = [feed_io, accepted_plus_one, premature_commit_ok, allocation_into_live_b, missing_commit_flush,
            pcm_bit_flip_with_spoofed_pass, stale_free_chunks, committed_sequence_5, fixture_generation_edit]

for o in obs_all:
    oracle.check(cases[o["case"]], o)
print(f"clean: {len(obs_all)}/{len(obs_all)} Product observations pass the unchanged oracle")
for control in CONTROLS:
    red = 0
    reasons = set()
    for o in obs_all:
        bad = copy.deepcopy(o)
        control(bad)
        try:
            oracle.check(cases[o["case"]], bad)
        except AssertionError as exc:
            red += 1
            reasons.add(str(exc)[:60])
    status = "KILLED" if red == len(obs_all) else "SURVIVED"
    print(f"{status} {control.__name__}: red in {red}/{len(obs_all)} cases; reasons {sorted(reasons)}")
    assert red == len(obs_all), control.__name__
