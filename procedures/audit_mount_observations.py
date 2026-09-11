#!/usr/bin/env python3
"""Recompute the 7 September DRAFT-8 mount-log verdicts independently."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path
import sys


SPEC_HASHES = {
    "tapefs-v1.md": "3bffa0ec46d7ba3779b02cbee6fac1edaf5094553f78270ee379759655147cbb",
    "engine-api.md": "537eadc423e1a7bde726d689206b8fe93bef164d57e48e8ff71e07eaf8a7e3a1",
    "acceptance.md": "7f78fba7b66b4fc6e96d15399c62468249bb30fbccbb59bf9f57b4532f56b6b7",
}

EXPECTED = {
    "pr20-before.jsonl.gz": {
        "compressed_sha256": "b0debac21bd426d441bebfa752b0f044a2cfdcfa650cc38610c53f900cbd9784",
        "failed_ids": [
            "M-phase0-1",
            "M-phase0-2",
            "M-phase0-2047",
            "M-phase0-2048",
            "M-repair-0-stale-rw",
            "M-repair-0-stale-ro",
            "M-repair-0-stale-minor",
            "M-repair-0-stale-writefail",
            "M-repair-0-stale-flushfail",
            "M-repair-1-stale-rw",
            "M-repair-1-stale-ro",
            "M-repair-1-stale-minor",
            "M-repair-1-stale-writefail",
            "M-repair-1-stale-flushfail",
            "M-newer-water-wins",
        ],
    },
    "pr20-after.jsonl.gz": {
        "compressed_sha256": "188f4e564ac025c6d3f543f2d7dd1b0087eb339e64ac9bc1992f7cec5f3ade48",
        "failed_ids": [],
    },
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("product_root", type=Path)
    args = parser.parse_args()
    root = args.product_root.resolve()
    tests = root / "tests" / "mount_draft8"
    runs = root / "docs" / "verification" / "runs" / "2026-09-07"

    sys.path.insert(0, str(tests))
    from cases import SEED, cases  # pylint: disable=import-outside-toplevel
    from run import check  # pylint: disable=import-outside-toplevel

    defects: list[str] = []
    for name, expected_hash in SPEC_HASHES.items():
        canonical = root / "spec" / name
        packaged = tests / "spec" / name
        if sha256(canonical) != expected_hash:
            defects.append(f"canonical spec hash mismatch: {name}")
        if sha256(packaged) != expected_hash:
            defects.append(f"test-package spec hash mismatch: {name}")

    expected_cases = cases()
    expected_ids = [case.id for case in expected_cases]
    by_id = {case.id: case for case in expected_cases}
    summaries = []

    for name, expected in EXPECTED.items():
        path = runs / name
        actual_compressed_hash = sha256(path)
        log_defects: list[str] = []
        if actual_compressed_hash != expected["compressed_sha256"]:
            log_defects.append("compressed SHA-256 mismatch")

        try:
            with gzip.open(path, "rt", encoding="utf-8", newline="") as stream:
                records = [json.loads(line) for line in stream]
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            defects.append(f"{name}: unreadable JSONL: {exc}")
            continue

        if not records:
            defects.append(f"{name}: empty log")
            continue
        provenance, rows = records[0], records[1:]
        if provenance.get("kind") != "provenance":
            log_defects.append("missing provenance")
        if provenance.get("seed") != SEED:
            log_defects.append("seed mismatch")
        if provenance.get("candidate") is not True:
            log_defects.append("candidate flag mismatch")
        if provenance.get("cases") != len(expected_cases):
            log_defects.append("provenance case count mismatch")
        if len(rows) != len(expected_cases):
            log_defects.append("case row count mismatch")
        ids = [row.get("id") for row in rows]
        if ids != expected_ids:
            log_defects.append("case order or set mismatch")
        if len(set(ids)) != len(ids):
            log_defects.append("duplicate case ID")

        failed_ids = []
        for row in rows:
            case_id = row.get("id")
            case = by_id.get(case_id)
            if case is None:
                log_defects.append(f"unknown case ID: {case_id!r}")
                continue
            if row.get("fixture_sha256") != hashlib.sha256(case.encode()).hexdigest():
                log_defects.append(f"{case_id}: fixture hash mismatch")
            if tuple(row.get("allowed", ())) != case.allowed:
                log_defects.append(f"{case_id}: allowed-result mismatch")
            try:
                observation = json.loads(row["stdout"])
                errors = (
                    check(case, observation)
                    if row.get("returncode") == 0
                    else ["adapter process failed"]
                )
            except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
                errors = ["missing/malformed observation or adapter timeout/failure"]
                log_defects.append(f"{case_id}: observation parse/check error: {exc}")
            status = "FAIL" if errors else "PASS"
            if row.get("errors") != errors:
                log_defects.append(f"{case_id}: stored errors differ from recomputed")
            if row.get("status") != status:
                log_defects.append(f"{case_id}: stored status differs from recomputed")
            if errors:
                failed_ids.append(case_id)

        if failed_ids != expected["failed_ids"]:
            log_defects.append("recomputed failure set mismatch")
        defects.extend(f"{name}: {item}" for item in log_defects)
        summaries.append(
            {
                "file": name,
                "compressed_sha256": actual_compressed_hash,
                "adapter_sha256": provenance.get("adapter_sha256"),
                "records": len(records),
                "cases": len(rows),
                "recomputed_pass": len(rows) - len(failed_ids),
                "recomputed_fail": len(failed_ids),
                "failed_ids": failed_ids,
                "integrity_defects": log_defects,
            }
        )

    print(json.dumps({"logs": summaries, "defects": defects}, indent=2, sort_keys=True))
    return 1 if defects else 0


if __name__ == "__main__":
    raise SystemExit(main())

