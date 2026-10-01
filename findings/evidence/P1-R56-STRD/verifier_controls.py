#!/usr/bin/env python3
"""#131 verifier-owned controls on the retained Product evidence of PR #343 (f2bff1f9).

Run from tests/strengthen_r55 of the publication worktree (7a914cd7). Each control is applied to every case
of its row; the expected kill set is stated and asserted exactly. Mutations are resealed where a digest
would otherwise catch them, so only the semantic check under test can kill them.
"""
import copy, gzip, hashlib, json, struct, sys, zlib
import oracle as O
import rows as R

BLOCK = 512


def sha(b):
    return hashlib.sha256(b).hexdigest()


def kills(case, obs):
    try:
        O.check(case, obs)
        return False
    except (AssertionError, KeyError, TypeError, ValueError, IndexError):
        return True


# V1: realistic V-R54-02 mutant: only block 0 (128 frames) is copied; every later block keeps what the
# destination held before (zero on blank, old album on healthy_pair). The renders are left at the
# truth so only the raw-copy check can kill it. Single-block sources (128 frames) must survive.
def v1_copy_block0_only(case, o):
    f = case["frames"]
    want = R.dup_expected_timeline(f)
    dest = R.dup_destination_image(case["destination"])
    base = R.B.LBA_CHUNK_BASE * BLOCK
    raw = bytearray(dest[base:base + f * 4])
    raw[:BLOCK] = want[:BLOCK]
    o["copy_raw_sha256"] = sha(bytes(raw))


# V2: pass 2 commits B0 before writing its destination chunk (index ahead of data).
def v2_pass2_commit_before_data(case, o):
    ev = o["events"]
    i = max(k for k, e in enumerate(ev) if e["op"] == "write" and R.B.LBA_CHUNK_BASE <= e["lba"] < 7168)
    w, fl = ev[i], ev[i + 1]
    del ev[i:i + 2]
    ev.extend([w, fl])


# V3: pass 2 lands below a_high_water (chunk 1, into Side A's region); commits rewritten to match.
def v3_pass2_below_high_water(case, o):
    for e in o["events"]:
        if e["op"] == "write" and e["lba"] == 2048 + 2 * 1024:
            e["lba"] = 2048 + 1 * 1024


# V4: a stray superblock write during re-spool (no stage clearing applies).
def v4_superblock_write(case, o):
    o["events"].insert(0, {"op": "write", "lba": 0, "count": 1, "data": "00" * BLOCK})


def _reseal(o):
    o["fixture_sha256"] = hashlib.sha256(O.canonical(o["raw_before"]).encode()).hexdigest()


# V5: A1 is a valid Side-A index at sequence 5 > 3: cartridge_sequence would be 5, so the #99 premise
# (commit at 4) is false. Fixture digest resealed.
def v5_a1_valid_seq5(case, o):
    h = bytearray(bytes.fromhex(o["raw_before"]["A0"]["header"]))
    h[8:12] = (5).to_bytes(4, "little")
    struct.pack_into("<I", h, 60, zlib.crc32(bytes(h[:60])))
    o["raw_before"]["A1"] = {"header": bytes(h).hex(), "entries": ""}
    _reseal(o)


# V6: A0 entries non-empty (a Side-A index that is not empty), header count and CRC consistent.
def v6_a0_not_empty(case, o):
    h = bytearray(bytes.fromhex(o["raw_before"]["A0"]["header"]))
    print_once("A0 header[0:24]", bytes(h[:24]).hex())
    h[16:20] = (1).to_bytes(4, "little")
    struct.pack_into("<I", h, 60, zlib.crc32(bytes(h[:60])))
    o["raw_before"]["A0"] = {"header": bytes(h).hex(), "entries": struct.pack("<III", 0, 0, 10).hex()}
    _reseal(o)


_seen = set()
def print_once(k, v):
    if k not in _seen:
        _seen.add(k)
        print(" ", k, v)


CONTROLS = [  # (name, row, mutate, expected killed predicate)
    ("v1_copy_block0_only", 1, v1_copy_block0_only, lambda c: c["frames"] > 128),
    ("v2_pass2_commit_before_data", 2, v2_pass2_commit_before_data, lambda c: True),
    ("v3_pass2_below_high_water", 2, v3_pass2_below_high_water, lambda c: True),
    ("v4_superblock_write", 2, v4_superblock_write, lambda c: True),
    ("v5_a1_valid_seq5", 3, v5_a1_valid_seq5, lambda c: True),
    ("v6_a0_not_empty", 3, v6_a0_not_empty, lambda c: True),
]


def main():
    obs = [json.loads(l) for l in gzip.open(sys.argv[1])]
    cases = list(O.iter_cases())
    assert len(obs) == len(cases) == 40
    for c, o in zip(cases, obs):
        assert not kills(c, o), c
    print("clean: 40/40 PASS")
    ok = True
    for name, row, fn, exp in CONTROLS:
        got, want = set(), set()
        for c, o in zip(cases, obs):
            if c["row"] != row:
                continue
            m = copy.deepcopy(o)
            fn(c, m)
            if kills(c, m):
                got.add(c["index"])
            if exp(c):
                want.add(c["index"])
        good = got == want
        ok &= good
        print(f"{'killed' if good else 'MISMATCH'} {name}: {len(got)} killed, expected exactly {len(want)} "
              f"(row {row}){'' if good else f' got {sorted(got)} want {sorted(want)}'}")
    print("ALL CONTROLS ON EXACT SETS" if ok else "CONTROL FAILURE")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
