#!/usr/bin/env python3
from __future__ import annotations

from fixture import (
    BASE, DECLINE_AUDIO_SHA256, LIVE_A_SHA256, V3_AUDIO_SHA256,
    clean_cases, compact, empty_at, functional_fixture_errors,
)
from oracle import (
    COLUMNS, FAULTED_ALLOWED, RESPOOL_ALLOWED, OracleError, case_id,
    expected_layout, expected_target_lba, transaction_media,
    validate_clean_case, validate_crash_observation, validate_longop_contract,
    validate_zero_needed_empty,
)
from planner import (
    EXPECTED_CASESET_SHA256, EXPECTED_TOTAL_CASES, case_counts,
    caseset_digest, iter_cases, validate_planner,
)

def need(cond, msg):
    if not cond:
        raise AssertionError(msg)

def expect_reject(fn, needle=None):
    try:
        fn()
    except OracleError as exc:
        if needle is not None:
            need(needle in str(exc), f"wrong rejection: {exc}")
        return
    raise AssertionError("negative control was accepted")

def find_case(fixture, pass_name, mode, target, kind, ordinal=None):
    for c in iter_cases():
        if (
            c["fixture"] == fixture and c["pass"] == pass_name
            and c["mode"] == mode and c["target"] == target
            and c["injection"]["kind"] == kind
        ):
            if ordinal is None or c["injection"].get("write_ordinal") == ordinal:
                return c
    raise AssertionError("case not found")

def synthetic_crash(case):
    pre, committed = transaction_media(case)
    layout = expected_layout(case)
    post = pre
    if layout.startswith("post_"):
        post = committed

    lba = expected_target_lba(case)
    target_event = {"target": case["target"]}
    if lba is None:
        target_event.update({"op": "flush"})
    else:
        target_event.update({"op": "write", "lba": lba, "count": 1})

    hashes = {"live_a": LIVE_A_SHA256}
    if case["fixture"] == "v3_003":
        if case["pass"] == "pass1":
            hashes["source_10_12"] = V3_AUDIO_SHA256
            if layout == "post_pass1":
                hashes["copy_12_14"] = V3_AUDIO_SHA256
        else:
            hashes["pass1_12_14"] = V3_AUDIO_SHA256
            if layout == "post_pass2":
                hashes["copy_10_12"] = V3_AUDIO_SHA256
    else:
        hashes["source_fragments"] = DECLINE_AUDIO_SHA256
        if layout == "post_pass1":
            hashes["copy_10_frames"] = DECLINE_AUDIO_SHA256

    return {
        "format": "WP10-RESPOOL-OBSERVATION-1",
        "case_id": case_id(case),
        "injection_fired": True,
        "fresh_remount_from_durable_only": True,
        "actual_remount_result": "TAPE_OK",
        "pre_snapshot": compact(pre),
        "post_snapshot": compact(post),
        "target_event": target_event,
        "live_a_sha256": LIVE_A_SHA256,
        "raw_region_sha256": hashes,
    }

def row_observation(*, faulted=False):
    allowed = FAULTED_ALLOWED if faulted else RESPOOL_ALLOWED
    row = []
    token = "op-72"
    for name in COLUMNS:
        if faulted:
            result = "TAPE_OK" if name in allowed else "TAPE_ERR_FAULTED"
        else:
            result = "TAPE_OK" if name in allowed else "TAPE_ERR_BUSY"
        cell = {
            "call": name,
            "result": result,
            "block_ops": 0,
            "operation_token_before": token,
            "operation_token_after": token,
        }
        if not faulted and name == "respool":
            cell.update({"progress_before": 4, "progress_after": 5})
        row.append(cell)
    return row

def longop_observation():
    return {
        "in_progress_row": row_observation(),
        "faulted_row": row_observation(faulted=True),
        "small_budget_calls": [
            {"result": "TAPE_OK", "block_budget": 1, "more_work": True,
             "operation_token": "op-small", "progress_before": 0, "progress_after": 1},
            {"result": "TAPE_OK", "block_budget": 1, "more_work": True,
             "operation_token": "op-small", "progress_before": 1, "progress_after": 2},
            {"result": "TAPE_OK", "block_budget": 2, "more_work": False,
             "operation_token": "op-small", "progress_before": 2, "progress_after": 4},
        ],
        "zero_budget": [
            {"phase": "initiation", "block_budget": 0, "result": "TAPE_ERR_INVALID_ARG",
             "block_ops": 0, "state_before": "idle", "state_after": "idle"},
            {"phase": "continuation", "block_budget": 0, "result": "TAPE_ERR_INVALID_ARG",
             "block_ops": 0, "state_before": "respool:2", "state_after": "respool:2"},
        ],
        "busy_then_continue": {
            "busy": {
                "result": "TAPE_ERR_BUSY", "block_ops": 0,
                "operation_token_before": "op-busy", "operation_token_after": "op-busy",
            },
            "continuation": {
                "result": "TAPE_OK", "operation_token": "op-busy",
                "progress_before": 6, "progress_after": 7,
            },
        },
        "own_device_failures": [
            {"failure": "write", "result": "TAPE_ERR_IO", "more_work": False, "state_after": "FAULTED"},
            {"failure": "flush", "result": "TAPE_ERR_IO", "more_work": False, "state_after": "FAULTED"},
        ],
        "faulted_over_armed": {
            "armed": True, "frames_owed": 3, "respool_result": "TAPE_ERR_FAULTED", "block_ops": 0,
        },
        "faulted_ring_drain": {
            "rendered_frames": [4, 2, 1, 0], "underrun": True, "abort_result": "TAPE_OK",
        },
        "stable_continuation_args": [],
        "progress_callback_reentry_applicable": False,
    }

