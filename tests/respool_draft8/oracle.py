#!/usr/bin/env python3
"""Independent DRAFT-8 WP-12 re-spool oracle. No product implementation imports."""
from __future__ import annotations

import struct
import zlib
from dataclasses import dataclass

CF = 131072
SAMPLE_RATE = 44100
NOMINAL_LENGTH_S = 60
CHUNK_BYTES = 524288
BLOCK = 512
BLOCKS_PER_CHUNK = CHUNK_BYTES // BLOCK
SLOT_BYTES = 65536
TAPE_MAX_ENTRIES = 4096
LBA_A0, LBA_A1, LBA_B0, LBA_B1, LBA_CHUNK_BASE = 8, 136, 264, 392, 2048
HASHES = {
    "tapefs-v1.md": "3bffa0ec46d7ba3779b02cbee6fac1edaf5094553f78270ee379759655147cbb",
    "engine-api.md": "537eadc423e1a7bde726d689206b8fe93bef164d57e48e8ff71e07eaf8a7e3a1",
    "acceptance.md": "7f78fba7b66b4fc6e96d15399c62468249bb30fbccbb59bf9f57b4532f56b6b7",
}


@dataclass(frozen=True)
class Media:
    blocks: int
    primary: bytes
    mirror: bytes
    slots: tuple[bytes, bytes, bytes, bytes]

    def encode(self) -> bytes:
        return b"VO08" + struct.pack("<I", self.blocks) + self.primary + self.mirror + b"".join(self.slots)

    @staticmethod
    def decode(data: bytes) -> "Media":
        need = 8 + 2 * BLOCK + 4 * SLOT_BYTES
        if len(data) != need or data[:4] != b"VO08":
            raise ValueError("bad VO08")
        blocks = struct.unpack_from("<I", data, 4)[0]
        p = 8
        primary = data[p : p + BLOCK]
        p += BLOCK
        mirror = data[p : p + BLOCK]
        p += BLOCK
        slots = [data[p + i * SLOT_BYTES : p + (i + 1) * SLOT_BYTES] for i in range(4)]
        return Media(blocks, primary, mirror, tuple(slots))


@dataclass(frozen=True)
class Case:
    id: str
    pre: Media
    expect_writes: bool
    expect_result: str
    expect_promote: str | None
    expect_entries: list[tuple[int, int, int]] | None
    expect_seq: int | None
    pass1_chunks: tuple[int, int] | None
    pass2_chunks: tuple[int, int] | None


def derived_total_chunks(nominal=NOMINAL_LENGTH_S) -> int:
    return (nominal * SAMPLE_RATE + CF - 1) // CF


def sb(*, generation=7, high=3, chunks=None, blocks=None, stage=0) -> bytes:
    if chunks is None:
        chunks = derived_total_chunks()
    if blocks is None:
        blocks = LBA_CHUNK_BASE + chunks * BLOCKS_PER_CHUNK + 1
    b = bytearray(BLOCK)
    b[:8] = b"TAPEFS\0\x01"
    struct.pack_into("<H", b, 8, 1)
    struct.pack_into("<H", b, 10, 0)
    struct.pack_into("<I", b, 12, generation)
    b[20:36] = bytes(range(16))
    struct.pack_into("<I", b, 36, SAMPLE_RATE)
    struct.pack_into("<H", b, 40, 2)
    struct.pack_into("<H", b, 42, 16)
    struct.pack_into("<I", b, 44, CHUNK_BYTES)
    struct.pack_into("<I", b, 48, NOMINAL_LENGTH_S)
    struct.pack_into("<I", b, 52, chunks)
    struct.pack_into("<I", b, 56, high)
    struct.pack_into("<I", b, 60, SLOT_BYTES)
    struct.pack_into("<I", b, 64, LBA_A0)
    struct.pack_into("<I", b, 68, LBA_A1)
    struct.pack_into("<I", b, 72, LBA_B0)
    struct.pack_into("<I", b, 76, LBA_B1)
    struct.pack_into("<I", b, 80, LBA_CHUNK_BASE)
    struct.pack_into("<I", b, 84, blocks - 1)
    struct.pack_into("<I", b, 124, stage)
    struct.pack_into("<I", b, 508, zlib.crc32(b[:508]))
    return bytes(b)


def idx(side: int, entries, sequence: int) -> bytes:
    b = bytearray(SLOT_BYTES)
    b[:8] = b"TAPEIDX\x01"
    total = sum(e[2] for e in entries)
    struct.pack_into("<IB3xIQ", b, 8, sequence, side, len(entries), total)
    for i, e in enumerate(entries):
        struct.pack_into("<III", b, 512 + 12 * i, *e)
    struct.pack_into("<I", b, 60, zlib.crc32(b[:60] + b[512 : 512 + 12 * len(entries)]))
    return bytes(b)


