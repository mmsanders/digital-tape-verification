#!/usr/bin/env python3
from __future__ import annotations

from oracle import Case, Media, check, fixture_contract_errors, idx, make_cases, synth_observation


def expect_fail(case, post, ev, calls, label):
    errors = check(case, post, ev, calls)
    if not errors:
        raise AssertionError("mutation escaped: " + label)
    print("CAUGHT", label, "=>", errors[0])


def main():
    cases = {c.id: c for c in make_cases()}
    for case in cases.values():
        errors = fixture_contract_errors(case)
        if errors:
            raise AssertionError((case.id, errors))
        post, ev, calls = synth_observation(case)
        errors = check(case, post, ev, calls)
        if errors:
            raise AssertionError((case.id, errors))
        print("PASS conforming", case.id)

    empty = cases["WP12-EMPTY"]
    post, ev, calls = synth_observation(empty)
    expect_fail(empty, post, [{"phase": "respool", "op": "write", "lba": 264, "count": 1}], calls, "empty respool wrote")

    two = cases["WP12-TWOPASS"]
    post, ev, calls = synth_observation(two)
    bad = list(post.slots)
    bad[3] = idx(1, [(12, 0, 2 * 131072)], 702)
    expect_fail(two, Media(post.blocks, post.primary, post.mirror, tuple(bad)), ev, calls, "stopped after pass 1")

    ev2 = [e for e in ev if not (e.get("op") == "write" and e.get("lba", 0) >= 2048 + 12 * 1024)]
    expect_fail(two, post, ev2, calls, "missing pass-1 writes")

    full = cases["WP12-FULL"]
    post, ev, calls = synth_observation(full)
    mutated = [dict(c) for c in calls]
    for c in mutated:
        if c.get("fn") == "tape_respool":
            c["result"] = "TAPE_OK"
    expect_fail(full, post, ev, mutated, "full dest accepted")

    print("PASS all WP-12 re-spool self-tests")


if __name__ == "__main__":
    main()
