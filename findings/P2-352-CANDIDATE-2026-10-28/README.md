# Verification352 — exact612 candidate BUILD/ARCHIVE PASS, bounded task returned

Michael manually resumed the final byte-only stage. Live352 updated2026-10-28T05:24:35Z
and Software612 return6471446998 read; canonical four at current Product main
**fce1d644f03ed1220e40133be0c33bd30e519203**, Verification input
**6fa36426d865f212174d3df1108766d9902dc435**; Started6472306888.
This completes352's issued source/build/byte-audit deliverable. It grants no runtime
or new human task and does not advance7/12.

## Exact candidate and measured bytes

| File | Bytes | SHA256 |
|---|---:|---|
| Digital-Tape-Windows11-x64-replacement-candidate.zip |2552029|f6a908296e26db5eb17e55f89674be263b7b6afd7d6b26a3f2c30e5f721ae3ac|
| digital-tape.exe |5057536|ccae0cf5098aed601fd17b4af1c0d62a33ad28dfb734add1c5df3a67df807c96|
| ingest.exe |889856|3895f3f356c91b8a9fe870c33694da64bf2765df308bef118d657c1be4bb9a20|
| tapectl.exe |493712|44ef26869ba2d01a8a183660a2c7a050d0e7e9ff37c40b727131512739ea6ded|
| BUILD.json |5086|276ebe08d977a2e20d8e90d87641fd6b7c390a5f0fdd244e8c4618ae7946b3ae|
| README.txt |2371|9a8c5c2c3aedd2aa687e3d99a83e1ed9d361ecf5aee2a081fa9b4fa2c5d10489|
| External INVENTORY.json |952|e74d07b9431cf049c656422bf6da0a46f3049a295afc322199c0b620756330d0|
| External MANUAL-TEST-SHEET.txt |3409|5492208a840558927f8faef029be569ec93495b4e9a28c561e29f1f9327a4d28|

The ZIP has exactly the closed five flat members above, no links/extra payloads,
all CRCs and measured bytes/hashes match the inventory and BUILD records. Sidecars
stay outside the ZIP. PE header inspection only: all three are x64/PE32+, the app
uses GUI subsystem2. No image was mapped, launched or invoked. All four compiled
child-pin/version strings occur in app bytes, as does the opt-in literal. This is
not a runtime/behavior measurement. The app is distinct from old564 and old585.

The accepted Provenance::bound_source uses the measured app hash and compiled
child pins to bind sibling BUILD.json to source, rather than embedding a compile-time
source hash. The sidecar agrees with the actual build source/tree and app hash.
No DT_SOURCE_HEAD or diagnostic/test opt-in environment was injected into the
release build. Diagnostics defaultOFF is carried from the exactly cleared source.

## Integration, build order and budget

PR615 integrated the exact cleared7d1fd979 as **fce1d644** at05:35:10Z after
**122/122SUCCESS**, no moved base/rebase. host/app tree
**e658e8b227c8df08ed9cb0dbabc31852cdc48fa8** equals the cleared tree. Source root
6cd08cc09aaeec73d5727aad6e20661a0b639dec, tools/app
be6eecf128a79c8ae5064b5d15330788c9df3bc1, engine
d96b4245e04d74078f8938744b1394c3018516f7 authenticate from Git objects.
The build's Cargo.lock is byte-equal to the integrated source and its recorded hash.
Compiler/toolchain/build argv/env/logs are retained and their hashes are in RESULT.
One unused Refusal import warning is disclosed in the successful release log;
no source change or rebuild is requested for it.

**One compilation attempt / one uploaded candidate.** Run **40703625246**, run_attempt1,
started **2026-10-28T14:12:55Z**, finished **14:17:06Z**, exit0. Independent source
clearance6fa36426 at05:24:32Z and protected integration at05:35:10Z both precede it.
The retained prior-attempts.json is[], the actual RECORD has one attempt, and the
workflow/run/artifact census finds exactly this one612 run, one candidate artifact
and one build-evidence artifact. No second/reproducibility attempt. The max2 budget
does not license another compilation after this successful one-candidate return.

The command was cargo build --release --locked --bin digital-tape on a fresh
app-source checkout. Children were retrieved from authenticated old transports
(INGEST12578829894 and S2tapectl12610149859), measured against the accepted hashes,
and reused unchanged. Neither child was rebuilt or invoked. Their accepted direct
INGEST rows carry by exact binary identity; no unchanged actual row was rerun.

