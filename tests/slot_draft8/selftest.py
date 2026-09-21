#!/usr/bin/env python3
from __future__ import annotations

from oracle import check, make_cases, synth_observation


def expect_fail(case, post, ev, calls, label):
    errors = check(case, post, ev, calls)
    if not errors:
        raise AssertionError("mutation escaped: " + label)
    print("CAUGHT", label, "=>", errors[0])


def main():
    for case in make_cases():
        post, ev, calls = synth_observation(case)
        errors = check(case, post, ev, calls)
        if errors:
            raise AssertionError((case.id, errors))
        print("PASS conforming", case.id)

    src = next(c for c in make_cases() if c.id == "WP36-SRC-MUTATORS")
    post, ev, calls = synth_observation(src)
    expect_fail(src, post, [{"phase": "arm", "op": "write", "lba": 0, "count": 1}], calls, "source-slot write")
    mutated = [dict(c) for c in calls]
    for c in mutated:
        if c.get("fn") == "tape_arm":
            c["result"] = "TAPE_OK"
    expect_fail(src, post, ev, mutated, "arm succeeded on source slot")
    print("PASS all WP-36 source-slot self-tests")


if __name__ == "__main__":
    main()
