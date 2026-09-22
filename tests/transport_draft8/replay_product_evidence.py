#!/usr/bin/env python3
"""Independent replay of the exact P1-R25 transport/warm product evidence."""
from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path
import zlib

from oracle import check, fixture_contract_errors, make_cases

JSONL_SHA256 = "7fe8a9096ac57abd7ed62c22ace39b432de52801207f9ae396edf08ae57a7997"
COMPRESSED_SHA256 = "5e4a8df8f4f1af40eece3fde8325adff400ee1ff5b9c21f2b647881366db458d"
PRODUCT_COMMIT = "dbd5a23291521cfe21da571fa97e14b806ace500"
VERIFIER_PUBLICATION = "5d97073ca03014e9d4055014f294709a78506b9e"
VERIFIER_TREE = "05aafde29e3d8048bec669053b1bafcd0104cbd3"
OBS_FORMAT = "WP-TRANSPORT-OBSERVATION-1"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def retained_bytes() -> bytes:
    here = Path(__file__).resolve().parent
    encoded = (here / "evidence" / "p1-r25-product" / "observations.jsonl.zlib.b64").read_text().strip()
    compressed = base64.b64decode(encoded, validate=True)
    if sha(compressed) != COMPRESSED_SHA256:
        raise RuntimeError("retained compressed evidence hash mismatch")
    raw = zlib.decompress(compressed)
    if sha(raw) != JSONL_SHA256:
        raise RuntimeError("retained observations.jsonl hash mismatch")
    return raw


def replay() -> tuple[int, list[dict]]:
    raw = retained_bytes()
    records = [json.loads(line) for line in raw.splitlines() if line.strip()]
    cases = make_cases()
    expected_ids = [case.id for case in cases]
    actual_ids = [record.get("case") for record in records]
    if len(cases) != 16:
        raise RuntimeError(f"verifier case-count drift: {len(cases)}")
    if actual_ids != expected_ids:
        raise RuntimeError(f"case set/order mismatch: {actual_ids!r}")

    failures = 0
    dispositions = []
    for case, record in zip(cases, records):
        errors = list(fixture_contract_errors(case))
        expected_media_hash = sha(case.pre.encode())

        if record.get("case") != case.id:
            errors.append("case id mismatch")
        if record.get("argv") != ["wp_transport_probe", case.id]:
            errors.append(f"argv mismatch: {record.get('argv')!r}")
        if record.get("exit") != 0:
            errors.append(f"adapter exit {record.get('exit')!r}")
        if record.get("input_sha256") != expected_media_hash:
            errors.append("input media hash does not match verifier fixture")
        if record.get("output_sha256") != expected_media_hash:
            errors.append("output media hash does not match unchanged verifier fixture")

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
                # oracle.check requires final media. The retained collector hashed the
                # actual OUTPUT.vo08, and every transport case normatively requires
                # byte-identical media; the authenticated output hash above therefore
                # binds the final media to case.pre without trusting Software's verdict.
                errors.extend(check(case, case.pre, events, calls))

        status = "PASS" if not errors else "FAIL"
        failures += bool(errors)
        dispositions.append({
            "case": case.id,
            "status": status,
            "errors": errors,
            "stored_software_errors": record.get("errors"),
            "input_sha256": record.get("input_sha256"),
            "output_sha256": record.get("output_sha256"),
        })
        print(f"{status} {case.id}")
        for error in errors:
            print("  " + error)

    flushes = sum(
        1
        for record in records
        for event in (record.get("observation") or {}).get("events", [])
        if event.get("op") == "flush"
    )
    writes = sum(
        1
        for record in records
        for event in (record.get("observation") or {}).get("events", [])
        if event.get("op") == "write"
    )
    print()
    print(f"evidence_sha256={sha(raw)}")
    print(f"product_commit={PRODUCT_COMMIT}")
    print(f"verifier_publication={VERIFIER_PUBLICATION}")
    print(f"verifier_tree={VERIFIER_TREE}")
    print(f"observed_write_callbacks={writes}")
    print(f"observed_flush_callbacks={flushes}")
    print(f"{len(dispositions)-failures}/{len(dispositions)} independently replayed cases PASS")
    return failures, dispositions


if __name__ == "__main__":
    failures, _ = replay()
    raise SystemExit(1 if failures else 0)
