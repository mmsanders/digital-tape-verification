#!/usr/bin/env python3
"""Retain an exact, replayable failure record for a product-binding run."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

def canonical(obj) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode("ascii")

def retain_failure(path: str | Path, case: dict, observation: dict, reason: str) -> str:
    required = ("pre_snapshot", "post_snapshot", "target_event", "raw_region_sha256")
    missing = [x for x in required if x not in observation]
    if missing:
        raise ValueError("observation missing exact failure material: " + ",".join(missing))
    record = {
        "format": "WP10-RESPOOL-FAILURE-1",
        "reason": reason,
        "case": case,
        "observation": observation,
    }
    data = canonical(record)
    Path(path).write_bytes(data)
    return hashlib.sha256(data).hexdigest()
