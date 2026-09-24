#!/usr/bin/env python3
"""Deterministic DRAFT-8 full re-spool crash case planner."""
from __future__ import annotations

import hashlib
import json

BLOCK_BYTES = 512
DURABILITY_MODES = ("flush_required", "write_through")
CRASH_PASSES = (
    ("v3_003", "pass1", 2048),
    ("v3_003", "pass2", 2048),
    ("no_lower_run", "pass1", 1),
)

EXPECTED_TOTAL_CASES = 22562
EXPECTED_CASESET_SHA256 = "bc3e4cff6f61888faf9c5b97ccd136e9fec4417ef9cab4a46d084b4aae7ec444"
EXPECTED_BY_PASS = {
    "no_lower_run:pass1": 2062,
    "v3_003:pass1": 10250,
    "v3_003:pass2": 10250,
}
EXPECTED_BY_MODE = {"flush_required": 11281, "write_through": 11281}
EXPECTED_BY_TARGET = {
    "chunk_copy": 16388,
    "chunk_flush": 6,
    "entry_block": 3078,
    "entry_block_flush": 6,
    "header_block": 3078,
    "header_block_flush": 6,
}

def canonical_json(obj: dict) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)

def iter_cases():
    index = 0
    for fixture, pass_name, chunk_blocks in CRASH_PASSES:
        for mode in DURABILITY_MODES:
            # Chunk-copy interruption points are every copied block boundary.
            # The frozen request requires chunk-copy interruptions, while the
            # exhaustive 1..511 torn-prefix enumeration is specifically for
            # targeted one-block metadata writes.
            for ordinal in range(chunk_blocks):
                for kind, landed in (("before_write", 0), ("after_write", BLOCK_BYTES)):
                    yield {
                        "case_index": index, "fixture": fixture, "pass": pass_name,
                        "mode": mode, "target": "chunk_copy",
                        "injection": {
                            "kind": kind, "write_ordinal": ordinal,
                            "landed_bytes": landed,
                        },
                    }
                    index += 1

            yield {
                "case_index": index, "fixture": fixture, "pass": pass_name,
                "mode": mode, "target": "chunk_flush",
                "injection": {"kind": "at_flush", "flush_ordinal": 0},
            }
            index += 1

            # Each pass has one one-block entry-array write and one one-block
            # header commit. Both receive before, all 511 nontrivial tears,
            # after-write, and following-flush fault coverage.
            for target, ordinal in (("entry_block", 0), ("header_block", 1)):
                yield {
                    "case_index": index, "fixture": fixture, "pass": pass_name,
                    "mode": mode, "target": target,
                    "injection": {
                        "kind": "before_write", "write_ordinal": ordinal,
                        "landed_bytes": 0,
                    },
                }
                index += 1
                for landed in range(1, BLOCK_BYTES):
                    yield {
                        "case_index": index, "fixture": fixture, "pass": pass_name,
                        "mode": mode, "target": target,
                        "injection": {
                            "kind": "torn_write", "write_ordinal": ordinal,
                            "landed_bytes": landed,
                        },
                    }
                    index += 1
                yield {
                    "case_index": index, "fixture": fixture, "pass": pass_name,
                    "mode": mode, "target": target,
                    "injection": {
                        "kind": "after_write", "write_ordinal": ordinal,
                        "landed_bytes": BLOCK_BYTES,
                    },
                }
                index += 1
                yield {
                    "case_index": index, "fixture": fixture, "pass": pass_name,
                    "mode": mode, "target": target + "_flush",
                    "injection": {"kind": "at_flush", "flush_ordinal": ordinal + 1},
                }
                index += 1

def case_counts() -> dict:
    by_pass, by_mode, by_target = {}, {}, {}
    total = 0
    for case in iter_cases():
        total += 1
        p = f"{case['fixture']}:{case['pass']}"
        by_pass[p] = by_pass.get(p, 0) + 1
        by_mode[case["mode"]] = by_mode.get(case["mode"], 0) + 1
        by_target[case["target"]] = by_target.get(case["target"], 0) + 1
    return {
        "total": total,
        "by_pass": dict(sorted(by_pass.items())),
        "by_mode": dict(sorted(by_mode.items())),
        "by_target": dict(sorted(by_target.items())),
    }

def caseset_digest() -> str:
    h = hashlib.sha256()
    for case in iter_cases():
        h.update((canonical_json(case) + "\n").encode("ascii"))
    return h.hexdigest()

def validate_planner() -> list[str]:
    errors = []
    counts = case_counts()
    if counts["total"] != EXPECTED_TOTAL_CASES:
        errors.append("total case count drift")
    if counts["by_pass"] != EXPECTED_BY_PASS:
        errors.append("per-pass count drift")
    if counts["by_mode"] != EXPECTED_BY_MODE:
        errors.append("durability-mode count drift")
    if counts["by_target"] != EXPECTED_BY_TARGET:
        errors.append("target count drift")
    if caseset_digest() != EXPECTED_CASESET_SHA256:
        errors.append("case-set digest drift")
    return errors
