#!/usr/bin/env python3
"""Independent DRAFT-8 transport extras: tape_set_side + warm-start negatives.

No product implementation imports. Not WP-11 goldens and not a listened fixture.
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
LBA_A0, LBA_A1, LBA_B0, LBA_B1, LBA_CHUNK_BASE = 8, 136, 264, 392, 2048


@dataclass(frozen=True)
class Media:
    blocks: int
    primary: bytes
    mirror: bytes
    slots: tuple[bytes, bytes, bytes, bytes]

    def encode(self) -> bytes:
        return b"VO08" + struct.pack("<I", self.blocks) + self.primary + self.mirror + b"".join(self.slots)


@dataclass(frozen=True)
class Case:
    id: str
    pre: Media
    mount_side: str
    kind: str
    expect: str


def derived_total_chunks() -> int:
    return (NOMINAL_LENGTH_S * SAMPLE_RATE + CF - 1) // CF


def sb(*, high=3) -> bytes:
    chunks = derived_total_chunks()
    blocks = LBA_CHUNK_BASE + chunks * BLOCKS_PER_CHUNK + 1
    b = bytearray(BLOCK)
    b[:8] = b"TAPEFS\0\x01"
    struct.pack_into("<H", b, 8, 1)
    struct.pack_into("<H", b, 10, 0)
    struct.pack_into("<I", b, 12, 7)
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


def healthy() -> Media:
    s = sb()
    chunks = derived_total_chunks()
    blocks = LBA_CHUNK_BASE + chunks * BLOCKS_PER_CHUNK + 1
    return Media(blocks, s, s, (idx(0, [(0, 0, 256)], 10), invalid_slot(), idx(1, [(0, 0, 64)], 20), invalid_slot()))


def degraded() -> Media:
    s = sb()
    chunks = derived_total_chunks()
    blocks = LBA_CHUNK_BASE + chunks * BLOCKS_PER_CHUNK + 1
    return Media(
        blocks,
        s,
        s,
        (idx(0, [(0, 0, 256)], 10), invalid_slot(), idx(1, [(0, 0, 64)], 500), idx(1, [(1, 0, 32)], 500)),
    )


def make_cases() -> list[Case]:
    h = healthy()
    d = degraded()
    return [
        Case("SS-A-TO-B", h, "A", "set_side", "TAPE_OK"),
        Case("SS-SAME-A", h, "A", "set_side_same", "TAPE_OK"),
        Case("SS-DEGRADED-B", d, "A", "set_side", "TAPE_ERR_NO_VALID_INDEX"),
        Case("SS-ARMED-BUSY", h, "B", "set_side_armed", "TAPE_ERR_BUSY"),
        Case("WARM-NULL", h, "A", "warm_null", "TAPE_OK"),
        Case("WARM-DATA-NULL", h, "A", "warm_data_null", "TAPE_OK"),
        Case("WARM-ZERO-FRAMES", h, "A", "warm_zero", "TAPE_OK"),
        Case("WARM-SHORT-BUF", h, "A", "warm_short", "TAPE_OK"),
        Case("WARM-PAST-END", h, "A", "warm_past", "TAPE_OK"),
        Case("WARM-RESUME-OUT", h, "A", "warm_resume", "TAPE_OK"),
        Case("WARM-UUID", h, "A", "warm_uuid", "TAPE_OK"),
        Case("WARM-SIDE", h, "A", "warm_side", "TAPE_OK"),
    ]


def check(case: Case, post: Media, events: list[dict], calls: list[dict]) -> list[str]:
    err = []

    def req(cond, msg):
        if not cond:
            err.append(msg)

    req(post.encode() == case.pre.encode(), "transport extras wrote media")
    req(not any(e.get("op") == "write" for e in events), "transport extras issued a write")
    mounts = [c for c in calls if c.get("fn") == "tape_mount"]
    req(bool(mounts) and mounts[0].get("result") == "TAPE_OK", "mount failed")

    if case.kind.startswith("warm"):
        req(mounts[0].get("warm_start_used") is False, "warm negative used the descriptor")
        infos = [c for c in calls if c.get("fn") == "tape_get_info"]
        req(bool(infos) and infos[0].get("warm_start_used") is False, "info.warm_start_used not false")
        return err

    if case.kind == "set_side_same":
        hits = [c for c in calls if c.get("fn") == "tape_set_side"]
        req(bool(hits) and hits[0].get("result") == "TAPE_OK" and hits[0].get("side") == "A", "same-side set_side")
        return err

    if case.kind == "set_side_armed":
        arms = [c for c in calls if c.get("fn") == "tape_arm"]
        req(bool(arms) and arms[0].get("result") == "TAPE_OK", "armed fixture failed to arm")
        hits = [c for c in calls if c.get("fn") == "tape_set_side"]
        req(bool(hits) and hits[0].get("result") == "TAPE_ERR_BUSY", "set_side while armed was not BUSY")
        return err

    hits = [c for c in calls if c.get("fn") == "tape_set_side"]
    req(bool(hits) and hits[0].get("result") == case.expect and hits[0].get("side") == "B", "set_side result")
    if case.expect == "TAPE_OK":
        tells = [c for c in calls if c.get("fn") == "tape_tell"]
        req(bool(tells) and tells[0].get("frame") == 0, "set_side did not reset position to 0")
        stats = [c for c in calls if c.get("fn") == "tape_status"]
        req(bool(stats) and stats[0].get("at_end") is False and stats[0].get("at_start") is False, "endpoint flags not cleared")
        infos = [c for c in calls if c.get("fn") == "tape_get_info"]
        req(bool(infos) and infos[0].get("warm_start_used") is False, "set_side left warm_start_used")
        renders = [c for c in calls if c.get("fn") == "tape_render"]
        req(bool(renders) and renders[0].get("rendered") == 0, "stale ring rendered after set_side")
    return err


def synth_observation(case: Case):
    calls = [{"phase": "mount", "fn": "tape_mount", "result": "TAPE_OK", "side": case.mount_side, "warm_start_used": False}]
    if case.kind.startswith("warm"):
        calls.append({"phase": "info", "fn": "tape_get_info", "result": "TAPE_OK", "warm_start_used": False})
    elif case.kind == "set_side_same":
        calls.append({"phase": "set_side", "fn": "tape_set_side", "result": "TAPE_OK", "side": "A"})
    elif case.kind == "set_side_armed":
        calls.append({"phase": "arm", "fn": "tape_arm", "result": "TAPE_OK", "mode": "overwrite"})
        calls.append({"phase": "set_side", "fn": "tape_set_side", "result": "TAPE_ERR_BUSY", "side": "A"})
        calls.append({"phase": "abort", "fn": "tape_abort", "result": "TAPE_OK"})
    else:
        calls.append({"phase": "seek", "fn": "tape_seek", "result": "TAPE_OK", "frame": 10})
        calls.append({"phase": "set_side", "fn": "tape_set_side", "result": case.expect, "side": "B"})
        if case.expect == "TAPE_OK":
            calls.append({"phase": "tell", "fn": "tape_tell", "result": "TAPE_OK", "frame": 0})
            calls.append({"phase": "status", "fn": "tape_status", "result": "TAPE_OK", "at_end": False, "at_start": False})
            calls.append({"phase": "info", "fn": "tape_get_info", "result": "TAPE_OK", "warm_start_used": False, "total_frames": 64})
            calls.append({"phase": "render", "fn": "tape_render", "result": "TAPE_ERR_UNDERRUN", "rendered": 0})
    calls.append({"phase": "unmount", "fn": "tape_unmount", "result": "TAPE_OK"})
    return case.pre, [], calls