def main():
    errors = validate_planner()
    need(not errors, "planner: " + "; ".join(errors))
    need(case_counts()["total"] == EXPECTED_TOTAL_CASES, "planner total")
    need(caseset_digest() == EXPECTED_CASESET_SHA256, "planner digest")
    print("PASS planner", EXPECTED_TOTAL_CASES, EXPECTED_CASESET_SHA256)

    errors = functional_fixture_errors()
    need(not errors, "fixtures: " + "; ".join(errors))
    print("PASS verifier-owned fixture premises and pinned base oracle")

    # Full clean WP-12 shapes, excluding the stage-clear transaction already accepted
    # in Verification #69.
    for c in clean_cases():
        post, events, calls = BASE.synth_observation(c)
        validate_clean_case(c, post, events, calls)
    print("PASS clean WP-12 functional/headroom shapes")

    # Empty respool consumes neither counter. Test the normal cap and deliberately
    # crafted reserved values for both sequence and sb_generation.
    for seq, generation in ((0xFFFFFFFD, 7), (0xFFFFFFFF, 0xFFFFFFFF)):
        pre = empty_at(seq, generation)
        validate_zero_needed_empty(
            pre, pre, [],
            {"result": "TAPE_OK", "more_work": False, "block_budget": 1},
        )
    print("PASS zero-needed empty counter boundaries")

    representatives = [
        find_case("v3_003", "pass1", "flush_required", "chunk_copy", "after_write", 700),
        find_case("v3_003", "pass1", "write_through", "entry_block", "torn_write", 0),
        find_case("v3_003", "pass1", "write_through", "header_block", "after_write", 1),
        find_case("v3_003", "pass2", "flush_required", "chunk_copy", "before_write", 0),
        find_case("v3_003", "pass2", "write_through", "header_block_flush", "at_flush"),
        find_case("no_lower_run", "pass1", "flush_required", "entry_block_flush", "at_flush"),
        find_case("no_lower_run", "pass1", "write_through", "header_block", "after_write", 1),
    ]
    for case in representatives:
        validate_crash_observation(case, synthetic_crash(case))
    print("PASS representative crash/raw-layout oracles across pass/mode/target classes")

    longop = longop_observation()
    validate_longop_contract(longop)
    print("PASS complete respool/Faulted state rows and long-operation contract")

    # Required negative controls.
    case = representatives[0]
    obs = synthetic_crash(case)
    obs["raw_region_sha256"]["live_a"] = "0" * 64
    expect_reject(lambda: validate_crash_observation(case, obs), "Side A")
    print("PASS overlap/live-set corruption negative control")

    case = find_case("v3_003", "pass1", "flush_required", "header_block", "after_write", 1)
    obs = synthetic_crash(case)
    _, committed = transaction_media(case)
    obs["post_snapshot"] = compact(committed)
    expect_reject(lambda: validate_crash_observation(case, obs), "selected layout")
    print("PASS stale/illegal layout-selection negative control")

    case = find_case("v3_003", "pass2", "write_through", "chunk_copy", "after_write", 0)
    obs = synthetic_crash(case)
    obs["target_event"]["lba"] += 2 * BASE.BLOCKS_PER_CHUNK
    expect_reject(lambda: validate_crash_observation(case, obs), "destination")
    print("PASS wrong pass-2 destination negative control")

    bad = longop_observation()
    seek = next(c for c in bad["in_progress_row"] if c["call"] == "seek")
    seek["operation_token_after"] = "restarted"
    expect_reject(lambda: validate_longop_contract(bad), "terminated/restarted")
    print("PASS false-BUSY-termination negative control")

    bad = longop_observation()
    service = next(c for c in bad["faulted_row"] if c["call"] == "service")
    service["result"] = "TAPE_OK"
    service["block_ops"] = 1
    expect_reject(lambda: validate_longop_contract(bad), "leaked")
    print("PASS FAULTED-row leakage negative control")

if __name__ == "__main__":
    main()
