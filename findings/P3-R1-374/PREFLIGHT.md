# DRAFT-11 / FW-1 independent preflight

Authority: Verification #374. Product input
`3826018653e504217f37a16d8864fb0d597e22e6`; Verification input
`1938e65130d338a11404ba5dedae0b1c471203da`. DRAFT-10 remains in force.
No firmware implementation was inspected; no frozen reference was regenerated.

**Recommendation: revise before issuance.** The design can be expressed without
changing engine behavior or golden bytes, but the proposal does not yet reconcile
the frozen descriptive text and existing golden vector it claims to preserve.
Hardware still owns S2 research and Michael owns authorization.

| Row | Independent preflight / test method |
|---|---|
| End of tape | Audio-stop <50 ms from `at_end`, latched key unchanged, end indication until Stop are observable with GPIO/I²S plus key/LED record. **F374-1:** engine-api §11 still says firmware makes Play pop up. Include the descriptive correction in the issued bundle, without changing the engine API/behavior. Clarify whether reverse `at_start` has the same indication; current proposal only names forward end |
| Full while recording | Record until full, retain public error, commit result, LED and cold remount/PCM. **F374-2:** the retained Record-light row still says “at 0 the record button does not hold.” Reconcile it with the new “Keys stay where they are.” Commit failure must retain its existing engine fault outcome; do not promise successful recording preservation after failed commit |
| Depth scrub | Monotonic mapping, signed endpoints, all Play-latch states and both-pressed cases are testable once WP-20 fixes lightest rate/curve. **F374-3:** engine-api §6.2 calls the firmware policy a time schedule; update that descriptive policy reference when issuing. **F374-4:** the existing published scrub-forward golden is `0.25:32000,0.5:32000,1:32000,2:32000,4:16000`, with reverse vectors -1x and -2x. It is not the old acceptance row's 4x→12x over 1.5 seconds. Preserve the actual MANIFEST/reference identities explicitly. No frozen samples need change; do not claim the absent old ramp vector is preserved |
| Output caps | Headphone/aux-out electrical path can retain the existing reference-headphone cap. Speaker row needs S2 value, distance, weighting, signal/duration and uncertainty before pass/fail is defined. Hardware supplies these; Verification does not choose a value. Test boot reassertion and every reachable user setting. This review establishes no acoustic safety acceptance |
| Speaker mute | Headphone insertion and recording are separately testable, including transitions and combinations. Define a maximum mute response time and measurable silence threshold/reference point in WP-19; “silent” alone lacks an instrument decision rule. Clarify the intended recording headphone signal (monitor input or tape playback) before asserting its continuity |
| Record source | Plug detection plus distinguishable mic/aux test tones can verify selection. Define whether a plug transition during recording switches source immediately or at the next arm, plus settling/debounce behavior, before its transition test. Steady-state aux preference is clear |
| Solenoid rows removed | Consistent with no actuator. Verify schematic/BOM and actual controls under the Hardware package, not by a firmware timing test. Remove contradictory release instructions as above |
| Remaining safety limits | Charge window, thermal and deep-discharge limits remain unchanged. This preflight supplies no measurements or sign-off |
| Unchanged engine/TAPEFS | No proposed byte layout, exported API, numeric error, render algorithm or crash outcome needs change. `engine/` remains pinned at d96b4245; DRAFT-11 may update descriptive policy text without licensing engine edits |

## FW-1 acceptance clarifications

**F374-5 (F1 artifact semantics).** FW-1 says every WP-11 golden at 1x and permits
comparing rendered PCM SHA-256 to `tests/golden/SHA256SUMS`. That file hashes whole
WAVs (and source/package files), not raw PCM. Three golden outputs use scrub rates
and cannot be produced by simply rendering the prepared cartridge at 1x. The
package explicitly separates seven normal-rate cases from three rate vectors and
compares canonical WAV bytes on host / extracted payload bytes on target. PM should
state this in FW-1 rather than requiring Software to infer it.

**Partition authority, resolved by existing E-1.** FW-1's TAPEFS §3 reference is
read with the Michael-approved normative overlay `docs/SPEC-ERRATA.md` and its
integrity manifest: P1 type 0x0e FAT16, start 2048, size 32768, P2 start 34816,
remainder type 0xda. This supersedes the base §3 0x0c FAT32 row for whole-card
provisioning. No fresh decision or frozen-base edit is needed. The unchanged
WP-14 independent fixtures are therefore suitable for the firmware partition test.

**F2 accounting.** Guardrail 08 / engine-api §4 scope engine .data + .bss plus the
caller instance. Candidate reports should show these separately from board/core
statics, identify the instance storage and avoid counting it twice. A full-board
RAM number is useful but does not identify those terms by itself. The static gate
does not accept target stack use; painted-stack evidence remains pending.

These are findings to PM. The proposed DRAFT-11 text remains **not in force**;
no purchase, physical operation, firmware integration or output-cap waiver follows.
