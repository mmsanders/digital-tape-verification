# Windows 11 INGEST collection receipt — 20 October 2026

**Disposition: collection completed and receipt verified; full independent INGEST acceptance remains pending.**

Michael authorized the local Verification lead takeover, launcher troubleshooting, and this write-up/return to PM. Inputs: Verification main `5d28b21d2c79d0d2fc46f40cefb22f26a9124e9b`; Product main `6130c8f826e3586dab149e3d4484edb18c04689a`. Current hands-on brief: Product #473. Prior policy continuation: Verification #222 / PR #224.

## Result and identity

- Candidate: `50bc4160f6da527da8c684d05264f99815aaa870`.
- Actual collector exit: **0**; stdout includes PACKET, SHA256 and return instructions.
- Archive: `ingest-win11-packet-50bc4160f6da.zip`, **198,343,663 bytes**.
- SHA256: `e6d3f2b9e60e93bc90a7516e66418da301c4c0dc3a306dfea3e1394a81731ff3`.
- Collector script SHA256: `74e1af2cb91a3f9b418363941c48a60eee972481a32cbb9af22d8f3060318f9e`.
- Kit SHA256: `ffb0f78ac3980fa1bb130f0aff22d53ebb100ed3323a8e50ba62a6ee1819c865`.
- Shipping binary SHA256: `d923613badda95baeb387d5415d5212a5dedb7c5c7144b21874479babd178f5b`.
- Observation binary SHA256: `d544b6f5c82e653842625080a87ac63cb52353aaeca62494dd5d08eedb844d9a`.
- Recorded platform: Windows 11 x64, build 26200, Home/Core, Python 3.12.10; profile INGEST1-AP4.

## Launcher correction

The PR224 instruction block selected a fresh work directory but also refused to proceed when the older October 15 work directory existed. Inspection established that the preserved packet targeted older candidate `c4f94336136b0b91ed7ae0ded0487786fa26dfc0`, with all 1,927 case directories and an unqualified observer. It could not stand in for the requested candidate.

The local correction checked only the selected new work directory for a collision. The old evidence was left intact. Collector, kit, executable identities, actual exit handling and fresh receipt behavior were unchanged. Michael's previously approved RemoteSigned setting applied to the collector child process; no new persistent policy change was issued.

Exact local corrected launcher SHA256: `9f5125dc7023d261a930770d166f1b69cff9a02e0d7136e6605d6de471ee9266`. Before the run, PowerShell parsing passed; the unused selected work directory was allowed while the older directory existed, and an existing selected work directory was refused. The full harmless process-policy control suite was not rerun for this local edit; PR224's historical controls retain their original scope. This receipt is not new readiness to rerun.

## Independent receipt checks actually executed

The unchanged imported `check_pins.py` passed authority, census and closed-file hashes. A separate read-only ZIP receipt checker verified:

1. Archive SHA256 and exit0 receipt.
2. Unique archive member names and absence of absolute/traversal names.
3. Exact candidate and binary identity pins, config/platform hashes.
4. Exact census membership: **1,927/1,927** case records.
5. Expected case exits, config binding, record/native exit agreement and SHA256 of every census case's raw trace.
6. Presence/readability of the case stdout/stderr.
7. Recorded observer qualification, all recorded observer checks true, and all four recorded false-pass controls marked rejected.
8. **1,640** case records contain shipping equivalence marked identical. This is an observed claim in those records, not independent recomputation of every payload.

The initial attempt to launch the collection-created venv interpreter from this desktop environment failed to create its Store Python process. No evidence predicate ran in that failed attempt. The above checks then passed using the bundled local Python runtime with bytecode writing disabled; the collector's original Windows 11 execution remains a separate fact.

## Collector observations, not independently rederived acceptance

The collector summary reports:
- census 1,927 ran; unavailable/missing/expected-exit differences/shipping-observation byte differences all zero;
- observer selftest qualified;
- CSV/PML alignment: **595,954** records/events, zero mismatches;
- session partition: **595,954 owned**, zero unowned or multiply owned;
- zero incomplete native records;
- unchanged transaction diagnostic: zero failures among 1,931 native records.

The collection stderr consists of case progress, including intentionally named error scenarios; nonempty stderr is not itself evidence of collector failure.

## Scope, retention and next owner

**Not performed:** full audio/numerical replay, independent interpretation of every native event, exhaustive ZIP member CRC/large-WAV payload replay, or a full independent rerun of observer/shipping equivalence judgments. No cross-platform, physical-card, exact-shipping exhaustion, full WP16 or Product integration acceptance is issued. Existing visibility and other acceptance holds survive.

Original archive, stdout, stderr, exit receipt and work trees remain retained locally by Michael. The full raw machine trace is not included in this proposed public publication. Cloud-only reviewers do not yet have a public raw-evidence download from this return; any later full review must use the retained files through approved access, not infer acceptance from this report.

**PM return:** change #473's INGEST collection state from paused to received / receipt verified, and retire obsolete policy-diagnostic and collection instructions. No further human commands, card actions or collection rerun are requested. Keep the separate physical A6 method work with Verification #223 / PM #476. The next technical step is a bounded independent disposition of the retained Windows 11 packet and any remaining exact-head INGEST gaps, with existing numerical/source work carried by identity.

This publication/return does not contact or assign Software, alter Product code, or claim package acceptance.
