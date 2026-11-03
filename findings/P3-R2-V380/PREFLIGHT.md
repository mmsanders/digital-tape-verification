# V380 Stage A preflight and interface dependencies

Product input/current fetched main: `cc23b87f38a86d44321a99d4147da4529af465f7`,
PM653 merge; PM head `ee47cf8224fa227ccf337d2d8af1e1907879c51b`.
Issue380 updated `2026-11-02T23:08:29Z`, manually activated by Michael.
Parts not ordered. No target, physical, acoustic or card qualification work.

## Revised DRAFT-11

The PM648 revision addresses the specific F374-1…4 proposal wording: descriptive
engine-api sections11/6.2 are named for correction; Record light no longer promises
mechanical release; failed commit retains existing FAULTED/remount outcomes; the
actual scrub MANIFEST schedule is preserved. ADR202/FW1 resolves F374-5 with seven
normal-rate PCM vectors and whole-WAV versus payload distinction. These are
proposal/contract consistency findings, not issuance or exact future bundle review.

Still open: reverse at_start indication/reset; lightest scrub rate/curve in WP20;
speaker mute latency and measurable silence threshold/reference; recording headphone
signal; plug-transition source behavior and settling/debounce; source-supported S2
limit, distance, weighting, signal/duration, uncertainty and independent method.
Hardware supplies S2, Michael authorizes issuance; Verification selects no value.
The proposal's issuance list still names the old P3-R1 preflight issue; current
preflight is V380. PM should carry this return into the exact issued bundle review.
No frozen DRAFT10, engine, golden, crash or safety limit bytes are edited here.

## BE-1

BE1 defines testable report states, exit semantics, incompleteness and provenance
boundaries. It correctly separates offline artifact consistency from actual
hardware evidence and independent acceptance. No specification disagreement found.
The command is fixed; manifest/report versions, file paths, per-case identities,
serial grammar, numeric encoding/units and budget terms are not yet declared.
Software652 had no declaration/return comment at activation. No new checker was
read. Therefore no bundle-shaped positive or raw-transcript fixture is claimed
authored/executed. [The independent case matrix](BE1-EXPECTATIONS.md) is ready to
bind to the declaration; inventing a competing manifest would not test Software's
promised interface. Software must publish that declaration before covered code.

## Rig

Published executable correction regressions cover the preserved public revision3
aggregation interface. New actual-edge/busy/calibration and CID fields are absent;
the [method cases](../../tests/rig_correction_r2/EXPECTATIONS.md) are authored but
unbound, not executed. Hardware651 had no declaration/return at activation.
The old judge blob is identical on Product main and the rejected Hardware80d26364.
Replaying it detects six retained late-corruption gaps, including all four neighbours.
No current corrected circuit/method/judge is disposed. Electrical R374-3/4 and
SPI-only R374-5 remain open. Original Hardware method blob641dbfe2 is carried,
not reviewed again or replaced by inferred changes.

Next owners: Software652 public BE1 manifest/transcript/report declaration;
Hardware651 public corrected method/schema/electrical justification. No waiting
or repeated campaigns. StageB exact-head review requires those named returns.
