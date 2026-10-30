# C2 human return: cartridge PASS; one presentation finding

29 October 2026 PDT. Verification370 Stage B, activated directly by Michael with
his completed C2 return in the Verification chat. Product input main
`1d341573989d1d768a718371bd6af2b6c2b74b51`; Verification input main
`2a638434e658521de74d9d851aad8f5654d9958b`. Both refs fetched. Live issue370
(updated2026-10-29T15:41:46Z), its scope updates, and canonical four read at the
Product input ref. The older local Product checkout is not the normative input.
APP-1 at that ref, ADR-195/196, the issued C2 checklist and the published C1
clearance control this review. No new Product build, implementation inspection,
native execution, physical test, trace or subworker.

**Real-card C2 make/verify/dump/pull/remake outcomes PASS. G1 and G5 PASS on the
exact candidate. Required G3 messages and pull recovery PASS with existing CI.
G4's no-lists criterion and four-state layout PASS, but complete APP-1 presentation
acceptance is HELD on F370-1 and an unconfirmed native-usability observation.**
Do not declare all G1/G3/G4/G5 complete or clear G2 from this return. No new data
integrity or safety failure is observed. This is a small presentation closeout,
not a reason to repeat the successful destructive card session.

## Inputs and privacy

Michael supplied `Digital-Tape-C2.zip` and `evidence-C2.zip` directly in chat.
This supersedes the checklist's old return destination and supplies Stage B's
input without requiring a repost on Product628. Notes say administrator account,
Keep card chosen once, removal at erase confirmation returned "Put a card in"
without UAC, and everything went as anticipated. His direct message says the run
went fine. Follow-up confirms normal launch: first-open Windows consent, no
blocking on the subsequent launch; no unexpected console flashes, stalls or
automatic retry, and successful remake after one new UAC prompt. He did not
understand the editing/polling question, so that is **unconfirmed**, not a pass or
an observed failure. Exact UAC wording beyond the named tool is not retained.

Michael identifies the same Transcend reader as previous runs. Repository identity
is **TS-RDF5 SD Transcend**, USB, as in
[the October14 physical disposition](../P2-R1-WP14-PULLS-2026-10-14.md).
The current app shows63GB. Historical physical evidence records62,537,072,640B;
this is contextual equipment provenance, not a fresh C2 disk/CID measurement.
The checklist names the expendable PNY card; the C2 packet does not independently
record card SKU/CID. No media qualification follows. Elapsed session time is not
reported and is not used to infer performance.

| Private original packet | SHA-256 |
|---|---|
| Digital-Tape-C2.zip | `5f7a3a13755c725675ade37dc2fbadc46a54507047e898eb0a03f12d2b8d208f` |
| evidence-C2.zip | `dfc39269f34c598d5122a2238182baebc729e9c21638070fd4be59373863f0f8` |

Raw screenshots include personal account information and the WAVs contain user
music. Originals remain in Michael's private workspace; no public release upload
or tree inclusion. [AUDIT.json](AUDIT.json) records every returned member's hash
and length plus the independent byte judgments. This public record cannot replay
private screenshots or audio without Michael's originals. `audit.py` consumes the
two original private ZIPs directly, read-only, without extraction or Product execution.
BUILD.json's historical "not cleared" description records build-time scope; it
does not override the later independent C1 clearance or issue authority.

## Identity and G1/G5

Exact cleared source **`5101e3f32f259beeca91dd829f83d60edd6c2a22`**, integrated by
Product `ea54a41850a37335ca857486b24d15ea1583caf1` with an identical root tree.
Current Product app tree remains `fd7032d580e13d668c67c519508edcca25eb643f`.