def invalid_slot() -> bytes:
    return bytes(SLOT_BYTES)


def sb_valid(b: bytes) -> bool:
    return len(b) == BLOCK and b[:8] == b"TAPEFS\0\x01" and struct.unpack_from("<I", b, 508)[0] == zlib.crc32(b[:508])


def select_sb(m: Media) -> bytes:
    if sb_valid(m.primary) and sb_valid(m.mirror):
        if m.primary != m.mirror and struct.unpack_from("<I", m.primary, 12)[0] == struct.unpack_from("<I", m.mirror, 12)[0]:
            raise ValueError("divergent")
        gp = struct.unpack_from("<I", m.primary, 12)[0]
        gm = struct.unpack_from("<I", m.mirror, 12)[0]
        return m.primary if gp >= gm else m.mirror
    if sb_valid(m.primary):
        return m.primary
    if sb_valid(m.mirror):
        return m.mirror
    raise ValueError("no sb")


def parse_entries(s: bytes):
    count = struct.unpack_from("<I", s, 16)[0]
    return [struct.unpack_from("<III", s, 512 + 12 * i) for i in range(count)]


def structural_sequence(s: bytes):
    if len(s) != SLOT_BYTES or s[:8] != b"TAPEIDX\x01":
        return None
    count = struct.unpack_from("<I", s, 16)[0]
    if count > TAPE_MAX_ENTRIES:
        return None
    stored = struct.unpack_from("<I", s, 60)[0]
    if stored != zlib.crc32(s[:60] + s[512 : 512 + 12 * count]):
        return None
    return struct.unpack_from("<I", s, 8)[0]


def semantic_valid(s: bytes, side: int, superblock: bytes) -> bool:
    if structural_sequence(s) is None:
        return False
    if s[12] != side:
        return False
    entries = parse_entries(s)
    if struct.unpack_from("<Q", s, 20)[0] != sum(e[2] for e in entries):
        return False
    chunks = struct.unpack_from("<I", superblock, 52)[0]
    high = struct.unpack_from("<I", superblock, 56)[0]
    intervals = []
    for first, start, n in entries:
        if n < 1 or start >= CF:
            return False
        last = first + (start + n - 1) // CF
        if last >= chunks or (side == 0 and last >= high):
            return False
        lo = first * CF + start
        intervals.append((lo, lo + n))
    intervals.sort()
    return not any(intervals[i][1] > intervals[i + 1][0] for i in range(len(intervals) - 1))


def live_slot(m: Media, side: int):
    sbx = select_sb(m)
    ids = (0, 1) if side == 0 else (2, 3)
    valid = [i for i in ids if semantic_valid(m.slots[i], side, sbx)]
    if not valid:
        return None
    if len(valid) == 1:
        return valid[0]
    a, b = valid
    sa, sbq = structural_sequence(m.slots[a]), structural_sequence(m.slots[b])
    if sa == sbq:
        return None
    return a if sa > sbq else b


def cartridge_sequence(m: Media) -> int:
    seq = [structural_sequence(s) for s in m.slots]
    seq = [x for x in seq if x is not None]
    return max(seq)


def media(high: int, b_entries, b_seq=20, a_seq=10, partner_seq=700, b1=None) -> Media:
    chunks = derived_total_chunks()
    blocks = LBA_CHUNK_BASE + chunks * BLOCKS_PER_CHUNK + 1
    s = sb(high=high, chunks=chunks, blocks=blocks)
    b1s = invalid_slot() if b1 is None else idx(1, b1[0], b1[1])
    return Media(blocks, s, s, (idx(0, [(0, 0, 128)], a_seq), idx(1, [(1, 0, 64)], partner_seq), idx(1, b_entries, b_seq), b1s))


def chunk_lba(chunk: int) -> tuple[int, int]:
    return LBA_CHUNK_BASE + chunk * BLOCKS_PER_CHUNK, LBA_CHUNK_BASE + (chunk + 1) * BLOCKS_PER_CHUNK


def make_cases() -> list[Case]:
    empty = media(3, [])
    two = media(10, [(10, 0, 2 * CF)])
    full = media(19, [(19, 0, 2 * CF)])
    deg = media(3, [(0, 0, 256)], b_seq=500, b1=([(1, 0, 128)], 500))
    return [
        Case("WP12-EMPTY", empty, False, "TAPE_OK", "TAPE_ERR_INVALID_ARG", [], 700, None, None),
        Case("WP12-TWOPASS", two, True, "TAPE_OK", None, [(10, 0, 2 * CF)], 702, (12, 14), (10, 12)),
        Case("WP12-FULL", full, False, "TAPE_ERR_CARTRIDGE_FULL", None, [(19, 0, 2 * CF)], 700, None, None),
        Case("WP12-DEGRADED", deg, False, "TAPE_ERR_NO_VALID_INDEX", None, None, 700, None, None),
    ]


