#!/usr/bin/env python3
"""Fail-closed offline replay for a saved P1-R2-V playback evidence bundle."""
from __future__ import annotations
import argparse, gzip, json
from pathlib import Path
from oracle import VerificationError, check_run, load_package, sha256_file

OUTPUT_NAMES = {
    "forward_1x": "forward-1x.pcm",
    "seek_boundaries": "seek-boundaries.pcm",
    "reverse_neg1x": "reverse-neg1x.pcm",
}

def file_hash_map(root: Path) -> dict[str, str]:
    out = {}
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.name != "manifest.json":
            out[p.relative_to(root).as_posix()] = sha256_file(p)
    return out

def replay(evidence: Path) -> dict:
    manifest_path = evidence / "manifest.json"
    if not manifest_path.is_file():
        raise VerificationError("missing evidence manifest")
    manifest = json.loads(manifest_path.read_text())
    if manifest.get("schema") != "playback-draft8-evidence-v1":
        raise VerificationError("wrong evidence schema")
    if manifest.get("assignment") != "P1-R2-V":
        raise VerificationError("wrong evidence assignment")
    expected_files = manifest.get("files")
    if not isinstance(expected_files, dict):
        raise VerificationError("manifest missing file hashes")
    actual_files = file_hash_map(evidence)
    if set(actual_files) != set(expected_files):
        missing = sorted(set(expected_files) - set(actual_files))
        extra = sorted(set(actual_files) - set(expected_files))
        raise VerificationError(f"evidence file set mismatch: missing={missing} extra={extra}")
    for rel, want in sorted(expected_files.items()):
        if actual_files[rel] != want:
            raise VerificationError(f"evidence hash mismatch: {rel}")

    package = load_package(evidence / "input")
    if manifest.get("package_manifest_sha256") != sha256_file(evidence / "input/package.json"):
        raise VerificationError("manifest package hash mismatch")
    raw = gzip.decompress((evidence / "input" / package["fixture"]["archive"]).read_bytes())
    obs_path = evidence / "output/observation.json"
    if not obs_path.is_file():
        raise VerificationError("missing observation.json")
    observation = json.loads(obs_path.read_text())
    outputs = {}
    for family, name in OUTPUT_NAMES.items():
        p = evidence / "output" / name
        if not p.is_file():
            raise VerificationError(f"missing observed PCM: {name}")
        outputs[family] = p.read_bytes()
    result = check_run(raw, observation, outputs)
    saved_path = evidence / "result.json"
    if not saved_path.is_file():
        raise VerificationError("missing saved result.json")
    saved = json.loads(saved_path.read_text())
    if bool(saved.get("pass")) != bool(result.get("pass")):
        raise VerificationError("saved result disagrees with recomputed verdict")
    result["evidence"] = str(evidence)
    return result

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("evidence_dir")
    args = ap.parse_args()
    try:
        result = replay(Path(args.evidence_dir))
    except (VerificationError, ValueError, KeyError, json.JSONDecodeError, OSError) as exc:
        print(f"REPLAY FAIL: {exc}")
        return 1
    print(("REPLAY PASS" if result.get("pass") else "REPLAY VERDICT FAIL"), args.evidence_dir)
    for family, rec in result.get("families", {}).items():
        print(f"  {family}: {'PASS' if rec.get('match') else 'FAIL'}")
    return 0 if result.get("pass") else 1

if __name__ == "__main__":
    raise SystemExit(main())
