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

    ro = cases["FMT-RO"]
    post, ev, calls = synth_observation(ro)
    expect_fail(ro, post, [{"op": "write", "lba": 0, "count": 1, "phase": "format"}], calls, "format RO wrote")

    g0 = cases["FMT-GEOM-0"]
    post, ev, calls = synth_observation(g0)
    expect_fail(g0, post, [{"op": "read", "lba": 0, "count": 1, "phase": "format"}], calls, "geom-0 issued callback")

    alias = cases["DUP-ALIAS"]
    post, ev, calls = synth_observation(alias)
    bad = copy.deepcopy(calls)
    for c in bad:
        if c.get("fn") == "tape_dup":
            c["result"] = "TAPE_OK"
    expect_fail(alias, post, ev, bad, "alias dup allowed")

    small = cases["DUP-TOO-SMALL"]
    post, ev, calls = synth_observation(small)
    bad = copy.deepcopy(calls)
    for c in bad:
        if c.get("fn") == "tape_dup":
            c["result"] = "TAPE_OK"
    expect_fail(small, post, ev, bad, "too-small dup allowed")

    empty = cases["PROMOTE-EMPTY"]
    post, ev, calls = synth_observation(empty)
    expect_fail(empty, post, [{"op": "write", "lba": 8, "count": 1, "phase": "promote"}], calls, "empty promote wrote")
    bad = copy.deepcopy(calls)
    for c in bad:
        if c.get("fn") == "tape_promote":
            c["result"] = "TAPE_OK"
            c["more_work"] = False
    expect_fail(empty, post, ev, bad, "empty promote succeeded")

    print("PASS all format/dup/empty-promote refusal self-tests")


if __name__ == "__main__":
    main()