| Item | Independently checked SHA-256 |
|---|---|
| Cleared candidate ZIP | `b8a689cfbe926202b6d982dcdc5e5eaaa810d13a180556381d04811f9177ceab` |
| Returned digital-tape.exe | `aafb1f3444a9ddcaee599d3c1efb4dcc7e4d78dae82a0d61913abc25b80ad667` |
| Returned tapectl.exe | `0d92bee784c25a41b96c7a864a50d8199c1a2ae6361f225e8b54b303b7f53477` |
| Returned ingest.exe | `3895f3f356c91b8a9fe870c33694da64bf2765df308bef118d657c1be4bb9a20` |

The hash screenshot truncates its hashes; it is not sufficient alone. Round1
review directly hashed Michael's original download/executables and matched all
four full pins. This final audit hashes all three returned executables and BUILD
head/member pins, and reauthenticates the retained cleared CI candidate ZIP.
The original desktop download ZIP is no longer present at review time; the audit
does not pretend the retained CI reference is a second copy of that download.

`winver.png`: **Windows11 Home25H2, OS build26200.9711**. App runs and completes
Make on that machine. `launch-digital-tape-exe.png` and `run-anyway.png` show the
initial SmartScreen unrecognized-app prompt, then its per-file Run anyway option.
The earlier round stopped there; continuation followed exact-byte authentication.
No machine security-policy change was instructed or observed. Unsigned family
builds are expressly allowed by APP-1 §7: this friction is not a G5 failure.

`post-erase-windows-warning.png` is **Open File – Security Warning**, naming
`tapectl.exe`, Unknown Publisher, Run/Cancel. It is not a UAC screenshot and does
not establish UAC text by itself. Michael's follow-up to the explicit normal-
launch/only-tapectl-elevation question supplies the human observation; successful
make and the UAC-decline screen corroborate the route. The accepted C1 static
check/negative control, asInvoker resources and Medium-parent evidence carry.
**G1 PASS under ADR-195; G5 PASS on this exact Windows11 build and candidate.**
No runtime device trace or stronger mechanism proof is claimed or requested.

## Manual screenshot disposition

All19 PNGs were inspected directly. Their hashes are in AUDIT.json; filenames
below identify the private originals, not public image links.

| Observation | Returned evidence and result |
|---|---|
| Empty | no-card: blank label,0min0s, zero bar, Put a card in, disabled Make. PASS. |
| Single card | card-ready: Card ready(63GB), no picker, blank label and Make disabled. PASS. |
| Check/ready prerequisites | loading-music: Checking the music, disabled Make; music-checked:3min1s, still blank label/disabled Make. Erase/making screens show C2 Music supplied and the successful Make route. No separate fully ready enabled-button screenshot; reachability is witnessed by erase/Make plus StageA72 current Bridge rows. |
| Erase decline | erase-modal: exact warning, Replace and Keep card. Notes confirm Keep card once; no failed outcome reported. |
| Making | making: one progress bar, Copying the music; no interactive lists/player/library. close-during-make: Wait until the cartridge is finished. PASS. |
| Done | cartridge-made and remake-after-pull: correct ready/take-card-out sentence and Make another/Start over. PASS. |
| File drop | single-song: correct folders-only sentence, disabled Make, nothing added. **No Show details control visible; F370-1.** |
| Too long | too-long:70min2s of60min;10min2s too long sentence; full red bar and disabled Make; Show details available. PASS shown facts. |
| Nonmusic | nono-music: names test-music-short folder and instructs songs-only; disabled Make; Show details available. PASS shown facts. |
| Declined UAC | cancel-UAC: computer-said-no/card-wasn't-changed message, retry offered and Show details. Human confirms no automatic retry. PASS. |
| Card missing at erase | Notes: remove then Replace gives Put a card in/no UAC. PASS human outcome. |
| Pull during load | pull-test: card-taken-out sentence, Put a card in, disabled Make, Start over, Show details open. Raw diagnostics include CARD_CHANGED, removal during load, ERROR_NO_SUCH_DEVICE; card check0offered. PASS. This is not proof that the partial card was usable or unchanged. |
| Remake | remake-after-pull Done plus successful second verify/dumps; human confirms one new UAC/no stall/retry. PASS. |
| Native interaction stability | Open details is visible in pull-test. Selecting/copying while polling, label caret/focus stability and unrelated error persistence across poll updates are not established by a still image or the human answer. UNCONFIRMED/UNRUN; existing component tests carry only their component scope. |

