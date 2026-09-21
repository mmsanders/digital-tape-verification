#!/usr/bin/env python3
"""Independent DRAFT-8 WP-36 source-slot oracle. write callback is NULL."""
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
MUTATORS = (
    "tape_arm",
    "tape_reset_side_b",
    "tape_promote",
    "tape_respool",
    "tape_feed",
    "tape_commit",
    "tape_format",
)


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
    mount_side: str
    writable_expected: bool


def derived_total_chunks() -> int:
    return (NOMINAL_LENGTH_S * SAMPLE_RATE + CF - 1) // CF


def sb(*, high=3, minor=0) -> bytes:
    chunks = derived_total_chunks()
    blocks = LBA_CHUNK_BASE + chunks * BLOCKS_PER_CHUNK + 1
    b = bytearray(BLOCK)
    b[:8] = b"TAPEFS\0\x01"
    struct.pack_into("<H", b, 8, 1)
    struct.pack_into("<H", b, 10, minor)
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


def cartridge() -> Media:
    s = sb()
    chunks = derived_total_chunks()
    blocks = LBA_CHUNK_BASE + chunks * BLOCKS_PER_CHUNK + 1
    return Media(
        blocks,
        s,
        s,
        (
            idx(0, [(0, 0, 128)], 10),
            invalid_slot(),
            idx(1, [(0, 0, 128)], 20),
            invalid_slot(),
        ),
    )


def make_cases() -> list[Case]:
    pre = cartridge()
    return [
        Case("WP36-SRC-A", pre, "A", False),
        Case("WP36-SRC-B", pre, "B", False),
        Case("WP36-SRC-MUTATORS", pre, "B", False),
    ]


def check(case: Case, post: Media, events: list[dict], calls: list[dict]) -> list[str]:
    err = []

    def req(cond, msg):
        if not cond:
            err.append(msg)

    req(post.encode() == case.pre.encode(), "source-slot media mutated")
    writes = [e for e in events if e.get("op") == "write"]
    req(not writes, "source-slot device received a write")
    infos = [c for c in calls if c.get("fn") == "tape_get_info"]
    req(bool(infos) and infos[0].get("writable") is False, "writable was not false")
    if case.id == "WP36-SRC-MUTATORS":
        for name in ("tape_arm", "tape_reset_side_b", "tape_promote", "tape_respool"):
            hits = [c for c in calls if c.get("fn") == name]
            req(bool(hits) and hits[0].get("result") == "TAPE_ERR_READ_ONLY", name + " not READ_ONLY")
    else:
        mounts = [c for c in calls if c.get("fn") == "tape_mount"]
        req(bool(mounts) and mounts[0].get("result") == "TAPE_OK", "source-slot mount failed")
        req(all(c.get("result") == "TAPE_OK" for c in calls if c.get("fn") in ("tape_seek", "tape_set_rate", "tape_render")), "playback path failed")
    return err


def synth_calls(case: Case) -> list[dict]:
    calls = [
        {"phase": "mount", "fn": "tape_mount", "result": "TAPE_OK", "side": case.mount_side},
        {"phase": "info", "fn": "tape_get_info", "result": "TAPE_OK", "writable": False},
    ]
    if case.id == "WP36-SRC-MUTATORS":
        calls.extend(
            [
                {"phase": "arm", "fn": "tape_arm", "result": "TAPE_ERR_READ_ONLY", "mode": "overwrite"},
                {"phase": "reset_b", "fn": "tape_reset_side_b", "result": "TAPE_ERR_READ_ONLY"},
                {"phase": "promote", "fn": "tape_promote", "result": "TAPE_ERR_READ_ONLY", "more_work": False},
                {"phase": "respool", "fn": "tape_respool", "result": "TAPE_ERR_READ_ONLY", "more_work": False},
            ]
        )
    else:
        calls.extend(
            [
                {"phase": "seek", "fn": "tape_seek", "result": "TAPE_OK", "frame": 0},
                {"phase": "rate", "fn": "tape_set_rate", "result": "TAPE_OK", "rate_q16_16": 65536},
                {"phase": "render", "fn": "tape_render", "result": "TAPE_OK", "rendered": 8},
                {"phase": "service", "fn": "tape_service", "result": "TAPE_OK", "more_work": False},
            ]
        )
    calls.append({"phase": "unmount", "fn": "tape_unmount", "result": "TAPE_OK"})
    return calls


def synth_observation(case: Case):
    return case.pre, [], synth_calls(case)
