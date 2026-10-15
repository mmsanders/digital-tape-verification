# P2V16-002: AIFC sowt precision interpretation

Independent Verification #179, arising during #169 INGEST-1 Stage1 authoring.
This is a contract/fixture-feasibility finding, not a Product defect or candidate
review. No Product implementation, design or private tests were inspected.

Product input main: `8f3c0f0eb3da74186ab8482e22e685c714a7a258`.
Verification input main: `66794e6e2fe5c66488ecfcdc5a8f9a23b0eedc2a`.
INGEST-1 contract blob: `7c6b4c7651eae68f11d30a0b5e7f01b1223916a7`.
ADR177/178 unchanged; all numeric tolerances and the zero-output refusal remain.

The §2 table groups AIFF/AIFC signed8/16/24/32 and AIFC NONE/sowt. A literal
cross-product supplies positive non16-bit sowt cells. But Apple's registered
`sowt` meaning is16-bit little-endian twos-complement. COMM sampleSize24 plus
sowt therefore does not unambiguously describe the intended24-bit samples.

| Generated file | COMM frames | COMM bits | Payload bytes | Frames as registered sowt16 | FFmpeg6.1.1 decoded frames |
|---|---:|---:|---:|---:|---:|
| sowt16.aif |256|16|512|256|256|
| sowt24.aif |256|24|768|384|384|

Both files are immediate mathematical signal derivatives from the independent
writer; no copyrighted music was used. Fixture bytes are dedicated to CC0-1.0.
`observations.json` pins their hashes, structural arithmetic and actual decode
command/results. FFprobe separately identifies the24-bit declaration as
`pcm_s16le,bits_per_sample16,duration_ts256`; that duration field alone therefore
does not prove actual decoded count. The actual decoded floating payload has384
frames. This distinction was caught by sample/count validation before publication.

Primary authority: [Apple sound sample descriptions](https://developer.apple.com/documentation/quicktime-file-format/sound_sample_descriptions)
lists k16BitLittleEndianFormat/sowt as16-bit little-endian. The public
[FFmpeg AIFF demuxer](https://www.ffmpeg.org/doxygen/trunk/aiffdec_8c_source.html)
retains the codec-tag interpretation for PCM_S16LE; this is third-party format
research, not Product inspection. These sources establish ambiguity in the
positive-cell interpretation; a decoder quirk alone would not authorize a waiver.

Requested narrow issuance: specify AIFF and AIFC NONE signed8/16/24/32, AIFC sowt
signed16 only, with contradictory sowt precision refused; or explicitly define an
INGEST-specific non16-bit sowt byte/count interpretation if that is intended.
Verification does not choose that policy. No existing assertion/tolerance is
weakened and no pending cell is silently removed or marked PASS.

The remaining host-only authoring continues. The preserved authoring checkpoint
at `tests/wp16_ingest_r2` records90 disputed cells as PENDING_CONTRACT_RULING. It is
not a complete/importable Stage1 package, a Software implementation acceptance,
or a reason to wait for Michael's physical A6 test. Required native/cross-platform
candidate evidence and all fullWP16/WP15/real-card holds remain.

Replay structural facts with Python3.12:

```sh
python3 -B findings/P2-R2-WP16-SOWT-2026-10-15/reproduce.py
# Optional actual reference decoder replay; authoring used FFmpeg6.1.1-3ubuntu5.
python3 -B findings/P2-R2-WP16-SOWT-2026-10-15/reproduce.py --decode
```