def fixture_contract_errors(case: Case) -> list[str]:
    err = []
    if derived_total_chunks() != 21:
        err.append("geometry drift")
    if case.id == "WP12-TWOPASS":
        if struct.unpack_from("<I", select_sb(case.pre), 56)[0] != 10:
            err.append("H!=10")
        if parse_entries(case.pre.slots[2]) != [(10, 0, 2 * CF)]:
            err.append("two-pass B premise")
        if live_slot(case.pre, 1) != 2:
            err.append("two-pass live B")
    if case.id == "WP12-EMPTY" and parse_entries(case.pre.slots[2]) != []:
        err.append("empty B premise")
    if case.id == "WP12-DEGRADED" and live_slot(case.pre, 1) is not None:
        err.append("degraded premise")
    return err


def _writes(events):
    return [e for e in events if e.get("op") == "write"]


def writes_in_chunks(events, lo_chunk, hi_chunk) -> bool:
    lo, _ = chunk_lba(lo_chunk)
    _, hi = chunk_lba(hi_chunk - 1)
    return any(e.get("op") == "write" and lo <= e.get("lba", -1) < hi for e in events)


def check(case: Case, post: Media, events: list[dict], calls: list[dict]) -> list[str]:
    err = []

    def req(cond, msg):
        if not cond:
            err.append(msg)

    req(post.blocks == case.pre.blocks, "block_count changed")
    req(post.primary == case.pre.primary and post.mirror == case.pre.mirror, "respool wrote superblock")
    res = [c for c in calls if c.get("fn") == "tape_respool"]
    req(bool(res) and res[-1].get("result") == case.expect_result, "respool result")
    if case.expect_result == "TAPE_OK":
        req(res[-1].get("more_work") is False, "more_work not false")
    if case.expect_promote:
        prom = [c for c in calls if c.get("fn") == "tape_promote"]
        req(bool(prom) and prom[0].get("result") == case.expect_promote, "empty promote asymmetry")
    if not case.expect_writes:
        req(not _writes(events), "zero-write case wrote")
        if case.id != "WP12-DEGRADED":
            req(post.slots == case.pre.slots, "zero-write case changed index")
        return err
    req(case.expect_entries is not None, "missing expected entries")
    live = live_slot(post, 1)
    req(live is not None, "post B not live")
    req(parse_entries(post.slots[live]) == case.expect_entries, "final not one compacted entry")
    req(cartridge_sequence(post) == case.expect_seq, "sequence not +2")
    req(writes_in_chunks(events, *case.pass1_chunks), "missing pass-1 destination writes")
    req(writes_in_chunks(events, *case.pass2_chunks), "missing pass-2 destination writes")
    for e in _writes(events):
        if e.get("lba", 0) >= LBA_CHUNK_BASE:
            chunk = (e["lba"] - LBA_CHUNK_BASE) // BLOCKS_PER_CHUNK
            req(chunk >= 10, "write below a_high_water")
    return err


def synth_calls(case: Case) -> list[dict]:
    calls = [{"phase": "mount", "fn": "tape_mount", "result": "TAPE_OK", "side": "B"}]
    if case.expect_promote:
        calls.append({"phase": "promote", "fn": "tape_promote", "result": case.expect_promote, "more_work": False})
    if case.expect_writes:
        calls.append({"phase": "respool", "fn": "tape_respool", "result": "TAPE_OK", "more_work": True, "block_budget": 64})
        calls.append({"phase": "respool", "fn": "tape_respool", "result": "TAPE_OK", "more_work": False, "block_budget": 64})
    else:
        calls.append({"phase": "respool", "fn": "tape_respool", "result": case.expect_result, "more_work": False, "block_budget": 64})
    calls.append({"phase": "unmount", "fn": "tape_unmount", "result": "TAPE_OK"})
    return calls


def synth_post(case: Case):
    p = case.pre
    if not case.expect_writes:
        return p, []
    slots = list(p.slots)
    slots[3] = idx(1, case.expect_entries, case.expect_seq)
    ev = []
    for start, end in (case.pass1_chunks, case.pass2_chunks):
        lo, _ = chunk_lba(start)
        ev.append({"phase": "respool", "op": "write", "lba": lo, "count": 1})
        ev.append({"phase": "respool", "op": "flush"})
    ev.extend(
        [
            {"phase": "respool", "op": "write", "lba": LBA_B1 + 1, "count": 1},
            {"phase": "respool", "op": "flush"},
            {"phase": "respool", "op": "write", "lba": LBA_B1, "count": 1},
            {"phase": "respool", "op": "flush"},
        ]
    )
    return Media(p.blocks, p.primary, p.mirror, tuple(slots)), ev


def synth_observation(case: Case):
    post, ev = synth_post(case)
    return post, ev, synth_calls(case)
