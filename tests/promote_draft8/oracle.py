#!/usr/bin/env python3
"""Independent DRAFT-8 promote classification + completed-path oracle.

TapeFS §9.3.0 classification and one uninterrupted FRESH adopt-in-place
completion plus the step-5 decline. No crash injection, no RESUME rows,
no WP-12a continuation identity. No product implementation imports.
"""
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
SEQ_MAX_MINUS_2 = 0xFFFFFFFD


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
    expect: str
    expect_writes: bool
    expect_high: int | None
    expect_stage: int | None
    expect_entries: list[tuple[int, int, int]] | None
    expect_seq: int | None
    phase2: str | None  # "complete" | "decline" | None


def derived_total_chunks() -> int:
    return (NOMINAL_LENGTH_S * SAMPLE_RATE + CF - 1) // CF


def sb(*, generation=7, high=3, stage=0, staging=0) -> bytes:
    chunks = derived_total_chunks()
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
    struct.pack_into("<I", b, 128, staging)
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


def media(*, high, a_entries, b_entries, a_seq=10, b_seq=20, partner_seq=700, b1=None, generation=7):
    chunks = derived_total_chunks()
    blocks = LBA_CHUNK_BASE + chunks * BLOCKS_PER_CHUNK + 1
    s = sb(generation=generation, high=high)
    b1s = invalid_slot() if b1 is None else idx(1, b1[0], b1[1])
    return Media(
        blocks,
        s,
        s,
        (
            idx(0, a_entries, a_seq),
            idx(0, [(1, 0, 64)], partner_seq) if partner_seq else invalid_slot(),
            idx(1, b_entries, b_seq),
            b1s,
        ),
    )


def make_cases() -> list[Case]:
    empty = media(high=3, a_entries=[(0, 0, 128)], b_entries=[])
    deg = media(high=3, a_entries=[(0, 0, 128)], b_entries=[(0, 0, 64)], b_seq=500, b1=([(1, 0, 32)], 500))
    nothing = media(high=3, a_entries=[(0, 0, 128)], b_entries=[(0, 0, 128)])
    exhausted = media(high=3, a_entries=[(0, 0, 128)], b_entries=[(3, 0, CF)], a_seq=SEQ_MAX_MINUS_2, b_seq=SEQ_MAX_MINUS_2, partner_seq=0)
    full = media(high=19, a_entries=[(0, 0, 128)], b_entries=[(19, 10, CF)])
    adopt = media(high=10, a_entries=[(0, 0, 128)], b_entries=[(10, 0, 2 * CF)])
    decline = media(high=2, a_entries=[(0, 0, 128)], b_entries=[(2, 0, 10 * CF)])
    return [
        Case("PR-EMPTY", empty, "TAPE_ERR_INVALID_ARG", False, None, None, None, None, None),
        Case("PR-DEGRADED", deg, "TAPE_ERR_NO_VALID_INDEX", False, None, None, None, None, None),
        Case("PR-NOTHING", nothing, "TAPE_OK", False, 3, 0, [(0, 0, 128)], 700, None),
        Case("PR-SEQ-EXHAUSTED", exhausted, "TAPE_ERR_SEQUENCE_EXHAUSTED", False, None, None, None, None, None),
        Case("PR-FULL", full, "TAPE_ERR_CARTRIDGE_FULL", False, None, None, None, None, None),
        Case("PR-ADOPT-COMPLETE", adopt, "TAPE_OK", True, 2, 0, [(0, 0, 2 * CF)], 704, "complete"),
        Case("PR-ADOPT-DECLINE", decline, "TAPE_OK", True, 12, 0, [(2, 0, 10 * CF)], 702, "decline"),
    ]


