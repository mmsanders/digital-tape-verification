# Verification204: correction required; Windows11 collection remains PAUSED

Authority: ADR186/187, PM460 and Software461 return to Verification204.
Product input main5d2e37dd4b08883e1b12ae33be72db4f83d860f4;
Verification input9997bc1c388796283dc138d8bf6e6200e02cc390.
Required Product AGENTS, CLAUDE, STATUS and Verification charter and live assignments
read. Individual lead; no subworkers or engine implementation read/change.
Review target tooling5cfcebce61018325786dfb9ebbedae08891e8802; proposed runbook
SHA25693860685c386de8d04d3d4d56c0a34aee439f3804dd52d564a6ff7e2a6ed750f.

## Disposition

No readiness PASS and no new Michael447 collection commands. Two bounded transport
corrections return directly to Software461; no Product merge authorization.

1. Runbook invokes `powershell -ExecutionPolicy Bypass -File`. Software461 authorizes
   ordinary policy/no bypasses. Remove the override, use `powershell.exe -NoProfile
   -File`, and report actual policy rejection if the authorized invocation is blocked.
   Do not change policy or disguise file execution. Initial direct return6251215625.
2. Script9d850667 invokes pinned `summarize_packet.py` without checking native exit,
   then creates a packet and prints the send instruction. The actual summarizer
   returns1 for missing census records, exit mismatches or shipping byte differences.
   `reproduce.py` exercises the exact unmodified summary/ZIP tail with the actual
   pinned summarizer and paired synthetic complete/missing-record packets. Windows
   CI39137772871/job117705698803 independently reproduced summary0/tail0/ZIP
   and summary1/tail0/ZIP/send respectively. A green detector means the known RED was reproduced, not acceptance.
   Require an explicit immediate nonzero guard before packaging, truthful exit/error
   capture, and a newly pinned script with adjacent complete/failing-summary controls.
   Keep valid collected diagnostics on failure, but never send a success-shaped ZIP
   instruction for this failure. Rehearse ordinary policy; no physical-device test
   or collection campaign is requested. A transport-only patch need not rebuild exes.

Generic PowerShell exceptions need not contain the custom `STOPPED` marker, so the
runbook must require stopping/reporting every nonzero/error, not just that marker.
New script/source pin must remain explicitly distinct from binary candidate50bc416.
No source/contract expansion is requested; route any necessary expansion separately.

## Authentication completed

Anonymous download of the actual prerelease kit:2,604,482 bytes,
SHA256ffb0f78ac3980fa1bb130f0aff22d53ebb100ed3323a8e50ba62a6ee1819c865.
All18 ZIP members CRC-valid,3,700,487 uncompressed bytes. Full independent member
sizes/hashes are KIT-INDEPENDENT.json. Shipping848384 bytes/d923613badda95baeb387d5415d5212a5dedb7c5c7144b21874479babd178f5b;
observe956928 bytes/d544b6f5c82e653842625080a87ac63cb52353aaeca62494dd5d08eedb844d9a.
Both version strings `ingest 0.1.1 INGEST-1 arithmetic-profile INGEST1-AP4` in build
receipts. KIT.json authenticates source50bc4160f6da527da8c684d05264f99815aaa870,
treeea0c9ae717a8478ca357fd01186f2a4d912a1193. Build39104751447 attempt1,
job117608086313, workflow4bda3f5fa0afc8bda8e0f9c1427b2596153c49f2,
Rust1.97.0, locked shipping/observe builds. Later tooling changes are documentation.
Different hashes from other same-source builds are retained; reproducibility is
not asserted and old/rebuilt exe hashes are never substituted for these kit bytes.

All15 profile members equal the authenticated rehearsal bytes; all14 coefficient
hashes match their profile declarations. profile/profile.json SHA2569364a862ed33c25591a17f60a375dc5af8583f0edb8b4ce5b23dbfb6ec172fc5
differs from the previously reviewed e75da2ab8b98973f3ce6a97f566b0663fa0406fc218f23bfbc08deba053ead99
only by tool_version0.1.0 ->0.1.1 (replacing that field in current bytes exactly
reproduces the old whole-file hash). No arithmetic/profile retest is implied.
Published inventory SHA25628947fb16fcb99b0d18514043ebe4ece5e9790283598f6c08fef972ffdfdc078
independently matches every member's size/hash; KIT-PUBLISHED.json retains it.