Normal packaging PR CI is separately inventoried in RESULT's run list; **117 checks
SUCCESS, none pending** at review. Test/bridge/interactions builds are not candidate
compilations. No old564 or585 candidate workflow appears in this head's run census.
Source615's earlier test builds are also separate and not relabelled as candidates.

## Independent byte judge and packaging review

audit.py directly ran the unchanged independently published
windows_cards_receipts_r1/candidate.py on the actual archive/record. It PASSed,
including truthful count1, source clearance/integration, child pins, closed layout,
defaultOFF and no-native-acceptance guards. The verifier did not call oldr2 with a
fabricated count1 or use the old585 exception. Three actual-data mutations were
independently rejected: old tapectl pin, false attempt count and promoted native
admission. These are offline bytes only, not new binary execution.

REGISTRY.json is an independently scoped copy of the measured component identities:
allowed claims are narrowed to the carried direct INGEST positive/refusal facts.
It does not promote producer DRAFT native-window/quit allowance into new612 evidence.
Both the original technical registry and this narrow registry pass the frozen judge.
Preview metadata and guides explicitly exclude new-app startup/window/quit, actual
UI, app-driven children, poller/receipt sessions, card handling/Make, fullAPP/INGEST,
CLI A6/G2. The optional sheet grants no permission, does not repeat old564 partial
visual rows, replaces unrun585 and labels every new612 row unexecuted. First-party
receipts are not independent G1/device-absence proof.

PR616 exact **e8f6197540cbf423428c2956a2c37687513a63e4** changes only:
tools/app/package_candidate_612.py and .github/workflows/windows-candidate-612.yml.
The new profile reuses unchanged585 member/sidecar functions, replaces guide/sheet/
metadata with truthful612 identity, and imports the unchanged Verification judge.
App/engine/pins/old packager are byte-unchanged. The workflow separates packaging
tooling from the cleared app-source checkout; actual packager_source is e8f61975
while compiled app source is fce1d644. Its serial budget guard skips future builds
when the candidate exists. No new observer/service/framework or shipping fake path.

**Express narrow packaging integration clearance:** Software may merge exactPR616
e8f61975 through normal current-base CI, reviews and protections with these two
files unchanged, preserving the already-audited candidate bytes. No additional
compilation/reproducibility or new upload is authorized by this return. Verification
does not merge Product code, rerun a build or enable a listener. Functional scope
changes or conflicting integration require independent review. No Product release,
shipping qualification or new native action is implied.

## Retention and replay

Artifacts from run40703625246:

* candidate **12822109981**, API transport digest7bcf05394bb6cafc3e149231bb9302f4d475e2d87eef2d018e0ad3d5807fe8b4;
* build records **12823816475**, API digest a8adcc64189d3634b330ccb630d1849eb38f5dd6f224203fb005462fa819a548.

Both were downloaded once, originals retained in this chat's owned private staging
directory, hashes for every downloaded file in RESULT. API transport digests are
reported as API metadata; the inner candidate ZIP/member/sidecar hashes above were
independently measured. No binary is committed in this findings tree. Actions
artifacts have30-day retention; the local retained copy remains an independent
replay input if remote transport expires. No new public binary release was made.

Download the two named artifacts using gh run download40703625246 into candidate/
and build/ in an owned folder. runs.json/jobs.json are the retained read-only API
census; adjacent audit.py expects these plus the retained artifacts. Run with
--root <owned-dir> --product <Product-git-repo> --out <new-result.json>. It reads
archive/metadata/Git bytes only, never extracts or executes payloads. --self-check
is publication integrity only, not a substitute for the recorded actual byte audit.

## Final bounded return

352 source extension and independently audited usable replacement BUILD/ARCHIVE
deliverable is complete; close352 after direct Software612/PM611/PR616 handoff.
Next owner Software integrates only cleared packaging; PM owns any newly issued
runtime/method/human task against this exact ZIP/app hash. **Runtime remains
UNISSUED.**353's SplitIo blocker, physical/native/session/A6/INGEST/fullAPP/G2 holds,
old originals/STOPs and7/12 remain. No old return reopened, no new selfassigned task,
native launch, human repeat, listener or automatic next-stage continuation.
