# Verification193: corrected Windows method and retained rehearsal PASS

**Overall exact-head Windows capture-method/rehearsal PASS** at Product441
`a50a211679b7893c7ac581d392784191519525d6`. V146-WIN-R3-01 and02 are closed
together. This explicit method PASS plus all four required checks satisfies
193's preauthorization for **Software-owned integration of that exact head**.
Verification does not merge Product code. Physical Windows A6 and full WP14
remain HELD pending the separate actual-card capture. Mac remains separately held.

Michael's16October PDT activation; current Product input
`7b722dc716ad296a2e0664050bb731718b75a371`, Verification input
`fc80e0ece3f84f8c7ad468c695cb22b3d6abd21d`. Required four documents and live
role/Michael queues read. Issue193 updated `2026-10-17T05:52:25Z`, no scope
comments at start. Authority Product446/ADR184; issue192 follows this stop.
DRAFT-10 hashes and A8 engine boundary unchanged. No engine implementation read.

## Exact checks and carried evidence

Checker SHA256 `7cbba051629d56bffd85e715fe34cb909421aa6b105a52c883f383aed10b8d89`.
All four exact-head PR workflows independently SUCCESS: engine38994450318,
integrity38994450349, hygiene38994450320, publication38994450322. Those workflows
do not execute the capture-tool tests; the local executions below are separate.

| Independent execution | Result |
|---|---|
| Unchanged Verification R3 controls,16 cases |16/16 expected outcomes |
| Same original Windows11 capture, all1,232,801 XML events |PASS; exact Software result reproduced |
| Software selftest run locally |193 cases,0 unexpected; six native Linux cases explicitly skipped |

The original98,602,972-byte ZIP remains
`9b23466b502f386bc3c12ac8a6674710d0caf9491358c2c654bb5717d7cbd755`.
Every used member was pin-checked by retained-win11.py before replay. XML SHA256
`e50da0d54c0ab406e49431ff23f189ce28475670358e19dc4978232899f834d8`.
The complete new result equals the committed Software result after normalizing
only the local archive basename. We executed no Windows binary here.
Original source/geometry/identity and Verification-owned raw decoder facts in
PR190 are carried unchanged; the input bytes and residual records are identical.
No redundant raw XML audit or physical rehearsal is requested.

Both512-byte reads at4296015360 retain native OpEnd success/returned-length
evidence. Four target objects and the one target key remain identified. No
target write or unresolved write is reported. All ten post-exit records retain
their exclusions: six unrelated Cleanup/Close, two backing-disk writes without a
target key, and two FileIo writes124471/124519. The latter each retain their
FileObject, FileKey, offset,4096-byte length, stream and exact native identity basis.
They are excluded as positively unrelated streams, never revived as process-owned
events and never counted as read coverage. The prior independent raw decoder
already established their FileKey/name evidence; the name string alone is not proof.

## Why both corrections pass

The classifier now distinguishes missing name evidence from invalid key history.
Explicit FileDelete or conflicting names stay unresolved despite a known Create
path and complete target-key set. Positive target object/key evidence retains
priority. Both previously falsely accepted controls now HOLD.

A post-exit FileIo write is excluded only for an IMAGE target when the same
object/key/name-lifecycle rules positively prove an unrelated stream. Its basis
is retained in the result. This closes our former overbroad rejection; the new
positive control now PASSes. Target, unknown identity and post-exit read controls
stay non-PASS. The raw PhysicalDrive target retains its whole-disk write rule;
there is no image-style exemption for its unrelated named streams. Existing
loss/error, IRP/OpEnd and source/target binding controls remain effective.

The independently authored R3 source is unchanged, SHA256
`17b12a38264f1b4f7c0ea2bb0e0346bfe336d98e6e2e8b44d8c7c5ada121192f`;
controls-result.json records trace hashes and each outcome. The exact source
hash is checked before relying on this reference; old publications are immutable.
The local193-case Software selftest is supplementary and is not described as
our execution of Software's199-case run. Its six released-Linux native cases
were unavailable without TAPECTL and are explicitly skipped in the retained log.

## Ready physical collection and bounded stop

[WINDOWS-READY.md](WINDOWS-READY.md) contains complete reviewed instructions for
one short `verify` with the SAME shipping binary, hash
`82798af2899e9364b9c9bfaa2021daf6cc51ccd0c6562598d50e0a86944bb7a9`, on the
positively reidentified existing card. It records actual process/tracer exits,
geometry/OS/binary identity, raw ETL/XML and diagnostics; all native coverage
gaps remain honest HELD outcomes. Output is on the computer. No provision/load,
dump/pull/README repetition, security change, injection or rebuilt binary.
These are reviewed PowerShell instructions using the existing capture transport,
not a claim that this Linux review executed physical Windows commands.

Post the immutable instructions and their SHA256 directly to Michael447. He can
batch this with later ready Windows INGEST work in one sitting. The future actual
physical return receives its own bounded Verification issue. Close193 after the
published report/ready instructions and direct Software/PM return; do not leave a
waiting issue. Continue192. No Mac method is ready and no Mac run is requested.

## Reproduce

Fetch and hash the SAME original ZIP from Product release `wp14-a6-win-rehearsal`.
Use Product441 at the exact head above and Verification PR190's unchanged source:

```sh
python3 -B findings/P2-R1-WP14-A6-R3-2026-10-16/controls.py --checker PRODUCT/tools/wp14-capture/a6check.py --out controls.json
python3 -B PRODUCT/tools/wp14-capture/retained-win11.py ORIGINAL.zip --out retained.json
python3 -B PRODUCT/tools/wp14-capture/selftest.py
```

retained-result.json, controls-result.json and software-selftest-local.txt retain
the actual executions. No new acceptance gate is introduced. This is method and
off-card rehearsal acceptance only; Windows physical A6, Mac, fullWP14/fullWP16,
app, write-command exclusions, frozen/target/hardware/media holds all survive.
