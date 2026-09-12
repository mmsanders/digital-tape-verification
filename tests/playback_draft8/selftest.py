#!/usr/bin/env python3
"""Package self-test and targeted negative controls for P1-R2-V."""
from __future__ import annotations
import copy, gzip, json, shutil, subprocess, sys, tempfile
from pathlib import Path
import oracle
from oracle import VerificationError

HERE = Path(__file__).resolve().parent
NAMES = {"forward_1x":"forward-1x.pcm", "seek_boundaries":"seek-boundaries.pcm", "reverse_neg1x":"reverse-neg1x.pcm"}

def must_fail(label, fn):
    try:
        fn()
    except (VerificationError, ValueError, KeyError, json.JSONDecodeError, OSError):
        print("CAUGHT", label)
        return
    raise AssertionError("negative control did not fail: " + label)

def run_checked(raw, obs, outs):
    r = oracle.check_run(raw, obs, outs)
    if not r["pass"]:
        raise VerificationError("PCM mismatch")
    return r

def main():
    pkg = oracle.load_package(HERE)
    raw = gzip.decompress((HERE / pkg["fixture"]["archive"]).read_bytes())
    fx = oracle.verify_fixture(raw)
    assert tuple(fx["index"]["entries"]) == oracle.EXPECTED_ENTRIES
    exp = oracle.expected_outputs(raw)
    for family, rec in pkg["goldens"].items():
        assert (HERE / rec["path"]).read_bytes() == exp[family]
    print("PASS authenticated DRAFT-8 package + fixture-derived candidate PCM")

    with tempfile.TemporaryDirectory(prefix="playback-draft8-selftest-") as td_s:
        td = Path(td_s); out = td / "adapter"; out.mkdir()
        rawp = td / "fixture.vo08"; rawp.write_bytes(raw)
        subprocess.run([sys.executable, str(HERE / "_synthetic_adapter.py"), "--fixture", str(rawp), "--out-dir", str(out)], check=True, stdout=subprocess.PIPE)
        obs = json.loads((out / "observation.json").read_text())
        outs = {f:(out/n).read_bytes() for f,n in NAMES.items()}
        run_checked(raw, obs, outs)
        print("PASS synthetic three-family public-call/callback observation")

        bad = dict(outs); b = bytearray(bad["seek_boundaries"]); b[0:4] = exp["forward_1x"][4:8]; bad["seek_boundaries"] = bytes(b)
        if oracle.check_run(raw, obs, bad)["pass"]: raise AssertionError("wrong first seek frame escaped")
        print("CAUGHT wrong first frame after seek")

        bad = dict(outs); b = bytearray(bad["seek_boundaries"]); b[3*4:4*4] = exp["forward_1x"][6*4:7*4]; bad["seek_boundaries"] = bytes(b)
        if oracle.check_run(raw, obs, bad)["pass"]: raise AssertionError("run boundary +1 escaped")
        print("CAUGHT run-boundary off-by-one")

        bad = dict(outs); bad["reverse_neg1x"] = oracle.draft5_bad_reverse(raw)
        if oracle.check_run(raw, obs, bad)["pass"]: raise AssertionError("reverse grid drift escaped")
        print("CAUGHT reverse interpolation/grid drift")

        badobs = copy.deepcopy(obs); render_i = next(i for i,c in enumerate(badobs["cases"]["forward_1x"]["calls"]) if c["call"]=="tape_render")
        badobs["cases"]["forward_1x"]["callbacks"].append({"call_index":render_i,"op":"read","lba":2048,"count":1,"rc":0})
        must_fail("callback I/O during render", lambda: run_checked(raw,badobs,outs))
        badobs = copy.deepcopy(obs); seek = next(c for c in badobs["cases"]["seek_boundaries"]["calls"] if c["call"]=="tape_seek"); seek["frame"] += 1
        must_fail("wrong public tape_seek target", lambda: run_checked(raw,badobs,outs))

        tamper = td / "tamper-package"; shutil.copytree(HERE, tamper, ignore=shutil.ignore_patterns("__pycache__", "evidence"))
        p = tamper / pkg["fixture"]["archive"]; d=bytearray(p.read_bytes()); d[-1] ^= 1; p.write_bytes(d)
        must_fail("altered fixture bytes", lambda: oracle.load_package(tamper))
        shutil.rmtree(tamper); shutil.copytree(HERE, tamper, ignore=shutil.ignore_patterns("__pycache__", "evidence"))
        p = tamper / pkg["goldens"]["forward_1x"]["path"]; d=bytearray(p.read_bytes()); d[0] ^= 1; p.write_bytes(d)
        must_fail("altered candidate PCM bytes", lambda: oracle.load_package(tamper))
        shutil.rmtree(tamper); shutil.copytree(HERE, tamper, ignore=shutil.ignore_patterns("__pycache__", "evidence"))
        p=tamper/"spec/engine-api.md"; p.write_bytes(p.read_bytes()+b"\nTAMPER\n")
        must_fail("tampered authenticated spec bytes", lambda: oracle.load_package(tamper))

        ev = td / "evidence"
        cmd=[sys.executable,str(HERE/"runner.py"),"--adapter-cmd",f"{sys.executable} {HERE/'_synthetic_adapter.py'}",
             "--adapter-kind","synthetic","--adapter-id","verifier-synthetic-public-api-model-v1",
             "--adapter-source",str(HERE/"_synthetic_adapter.py"),"--source-commit","SELFTEST",
             "--source-tree","SELFTEST","--evidence-dir",str(ev)]
        subprocess.run(cmd,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        subprocess.run([sys.executable,str(HERE/"replay.py"),str(ev)],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        print("PASS offline saved-evidence replay")

        missing=td/"missing"; shutil.copytree(ev,missing); (missing/"output/seek-boundaries.pcm").unlink()
        rc=subprocess.run([sys.executable,str(HERE/"replay.py"),str(missing)],stdout=subprocess.PIPE,stderr=subprocess.PIPE).returncode
        if rc==0: raise AssertionError("missing evidence replay escaped")
        print("CAUGHT missing evidence")
        changed=td/"changed"; shutil.copytree(ev,changed); p=changed/"output/reverse-neg1x.pcm"; d=bytearray(p.read_bytes()); d[0]^=1; p.write_bytes(d)
        rc=subprocess.run([sys.executable,str(HERE/"replay.py"),str(changed)],stdout=subprocess.PIPE,stderr=subprocess.PIPE).returncode
        if rc==0: raise AssertionError("tampered evidence replay escaped")
        print("CAUGHT tampered evidence")

    print("SELFTEST PASS: three families + required negative controls + provenance/replay controls")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