def fixture_contract_errors(case: Case) -> list[str]:
    err = []
    if derived_total_chunks() != 21:
        err.append("geometry drift")
    if case.id == "PR-EMPTY" and parse_entries(case.pre.slots[2]) != []:
        err.append("empty B premise")
    if case.id == "PR-DEGRADED" and live_slot(case.pre, 1) is not None:
        err.append("degraded premise")
    if case.id == "PR-NOTHING":
        if parse_entries(case.pre.slots[0]) != parse_entries(case.pre.slots[2]):
            err.append("nothing-to-do A/B not identical")
    if case.id == "PR-ADOPT-COMPLETE":
        if parse_entries(case.pre.slots[2]) != [(10, 0, 2 * CF)]:
            err.append("adopt B premise")
        if struct.unpack_from("<I", select_sb(case.pre), 56)[0] != 10:
            err.append("adopt H premise")
    if case.id == "PR-ADOPT-DECLINE":
        if parse_entries(case.pre.slots[2]) != [(2, 0, 10 * CF)]:
            err.append("decline B premise")
    if case.id == "PR-FULL":
        entries = parse_entries(case.pre.slots[2])
        if not entries or entries[0][1] == 0:
            err.append("full case must not adopt-in-place")
    return err


def _writes(events):
    return [e for e in events if e.get("op") == "write"]


def chunk_lba(chunk: int) -> int:
    return LBA_CHUNK_BASE + chunk * BLOCKS_PER_CHUNK


