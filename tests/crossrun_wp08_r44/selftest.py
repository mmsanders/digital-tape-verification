#!/usr/bin/env python3
"""Generate synthetic public observations and kill five arithmetic red controls."""
import copy
import hashlib

from oracle import RUN_LENGTHS, Transport, cases, check, digest_plan, fixture, pcm, schedules


def observation(case):
    _, frames = fixture()
    obs = {"schema": "wp08-r44-v1", "case": case.id,
           "fixture_sha256": hashlib.sha256(pcm(frames)).hexdigest(),
           "run_lengths": list(RUN_LENGTHS), "seek": case.seek, "rate": case.rate, "variants": {}}
    for label, schedule in schedules(case.count).items():
        budget = {"whole": 256, "single": 1, "uneven": 7}[label]
        model = Transport(frames, case.seek, case.rate)
        renders = []
        for requested in schedule:
            emitted = model.render(requested)
            renders.append({"requested": requested, "result": "TAPE_OK", "rendered": len(emitted),
                            "pcm_hex": pcm(emitted).hex(), "tell": model.pos >> 32,
                            "at_start": model.at_start, "at_end": model.at_end,
                            "block_events": []})
        obs["variants"][label] = {"render_sizes": schedule, "service_budget": budget,
                                   "services": [{"budget": budget, "blocks": min(budget, 4),
                                                 "result": "TAPE_OK", "more_work": False}]
                                   if budget >= 4 else
                                   [{"budget": budget, "blocks": 1, "result": "TAPE_OK",
                                     "more_work": j < 3} for j in range(4)],
                                   "renders": renders}
    return obs


def run():
    plan = cases()
    by_id = {c.id: c for c in plan}
    for case in plan:
        check(case, observation(case))
    controls = [
        ("seek off by one", "boundary-5+0-f", lambda o: o["variants"]["whole"]["renders"][0].update(tell=0)),
        ("stale run sample", "boundary-8+0-r", lambda o: o["variants"]["whole"]["renders"][0].update(pcm_hex="00000000" + o["variants"]["whole"]["renders"][0]["pcm_hex"][8:])),
        ("wrong negative interpolation rounding", "fraction-2", lambda o: o["variants"]["single"]["renders"][1].update(pcm_hex="00000000")),
        ("endpoint wrap", "huge-forward", lambda o: o["variants"]["whole"]["renders"][0].update(tell=0)),
        ("service-time drift", "fraction-3", lambda o: o["variants"]["uneven"]["renders"][0].update(pcm_hex="00000000")),
    ]
    for name, key, mutate in controls:
        obs = copy.deepcopy(observation(by_id[key]))
        mutate(obs)
        try:
            check(by_id[key], obs)
        except AssertionError:
            pass
        else:
            raise AssertionError("red control survived: " + name)
    print("PASS", len(plan), "synthetic cases;", len(controls), "red controls killed; plan", digest_plan())


if __name__ == "__main__":
    run()
