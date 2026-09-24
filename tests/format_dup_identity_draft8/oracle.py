#!/usr/bin/env python3
"""Exact durable-byte oracle for format/duplicate identity and duplicate WP-12a."""
from __future__ import annotations
import hashlib
from fixture import (
    BLOCK, LBA_MIRROR, initial_snapshot, final_index_heads,
    raw_shapes, target_writes, target_baseline,
)
from media import inspect_snapshot, identity_tuple
from planner import DUP_ROW_COLUMNS

class VerificationError(RuntimeError):
    pass

def need(c, m):
    if not c:
        raise VerificationError(m)

def _snapshot_bytes(snapshot):
    return {
        "primary": bytearray.fromhex(snapshot["primary_hex"]),
        "mirror": bytearray.fromhex(snapshot["mirror_hex"]),
    }

def _put_snapshot(snapshot, blocks):
    out = dict(snapshot)
    out["primary_hex"] = bytes(blocks["primary"]).hex()
    out["mirror_hex"] = bytes(blocks["mirror"]).hex()
    return out

def _copy_for_lba(lba):
    if lba == 0:
        return "primary"
    if lba == LBA_MIRROR:
        return "mirror"
    raise VerificationError("unexpected target LBA")

def expected_snapshot(case):
    need(case["scope"] == "crash", "not crash case")
    op, shape_name, mode = case["operation"], case["shape"], case["mode"]
    inj = case["injection"]
    snap = initial_snapshot(shape_name)
    working = _snapshot_bytes(snap)
    durable = {k: bytearray(v) for k, v in working.items()}
    targets = target_writes(op, shape_name)
    final_heads = False

    def successful_write(ord_):
        t = targets[ord_]
        name = _copy_for_lba(t["lba"])
        data = t["bytes"]
        working[name][:] = data
        if mode == "write_through":
            durable[name][:] = data

    def successful_flush():
        nonlocal durable
        durable = {k: bytearray(v) for k, v in working.items()}

    if inj["kind"] == "at_flush":
        stop = inj["flush_ordinal"]
        for o in range(stop):
            successful_write(o)
            successful_flush()
            if o == 1:
                final_heads = True
        if stop >= 2:
            final_heads = True
        successful_write(stop)
    else:
        stop = inj["write_ordinal"]
        for o in range(stop):
            successful_write(o)
            successful_flush()
            if o == 1:
                final_heads = True
        if stop >= 2:
            final_heads = True
        t = targets[stop]
        name = _copy_for_lba(t["lba"])
        data = t["bytes"]
        kind = inj["kind"]
        landed = inj.get("landed_bytes", 0)
        if kind == "before_write":
            pass
        elif kind == "torn_write":
            need(1 <= landed < BLOCK, "bad torn length")
            working[name][:landed] = data[:landed]
            durable[name][:landed] = data[:landed]
        elif kind == "after_write":
            need(landed == BLOCK, "bad complete length")
            working[name][:] = data
            if mode == "write_through":
                durable[name][:] = data
        else:
            raise VerificationError("unknown injection")

    out = _put_snapshot(snap, durable)
    if final_heads:
        a, b = final_index_heads(op)
        out["a0_head_hex"] = a.hex()
        out["b0_head_hex"] = b.hex()
    return out

def expected_crash_observation(case):
    pre = initial_snapshot(case["shape"])
    post = expected_snapshot(case)
    state = inspect_snapshot(post)
    obs = {
        "format": "FMTDUP-ID-OBSERVATION-1",
        "case_index": case["case_index"],
        "scope": "crash",
        "injection_fired": True,
        "pre_snapshot": pre,
        "post_snapshot": post,
        "target_baseline": target_baseline(case["operation"], case["shape"]),
        "actual_remount_result": state["mount_result"],
    }
    if state["mount_result"] == "TAPE_OK":
        obs["actual_selected_uuid"] = state.get("selected_uuid")
    return obs

BUSY_COLUMNS = frozenset(set(DUP_ROW_COLUMNS) - {"render", "service", "status_info_tell", "dup"})
REENTRY_ALLOWED = frozenset({"render", "status_info_tell"})

