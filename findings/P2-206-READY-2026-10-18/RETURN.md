# Verification206 — returned transport correction review

Michael manually activated18October2026,11:36PDT. Fresh206 created18:37:14Z to
track the returned corrections; closed204/201/457 remain closed. Product input
5d2e37dd4b08883e1b12ae33be72db4f83d860f4; Verification input
916a21e2b1263d61af916598e68a81453ee988c9. Required four onboarding docs, live206,
Software461 return6251660389 and204 return6251661527 read. ADR186/187 /PM460
pre-routed sequence retained. No subworkers or engine implementation read/change.

Review script e1e06fc599177872b4f5d39d46f59c8952d1c108/tools/win11-kit/win11_packet.ps1,
SHA25674e1af2cb91a3f9b418363941c48a60eee972481a32cbb9af22d8f3060318f9e.
Runbook head2df672a6a51e77da4e3a3da87286ca99dc2db5c0,
SHA2561c2d95491676a185097457dec24d782851e049fbd507358b2eeb63abbe178036.
Binary/transport/profile source remains50bc4160f6da527da8c684d05264f99815aaa870;
script-source and binary-source identities are intentionally separate.

## Exact scope and independent control

Static delta from historical9d850667 is header/policy instruction and immediate
summary exit guard only. All executable body outside that guard is identical;
Procmon, transport, candidate, package/tool guards are unchanged. New summary guard
records actual LASTEXITCODE before any later command, prints diagnostics and exits
that code before ZIP/send. No policy override occurs. The proposed invocation uses
powershell.exe -NoProfile -File; actual policy refusal is a stop, no workaround.
Generic errors no longer promise the custom STOPPED marker.

The unchanged binary kitffb0f78ac3980fa1bb130f0aff22d53ebb100ed3323a8e50ba62a6ee1819c865,
2604482 bytes, shippingd923613badda95baeb387d5415d5212a5dedb7c5c7144b21874479babd178f5b,
observed544b6f5c82e653842625080a87ac63cb52353aaeca62494dd5d08eedb844d9a,
18-member inventory, provenance/version/AP4/source/package/configuration pins carry
from204/PR205 on916a21e. There is no rebuild/hash substitution or new source campaign.

reproduce.py independently fetches/authenticates both exact scripts and actual
pinned summarizerdd18e797, verifies executable-body identity outside guard, then runs
eight Windows controls (original/corrected × complete/missing/exit-mismatch/byte-difference).
Synthetic inputs only; no Product exe, Procmon or device operation. Expected complete
both0/ZIP/send; original failing-summary1 still tail0/ZIP/send (real negative control);
corrected failing-summary1 must tail1/noZIP/noSend, original summary diagnostics and
custom stop retained. This uses204's already-published stop contract, not private
Software assertions. Native child module environment uses Windows PowerShell's own
default modules; no execution-policy setting changes. CI results/retention receipt
will be appended before publication. A Server run is mechanics, not Windows11 proof.

## Returned observations and limits

Software rehearsal39138302218/job117707277552 is WindowsServer2025Datacenter26100.
Actual outer artifact12141536738:201322332 bytes,
SHA25608fc23fdbf1c002ad5dc0406de2a2ea44308304de8b5880f5aa0f2aeca6f9716.
Actual inner packet212991256 bytes,
SHA2569485590db66f953d9bb22290accb2d0ea332d5c6fd80827c1f4cc4117dc1bb30.
Returned metadata/summary-controls authenticate the unchanged kit exes/candidate;
full returned run exits0 with1927/1927, no unavailable/missing/mismatch/byte-difference;
wrong shipping pin exits1/no packet. These are bounded returned mechanics, not
independent full census acceptance. Retain corrected raw rehearsal beyond Actions'
2027-01-16 expiration in Verification release, with exact fetch/hash replay.

Collection readiness permits one actual Windows11 x64/client/build22000+ host run
under ordinary policy with card/reader removed and current tool-authenticity checks.
No new device probe/rehearsal or actual collection is run by Verification here. The
existing narrowly scoped observer selftest is carried unchanged. No Product PR
merge, overall436/WP16/APP/native/Mac/physical/target qualification follows.
Physical read-only A6 remains independently ready; do not repeat earlier physical
pull/load/dump/README/off-card campaigns. Old kit/script evidence remains historical.
If an old packet already exists it is useful evidence: preserve/return it, no
automatic repeat. Reviewed current commands are in WINDOWS-READY.md, to be issued
only after normal CI and this publication's merge.
