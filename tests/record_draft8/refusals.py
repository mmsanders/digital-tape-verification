#!/usr/bin/env python3
"""Independent DRAFT-8 WP-09 refusal / abort rows.

Authored from Engine API §7 / §10 and TapeFS §4.5 / §8 / §9.1.
Does not inspect product implementation. Does not depend on acceptance
of the eight happy-path families.
"""
from __future__ import annotations

import struct

from oracle import (
    Media,
    base_fixture,
    cartridge_sequence,
    derived_total_chunks,
    free_next,
    idx,
    live_slot,
    parse_entries,
    sb,
    select_sb,
    semantic_valid,
)

TAPE_MAX_ENTRIES = 4096
SEQ_CAP = 0xFFFFFFFD


def _writes(events):
    return [e for e in events if e.get("op") == "write"]


def _flushes(events):
    return [e for e in events if e.get("op") == "flush"]


def refusal_cases():
    """Return (id, pre, mode, mount_side, expect) tuples."""
    pre = base_fixture()
    chunks = derived_total_chunks(60)

    slots = list(pre.slots)
    slots[1] = idx(1, [(1, 0, 64)], SEQ_CAP)
    exhausted = Media(pre.blocks, pre.primary, pre.mirror, tuple(slots))

    full_slots = list(pre.slots)
    full_slots[2] = idx(1, [(0, 0, 256), (chunks - 1, 0, 128)], 20)
    full = Media(pre.blocks, pre.primary, pre.mirror, tuple(full_slots))

    packed_entries = [(0, i, 1) for i in range(TAPE_MAX_ENTRIES)]
    packed_slots = list(pre.slots)
    packed_slots[2] = idx(1, packed_entries, 20)
    packed = Media(pre.blocks, pre.primary, pre.mirror, tuple(packed_slots))

    staged = sb(generation=7, high=3, chunks=chunks, stage=1)
    staged_slots = list(pre.slots)
    staged_slots[1] = idx(1, [(1, 0, 64)], SEQ_CAP)
    staged_exh = Media(pre.blocks, staged, staged, tuple(staged_slots))

    return [
        ("WP09-RO-SIDE-A", pre, "overwrite", "A", "TAPE_ERR_READ_ONLY"),
        ("WP09-SEQ-EXHAUSTED", exhausted, "overwrite", "B", "TAPE_ERR_SEQUENCE_EXHAUSTED"),
        ("WP09-INDEX-FULL", packed, "splice", "B", "TAPE_ERR_INDEX_FULL"),
        ("WP09-CART-FULL", full, "overwrite", "B", "TAPE_ERR_CARTRIDGE_FULL"),
        ("WP09-ABORT-DISARM", pre, "overwrite", "B", "TAPE_OK"),
        ("WP09-STAGE-REFUSE", staged_exh, "overwrite", "B", "TAPE_ERR_SEQUENCE_EXHAUSTED"),
    ]


def fixture_ok(cid, pre):
    errors = []
    if cid == "WP09-SEQ-EXHAUSTED":
        if cartridge_sequence(pre) != SEQ_CAP:
            errors.append("exhaustion fixture sequence is not 0xFFFFFFFD")
        if live_slot(pre, 1) != 2:
            errors.append("exhaustion fixture lost live B")
    if cid == "WP09-INDEX-FULL":
        if live_slot(pre, 1) != 2:
            errors.append("index-full fixture lost live B")
        if len(parse_entries(pre.slots[2])) != TAPE_MAX_ENTRIES:
            errors.append("index-full fixture is not packed to TAPE_MAX_ENTRIES")
        if not semantic_valid(pre.slots[2], 1, select_sb(pre)):
            errors.append("index-full fixture live B is not semantically valid")
    if cid == "WP09-CART-FULL":
        chunks = derived_total_chunks(60)
        if free_next(pre) != chunks:
            errors.append(f"full fixture free_next={free_next(pre)} != total_chunks={chunks}")
        if live_slot(pre, 1) != 2:
            errors.append("full fixture lost live B")
    if cid == "WP09-STAGE-REFUSE":
        if struct.unpack_from("<I", select_sb(pre), 124)[0] != 1:
            errors.append("stage-refuse fixture promote_stage is not 1")
        if cartridge_sequence(pre) != SEQ_CAP:
            errors.append("stage-refuse fixture sequence is not exhausted")
    return errors