def expected_contract_observation(case):
    fam = case["family"]
    o = {
        "format": "FMTDUP-ID-OBSERVATION-1",
        "case_index": case["case_index"],
        "scope": "contract",
        "family": fam,
    }
    if fam == "equal_divergent_refusal":
        v = case["variant"]
        o.update({
            "variant": v,
            "result": "TAPE_ERR_DEST_TOO_SMALL" if v == "dup_capacity" else "TAPE_ERR_GEOMETRY",
            "destination_events": [],
            "destination_superblock_reads": 0,
            "destination_writes": 0,
        })
    elif fam == "dup_in_progress_row":
        c = case["column"]
        o["column"] = c
        if c == "dup":
            o.update({"result": "TAPE_OK", "operation_running_after": True, "work_advanced": True})
        elif c in ("render", "service", "status_info_tell"):
            o.update({
                "result": "TAPE_OK", "operation_running_after": True,
                "work_advanced": False, "audio_continues": True,
            })
        else:
            o.update({
                "result": "TAPE_ERR_BUSY", "operation_running_after": True,
                "work_advanced": False, "next_continuation_advanced": True,
                "restart_count": 0,
            })
    elif fam == "zero_budget":
        v = case["variant"]
        o.update({
            "variant": v, "result": "TAPE_ERR_INVALID_ARG", "work_advanced": False,
            "operation_running_after": v == "continuation",
        })
    elif fam == "changed_argument":
        a = case["argument"]
        o["argument"] = a
        if a == "allowed_mutables":
            o.update({"result": "TAPE_OK", "work_advanced": True, "operation_running_after": True})
        else:
            o.update({
                "result": "TAPE_ERR_INVALID_ARG", "work_advanced": False,
                "operation_running_after": True,
            })
    elif fam == "destination_failure_playing":
        o.update({
            "result": "TAPE_ERR_IO", "more_work": False, "source_faulted": False,
            "transport_before": "Playing", "transport_after": "Playing",
            "rate_unchanged": True, "position_unchanged": True, "ring_unchanged": True,
            "audio_continues": True,
        })
    elif fam == "callback_reentry":
        c = case["column"]
        o["column"] = c
        if c in REENTRY_ALLOWED:
            o.update({"result": "TAPE_OK", "state_changed": False})
        else:
            o.update({"result": "TAPE_ERR_BUSY", "state_changed": False, "recursed": False})
        o.update({"operation_running_after": True, "next_ordinary_continuation_advanced": True})
    elif fam == "faulted_source":
        o.update({"variant": "dup_call", "result": "TAPE_ERR_FAULTED", "block_operations": 0})
    elif fam == "small_budget_completion":
        o.update({
            "variant": "dup", "result": "TAPE_OK", "calls": 3,
            "all_calls_same_function": True, "saw_more_work_true": True,
            "terminal_more_work": False, "restart_count": 0,
            "final_identity": {"sb_generation": 1, "a0_sequence": 1, "b0_sequence": 2},
        })
    else:
        raise VerificationError("unknown contract family")
    return o

def expected_observation(case):
    return expected_crash_observation(case) if case["scope"] == "crash" else expected_contract_observation(case)

def validate_case(case, obs):
    need(isinstance(obs, dict), "observation not object")
    need(obs.get("format") == "FMTDUP-ID-OBSERVATION-1", "observation format")
    need(obs.get("case_index") == case["case_index"], "case index")
    need(obs.get("scope") == case["scope"], "scope")
    exp = expected_observation(case)

    if case["scope"] == "crash":
        need(obs.get("injection_fired") is True, "planned injection did not fire")
        need(obs.get("pre_snapshot") == exp["pre_snapshot"], "raw pre snapshot mismatch")
        need(obs.get("post_snapshot") == exp["post_snapshot"], "raw durable post snapshot mismatch")
        need(obs.get("target_baseline") == exp["target_baseline"], "target baseline/order/bytes mismatch")

        parsed = inspect_snapshot(obs["post_snapshot"])
        need(obs.get("actual_remount_result") == parsed["mount_result"], "fresh remount disagrees with raw oracle")
        if parsed["mount_result"] == "TAPE_OK":
            need(obs.get("actual_selected_uuid") == parsed.get("selected_uuid"), "selected UUID mismatch")

        ident = identity_tuple(obs["post_snapshot"])
        if ident and ident[0] in (
            "a0a1a2a3a4a5a6a7a8a9aaabacadaeaf",
            "b0b1b2b3b4b5b6b7b8b9babbbcbdbebf",
        ):
            need(ident[1:] == (1, 1, 2), "identity-assignment boundary drift")

        inj = case["injection"]
        s = raw_shapes()[case["shape"]]
        if s.headroom:
            template_durable = False
            if inj["kind"] == "at_flush":
                template_durable = case["mode"] == "write_through" and inj["flush_ordinal"] <= 1
                if inj["flush_ordinal"] > 0:
                    template_durable = True
            elif inj["write_ordinal"] <= 1:
                if inj["kind"] == "after_write" and case["mode"] == "write_through":
                    template_durable = True
                if inj["write_ordinal"] == 1:
                    template_durable = True
            else:
                template_durable = True
            if (
                template_durable
                and parsed["mount_result"] == "TAPE_OK"
                and s.previous_uuid is not None
            ):
                need(
                    parsed.get("selected_uuid") != s.previous_uuid.hex(),
                    "previous UUID selected after durable template",
                )
    else:
        for k, v in exp.items():
            need(obs.get(k) == v, f"contract mismatch: {k}")
    return True

def failure_reproducer(case, obs, error):
    rep = {"format": "FMTDUP-ID-FAILURE-1", "case": case, "error": str(error)}
    if case["scope"] == "crash":
        rep.update({
            "pre_primary": (obs.get("pre_snapshot") or {}).get("primary_hex"),
            "pre_mirror": (obs.get("pre_snapshot") or {}).get("mirror_hex"),
            "post_primary": (obs.get("post_snapshot") or {}).get("primary_hex"),
            "post_mirror": (obs.get("post_snapshot") or {}).get("mirror_hex"),
            "actual_remount_result": obs.get("actual_remount_result"),
        })
        try:
            rep["raw_oracle_result"] = inspect_snapshot(obs.get("post_snapshot") or {})["mount_result"]
        except Exception as e:
            rep["raw_oracle_result"] = "PARSER_ERROR:" + str(e)
    return rep
