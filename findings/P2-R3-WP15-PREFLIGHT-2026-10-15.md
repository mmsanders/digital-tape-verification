# APP-1 independent contract preflight — Verification #183, Task 2

**Disposition: return for PM correction before Software build.** Four concrete
contract findings below; §3 interface bindings also need completion. This is a
paper preflight with a criterion/control map, not an APP test package, Product
implementation review, native execution or acceptance. No Michael test is needed
to resolve these findings.

Task 1 preceded this review: the any-subset model and controls are authored in
[`wp10_subset_r1`](../tests/wp10_subset_r1/README.md). Its current-engine campaigns
are blocked on the specific Product adapter import in `ADAPTER.md`; no engine
PASS is inferred from model self-tests. Both returns belong on #183 and PM
[Product #384](https://github.com/mmsanders/Digital-Tape/issues/384).

## Exact authority

Read APP-1 and WP-15 at PM PR #437 head
`b113639bae3c12e050bf20e9ab7631cee106a9c1`, as #183 permits before its merge:
[APP-1](https://github.com/mmsanders/Digital-Tape/blob/b113639bae3c12e050bf20e9ab7631cee106a9c1/docs/WP15-APP-CONTRACT.md),
[G1–G5](https://github.com/mmsanders/Digital-Tape/blob/b113639bae3c12e050bf20e9ab7631cee106a9c1/docs/PACKAGES/WP-15.md).
Other normative inputs at Product main
`c6ff868086e3333bb7568e60d3a2f4ec60fd3344`:

- [WP-14](https://github.com/mmsanders/Digital-Tape/blob/c6ff868086e3333bb7568e60d3a2f4ec60fd3344/docs/WP14-CLI-CONTRACT.md), blob `8c8e6d33fcc98ee54fab25f04b7a5f5c10eb0295`.
- [INGEST-1](https://github.com/mmsanders/Digital-Tape/blob/c6ff868086e3333bb7568e60d3a2f4ec60fd3344/docs/WP16-INGEST-CONTRACT.md), blob `712a0696917672afb639475960609b6367c1c7d4`.
- Canonical AGENTS, CLAUDE, STATUS and Verification charter; live #183 and #146.

Verification base `9587317ac4bca4e8164347f0ec62eeb719245cf7`.
Individual lead, no subworkers. No Product implementation or private test source
was inspected. APP-1 expressly controls the older WP-15 files-or-folders and
write-only-device wording: folders only and no app-process device reads are
intentional changes, not new findings.

## Findings requiring issuance

### P2V15-001 — Exact overage has no structured observation

APP-1 §§2/6 require the exact length/overage before Make; §6 decisions use exit
code plus report ID, never free text. INGEST-1 §§4/6 refuses one-frame overage
before output, so that run has no successful manifest with `total_frames`.
APP-1 §3's failure record carries only `t`, `id`, `subject`; its progress counts
have no issued frame unit, terminal exact count or capacity/excess semantics.

Minimal case: capacity 158,760,000 frames (3600 s), input 158,760,001 frames.
Exit 2 plus `{t:refusal,id:OVERAGE,subject:...}` cannot distinguish this from an
input exceeding capacity by 8,467,200 frames. The required rounded-up sentence
differs. Guessing from progress or parsing stderr is not an independent oracle.

PM should issue structured exact integer frame facts for overage (for example
total/capacity/excess), including folder gaps and the existing `ceil(E/44100)`
phrasing. No failed-run manifest, changed arithmetic or audio output is needed.
Controls: exact fit, one-frame over, and different excesses with the same ID;
change stderr wording without changing the app result. Also define whether a
failed check shows an overfull bar or only its error sentence.

### P2V15-002 — Report-file lifecycle conflicts with ingest publication/safety

INGEST-1 §6 forbids opening **any output or output-staging file** until complete
decode/count/validation and requires absent DEST, a two-file stage, and atomic
pair publication. APP-1 §3 requires an appended report for refusals/failures and
background progress. Even an empty-folder refusal needs a report despite never
passing preflight. APP-1 §5 also permits writes only inside temporary DEST and
the confirmed card.

Putting the report inside DEST creates DEST before ingest, or adds a third file
to its issued pair. Putting it elsewhere violates the literal app write scope.
Waiting until successful validation cannot report an input refusal. This is a
no-correct-program conflict under the literal rules, not permission to change
the existing transaction or silently weaken no-output semantics.

PM should issue a narrowly scoped, opt-in diagnostic-report exception and an
app-owned control directory distinct from the absent audio DEST/stage. Define
report-open/append/short-write failure, exit behavior, cleanup and partial-line
handling. Keep no-flag behavior and the two-file publication unchanged. Controls:
refusal creates only authorized diagnostic bytes; no WAV/manifest/stage on
preflight refusal; outside sentinel and concurrently-created DEST unchanged;
report path cannot target a card, source, arbitrary file or followed symlink in
the app's invocation. These are proposed bounded resolutions, not issued changes.

### P2V15-003 — Same path and capacity do not prove same card

APP-1 §4.1 defines sameness as path plus bytes; §5 requires stopping if a card
changes between steps. Two cards of equal capacity in one reader share both
facts. Swap them after recheck/confirmation or between provision and load: the
next child sees the same DEV and capacity. Existing WP-14 policy can accept both.
The app has no media-generation/identity field in `cards`, and it cannot open the
device itself. A cartridge UUID changes during provisioning and is not a stable
physical-medium identity.

PM must choose the enforceable identity/continuity guarantee and route it to the
device-owning tool. It needs revalidation across child boundaries and at the
destructive open, not merely a new app-level comparison before the race. A
platform continuity token or safely retained authorized device session may be
possible; capability must be demonstrated on Windows 11 and macOS arm64. If a
reader cannot detect replacement, issue the bounded policy/refusal instead of
claiming universal physical identity. Do not add a fresh physical witness now.
Controls: equal-size replacement at the same path, removal/reinsert, changed
capacity, and no-change positive; record zero writes to the replacement/foreign
device where the issued guarantee requires refusal. An unchanging clone cannot
be distinguished solely by these published facts.

### P2V15-004 — Not every message can originate in a real tool outcome

APP-1 §6 says each message comes from exit code plus report ID, and §7 requires
**every §6 row** to be driven by real tool outcomes. But §§2/6 require a dropped
file or mixed gesture to be rejected before it is added. No ingest invocation
corresponds to that rejection. Elevation can also be declined before the device
child starts; spawn failure has no child-written report. Fabricating child
outcomes would satisfy a test harness while violating the process boundary.

Issue explicit app-origin events for gesture rejection, spawn/authentication and
card continuity, with real OS/UI negative controls; require real child exit/report
outcomes for actual child-origin cases. Test mixed drop atomically rejects all
additions with zero child/device calls. Native authorization-decline controls
must prove no destructive child started before step 3; post-start failures keep
their different card-state boundary. Do not introduce a shipping fake-outcome
switch or weaken the real-tool requirement for ingest/device failures.

## §3 bindings to settle before independent package authoring

These are explicitly unfinished interface facts, not extra Product defects.
Software's ingest-ID proposal is already contemplated by §3; PM/Verification
must finish its issued mapping before a frozen app test expects exact IDs.

1. WP-14 §5 lists refusal IDs, but §7 mostly gives exit categories, not stable IDs
   for usage/label/capacity/WAV/OS-I/O failures. Publish closed lists per command,
   `verify` finding payloads and precedence (a `READ_ERROR` is both I/O and a
   verify finding), source/boundary subjects, and app-origin events from 004.
   `ingest` logical ordinal paths need a defined mapping to displayed basename
   or dropped-folder name, particularly folder-level and join-boundary refusals.
2. Define progress step names/units, integer ranges, whether monotonicity is per
   step or per invocation, total=0/unknown, and valid sparse/no-progress success.
   Record weights and monotonic app aggregation without requiring a particular
   frequency, elapsed time or engine call grouping. An exact terminal overage
   fact from 001 cannot be inferred from an optional progress stream.
3. Define report per-invocation ownership/truncation versus append and binding
   to the launched child so stale lines cannot determine a new job. A concrete
   failure policy is needed if FILE cannot be written: the only structured
   error channel must not recursively depend on writing that same failed FILE.
4. `cards` must distinguish exact §2 provisioning recognition from the §4.1
   verify-only candidate predicate. Test bare CRC ending `55 AA`, damaged/empty
   MBR and all exact layout fields. Underlying probe errors and insufficient
   privilege need a stated enumerator exit/omission policy; `exit 0 even none`
   alone cannot tell a user no card exists versus discovery being unavailable.

## Criterion and negative-control map

Methods below are independently authorable after corrections. This is a plan,
not a claim any native tracer or app artifact has passed.

| Criterion | Positive observation | Real negative control / limits |
|---|---|---|
| G1 static | Audit app boundary and bundled child hashes; no TAPEFS/engine logic or app device access | Deliberate app-process device open must fail the check. Ordinary filesystem APIs also open temp/source/report files, so a blanket `open`/`CreateFile` ban would reject a correct program; check device targets/data flow, not just a shared API spelling. |
| G1 runtime | Process-attributed native open trace includes app, helper and child PIDs with argv/hash identity; all device opens owned by authorized tapectl children | Controlled app-process read as well as write open is detected. On Windows 11 use native process/open observations; on macOS arm64 qualify a SIP-compatible process-attributed method. Linux CI cannot substitute for those native observations. Zero-event traces alone need a known detected-open control. |
| G2 | Exact-head witnessed unaided run by D6 tester, Michael witnessing, verify/dump success, one attempt, timing excluding load, every hesitation recorded | Independent CI cannot replace the human record. Real-card gate remains WP14 physical A6 plus WP16 acceptance. No witness requested by this preflight. |
| G3 ingest | Real pinned ingest process on generated/licensed inputs: overage, protected header, corrupt/unsupported, folder/symlink/empty, zero-output source/collision; report maps to sentence and correct NAME | Near-boundary admitted inputs, exact-fit/one-frame excess, malformed/unknown report and stderr-text change. Generated recognized protection headers suffice under INGEST-1; no acquired DRM music or universal DRM detection claim. |
| G3 device | Real provision/load/verify results for geometry, policy, read/flush error, removal and verify findings; untouched foreign-disk sentinels and actual I/O observations | Paired refused target and admissible target; wrong-device/continuity control from 003; deliberate no-op failure and foreign-write detection controls. Pull fixture must cause real I/O failure, not just a fabricated UI event. |
| G3 app-origin | Real rejected drop, native auth decline, missing child/spawn failure and continuity event | No invocation for mixed/file drop; no write-capable child before denied authorization. Requires 004 correction. |
| G4 | Empty/Ready/Making/Done/Problem screens on native platforms; label 1–32 UTF-8 bytes, no prefill, exact Make guards, one-card line and 2-second idle poll | File/mixed drop, multi-byte overflow, 0/2+ cards, rapid successive drops/stale results, cancel before/after erase, close/forced termination and stale-temp ownership/symlink sentinels. No lists beyond issued copyable details. Serializing/cancelling background checks is an implementation choice if stale results cannot enable Make. |
| G5 | Install and launch bundled artifact on Windows 11 x64 and current macOS arm64; exact OS/build and app/child hashes, normal app/ingest privilege, device-child elevation | Missing/mismatched child, elevation denied, launch from ordinary install path; unsigned acceptable. Linux build is CI only. Prompt count is an aim and G2 hesitation evidence, not a new binary failure gate. |
| §3 cards probe/policy | Enumerate whole disks, read-only opens and zero writes; exact `{path,bytes,provisioned}` JSONL; exit 0/no rows with none; repeated discoveries | Refuse path/slice, fixed/virtual media, >128 GiB, system/boot/swap, foreign mount; erase confirmation is intentionally excluded. Existing admitted test-only fact route exercises policy; shipped-binary controls establish seam absence and actual refusal, not injected shipping facts. |
| §3 cards refusal controls | Actual shipped command on an available refused device/path; each policy reason also exercised deterministically by the existing test build | WP-14 §5 deliberately refuses Linux loop/virtual devices in shipped binaries. A loop-only CI cannot pretend to furnish every real removable/system/mount fact on both native OSes. Reuse WP-14's paired test-only route and shipped controls, and record native probe capability; if §3 instead requires every native policy reason physically realized in shipping CI, PM must issue a feasible fixture scope. |
| §3 report additions | Real process emits parsed report for each command's progress/failure, with binding facts above; existing no-flag stdout/stderr/exits/output bytes regress unchanged | Bad/unwritable FILE, partial line, unknown ID, stale record, concurrent invocation, nonmonotonic counts, missing optional progress; no device writes from cards/verify. No report parser may alter no-flag behavior or authorize a new target. |
| §3 ordering / independent acceptance | Independently authored tests plus controls before exact-head app disposition, pinned shipped children | Modified child/hash, missing import or missing actual run is held; synthetic controls alone do not accept Product. |

G3 CI images exercise file targets; successful real-device loops use only WP-14's
existing compiled test route and paired shipped refusal, never a new seam in the
released binary. Real native removal/open/elevation observations require platform
fixtures and trace capability; none is established by this paper map. A4's
zero-foreign-write guarantee is checked at the device boundary, separately from
legitimate app-owned temp/report writes once 002 is resolved.

## Return / holds

PM should disposition P2V15-001…004 and issue §3 bindings on both lead issues
before Software's build issue. Full APP tests follow that build issue; none were
authored here. G2 remains dependent as issued. Task 1 execution remains its
separate Software-import dependency; an APP wording correction cannot close it.
No acceptance, rung, engine/format/port/firmware/hardware/media/atomicity or
batching change follows. WP14 A6, full WP16 and WP15 acceptance holds survive.