def check(case: Case, post: Media, events: list[dict], calls: list[dict]) -> list[str]:
    err: list[str] = []

    def req(cond, msg):
        if not cond:
            err.append(msg)

    req(not fixture_contract_errors(case), "fixture contract: " + ",".join(fixture_contract_errors(case)))
    mounts = [c for c in calls if c.get("fn") == "tape_mount"]
    req(bool(mounts) and mounts[0].get("result") == "TAPE_OK", "mount failed")
    hits = [c for c in calls if c.get("fn") == "tape_promote"]
    req(bool(hits) and hits[-1].get("result") == case.expect, "promote result")
    req(hits and hits[-1].get("more_work") is False, "more_work not false")

    if not case.expect_writes:
        req(post.encode() == case.pre.encode(), "classification wrote media")
        req(not _writes(events), "classification issued a write")
        req(not any(e.get("op") == "flush" for e in events), "classification issued a flush")
        return err

    sbx = select_sb(post)
    req(struct.unpack_from("<I", sbx, 56)[0] == case.expect_high, "a_high_water")
    req(struct.unpack_from("<I", sbx, 124)[0] == case.expect_stage, "promote_stage not cleared")
    req(struct.unpack_from("<I", sbx, 128)[0] == 0, "promote_staging_chunk not cleared")
    live_a = live_slot(post, 0)
    live_b = live_slot(post, 1)
    req(live_a is not None and live_b is not None, "post sides not live")
    req(parse_entries(post.slots[live_a]) == case.expect_entries, "post A entries")
    req(parse_entries(post.slots[live_b]) == case.expect_entries, "post B entries")
    req(cartridge_sequence(post) == case.expect_seq, "sequence after promote")
    req(struct.unpack_from("<I", sbx, 12)[0] > struct.unpack_from("<I", case.pre.primary, 12)[0], "sb_generation not incremented")

    if case.phase2 == "complete":
        req(any(e.get("op") == "write" and e.get("lba", -1) == chunk_lba(0) for e in events), "phase 2 did not write [0,len)")
        req(case.expect_high == 2, "completed phase 2 high-water")
    if case.phase2 == "decline":
        req(not any(e.get("op") == "write" and e.get("lba", 0) >= LBA_CHUNK_BASE and (e["lba"] - LBA_CHUNK_BASE) // BLOCKS_PER_CHUNK < 2 for e in events), "decline wrote below S")
        req(case.expect_high == 12, "decline left H = S+len")
    return err


def synth_post(case: Case):
    if not case.expect_writes:
        return case.pre, []
    p = case.pre
    gen0 = struct.unpack_from("<I", p.primary, 12)[0]
    if case.phase2 == "complete":
        final = sb(generation=gen0 + 2, high=2, stage=0, staging=0)
        slots = (
            idx(0, case.expect_entries, 703),
            p.slots[1],
            idx(1, case.expect_entries, 704),
            p.slots[3],
        )
        ev = [
            {"phase": "promote", "op": "write", "lba": LBA_A1 + 1, "count": 1},
            {"phase": "promote", "op": "flush"},
            {"phase": "promote", "op": "write", "lba": LBA_A1, "count": 1},
            {"phase": "promote", "op": "flush"},
            {"phase": "promote", "op": "write", "lba": LBA_B1 + 1, "count": 1},
            {"phase": "promote", "op": "flush"},
            {"phase": "promote", "op": "write", "lba": LBA_B1, "count": 1},
            {"phase": "promote", "op": "flush"},
            {"phase": "promote", "op": "write", "lba": p.blocks - 1, "count": 1},
            {"phase": "promote", "op": "flush"},
            {"phase": "promote", "op": "write", "lba": 0, "count": 1},
            {"phase": "promote", "op": "flush"},
            {"phase": "promote", "op": "write", "lba": chunk_lba(0), "count": 1},
            {"phase": "promote", "op": "flush"},
            {"phase": "promote", "op": "write", "lba": LBA_A0 + 1, "count": 1},
            {"phase": "promote", "op": "flush"},
            {"phase": "promote", "op": "write", "lba": LBA_A0, "count": 1},
            {"phase": "promote", "op": "flush"},
            {"phase": "promote", "op": "write", "lba": LBA_B0 + 1, "count": 1},
            {"phase": "promote", "op": "flush"},
            {"phase": "promote", "op": "write", "lba": LBA_B0, "count": 1},
            {"phase": "promote", "op": "flush"},
            {"phase": "promote", "op": "write", "lba": p.blocks - 1, "count": 1},
            {"phase": "promote", "op": "flush"},
            {"phase": "promote", "op": "write", "lba": 0, "count": 1},
            {"phase": "promote", "op": "flush"},
        ]
        return Media(p.blocks, final, final, slots), ev
    final = sb(generation=gen0 + 2, high=12, stage=0, staging=0)
    slots = (
        idx(0, case.expect_entries, 701),
        p.slots[1],
        idx(1, case.expect_entries, 702),
        p.slots[3],
    )
    ev = [
        {"phase": "promote", "op": "write", "lba": LBA_A1 + 1, "count": 1},
        {"phase": "promote", "op": "flush"},
        {"phase": "promote", "op": "write", "lba": LBA_A1, "count": 1},
        {"phase": "promote", "op": "flush"},
        {"phase": "promote", "op": "write", "lba": LBA_B1 + 1, "count": 1},
        {"phase": "promote", "op": "flush"},
        {"phase": "promote", "op": "write", "lba": LBA_B1, "count": 1},
        {"phase": "promote", "op": "flush"},
        {"phase": "promote", "op": "write", "lba": p.blocks - 1, "count": 1},
        {"phase": "promote", "op": "flush"},
        {"phase": "promote", "op": "write", "lba": 0, "count": 1},
        {"phase": "promote", "op": "flush"},
        {"phase": "promote", "op": "write", "lba": p.blocks - 1, "count": 1},
        {"phase": "promote", "op": "flush"},
        {"phase": "promote", "op": "write", "lba": 0, "count": 1},
        {"phase": "promote", "op": "flush"},
    ]
    return Media(p.blocks, final, final, slots), ev


def synth_calls(case: Case) -> list[dict]:
    calls = [{"phase": "mount", "fn": "tape_mount", "result": "TAPE_OK", "side": "B"}]
    if case.expect_writes:
        calls.append({"phase": "promote", "fn": "tape_promote", "result": "TAPE_OK", "more_work": True, "block_budget": 64})
        calls.append({"phase": "promote", "fn": "tape_promote", "result": "TAPE_OK", "more_work": False, "block_budget": 64})
    else:
        calls.append({"phase": "promote", "fn": "tape_promote", "result": case.expect, "more_work": False, "block_budget": 64})
    calls.append({"phase": "unmount", "fn": "tape_unmount", "result": "TAPE_OK"})
    return calls


def synth_observation(case: Case):
    post, ev = synth_post(case)
    return post, ev, synth_calls(case)
