#!/usr/bin/env python3
"""Independent offline replay for issue #44 respool product observations.

Usage:
    python3 tools/replay_p1_r25_respool_evidence.py observations.jsonl

The script ignores Software's stored verdict/errors, regenerates the unchanged
verifier fixtures/expected post-media, authenticates media hashes and product
identity, then reapplies tests/respool_draft8/oracle.py to raw calls/events.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "tests" / "respool_draft8"
sys.path.insert(0, str(PKG))

from oracle import check, fixture_contract_errors, make_cases  # noqa: E402

EVIDENCE_SHA256 = "5db21452b759b2f113508d6731ae90ac99bcf80e5c8a223ae521009d1d30c81c"
PRODUCT_COMMIT = "262db463680798c63fde8b18232e60bdbda15f0a"
VERIFIER_PUBLICATION = "6519220f161254c0453a30858eb3e7073e2eb82b"
VERIFIER_TREE = "caf607917240c5a96fd32f526ee8e2a4761ebb24"
OBS_FORMAT = "WP12-RESPOOL-OBSERVATION-1"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: replay_p1_r25_respool_evidence.py observations.jsonl", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    raw = path.read_bytes()
    got = sha(raw)
    if got != EVIDENCE_SHA256:
        print(f"FAIL evidence hash: got {got}, want {EVIDENCE_SHA256}", file=sys.stderr)
        return 2

    rows = [json.loads(line) for line in raw.splitlines() if line.strip()]
    cases = make_cases()
    expected_ids = [c.id for c in cases]
    actual_ids = [r.get("case") for r in rows]
    if actual_ids != expected_ids:
        print("FAIL case set/order mismatch", file=sys.stderr)
        print(" expected:", expected_ids, file=sys.stderr)
        print(" actual:  ", actual_ids, file=sys.stderr)
        return 2

    failures = 0
    for case, record in zip(cases, rows):
        errors = list(fixture_contract_errors(case))
        expected_post = case.expected_post if case.expected_post is not None else case.pre

        if record.get("argv") != ["wp12_respool_probe", case.id]:
            errors.append(f"argv mismatch: {record.get('argv')!r}")
        if record.get("exit") != 0:
            errors.append(f"adapter exit {record.get('exit')!r}")
        if record.get("input_sha256") != sha(case.pre.encode()):
            errors.append("input hash does not match verifier fixture")
        if record.get("output_sha256") != sha(expected_post.encode()):
            errors.append("output hash does not match verifier expected post-media")

        obs = record.get("observation")
        if not isinstance(obs, dict):
            errors.append("missing observation object")
        else:
            if obs.get("format") != OBS_FORMAT:
                errors.append(f"observation format {obs.get('format')!r}")
            if obs.get("adapter_kind") != "product":
                errors.append(f"adapter_kind {obs.get('adapter_kind')!r} is not product")
            if obs.get("event_overflow") is not False:
                errors.append("event trace overflowed or overflow flag missing")
            calls = obs.get("calls")
            events = obs.get("events")
            if not isinstance(calls, list):
                errors.append("calls is not a list")
            if not isinstance(events, list):
                errors.append("events is not a list")
            if isinstance(calls, list) and isinstance(events, list):
                errors.extend(check(case, expected_post, events, calls))

        status = "PASS" if not errors else "FAIL"
        print(status, case.id)
        for error in errors:
            print("  " + error)
        failures += bool(errors)

    print()
    print(f"evidence_sha256={got}")
    print(f"product_commit={PRODUCT_COMMIT}")
    print(f"verifier_publication={VERIFIER_PUBLICATION}")
    print(f"verifier_tree={VERIFIER_TREE}")
    print(f"{len(cases)-failures}/{len(cases)} independently replayed cases PASS")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
