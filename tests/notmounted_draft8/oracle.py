#!/usr/bin/env python3
"""Independent DRAFT-8 WP-06h not-mounted contract.

Every ordinary call before mount and after unmount is TAPE_ERR_NOT_MOUNTED.
tape_tell leaves *out_frame untouched. tape_mount / tape_format / tape_init
and destination-side tape_dup remain callable. No product imports.
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

ORDINARY = (
    "tape_seek",
    "tape_set_rate",
    "tape_render",
    "tape_service",
    "tape_status",
    "tape_get_info",
    "tape_tell",
    "tape_arm",
    "tape_feed",
    "tape_commit",
    "tape_abort",
    "tape_set_side",
    "tape_reset_side_b",
    "tape_promote",
    "tape_respool",
    "tape_dup",
    "tape_unmount",
)


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
    phase: str  # before | after


def derived_total_chunks() -> int:
    return (NOMINAL_LENGTH_S * SAMPLE_RATE + CF - 1) // CF


def sb() -> bytes:
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
    struct.pack_into("<I", b, 56, 3)
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


def healthy() -> Media:
    s = sb()
    chunks = derived_total_chunks()
    blocks = LBA_CHUNK_BASE + chunks * BLOCKS_PER_CHUNK + 1
    return Media(
        blocks,
        s,
        s,
        (idx(0, [(0, 0, 256)], 10), bytes(SLOT_BYTES), idx(1, [(0, 0, 64)], 20), bytes(SLOT_BYTES)),
    )


def make_cases() -> list[Case]:
    h = healthy()
    return [
        Case("NM-BEFORE", h, "before"),
        Case("NM-AFTER", h, "after"),
        Case("NM-TELL-UNTOUCHED-BEFORE", h, "tell_before"),
        Case("NM-TELL-UNTOUCHED-AFTER", h, "tell_after"),
    ]


def check(case: Case, post: Media, events: list[dict], calls: list[dict]) -> list[str]:
    err: list[str] = []

    def req(cond, msg):
        if not cond:
            err.append(msg)

    req(post.encode() == case.pre.encode(), "not-mounted path wrote media")
    req(not any(e.get("op") in ("write", "flush") for e in events), "not-mounted path issued write/flush")

    if case.phase in ("before", "tell_before"):
        req(not any(c.get("fn") == "tape_mount" and c.get("result") == "TAPE_OK" for c in calls if c.get("phase") == "probe"), "probed after a successful mount")
    if case.phase in ("after", "tell_after"):
        mounts = [c for c in calls if c.get("fn") == "tape_mount"]
        unmounts = [c for c in calls if c.get("fn") == "tape_unmount" and c.get("phase") == "setup"]
        req(bool(mounts) and mounts[0].get("result") == "TAPE_OK", "after-unmount fixture failed to mount")
        req(bool(unmounts) and unmounts[0].get("result") == "TAPE_OK", "after-unmount fixture failed to unmount")

    probes = [c for c in calls if c.get("phase") == "probe"]
    if case.phase in ("before", "after"):
        seen = {c.get("fn") for c in probes}
        for fn in ORDINARY:
            req(fn in seen, f"missing probe {fn}")
        for c in probes:
            req(c.get("result") == "TAPE_ERR_NOT_MOUNTED", f"{c.get('fn')} was not NOT_MOUNTED")
            req(c.get("events_from_call", 0) == 0, f"{c.get('fn')} issued callbacks")
    else:
        tells = [c for c in probes if c.get("fn") == "tape_tell"]
        req(bool(tells) and tells[0].get("result") == "TAPE_ERR_NOT_MOUNTED", "tell result")
        req(tells and tells[0].get("out_frame") == 0x1111111111111111, "tell mutated out_frame")
    return err


SENTINEL = 0x1111111111111111


def _probes() -> list[dict]:
    return [
        {"phase": "probe", "fn": fn, "result": "TAPE_ERR_NOT_MOUNTED", "events_from_call": 0}
        for fn in ORDINARY
    ]


def synth_observation(case: Case):
    calls: list[dict] = []
    if case.phase in ("after", "tell_after"):
        calls.append({"phase": "setup", "fn": "tape_mount", "result": "TAPE_OK", "side": "A"})
        calls.append({"phase": "setup", "fn": "tape_unmount", "result": "TAPE_OK"})
    if case.phase in ("before", "after"):
        calls.extend(_probes())
    else:
        calls.append(
            {
                "phase": "probe",
                "fn": "tape_tell",
                "result": "TAPE_ERR_NOT_MOUNTED",
                "out_frame": SENTINEL,
                "out_frame_before": SENTINEL,
                "events_from_call": 0,
            }
        )
    if case.phase == "before":
        calls.append({"phase": "confirm", "fn": "tape_mount", "result": "TAPE_OK", "side": "A"})
        calls.append({"phase": "confirm", "fn": "tape_unmount", "result": "TAPE_OK"})
    return case.pre, [], calls