Imported Stage1 tree609a4c819076a2b85b26cc4f3cd254b92caef6de matches Verification's
unchanged package. Script at50bc416 is identical to reviewed tooling head. It pins
run_packet.py d37d63e5b13b2fb64750e0f337f468e0f569630a42f1dfac82f9a96475b6dea2,
observers.py560cc9a592f53e06deb0bdac44b9f56b32b608f8f32ceba558885a49190dc62b,
summarize_packet.py dd18e797210da43021f1bac187bfdeb7b6a5f6ae7e9ae18d3098de8f9cf79f4a;
pins exes and ProcessMonitor.zip477754bf299c9e5b311c5666f7a4a48dfdb21265eaa8f0cca70ef9d9552e3a10,
requires valid Microsoft Authenticode, Python3.12, AMD64/client/build22000/admin,
25GB, fresh private Work, pinned requirements and procmon-parser0.4.0.
No bypass switch belongs in Michael's invocation. No reader/card, hosted Server
rehearsal exception never belongs in Windows11 commands. Existing narrow observer
selftest does not authorize any new device exercise.

## Returned rehearsal and durability

Original Software outer artifact12128173724:200928818 bytes,
SHA256615c6fc86950e2e0dcd8030947eb403ad7809e6d11686fea482f26608545a9b8.
Inner packet212596344 bytes,
SHA256cc51a76875c6564fee90801c2119f1f1750b3ddcc7193d53d94d59dd86ee7de9;
both downloaded/authenticated. Raw metadata is extracted in REHEARSAL-METADATA.json,
with ZIP backslash names normalized for reading. This is Windows Server2025
Datacenter26100/x64 mechanics, not Windows11. INDEX binds both actual kit exes,
1927 records, profile INGEST1-AP4/config profile tree5ff9591f. Returned selftest
qualifies and rejects four damaged-trace controls; partition records590717,
unowned0/multiply-owned0. Job117608260783 records child0, no unavailable/missing/
exit mismatch/byte difference, and wrong-shipping-pin STOPPED/exit1/no packet.
These returned observations are not a rerun or independent full census acceptance.
platform.json's ambient rustc/cargo1.99 differs from KIT build's pinned1.97: it
records collection-host tools, not a rebuilt-binary identity.

The Product kit prerelease is durable, anonymous and exact-pinned:
https://github.com/mmsanders/Digital-Tape/releases/tag/win11-kit-ingest-0.1.1-50bc4160f6da-r39104751447-1
Backup kit/rehearsal Actions artifacts expire2027-01-16. This review's normal CI
additionally retains original raw rehearsal and independent causal receipts in a
Verification release; final publication receipt records the concrete URL and tested
fetch hashes. Large raw bytes stay outside git. No claim that Actions retention alone
is permanent. Existing201/203 source dispositions stand; native Windows11, full436,
Mac/native, full app and physical A6 holds are unchanged. Old6126 kit stays PAUSED;
physical read-only A6 status is unchanged.

## Independent publication receipts

Causal control source485ae48c307adab8e05a3daf8b5bd74b4010e7ab;
normal CI39137772871. Original first/second harness attempts39137568660 and
39137661747 failed because the Python subprocess inherited PowerShell7's module
path. The corrected harness removes that variable case-insensitively so Windows
PowerShell uses its own default modules. No execution-policy setting is changed.
Both actual final child stderr streams are empty; ordinary File invocation returns0
for complete and failed-summary cases. This confirms the unchecked native failure.

Durable release:
https://github.com/mmsanders/digital-tape-verification/releases/tag/evidence-204-485ae48c307adab8e05a3daf8b5bd74b4010e7ab-39137772871-1

EVIDENCE.json pins raw rehearsal212596344 bytes/cc51a768… and independent
controls12153 bytes/a4a5d572742797915d02271d9789fbec2f98f134214e76073c9a4784e8f732a1.
Run `python -B findings/P2-204-KIT-2026-10-18/fetch.py --out /tmp/204 --raw`
to fetch/authenticate both, validate causal result pairs and original source pins.
Without --raw it validates small replayable control receipts and checksum manifest.
Run reproduce.py on Windows to execute the causal pair again; it fetches/authenticates
two original scripts and only creates private synthetic packets. It never invokes
Product binaries, Procmon or device probes. Scope ends at this published correction;
no waiting/polling for Software or Michael. Direct Software return6251307858 adds
summary guard requirements to earlier policy return6251215625. PM460 receives the
merged publication. Michael447 remains PAUSED, no new collection instructions.
