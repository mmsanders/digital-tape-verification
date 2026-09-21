#!/usr/bin/env python3
"""Negative controls for the WP-09 record oracle."""
from __future__ import annotations

import copy

from oracle import (
    Case,
    Media,
    check,
    fixture_contract_errors,
    idx,
    invalid_slot,
    make_cases,
    overdub_saturate,
    synth_observation,
)


def expect_fail(case, post, ev, calls, label):
    errors = check(case, post, ev, calls)
    if not errors:
        raise AssertionError("mutation escaped: " + label)
    print("CAUGHT", label, "=>", errors[0])


def main():
    cases = {c.id: c for c in make_cases()}
    print("PASS fixture construction:", ", ".join(cases))

    for existing, incoming, want in (
        (32767, 1, 32767),
        (-32768, -1, -32768),
        (20000, 20000, 32767),
        (-20000, -20000, -32768),
        (100, -40, 60),
        (32767, 32767, 32767),
        (-32768, -32768, -32768),
    ):
        got = overdub_saturate(existing, incoming)
        if got != want:
            raise AssertionError(("saturation", existing, incoming, got, want))
    print("PASS overdub saturation clamp")

    for case in cases.values():
        post, ev, calls = synth_observation(case)
        errors = check(case, post, ev, calls)
        if errors:
            raise AssertionError((case.id, errors))
        print("PASS conforming", case.id)

    ow = cases["WP09-OW-MID"]
    post, ev, calls = synth_observation(ow)
    bad_slots = list(post.slots)
    bad_slots[3] = idx(1, [(0, 0, 256)], 701)
    expect_fail(ow, Media(post.blocks, post.primary, post.mirror, tuple(bad_slots)), ev, calls, "overwrite kept tail")

    od = cases["WP09-OD-MID"]
    post, ev, calls = synth_observation(od)
    bad_slots = list(post.slots)
    bad_slots[3] = idx(1, [(0, 0, 128), (3, 0, 64)], 701)
    expect_fail(od, Media(post.blocks, post.primary, post.mirror, tuple(bad_slots)), ev, calls, "overdub truncated timeline")

    sp = cases["WP09-SP-MID"]
    post, ev, calls = synth_observation(sp)
    bad_slots = list(post.slots)
    bad_slots[3] = idx(1, [(0, 0, 128), (3, 0, 64)], 701)
    expect_fail(sp, Media(post.blocks, post.primary, post.mirror, tuple(bad_slots)), ev, calls, "splice dropped suffix")

    empty = cases["WP09-EMPTY-COMMIT"]
    post, ev, calls = synth_observation(empty)
    ev = [{"phase": "commit", "op": "write", "lba": 264, "count": 1}]
    expect_fail(empty, post, ev, calls, "empty commit wrote")

    busy = cases["WP09-ARMED-BUSY"]
    post, ev, calls = synth_observation(busy)
    mutated = copy.deepcopy(calls)
    for item in mutated:
        if item.get("fn") == "tape_seek" and item.get("phase") == "armed":
            item["result"] = "TAPE_OK"
    expect_fail(busy, post, ev, mutated, "armed seek allowed")

    rec = cases["WP09-SP-END"]
    post, ev, calls = synth_observation(rec)
    bad_slots = list(post.slots)
    bad_slots[3] = idx(1, rec.expected_entries, 21)
    expect_fail(rec, Media(post.blocks, post.primary, post.mirror, tuple(bad_slots)), ev, calls, "live-only sequence base")

    ev2 = [e for e in ev if not (e.get("phase") == "commit" and e.get("op") == "flush")]
    expect_fail(rec, post, ev2, calls, "commit flush count")

    ev3 = list(ev)
    ev3[0] = {"phase": "service", "op": "write", "lba": 8, "count": 1}
    expect_fail(rec, post, ev3, calls, "service write below H")

    print("PASS all WP-09 record self-tests")


if __name__ == "__main__":
    main()
