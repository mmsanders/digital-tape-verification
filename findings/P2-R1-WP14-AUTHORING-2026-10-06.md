# P2-R1 complete WP14 authored package, 6 October 2026 UTC

Verification #146, update 2026-10-06T04:09:37Z. Input Verification
`ce60d348105d4851fa1f449d57e5f0e69a28e403`; normative Product ADR165/#396
`6f362f093435ab1a1501055b3bb1cdbe37a5b04c`. Product main subsequently
`87f01bfeb05aff153668bafdaa1e4abbf28797c7` adds only the PM dashboard in
#398; no new normative input is inferred. Single independent lead, no subworkers;
no WP14 implementation read. All writes confined to Verification.

## Delta preflight result: resolved

P2V001…004 remain carried from ADR164. ADR165 upholds P2V005 and resolves it by
target kind. Regular-file candidate predicate is nonzero 446–507, independent of
signature/CRC. Whole-device predicate is nonzero entries OR 55 AA, after §5.
The original valid CRC-signature fixture is now a clean-bare case; its two-bad-CRC
counterpart stays bare but fails by the engine. Empty/signed zero-table files use
normal engine MOUNT errors, not MBR_LAYOUT. Signed zero-table devices reach layout
findings without mount; zero type bytes additionally produce PARTITION_TYPE under
the existing finding table. Surviving-entry damaged signatures reach MBR_LAYOUT.
No host magic/CRC/TAPEFS validity parser is introduced to choose target kind.

Contract SHA256:
`01305d9cc412a2e518fd7884e5ff99d97ae3498f63c22a5c7b418ec547e0eecd`.
Git blob matches issued `aa020b4946eb76c8260fbc32499c06d90c086af2`.
All six frozen + four ADR164 + one ADR165 input hashes checked. E-1 overlay hash
`0cd814527f1c2a2e2d54de0f7a34e7195cb918262632e07d0b194831bade02a1`
and supplemental manifest linkage remain exact. Type 0x0E / 16MiB / 2KiB and
unchanged starts/engine/API/mirror/migration semantics carried from the prior
exact confirmation. No repeated E-1 or Q-P2-1(a) paper review. No new spec conflict.

## Complete authored coverage/census

Package `tests/wp14_r1`, full table in COVERAGE.md; executable catalog.py:
79 image cases and 11 output controls; 97 Linux / 96 macOS / 96 Windows static
native requests, plus every generated provision replay. Ten original references
and full C60, exact bare/whole/native both-side round trips, native OS README,
UTC/entropy/UTF8/determinism, all safety/refusal/closed-finding cases, literal NULL
and actual non-NULL faults, native barriers/failures/64-bit extents, capacity, A8
identity and completeness gates. Every case is required, not an optional skip.

Native journal replay consumes actual authenticated payloads and flush results,
then executes native verification on representative persistence cuts at each
actual successful flush epoch. Old / unprovisioned / complete-new are distinct;
no old-preservation expectation after destructive invalidation. Count follows
the actual legal trace, not one fixed format-call count. This is not exhaustive
any-subset WP10/media qualification or batching permission.

Original paper/evidence and spec bytes remain preserved. Preliminary invented
guard-bypass/finding-suppression profiles are replaced by actual isolated forbidden
facts/corrupted targets against repaired/clean native counterparts, with unchanged
required expectations. Real no-op/hidden-error/non-NULL/read-error profiles match
Software's supplied interface. Native OS failure/unmount/LBA0 injection are
test-only mechanical setups, not new public APIs. All verdicts stay in Verification.

A8 metadata-only check confirms normative engine tree
`b80a8e54775c5aabad7bc338a6e30db3596b657b`, and seven source/reference/model/
manifest Git objects match the unchanged Verification golden publication. No
implementation blobs were opened. Final imported/bound head, ancestry, full
unchanged Phase1 replays and qualified CI still require Stage2 authentication.

## Actual validation and holds

Historical selftest: 36 checks / 15 controls, carried. Updated amendment selftest:
52 checks / 31 controls. Completion selftest: 97 checks / 166 controls, including
classifier, closed findings/read/mount context, symbol/config absence, altered
metadata, census omission/duplication/replay omission, ordered provision and
payload controls. All are verifier oracle tests, **zero Product/native executions**.
Latest contract-byte tamper control must go red. Compilation/help/pin/whitespace
and green publication CI qualify this source publication only.

Software #392 now has a complete independent authoring target for byte-identical
import and mechanical binding. It must supply ordinary native read extents,
actual raw-macOS unsupported cause, engine mount/info/service observations,
authenticated replay payloads and failed native-call setups at the final head.
Earlier 8GiB Windows capture cannot satisfy 64GB A6; informational `8e79710` is
not a disposition head. No native evidence is fabricated from missing events.

Physical script includes macOS successful full-C60/eject/reinsert/README/ten pulls,
Windows10 readback followed by fresh Windows provision/load/reinsert/README,
native >4GiB capture and A9 timings. **Not script-ready until immutable tested
platform binary release URLs/hashes are supplied**; no physical execution performed.
Named Windows10 and physical A1/A2/A3/A6 remain separate holds; Server2025 is
supplemental. Keep #146 open across stages, dispose final #392 head directly when
posted, and leave integration/witness to Michael. No Product acceptance here.