def check_refusal(cid, pre, mode, mount_side, expect, post, events, calls):
    err = []

    def req(cond, msg):
        if not cond:
            err.append(msg)

    req(post.encode() == pre.encode(), "refusal or abort wrote media bytes")
    req(not _writes(events), "refusal or abort issued a write")
    req(not _flushes(events), "refusal or abort issued a flush")
    req(post.primary == pre.primary and post.mirror == pre.mirror, "superblock bytes changed")
    req(post.slots == pre.slots, "index slot bytes changed")

    mounts = [c for c in calls if c.get("fn") == "tape_mount"]
    req(bool(mounts) and mounts[0].get("result") == "TAPE_OK", "mount did not succeed")
    req(mounts[0].get("side") == mount_side, "mounted the wrong side")

    if cid == "WP09-RO-SIDE-A":
        arms = [c for c in calls if c.get("fn") == "tape_arm"]
        req(bool(arms) and arms[0].get("result") == expect and arms[0].get("mode") == mode, "Side-A arm was not READ_ONLY")
        req(not any(c.get("fn") == "tape_feed" for c in calls), "Side-A refusal fed frames")
    elif cid in ("WP09-SEQ-EXHAUSTED", "WP09-INDEX-FULL", "WP09-STAGE-REFUSE"):
        arms = [c for c in calls if c.get("fn") == "tape_arm"]
        req(bool(arms) and arms[0].get("result") == expect and arms[0].get("mode") == mode, "arm refusal mismatch")
        req(not any(c.get("fn") == "tape_feed" for c in calls), "refused arm still fed")
        if cid == "WP09-STAGE-REFUSE":
            req(struct.unpack_from("<I", post.primary, 124)[0] == 1, "stage-clearing write ran on a refusal")
    elif cid == "WP09-CART-FULL":
        arms = [c for c in calls if c.get("fn") == "tape_arm"]
        req(bool(arms) and arms[0].get("result") == "TAPE_OK" and arms[0].get("mode") == mode, "full-cartridge arm should succeed")
        feeds = [c for c in calls if c.get("fn") == "tape_feed"]
        req(
            bool(feeds)
            and feeds[0].get("result") == expect
            and feeds[0].get("accepted") == 0
            and feeds[0].get("events_from_call", 0) == 0,
            "cartridge-full short-accept missing",
        )
        aborts = [c for c in calls if c.get("fn") == "tape_abort"]
        req(bool(aborts) and aborts[0].get("result") == "TAPE_OK", "full-cartridge abort missing")
    elif cid == "WP09-ABORT-DISARM":
        arms = [c for c in calls if c.get("fn") == "tape_arm"]
        req(bool(arms) and arms[0].get("result") == "TAPE_OK", "abort case arm failed")
        aborts = [c for c in calls if c.get("fn") == "tape_abort"]
        req(bool(aborts) and aborts[0].get("result") == "TAPE_OK", "abort was not TAPE_OK")
        req(not any(c.get("fn") == "tape_commit" for c in calls), "abort case committed")
    return err


def synth_refusal(cid, pre, mode, mount_side, expect):
    calls = [{"phase": "mount", "fn": "tape_mount", "result": "TAPE_OK", "side": mount_side}]
    if cid == "WP09-RO-SIDE-A":
        calls.append({"phase": "arm", "fn": "tape_arm", "result": expect, "mode": mode})
    elif cid in ("WP09-SEQ-EXHAUSTED", "WP09-INDEX-FULL", "WP09-STAGE-REFUSE"):
        calls.append({"phase": "seek", "fn": "tape_seek", "result": "TAPE_OK", "frame": 0})
        calls.append({"phase": "arm", "fn": "tape_arm", "result": expect, "mode": mode})
    elif cid == "WP09-CART-FULL":
        calls.append({"phase": "seek", "fn": "tape_seek", "result": "TAPE_OK", "frame": 0})
        calls.append({"phase": "arm", "fn": "tape_arm", "result": "TAPE_OK", "mode": mode})
        calls.append(
            {
                "phase": "feed",
                "fn": "tape_feed",
                "result": expect,
                "requested": 64,
                "accepted": 0,
                "events_from_call": 0,
            }
        )
        calls.append({"phase": "abort", "fn": "tape_abort", "result": "TAPE_OK"})
    elif cid == "WP09-ABORT-DISARM":
        calls.append({"phase": "seek", "fn": "tape_seek", "result": "TAPE_OK", "frame": 128})
        calls.append({"phase": "arm", "fn": "tape_arm", "result": "TAPE_OK", "mode": mode})
        calls.append({"phase": "abort", "fn": "tape_abort", "result": "TAPE_OK"})
    calls.append({"phase": "unmount", "fn": "tape_unmount", "result": "TAPE_OK"})
    return pre, [], calls
