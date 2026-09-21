#!/usr/bin/env python3
"""WP-09 extra families that do not depend on crash or continuation oracles.

- multi-chunk overwrite
- splice onto empty Side B
- empty commit in overdub and splice
- successful stage-1 clearing write on arm, then ordinary record
"""
from __future__ import annotations

import struct
import zlib

from oracle import (
    BLOCK,
    CF,
    LBA_B1,
    LBA_CHUNK_BASE,
    Media,
    base_fixture,
    cartridge_sequence,
    derived_total_chunks,
    free_next,
    idx,
    invalid_slot,
    live_slot,
    parse_entries,
    sb,
    select_sb,
    semantic_valid,
)

BLOCKS_PER_CHUNK = 1024


def _writes(events, phase=None):
    return [e for e in events if e.get("op") == "write" and (phase is None or e.get("phase") == phase)]


def _chunk_lo(chunk: int) -> int:
    return LBA_CHUNK_BASE + chunk * BLOCKS_PER_CHUNK


def empty_b_fixture() -> Media:
    pre = base_fixture()
    slots = list(pre.slots)
    slots[2] = idx(1, [], 20)
    return Media(pre.blocks, pre.primary, pre.mirror, tuple(slots))


def staged_fixture() -> Media:
    chunks = derived_total_chunks(60)
    staged = bytearray(sb(generation=7, high=3, chunks=chunks, stage=1))
    struct.pack_into("<I", staged, 128, 12)
    struct.pack_into("<I", staged, 508, zlib.crc32(staged[:508]))
    staged = bytes(staged)
    pre = base_fixture()
    return Media(pre.blocks, staged, staged, pre.slots)


def extra_cases():
    pre = base_fixture()
    empty_b = empty_b_fixture()
    staged = staged_fixture()
    feed_n = CF + 64
    return [
        ("WP09-OW-MULTICHUNK", pre, "overwrite", "B", 0, feed_n, "happy"),
        ("WP09-SP-EMPTY-B", empty_b, "splice", "B", 0, 64, "happy"),
        ("WP09-EMPTY-OD", pre, "overdub", "B", 128, 0, "empty"),
        ("WP09-EMPTY-SP", pre, "splice", "B", 128, 0, "empty"),
        ("WP09-STAGE-CLEAR", staged, "overwrite", "B", 128, 64, "stage"),
    ]


def fixture_ok(cid, pre):
    err = []
    if cid == "WP09-SP-EMPTY-B":
        if parse_entries(pre.slots[2]) != []:
            err.append("empty-B fixture not empty")
        if live_slot(pre, 1) != 2:
            err.append("empty-B lost live B")
    if cid == "WP09-STAGE-CLEAR":
        if struct.unpack_from("<I", select_sb(pre), 124)[0] != 1:
            err.append("stage-clear fixture promote_stage is not 1")
        if struct.unpack_from("<I", select_sb(pre), 56)[0] != 3:
            err.append("stage-clear fixture H drift")
    if cid == "WP09-OW-MULTICHUNK":
        if free_next(pre) != 3:
            err.append("multi-chunk fixture free_next drift")
    return err


def cleared_sb(pre: Media) -> bytes:
    b = bytearray(select_sb(pre))
    gen = struct.unpack_from("<I", b, 12)[0]
    struct.pack_into("<I", b, 12, gen + 1)
    struct.pack_into("<I", b, 124, 0)
    struct.pack_into("<I", b, 128, 0)
    struct.pack_into("<I", b, 508, zlib.crc32(b[:508]))
    return bytes(b)


def check_extra(cid, pre, mode, mount_side, seek, feed, kind, post, events, calls):
    err = []

    def req(cond, msg):
        if not cond:
            err.append(msg)

    mounts = [c for c in calls if c.get("fn") == "tape_mount"]
    req(bool(mounts) and mounts[0].get("result") == "TAPE_OK", "mount failed")
    arms = [c for c in calls if c.get("fn") == "tape_arm"]
    req(bool(arms) and arms[0].get("result") == "TAPE_OK" and arms[0].get("mode") == mode, "arm mismatch")

    if kind == "empty":
        req(not _writes(events), "empty commit wrote")
        req(post.encode() == pre.encode(), "empty commit changed media")
        commits = [c for c in calls if c.get("fn") == "tape_commit"]
        req(bool(commits) and commits[0].get("result") == "TAPE_OK", "empty commit not OK")
        return err

    feeds = [c for c in calls if c.get("fn") == "tape_feed"]
    req(bool(feeds) and feeds[0].get("accepted") == feed and feeds[0].get("result") == "TAPE_OK", "feed mismatch")
    req(feeds[0].get("events_from_call", 0) == 0, "feed issued I/O")
    commits = [c for c in calls if c.get("fn") == "tape_commit"]
    req(bool(commits) and commits[0].get("result") == "TAPE_OK", "commit not OK")
    req(structural_ok(post), "post B1 invalid")
    req(structural_sequence(post) == 701, "sequence not 701")
    req(live_slot(post, 1) == 3, "B1 not live")
    req(post.slots[0] == pre.slots[0] and post.slots[2] == pre.slots[2], "source slots changed")

    if cid == "WP09-OW-MULTICHUNK":
        req(parse_entries(post.slots[3]) == [(3, 0, feed)], "multi-chunk index shape")
        req(free_next(post) == 5, "multi-chunk free_next")
        req(any(e.get("lba", -1) >= _chunk_lo(3) and e.get("lba", -1) < _chunk_lo(4) for e in _writes(events, "service")), "missing chunk-3 write")
        req(any(e.get("lba", -1) >= _chunk_lo(4) and e.get("lba", -1) < _chunk_lo(5) for e in _writes(events, "service")), "missing chunk-4 write")
        req(post.primary == pre.primary, "ordinary multi-chunk wrote superblock")

    if cid == "WP09-SP-EMPTY-B":
        req(parse_entries(post.slots[3]) == [(3, 0, 64)], "empty-B splice shape")
        req(struct.unpack_from("<Q", post.slots[3], 20)[0] == 64, "empty-B total")
        req(post.primary == pre.primary, "empty-B splice wrote superblock")

    if cid == "WP09-STAGE-CLEAR":
        req(struct.unpack_from("<I", post.primary, 124)[0] == 0, "stage not cleared")
        req(struct.unpack_from("<I", post.primary, 128)[0] == 0, "staging chunk not cleared")
        req(struct.unpack_from("<I", post.primary, 12)[0] == 8, "generation not +1")
        req(struct.unpack_from("<I", post.primary, 56)[0] == 3, "H moved during stage clear")
        req(post.primary == post.mirror, "cleared copies diverged")
        sb_writes = [e for e in _writes(events, "arm") if e.get("lba") in (0, pre.blocks - 1)]
        req(len(sb_writes) >= 2, "stage-clear missing partner/candidate writes")
        if len(sb_writes) >= 2:
            req(sb_writes[0]["lba"] == pre.blocks - 1, "stage-clear did not write partner (mirror) first")
            req(sb_writes[1]["lba"] == 0, "stage-clear did not write candidate (primary) last")
        req(parse_entries(post.slots[3]) == [(0, 0, 128), (3, 0, 64)], "stage-clear record shape")
        req(all(e.get("lba") in (0, pre.blocks - 1) for e in _writes(events, "arm")), "arm wrote a non-superblock LBA")
    return err


