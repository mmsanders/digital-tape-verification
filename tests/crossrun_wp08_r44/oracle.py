"""DRAFT-9 independent multi-run Q16.16 playback property oracle."""
from __future__ import annotations

import hashlib
import json
import struct
from dataclasses import dataclass

SEED = 0xA51CE55D
RUN_LENGTHS = (5, 3, 7, 2)  # nonconstant, short final run
ONE = 1 << 32
RATES = (65536, -65536, 32768, -32768, 98304, -98304, 0x7FFFFFFF, -0x80000000)


def need(ok, msg):
    if not ok:
        raise AssertionError(msg)


def pcm(frames):
    return b"".join(struct.pack("<hh", *f) for f in frames)


def fixture():
    x = SEED
    runs = []
    for n in RUN_LENGTHS:
        run = []
        for _ in range(n):
            x ^= (x << 13) & 0xFFFFFFFF
            x ^= x >> 17
            x ^= (x << 5) & 0xFFFFFFFF
            x &= 0xFFFFFFFF
            run.append(((x & 65535) - 32768, ((x >> 16) & 65535) - 32768))
        runs.append(run)
    frames = [f for run in runs for f in run]
    need(len(frames) == 17 and len(set(frames)) == 17, "nonconstant fixture")
    return runs, frames


@dataclass(frozen=True)
class Case:
    id: str
    seek: int
    rate: int
    count: int


def cases():
    out = []
    for boundary in (5, 8, 15):
        for offset in (-1, 0, 1):
            for rate in (65536, -65536):
                out.append(Case(f"boundary-{boundary}{offset:+d}-{'f' if rate > 0 else 'r'}",
                                boundary + offset, rate, 8))
    out += [Case(f"fraction-{j}", start, rate, 11) for j, (start, rate) in enumerate((
        (4, 32768), (7, -32768), (14, 98304), (16, -98304),
        (5, -32768), (8, 98304), (15, -98304), (1, 32768)), 1)]
    out += [Case("end-reverse", 17, -65536, 20), Case("start-reverse", 0, -65536, 3),
            Case("end-forward", 17, 65536, 3), Case("beyond-end", 100, 65536, 3),
            Case("zero-rate", 8, 0, 5), Case("huge-forward", 16, 0x7FFFFFFF, 3),
            Case("huge-reverse", 17, -0x80000000, 3)]
    need(len(out) == 33 and len({c.id for c in out}) == 33, "case census")
    return out


def interpolate(a, b, fractional):
    return tuple(a[ch] + ((b[ch] - a[ch]) * fractional // ONE) for ch in (0, 1))


class Transport:
    def __init__(self, frames, seek, rate):
        self.frames = frames
        self.max_pos = len(frames) * ONE
        self.pos = min(seek, len(frames)) * ONE
        self.step = rate * 65536
        self.at_start = False
        self.at_end = False

    def render(self, requested):
        emitted = []
        if not self.frames:
            self.at_end = True
            return emitted
        if self.step == 0:
            return emitted
        if self.step < 0 and self.pos >= self.max_pos:
            self.pos = (len(self.frames) - 1) * ONE
        for _ in range(requested):
            if self.step > 0 and self.pos >= self.max_pos:
                self.at_end = True
                break
            if self.step < 0 and self.at_start:
                break
            i, f = divmod(self.pos, ONE)
            a = self.frames[i]
            b = self.frames[i + 1] if i + 1 < len(self.frames) else a
            emitted.append(interpolate(a, b, f))
            if self.step > 0:
                self.at_start = False
                if self.pos >= self.max_pos or self.step >= self.max_pos - self.pos:
                    self.pos = self.max_pos
                    self.at_end = True
                else:
                    self.pos += self.step
            else:
                self.at_end = False
                s = -self.step
                if self.pos == 0:
                    self.at_start = True
                elif self.pos <= s:
                    self.pos = 0
                else:
                    self.pos -= s
        return emitted


def schedules(count):
    return {"whole": [count], "single": [1] * count,
            "uneven": [3, 2] * (count // 5) + ([count % 5] if count % 5 else [])}


def check(case, obs):
    runs, frames = fixture()
    need(obs.get("schema") == "wp08-r44-v1" and obs.get("case") == case.id, "schema/case")
    need(obs.get("fixture_sha256") == hashlib.sha256(pcm(frames)).hexdigest(), "fixture digest")
    need(obs.get("run_lengths") == list(RUN_LENGTHS), "run partition")
    need(obs.get("seek") == case.seek and obs.get("rate") == case.rate, "seek/rate")
    variants = obs.get("variants")
    need(isinstance(variants, dict) and set(variants) == set(schedules(case.count)), "subdivision variants")
    outputs = []
    for label, schedule in schedules(case.count).items():
        v = variants[label]
        need(v.get("render_sizes") == schedule, "render subdivision")
        budget = {"whole": 256, "single": 1, "uneven": 7}[label]
        need(v.get("service_budget") == budget, "service subdivision")
        services = v.get("services")
        need(isinstance(services, list) and services and all(s.get("budget") == budget and
             0 <= s.get("blocks", -1) <= budget and s.get("result") == "TAPE_OK" for s in services),
             "service budget/callback trace")
        need(services[-1].get("more_work") is False, "service did not complete")
        actual = v.get("renders")
        need(isinstance(actual, list) and len(actual) == len(schedule), "render call count")
        model = Transport(frames, case.seek, case.rate)
        total_pcm = b""
        for j, (request, r) in enumerate(zip(schedule, actual)):
            expected = pcm(model.render(request))
            need(r.get("requested") == request and r.get("result") == "TAPE_OK", "render request/result")
            need(r.get("rendered") == len(expected) // 4 and r.get("pcm_hex") == expected.hex(),
                 f"{label} render {j} exact PCM")
            need(r.get("tell") == model.pos >> 32 and r.get("at_start") is model.at_start
                 and r.get("at_end") is model.at_end, f"{label} render {j} position/endpoint")
            need(r.get("block_events") == [], "render block I/O")
            total_pcm += expected
        outputs.append(total_pcm)
    need(outputs[0] == outputs[1] == outputs[2], "subdivision changed logical output")
    return True


def digest_plan():
    return hashlib.sha256(json.dumps([c.__dict__ for c in cases()], sort_keys=True).encode()).hexdigest()
