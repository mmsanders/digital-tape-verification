#!/usr/bin/env python3
from __future__ import annotations

import copy

from oracle import check, make_cases, synth_observation


def expect_fail(case, post, ev, calls, label):
    errors = check(case, post, ev, calls)
    if not errors:
        raise AssertionError("mutation escaped: " + label)
    print("CAUGHT", label, "=>", errors[0])


def main():
    cases = {c.id: c for c in make_cases()}
    print("PASS fixture construction:", ", ".join(cases))
    for case in cases.values():
        post, ev, calls = synth_observation(case)
        errors = check(case, post, ev, calls)
        if errors:
            raise AssertionError((case.id, errors))
        print("PASS conforming", case.id)

    arm = cases["W06A-ARM"]
    post, ev, calls = synth_observation(arm)
    expect_fail(arm, post, [{"op": "write", "lba": 8, "count": 1, "phase": "arm"}], calls, "v1.1 arm wrote")
    bad = copy.deepcopy(calls)
    for c in bad:
        if c.get("fn") == "tape_arm":
            c["result"] = "TAPE_OK"
    expect_fail(arm, post, ev, bad, "v1.1 arm allowed")

    info = cases["W06A-INFO"]
    post, ev, calls = synth_observation(info)
    bad = copy.deepcopy(calls)
    for c in bad:
        if c.get("fn") == "tape_get_info":
            c["writable"] = True
    expect_fail(info, post, ev, bad, "torn v1.1 reported writable")
    bad = copy.deepcopy(calls)
    for c in bad:
        if c.get("fn") == "tape_get_info":
            c["needs_repair"] = False
    expect_fail(info, post, ev, bad, "torn v1.1 hid needs_repair")

    feed = cases["W06A-FEED"]
    post, ev, calls = synth_observation(feed)
    bad = copy.deepcopy(calls)
    for c in bad:
        if c.get("fn") == "tape_feed":
            c["result"] = "TAPE_ERR_READ_ONLY"
    expect_fail(feed, post, ev, bad, "idle feed returned READ_ONLY")

    print("PASS all WP-06a writability self-tests")


if __name__ == "__main__":
    main()
