#!/usr/bin/env python3
"""Independent DRAFT-8 WP-06a effective-writability mutator oracle.

Mount coverage already admits v1.1 as writable=false. This package exercises
the remaining WP-06a rows: mutators on a *writable device* carrying valid
v1.1 media must be READ_ONLY; feed/commit must be BUSY; repair is skipped
and needs_repair stays true; zero writes. No product implementation imports.
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
    side: str
    kind: str
    expect: str


def derived_total_chunks() -> int:
    return (NOMINAL_LENGTH_S * SAMPLE_RATE + CF - 1) // CF


def sb(*, generation=7, minor=1, high=3) -> bytes:
    chunks = derived_total_chunks()
    blocks = LBA_CHUNK_BASE + chunks * BLOCKS_PER_CHUNK + 1
    b = bytearray(BLOCK)
    b[:8] = b"TAPEFS\0\x01"
    struct.pack_into("<H", b, 8, 1)
    struct.pack_into("<H", b, 10, minor)
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


def v11_media(*, torn_partner: bool) -> Media:
    chunks = derived_total_chunks()
    blocks = LBA_CHUNK_BASE + chunks * BLOCKS_PER_CHUNK + 1
    primary = sb(generation=7, minor=1)
    if torn_partner:
        mirror = sb(generation=6, minor=1)
        # Corrupt the partner CRC so it is structurally invalid at a lower generation.
        mirror = bytearray(mirror)
        mirror[508:512] = b"\x00\x00\x00\x00"
        mirror = bytes(mirror)
    else:
        mirror = primary
    slots = (
        idx(0, [(0, 0, 256)], 10),
        invalid_slot(),
        idx(1, [(0, 0, 64)], 20),
        invalid_slot(),
    )
    return Media(blocks, primary, mirror, slots)


def make_cases() -> list[Case]:
    healthy = v11_media(torn_partner=False)
    torn = v11_media(torn_partner=True)
    return [
        Case("W06A-INFO", torn, "A", "info", "TAPE_OK"),
        Case("W06A-ARM", torn, "B", "arm", "TAPE_ERR_READ_ONLY"),
        Case("W06A-RESET-B", torn, "A", "reset_b", "TAPE_ERR_READ_ONLY"),
        Case("W06A-PROMOTE", torn, "A", "promote", "TAPE_ERR_READ_ONLY"),
        Case("W06A-RESPOOL", torn, "B", "respool", "TAPE_ERR_READ_ONLY"),
        Case("W06A-FEED", torn, "B", "feed", "TAPE_ERR_BUSY"),
        Case("W06A-COMMIT", torn, "B", "commit", "TAPE_ERR_BUSY"),
        Case("W06A-HEALTHY-ARM", healthy, "B", "arm", "TAPE_ERR_READ_ONLY"),
    ]


def check(case: Case, post: Media, events: list[dict], calls: list[dict]) -> list[str]:
    err: list[str] = []

    def req(cond, msg):
        if not cond:
            err.append(msg)

    req(post.encode() == case.pre.encode(), "v1.1 mutator wrote media")
    req(not any(e.get("op") in ("write", "flush") for e in events), "v1.1 issued a write or flush")
    mounts = [c for c in calls if c.get("fn") == "tape_mount"]
    req(bool(mounts) and mounts[0].get("result") == "TAPE_OK", "v1.1 mount failed")
    infos = [c for c in calls if c.get("fn") == "tape_get_info"]
    req(bool(infos), "missing tape_get_info")
    if infos:
        req(infos[0].get("writable") is False, "info.writable not false")
        req(infos[0].get("version_minor") == 1, "version_minor not 1")
        if case.pre.primary != case.pre.mirror:
            req(infos[0].get("needs_repair") is True, "torn v1.1 partner did not report needs_repair")
        else:
            req(infos[0].get("needs_repair") is False, "identical v1.1 pair reported needs_repair")

    fn = {
        "info": None,
        "arm": "tape_arm",
        "reset_b": "tape_reset_side_b",
        "promote": "tape_promote",
        "respool": "tape_respool",
        "feed": "tape_feed",
        "commit": "tape_commit",
    }[case.kind]
    if fn:
        hits = [c for c in calls if c.get("fn") == fn]
        req(bool(hits) and hits[0].get("result") == case.expect, f"{fn} result")
        if case.kind in ("promote", "respool") and hits:
            req(hits[0].get("more_work") is False, f"{fn} left more_work true")
        if case.kind == "feed" and hits:
            req(hits[0].get("accepted", 0) == 0, "idle feed accepted frames")
    return err


def synth_observation(case: Case):
    calls = [
        {
            "phase": "mount",
            "fn": "tape_mount",
            "result": "TAPE_OK",
            "side": case.side,
            "writable_device": True,
        },
        {
            "phase": "info",
            "fn": "tape_get_info",
            "result": "TAPE_OK",
            "writable": False,
            "version_minor": 1,
            "needs_repair": case.pre.primary != case.pre.mirror,
        },
    ]
    if case.kind == "arm":
        calls.append({"phase": "arm", "fn": "tape_arm", "result": case.expect, "mode": "overwrite"})
    elif case.kind == "reset_b":
        calls.append({"phase": "reset_b", "fn": "tape_reset_side_b", "result": case.expect})
    elif case.kind == "promote":
        calls.append({"phase": "promote", "fn": "tape_promote", "result": case.expect, "more_work": False, "block_budget": 64})
    elif case.kind == "respool":
        calls.append({"phase": "respool", "fn": "tape_respool", "result": case.expect, "more_work": False, "block_budget": 64})
    elif case.kind == "feed":
        calls.append({"phase": "feed", "fn": "tape_feed", "result": case.expect, "accepted": 0, "frames": 64})
    elif case.kind == "commit":
        calls.append({"phase": "commit", "fn": "tape_commit", "result": case.expect})
    calls.append({"phase": "unmount", "fn": "tape_unmount", "result": "TAPE_OK"})
    return case.pre, [], calls
