#!/usr/bin/env python3
"""Verification #132: narrow identity disposition of the Product record bundle c461e9e0...

usage: python3 P1-R57-W89D-record-identity.py <Product observations.jsonl (c461e9e0...)>

1. Authenticates the candidate bytes by SHA-256.
2. Diffs them record by record against the accepted P1-R25 bytes a88850df... in
   tests/record_draft8/evidence/p1-r25-product, reporting every differing JSON path.
3. Replays them through the unchanged, corrected tests/record_draft8 replay
   (PR #39), substituting only the authenticated bundle SHA the replay pins.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "tests" / "record_draft8"
CANDIDATE_SHA = "c461e9e00d47e6ae9c47827fbba68a2a796aed9b418f3aad94c6b34e3591db8f"
ACCEPTED_SHA = "a88850df6554df973fdda6071f65184fcd9012b8886c253dafbff4fc9e0966fc"


def diff(a, b, path=""):
    if type(a) is not type(b):
        return [(path, a, b)]
    if isinstance(a, dict):
        out = []
        for k in sorted(set(a) | set(b)):
            out += diff(a.get(k, "<absent>"), b.get(k, "<absent>"), f"{path}.{k}")
        return out
    if isinstance(a, list):
        if len(a) != len(b):
            return [(path + ".len", len(a), len(b))]
        return [d for i, (x, y) in enumerate(zip(a, b)) for d in diff(x, y, f"{path}[{i}]")]
    return [] if a == b else [(path, a, b)]


def main():
    candidate = Path(sys.argv[1]).read_bytes()
    # Exact committed bytes (a working copy may carry CRLF conversion).
    accepted = subprocess.run(["git", "-C", str(ROOT), "show",
                               "HEAD:tests/record_draft8/evidence/p1-r25-product/observations.jsonl"],
                              check=True, capture_output=True).stdout
    assert hashlib.sha256(candidate).hexdigest() == CANDIDATE_SHA, "candidate bytes are not c461e9e0..."
    assert hashlib.sha256(accepted).hexdigest() == ACCEPTED_SHA, "accepted bytes are not a88850df..."
    ca = [json.loads(x) for x in candidate.splitlines() if x.strip()]
    ac = [json.loads(x) for x in accepted.splitlines() if x.strip()]
    assert [r["case"] for r in ca] == [r["case"] for r in ac], "case order/set differs"
    diffs = [(r["case"], *d) for r, s in zip(ac, ca) for d in diff(r, s)]
    print(f"records: {len(ca)} candidate, {len(ac)} accepted, same case order")
    for case, path, old, new in diffs:
        print(f"DIFF {case} {path}: {json.dumps(old)} -> {json.dumps(new)}")
    paths = {(c, p.split("[")[0].replace(".len", "")) for c, p, _, _ in diffs}
    assert paths <= {("WP09-ARMED-BUSY", ".errors"), ("WP09-ARMED-BUSY", ".expected_blocked")}, \
        f"differences outside the two runner presentation fields: {sorted(paths)}"
    old = next(r for r in ac if r["case"] == "WP09-ARMED-BUSY")
    new = next(r for r in ca if r["case"] == "WP09-ARMED-BUSY")
    print(f"WP09-ARMED-BUSY errors {json.dumps(old['errors'])} -> {json.dumps(new['errors'])}; "
          f"expected_blocked {old['expected_blocked']} -> {new['expected_blocked']}")
    sys.path.insert(0, str(ROOT))
    import replay_product_evidence as rp  # unchanged corrected oracle (PR #39)
    rp.EVIDENCE_SHA256 = CANDIDATE_SHA
    failures, dispositions = rp.replay(Path(sys.argv[1]))
    assert failures == 0 and len(dispositions) == 26, "corrected oracle did not pass 26/26"
    print(f"IDENTITY OK: only {sorted(p for _, p in paths)} on WP09-ARMED-BUSY differ; "
          f"corrected record_draft8 replay {len(dispositions)}/{len(dispositions)} PASS")


if __name__ == "__main__":
    main()
