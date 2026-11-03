# BE-1 independent case matrix (schema binding pending)

Authority BE1/FW1 at Product cc23b87f. No new checker/private tests inspected.
No executable bundle is claimed until Software declares manifest/transcript/report
grammar. Bind these cases without changing their outcomes before implementation.

Command: `python firmware/bench/tools/bench_evidence.py --offline BUNDLE --out REPORT.json`.
The input must remain byte unchanged. No serial/device connection, flash,
provisioning/disk opening or network. Future execution should block/record these
effects while allowing only the bundle, local reference/tool inputs and output.
Use independently frozen references, never the checker to generate expectations.

| Case / detecting control | Required observation |
|---|---|
| Complete synthetic F1/F2/F5 raw fixtures with internally matching declared files | CONSISTENT for supported facts, physical_run false, target complete false, never target PASS/acceptance |
| All first-session observations absent/not_run | NOT_RUN, complete false; zero exit permitted; F3 pending/F4 deferred visible |
| Each required F1/F2/F5 observation individually omitted | NOT_RUN/incomplete, never omitted-to-complete |
| Exact seven normal-rate cases, raw PCM and independently extracted reference payload digest/frame count | Match only exact side/start/frame/mode/case reference identity; no scrub-at-1x substitution |
| Each of seven: flip one sample, same byte count, updated file hash | MISMATCH/nonzero for PCM, not concealed by internally consistent file hash |
| Whole-WAV hash supplied as PCM hash | MISMATCH/nonzero; file authentication and PCM identity remain separate |
| Frame count changed ±1, truncation, odd/incomplete sample, malformed/truncated serial record | INVALID for malformed supplied representation or MISMATCH for well-formed contradictory content; nonzero and explicit reason, never NOT_RUN |
| Wrong case/reference/side/start/rate/mode/candidate or contradictory candidate across artifacts | MISMATCH/nonzero (malformed encoding INVALID); identify conflicting source |
| Wrong manifest/file digest; missing declared file | Reject/nonzero; no evidence rewriting or dropping failed attempt |
| Correct map/reserve but no actual target instance or painted-stack observation | Missing target observation NOT_RUN, not inferred/zero |
| Actual instance > reserve; engine data+bss+instance >204800; rodata >32768; stack >8192 | MISMATCH/nonzero; report engine terms separately from core/board and count instance once |
| Actual equals reserve and budget/stack equals limits | Consistent numeric boundary when observations/provenance valid; not independent hardware acceptance |
| Negative/nonnumeric/contradictory stack or changed stack transcript vs summary | INVALID/MISMATCH nonzero; omission NOT_RUN; no fabricated zero |
| F5 missing Michael witness, Play/Stop/position continuity, before/after identity or manual verify | Incomplete, explicit reason, complete false; absent observation NOT_RUN, supplied contradictory/failed result MISMATCH |
| Verify supplied failure or changed card identity | MISMATCH/nonzero; no card preservation claim |
| Simulated manifest with actual/physical marker, target PASS or complete true | Contradiction rejected or explicitly normalized to nonphysical/incomplete with reason; no target PASS/complete true escapes |
| Firmware timestamps substituted for GPIO/I2S/instrument F3 evidence | NOT_RUN for target timing; development timestamps alone cannot satisfy timing |
| A mixed bundle with one actual capture and other simulated/not_run required observations | Per-observation provenance retained; target session cannot become complete through simulation |
| Failed attempt alongside later consistent attempt | Both retained and reported with source hashes; later result must not erase failure |

Output must name exact source identities/hashes, tool version, provenance and
per-criterion CONSISTENT/MISMATCH/INVALID/NOT_RUN with reasons. INVALID/MISMATCH
exit nonzero. Report `complete` only for explicitly requested observations, while
required first-session F1/F2/F5 omissions keep it false. Self-reported actual
provenance is only consistency information; raw audit and Michael witness remain.

Declaration requested from Software: schema version, required/optional keys and
types, artifact-relative path/hash rules, observation provenance markers; exact
seven-case reference inputs; raw serial framing/ordering/termination/error grammar;
map/static/actual/reserve/stack field units; F5 continuity/witness/manual-verify
representation; report keys/version/status aggregation and exit behavior. Supply
only public interface and non-behavioral examples before new covered implementation.