No screenshot shows a track/file/folder/card list, playback, library or tag editing.
The four APP-1 states and actionable messages are present. Existing28 exact-head
G3 Bridge rows (16 real child-origin,12 app-origin) and their negative controls,
plus the real human error cases, support the G3 outcome predicates. This does not
waive the remaining presentation requirement below.

## F370-1 — single-song rejection omits Show details

**Small APP-1 §6 / checklist4 presentation discrepancy; no data-loss observation.**
`single-song.png` shows the folders-only error, disabled Make and Start over, with
ample visible space beneath. There is no Show details button. The same packet's
other Problem screens do show it. APP-1 §6 says every Problem state has Show details;
checklist4 explicitly asks for the sentence and Show details for the file-drop case.

This is the exact native presentation question left open in
[C1 correction1 G3-D1](../P2-364-CORRECTION1-2026-10-28/DISPOSITION.md#g3-d1-verifier-correction-not-a-new-product-requirement).
That correction rightly permits empty child stderr for a zero-child rejected
drop, but expressly did **not** waive APP-1 or approve an unseen native screen.
The C2 screenshot now supplies that screen. Do not manufacture stderr, demand a
fictional child invocation, or silently reinterpret this notice as exempt.

**PM owns disposition:** either explicitly clarify that the zero-child folders-
only notice is exempt from Show details, or issue one bounded Software presentation
correction under the current contract. An explicit exception seems proportionate
for a notice with no child stderr, but Verification cannot issue the spec change.
Also decide the minimal closure for the unconfirmed native editing/details row;
do not repeat make/verify/pull merely to exercise a text selection. Until resolved,
complete APP-1/G4 presentation acceptance and G2 clearance remain HELD.

## Actual cartridge bytes

Both verify files contain exactly OK and exit=0; all four dump logs contain exit=0.
All four actual WAV files were independently compared, not just their printed
hash transcripts. **Each is31,752,236bytes, canonical44-byte RIFF/WAV header,
7,938,048 stereo frames,44,100Hz,16-bit PCM,180.001088435s.** A/B in each session
and first-versus-remake are byte-identical, with SHA-256
`b0da0c23bc8263924d95c2f8bde8072f7c77a69f83b6318b3f841231acb166ad`.
Both length and full-hash transcripts match those bytes. The UI's3min1s is
consistent with rounding fractional seconds up; it is not a180/181s mismatch.

No source-music comparison or listening claim is made. G2 still includes its own
audible playback observation. These results show successful cartridge verification
and deterministic duplicate sides after a real interrupted load and remake; they
do not qualify power-loss atomicity or hardware performance.

## Replay, return and stop

Private replay:

```text
python -B audit.py PRIVATE_PACKET_DIR --candidate CLEARED_REFERENCE_ZIP --out RESULT.json
python -B audit.py --selftest
```

Actual private audit PASS is retained in AUDIT.json. Six synthetic negative controls
reject differing side payload, truncated WAV, wrong rate, failed verify, missing OK,
and failed dump; valid PCM and UTF8/UTF16 logs pass. Public CI runs these **audit
controls only**, not Michael's private hardware/audio/screens. Existing C1/StageA
evidence is not rerun or mislabeled as new human evidence.

Publish by ready PR and merge commit after green CI, return on370, close370 at its
assigned defect-return stop. PM is the next owner for F370-1 and the small native
observation gap, and for Product status/628 synchronization. G2 is Michael's later
unaided witnessed record, not Verification sign-off. No Product edits or next-round
kickoff are issued here. StageA supersession and WP14/WP16 acceptance stand.
