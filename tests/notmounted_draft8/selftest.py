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

    before = cases["NM-BEFORE"]
    post, ev, calls = synth_observation(before)
    bad = copy.deepcopy(calls)
    for c in bad:
        if c.get("phase") == "probe" and c.get("fn") == "tape_tell":
            c["result"] = "TAPE_OK"
    expect_fail(before, post, ev, bad, "tell before mount succeeded")
    expect_fail(before, post, [{"op": "write", "lba": 0, "count": 1, "phase": "probe"}], calls, "not-mounted wrote")

    after = cases["NM-AFTER"]
    post, ev, calls = synth_observation(after)
    bad = copy.deepcopy(calls)
    for c in bad:
        if c.get("phase") == "probe" and c.get("fn") == "tape_seek":
            c["result"] = "TAPE_OK"
    expect_fail(after, post, ev, bad, "seek after unmount succeeded")

    tell = cases["NM-TELL-UNTOUCHED-BEFORE"]
    post, ev, calls = synth_observation(tell)
    bad = copy.deepcopy(calls)
    for c in bad:
        if c.get("fn") == "tape_tell":
            c["out_frame"] = 0
    expect_fail(tell, post, ev, bad, "tell mutated out_frame")

    print("PASS all WP-06h not-mounted self-tests")


if __name__ == "__main__":
    main()
