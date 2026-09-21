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

    sw = cases["SS-A-TO-B"]
    post, ev, calls = synth_observation(sw)
    bad = copy.deepcopy(calls)
    for c in bad:
        if c.get("fn") == "tape_tell":
            c["frame"] = 10
    expect_fail(sw, post, ev, bad, "set_side kept old position")

    deg = cases["SS-DEGRADED-B"]
    post, ev, calls = synth_observation(deg)
    bad = copy.deepcopy(calls)
    for c in bad:
        if c.get("fn") == "tape_set_side":
            c["result"] = "TAPE_OK"
    expect_fail(deg, post, ev, bad, "degraded set_side B allowed")

    armed = cases["SS-ARMED-BUSY"]
    post, ev, calls = synth_observation(armed)
    bad = copy.deepcopy(calls)
    for c in bad:
        if c.get("fn") == "tape_set_side":
            c["result"] = "TAPE_OK"
    expect_fail(armed, post, ev, bad, "armed set_side allowed")

    warm = cases["WARM-DATA-NULL"]
    post, ev, calls = synth_observation(warm)
    bad = copy.deepcopy(calls)
    for c in bad:
        if c.get("fn") in ("tape_mount", "tape_get_info"):
            c["warm_start_used"] = True
    expect_fail(warm, post, ev, bad, "null-data warm used")

    print("PASS all transport extra self-tests")


if __name__ == "__main__":
    main()