def structural_sequence(post: Media):
    from oracle import structural_sequence as ss
    return ss(post.slots[3])


def structural_ok(post: Media):
    return semantic_valid(post.slots[3], 1, select_sb(post))


def synth_extra(cid, pre, mode, mount_side, seek, feed, kind):
    calls = [{"phase": "mount", "fn": "tape_mount", "result": "TAPE_OK", "side": mount_side}]
    if cid != "WP09-SP-EMPTY-B" or seek is not None:
        calls.append({"phase": "seek", "fn": "tape_seek", "result": "TAPE_OK", "frame": seek})
    calls.append({"phase": "arm", "fn": "tape_arm", "result": "TAPE_OK", "mode": mode})
    events = []
    post = pre
    if kind == "empty":
        calls.append({"phase": "commit", "fn": "tape_commit", "result": "TAPE_OK"})
    else:
        calls.append(
            {
                "phase": "feed",
                "fn": "tape_feed",
                "result": "TAPE_OK",
                "requested": feed,
                "accepted": feed,
                "events_from_call": 0,
            }
        )
        calls.append({"phase": "service", "fn": "tape_service", "result": "TAPE_OK", "more_work": False})
        calls.append({"phase": "commit", "fn": "tape_commit", "result": "TAPE_OK"})
        if cid == "WP09-OW-MULTICHUNK":
            slots = list(pre.slots)
            slots[3] = idx(1, [(3, 0, feed)], 701)
            post = Media(pre.blocks, pre.primary, pre.mirror, tuple(slots))
            events = [
                {"phase": "service", "op": "write", "lba": _chunk_lo(3), "count": 1},
                {"phase": "service", "op": "flush"},
                {"phase": "service", "op": "write", "lba": _chunk_lo(4), "count": 1},
                {"phase": "service", "op": "flush"},
                {"phase": "commit", "op": "write", "lba": LBA_B1 + 1, "count": 1},
                {"phase": "commit", "op": "flush"},
                {"phase": "commit", "op": "write", "lba": LBA_B1, "count": 1},
                {"phase": "commit", "op": "flush"},
            ]
        elif cid == "WP09-SP-EMPTY-B":
            slots = list(pre.slots)
            slots[3] = idx(1, [(3, 0, 64)], 701)
            post = Media(pre.blocks, pre.primary, pre.mirror, tuple(slots))
            events = [
                {"phase": "service", "op": "write", "lba": _chunk_lo(3), "count": 1},
                {"phase": "service", "op": "flush"},
                {"phase": "commit", "op": "write", "lba": LBA_B1 + 1, "count": 1},
                {"phase": "commit", "op": "flush"},
                {"phase": "commit", "op": "write", "lba": LBA_B1, "count": 1},
                {"phase": "commit", "op": "flush"},
            ]
        elif cid == "WP09-STAGE-CLEAR":
            new_sb = cleared_sb(pre)
            slots = list(pre.slots)
            slots[3] = idx(1, [(0, 0, 128), (3, 0, 64)], 701)
            post = Media(pre.blocks, new_sb, new_sb, tuple(slots))
            events = [
                {"phase": "arm", "op": "write", "lba": pre.blocks - 1, "count": 1},
                {"phase": "arm", "op": "flush"},
                {"phase": "arm", "op": "write", "lba": 0, "count": 1},
                {"phase": "arm", "op": "flush"},
                {"phase": "service", "op": "write", "lba": _chunk_lo(3), "count": 1},
                {"phase": "service", "op": "flush"},
                {"phase": "commit", "op": "write", "lba": LBA_B1 + 1, "count": 1},
                {"phase": "commit", "op": "flush"},
                {"phase": "commit", "op": "write", "lba": LBA_B1, "count": 1},
                {"phase": "commit", "op": "flush"},
            ]
    calls.append({"phase": "unmount", "fn": "tape_unmount", "result": "TAPE_OK"})
    return post, events, calls
