#!/usr/bin/env python3
from __future__ import annotations

import copy

from oracle import check, fixture_contract_errors, make_cases, synth_observation


def expect_fail(case, post, ev, calls, label):
    errors = check(case, post, ev, calls)
    if not errors:
        raise AssertionError("mutation escaped: " + label)
    print("CAUGHT", label, "=>", errors[0])


def main():
    cases = {c.id: c for c in make_cases()}
    print("PASS fixture construction:", ", ".join(cases))
    for case in cases.values():
        ferr = fixture_contract_errors(case)
        if ferr:
            raise AssertionError((case.id, ferr))
        post, ev, calls = synth_observation(case)
        errors = check(case, post, ev, calls)
        if errors:
            raise AssertionError((case.id, errors))
        print("PASS conforming", case.id)

    empty = cases["PR-EMPTY"]
    post, ev, calls = synth_observation(empty)
    expect_fail(empty, post, [{"op": "write", "lba": 8, "count": 1, "phase": "promote"}], calls, "empty promote wrote")
    bad = copy.deepcopy(calls)
    for c in bad:
        if c.get("fn") == "tape_promote":
            c["result"] = "TAPE_OK"
    expect_fail(empty, post, ev, bad, "empty promote succeeded")

    nothing = cases["PR-NOTHING"]
    post, ev, calls = synth_observation(nothing)
    expect_fail(nothing, post, [{"op": "write", "lba": 0, "count": 1, "phase": "promote"}], calls, "nothing-to-do wrote")

    full = cases["PR-FULL"]
    post, ev, calls = synth_observation(full)
    bad = copy.deepcopy(calls)
    for c in bad:
        if c.get("fn") == "tape_promote":
            c["result"] = "TAPE_OK"
    expect_fail(full, post, ev, bad, "full promote allowed")

    done = cases["PR-ADOPT-COMPLETE"]
    post, ev, calls = synth_observation(done)
    expect_fail(done, post, [e for e in ev if e.get("lba") != 2048], calls, "phase 2 skipped [0,len)")

    dec = cases["PR-ADOPT-DECLINE"]
    post, ev, calls = synth_observation(dec)
    bad_ev = ev + [{"op": "write", "lba": 2048, "count": 1, "phase": "promote"}]
    expect_fail(dec, post, bad_ev, calls, "decline wrote chunk 0")

    print("PASS all promote classification/complete self-tests")


if __name__ == "__main__":
    main()
