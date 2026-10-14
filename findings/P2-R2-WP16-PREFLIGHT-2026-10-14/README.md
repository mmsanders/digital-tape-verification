# WP16 contract feasibility preflight — Verification #165

**14 October 2026 UTC. Recommendation only; not an issued contract, executable
acceptance package, implementation review or Product PASS.** Independently authored
without opening Product engine, host, ingest, design or implementer tests.

Inputs: Product assignment baseline `46b48edd6210e541adf3d3e64ec5fd691c2a75f9`,
current Product main/ADR-176 `b0d0847b85cee6eac4b2624f9835052a950b902e`,
Verification main `6899cf7b56decfbb9bf8fef6c5f2825513697c37`;
issue #165 updated `2026-10-14T02:13:22Z`. Required agreement/status/charter and
WP16/D3–D5/P2-R2 read. PM #384 owns issuance; #146 exclusively retains WP14 residual
physical review. Windows 11/current macOS/Linux CI remain the named platforms.

## Finding and recommended decisions

The package is feasible if PM distinguishes **exact structural invariants** from
**numerically bounded audio quality**. Literal I3 and the lossy continuous-tone
reading of I4 currently include impossible expectations. D4 already selects quieter
peak-limited songs; make that exception explicit rather than requiring every source
to reach the target. Arbitrary song endpoints and independent per-song gain cannot
guarantee click-free waveform continuity without a fade/crossfade, which D5's exact
concatenation does not authorize. Gapless means no inserted/deleted frames, not
lossless recovery or a guarantee that arbitrary endpoints have matching amplitude.

All defaults below are proposals requiring PM issuance. Alternatives identify real
choices, not permission for Software to pick a different contract silently.

| Decision / criteria | Exact recommended default | Alternative and consequence |
|---|---|---|
| C1 format scope, I1 | Publish the positive container/codec matrix below; inspect content, not suffix; refuse whole request on any unsupported/encrypted/corrupt source, naming path and reason | Broad decoder-supported scope makes portability and DRM refusal undefined; extend only by an explicit matrix revision |
| C2 conversion order, I2/I3 | Decode and trim declared codec delay/padding → mono duplication or preserve stereo → isolated resample to 44100 floating PCM → measure that stereo source → one constant gain → TPDF/16-bit quantization → measure final source and assembled output | Meter mono before duplication changes loudness by about 3 LU; normalize before resampling can miss reconstructed peaks |
| C3 target/peak, I3 | Finite gated loudness: target −16 ±0.5 LUFS only when feasible under the ceiling. Initial gain in dB `min(-16-L, -1-P-0.1)`; 0.1 dB is proposed meter headroom, not a relaxed ceiling. Recompute final measurements and reduce the SAME source-wide scalar if necessary. Record all resulting exceptions | Requiring −16 for peak-limited sources contradicts D4; dynamic loudnorm/compression/limiting is prohibited |
| C4 undefined loudness, I3 | All-zero source: exact zero PCM, 0 dB gain, loudness/peak JSON null with status `digital_silence`. Nonzero source with no finite gated result (including <400 ms or entirely gated out): no boost; gain `min(0,-1-P-0.1)`, status `unmeasurable`, record reason; still enforce final peak | Refuse these inputs by name; never invent −16 measurement or substitute an ungated meter without issuance |
| C5 state/join, I4/I6 | Every source is a standalone conversion: reset decoder, resampler, meter, gain selection and dither. Flush/truncate to exact declared output frame count; concatenate final PCM payloads. No join fades, shared resampler state, or album-wide gain | Stateful resampling may improve a split waveform but violates standalone byte identity; album normalization changes D4 per-song policy |
| C6 delay/padding, I4 | Use explicit validated metadata for lossy trim; record raw decoded frames, leading/trailing discard, evidence kind and effective frames. Missing metadata: accept untrimmed with `gapless_unknown`; invalid/contradictory metadata: refuse. Never infer padding by scanning silence | Strict refusal when metadata absent guarantees known trim but refuses common raw AAC/legacy MP3. PM must select and qualify the I4 claim |
| C7 TPDF/silence, I2/I4/I6 | Exact proposed PRNG/quantizer below; reset per source, independent stereo channels, duplicate quantized mono to guarantee L=R. Entire digital-silence sources and interfolder gaps bypass dither; gaps are exactly 88200 stereo frames/352800 zero bytes | Dithering gap buffers violates digital silence; resetting only per job violates standalone identity |
| C8 order/selection, I5 | Explicit ordered folder arguments; flat immediate regular files only, no recursive traversal or symlink following. Unsupported files cause named refusal; no hidden implicit skip. Natural comparator below; preserve folder argument order; empty folder refused; duplicate folder argument refused | Recursive flattening, ignoring art/hidden files, or globally sorting folders needs a separate issued selection rule; no music-manager expansion |
| C9 length/transaction, I7 | Exact frame arithmetic below; include folder gaps. Preflight full decode/count and validate all sources before writing any output/staging files. Overlength refuses without output and reports exact extra frames plus rounded-up mm:ss. No overwrite | Header/bitrate estimates miss padding/rate rounding; truncation to fit violates I4 |
| C10 manifest/determinism, I6/I7 | Versioned canonical UTF-8 JSON with explicit schema below; same ordered source bytes + logical names + options + build-profile ID produce identical WAV/manifest across supported machines. Define a scalar/reference FP path or prove optimized paths identical | Repeatability on one host alone is cheaper but is a narrower promise than portable bit identity; PM must label it explicitly |
| C11 numeric fidelity, I2/I8 | Propose ≤0.1 dB passband error over 20 Hz…min(18000 Hz,0.4×input rate), ≥80 dB alias rejection relative to the input tone for steady-state tones at/above 22050 Hz and below input Nyquist when downsampling (exclude filter transients), no frequency/time shift, and calibrated loudness error ≤0.1 LU. Use a true-peak meter with declared maximum under-read ≤0.1 dB and accept only its reading plus that bound ≤−1 dBTP. Permit different documented conforming resamplers; byte equality only for repeat/standalone structure and issued exact quantizer | Choosing one library's output bytes as universal truth incorrectly rejects other conforming filters |
| C12 assembled peak, I3/I4 | Measure true peak of final joined PCM, including joins and gaps. If join reconstruction exceeds −1 dBTP, refuse with boundary/source names; do not silently change gains based on neighbours | A uniform per-source headroom sufficient for all joins must be independently justified; context-dependent gain or inserted fades violates standalone identity |

PM should issue C1–C12 together. In particular C4, C6, C8, C10 and C12 are user-visible
choices. No purchase or Michael physical action is needed for these engineering defaults.

## Proposed positive matrix and refusal semantics (C1)

| Container | Named codec scope proposed for first contract | Explicit exclusions needing PM decision if desired |
|---|---|---|
| RIFF WAVE `.wav` | PCM unsigned 8/signed 16/24/32-bit, IEEE float 32/64-bit; extensible equivalent with supported mono/stereo layout | RF64/Wave64, ADPCM, μ-law/A-law, ambiguous channel masks |
| AIFF `.aif`/`.aiff`; AIFC `.aifc` | Signed PCM 8/16/24/32; AIFC NONE/sowt | Compressed AIFC; unsupported endian/float variants |
| Native FLAC `.flac` | Lossless integer PCM 8–32-bit | Ogg-FLAC; unsupported sample precision/profile |
| MPEG audio `.mp3` | MPEG-1/2/2.5 Layer III, CBR/VBR | Layer I/II, free-format unless deliberately supported |
| ISO BMFF `.m4a`/`.mp4` | One AAC-LC audio stream; no encrypted sample entries | HE-AAC/HE-AACv2, ALAC, video/multiple audio streams, protected entries |
| ADTS `.aac` | AAC-LC | ADIF/LATM/LOAS, HE profiles; no inferred gapless information |

Proposed channels: exactly 1 or 2; preserve stereo order, refuse others with no downmix.
Proposed decoded rates: 7350, 8000, 11025, 12000, 16000, 22050, 24000, 32000,
44100, 48000, 64000, 88200, 96000, 176400, 192000 Hz when valid for the codec.
Rates outside the set, changing-rate streams and zero-frame inputs are named refusals.
This is a proposed bounded interpretation of D3, **not a claim that D3 authorized
excluding HE-AAC or all uncommon WAVs**. PM must ratify/extend profiles before tests.

Decode to completion; reject nonfinite floating samples, fatal decode errors,
truncation/CRC errors and malformed metadata rather than publish concealed recovery.
A decoder's concealment-success exit is insufficient: contract needs an observable
strict-decode/error policy. Sniff supported containers even with misleading extensions;
a `.wav` containing unsupported bytes is refused. Never silently skip a source.
Refuse recognized encrypted/protected containers explicitly without attempting keys;
unknown/corrupt data may be called unsupported/corrupt, not positively DRM-free. There
is no reliable general claim of detecting every proprietary DRM scheme by filename.
Legal generated protected-entry fixtures can test detection without owning DRM music.

## Precise proposed audio rules (C2–C7/C12)

Use ITU-R BS.1770-5 integrated loudness/true peak and EBU Tech 3341 V4 gating; D4's
−16 target is a Product choice, **not EBU's −23 broadcast target**. Measure duplicated
mono as stereo, without an additional dual-mono compensation. One gain for both stereo
channels preserves image. Measure per-source before dither for gain planning, then
measure final quantized per-source PCM for the asserted ±0.5 LU/−1 dBTP results.
Also meter the complete assembled output for C12. Sample-peak checks alone do not
establish dBTP. Meter error/oversampling profile and a conservative acceptance decision
near the ceiling need issuance/calibration; proposed bounds are engineering defaults needing independent fixture preflight, not measured capability; 0.1 dB margin alone is no proof of meter accuracy.

For example `L=-30 LUFS, P=-2 dBTP` permits roughly +0.9 dB, not +14 dB;
output near −29.1 LUFS is correctly peak-limited. If original peaks already exceed
−1, attenuate even when the song is quiet. Absolute gating can change the participating
blocks after gain: remeasure instead of assuming `L+gain` is universally exact.
Never pad short sources merely to manufacture a gated measurement.

TPDF proposal: non-noise-shaped triangular dither in quantizer LSB units. Per-source
32-bit xorshift state starts at `0x6D2B79F5`; each draw performs `s ^= s<<13`,
`s ^= s>>17`, `s ^= s<<5`, with unsigned modulo-2^32 after each operation.
Map each draw to `u=(s+0.5)/2^32`. Quantize `32768*x + u1-u2` by nearest integer,
ties to even; output signed little-endian 16-bit. Stereo draw order is frame, L(u1,u2),
R(u1,u2). Mono uses one pair per frame and duplicates the quantized result; both
standalone and batch use the mono path. Refuse unexpected overflow, never hide it by
saturation. Apply this rule at every final floating→16-bit reduction (even if source
was 16-bit but gained/resampled); bypass only exact all-zero sources and inserted gaps.
An integer bit-preserving fast path would be a different PM option. Fixed reset seed
is independent of path, job order, neighbours and target length; it intentionally
makes repeated identical sources identical. The library must expose the required
sequence or the final quantizer must implement it. Library `triangular` alone does
not promise this seed or PRNG. This exact arithmetic is proposed, not a landed oracle.

For every effective input length N at decoded rate r, proposed output length is
`floor((N*44100 + floor(r/2))/r)` (nearest, half up), with integer checked arithmetic.
Resampler latency is compensated internally; emit exactly that many frames, with
zero extension only as documented filter support outside source boundaries, never as
extra frames. Content near each endpoint may differ from stateful resampling; this
is consistent with isolated conversion. Output join equals the concatenation of
standalone **PCM data**, not concatenation of WAV headers or standalone manifests.

For MP3 require a supported validated gapless tag carrying delay and padding; for M4A
require a supported edit/presentation interval and any needed priming/padding data.
PM should name exact supported metadata families (e.g. Xing/LAME delay/padding;
ISO BMFF edit-list timeline), units, precedence, rational-time rounding and rejection
of conflicting iTunSMPB/edit-list data. Decoder skip information is evidence to apply
once, not instructions to trim again after a decoder already did it. Present metadata
that does not unambiguously give an integer presentation interval is not fabricated
into exact source frames; refuse under C6. Raw ADTS has no general exact-original-length
promise. Manifest `gapless_unknown` prevents claiming unknown delay was removed.
Lossy fixtures can establish exact retained presentation length and absence of
inserted padding; their waveform is not required to equal the unencoded source.
Independently encoded pieces may have boundary artifacts and independent gains;
use matched sustained-tone segments for the positive join demonstration, and keep
fidelity tolerances distinct from frame-count assertions.

## Exact ordering, frame accounting and publication (C8–C10)

Proposed comparator: decode names as Unicode; normalize NFC; tokenize maximal ASCII
`[0-9]+` runs. Compare numeric runs by unbounded integer value; compare text by Unicode
scalar sequence after ASCII A–Z lowercasing only (locale independent). At unlike token
types numeric sorts first. Equal primary keys tie by original NFC name scalar sequence,
then raw UTF-8 name bytes. Prefix sorts before extension of the same token sequence.
Do not apply OS locale, filesystem enumeration order or full Unicode casefold implicitly.
Examples: `1.wav < 2.wav < 10.wav`; tied numeric names `02.wav < 2.wav`;
`A.wav < a.wav`; composed/decomposed `é` tie-break by raw bytes. Refuse unrepresentable
names on a required platform and manifest-normalized path collisions; do not invent
platform-dependent replacements. Test non-ASCII decimal-looking digits as text, case
collisions and Unicode normalization. Logical paths are `folder_ordinal/relative_name`,
using `/`, never drive letters, home directories or absolute dropped paths. Input names
are part of deterministic identity; relocating the same logical folders is not.

Total frames = sum(source output frames) + `88200*(folder_count-1)`. Capacity is the
integer frame capacity derived from target label seconds, `label_seconds*44100`, not
estimated compressed duration. Accept exact fit; refuse one-frame overage. For overage
E report E frames and `ceil(E/44100)` seconds formatted as mm:ss; include e.g. a one-frame
overrun reported `00:01 (1 frame)`. Reject RIFF size overflow before writing: `4*frames+36`
must fit uint32 for a canonical 44-byte PCM header. Header: PCM format1, stereo,
44100, byte rate176400, block align4, bits16, no extra chunks/timestamps/metadata.

Proposed transaction: after all length/decode/error preflight, stage a new output
**directory** adjacent to a nonexistent requested destination, containing `audio.wav`
and `manifest.json`. Flush/close both, then rename directory to destination without
replacement; cleanup unpublished stage on ordinary failure. This yields one logical
publication boundary for the pair; two separate file renames cannot atomically publish
a pair. Refuse existing destination. Process-crash cleanup and filesystem-specific
rename/durability must be specified; power-loss durability is not asserted merely by
rename. Private memory/temp decode before the length decision is allowed only if PM
changes the literal “before writing output” wording to distinguish private scratch;
the proposed literal default does no preflight disk staging and may reread sources.
Bind hashes/stat identity across passes; refuse source mutation instead of mixing bytes.
No card/block device is opened by ingest.

Manifest schema1 proposal: sorted UTF-8 JSON keys, LF newline, no volatile fields;
integer frame counts; finite gain/measurements as fixed six-decimal strings (round
half-even, normalize negative zero); undefined measurements null plus reason enum.
Top-level fields: schema/version, contract ID, build profile, tool version, pinned
library versions/config hashes, meter/resampler/dither profiles, ordered folders,
target label seconds/capacity frames, total frames, WAV SHA256. Source fields: logical
path, source SHA256, container/codec/profile/rate/channels, raw/effective decoded frames,
trim head/tail/evidence kind, output frames/start frame, measured input/output LUFS/dBTP,
applied gain dB, target gain, `peak_limited`, loudness status and gapless status. Gap
records carry start/count. No absolute paths, wall time, random run IDs, locale text or
machine-specific CPU identifiers. Exact profile IDs should differ if actual algorithms
change, not because a user runs on Windows rather than Mac.

Pinning libraries alone cannot ensure cross-CPU floating-point identity. Recommend a
single declared arithmetic/reference path (specified rounding, no accidental FMA or
parallel summation differences), with Windows x64, current macOS arm64 and Linux x64
byte comparisons before promising portability. Otherwise C10 must narrow determinism
to the same build/arithmetic profile; alternate conforming filters are allowed as
separately versioned profiles, not falsely required to match one another's WAV hashes.

## Independent experiments and primary references

Run from repo root:
`python3 findings/P2-R2-WP16-PREFLIGHT-2026-10-14/experiment.py <new-evidence-directory>`.
[Script](experiment.py), [exact argv/return codes/raw text](evidence/commands.json),
[observations](evidence/observations.json), and [SHA256 inventory](SHA256SUMS) preserve
feasibility evidence. Generated tones are authored here and dedicated CC0-1.0; no
copyrighted recording or Product executable was used. Outputs were not human-listened
and are not WP11 goldens. [All generated inputs/encoded files/raw PCM outputs](evidence/reference-bytes.zip)
are preserved losslessly; raw-output member names, sizes and hashes are in command logs.
Source PCM is also reproducible from script. Temp paths in raw argv are historical, not output
manifest policy. FFmpeg 6.1.1-3ubuntu5, libraries and build configuration plus Python
3.12.14/Linux x86_64 are in raw logs. No claim is made about newer library behaviour.

| Observation | Actual result | Inference / limit |
|---|---|---|
| High-crest 2s tone, measured by reference loudnorm | −43.25 LUFS, −1.06 dBTP; reference output −43.21/−1.00 | Raising to −16 is incompatible with ceiling; this is not certification of loudnorm or a candidate |
| 100ms tone / 2s digital silence | Integrated output/input −inf; tone has finite peak | A mandatory finite target is impossible; propose C4 rather than manufacture measurements |
| Two 6001-frame/48k sources resampled alone vs joined | 5514+5514 frames vs 11027, but unequal payload bytes | Isolation changes filter boundary bytes and length rounding; shared state cannot satisfy standalone identity |
| SWR vs SOXR 48k→44.1k TPDF conversion | Both 44100 frames, distinct SHA256 | Different paths need fidelity/boundary evaluation, not universal hash identity; not yet proven conforming to a future quality bound |
| Dithered 2s silence | 88200 frames, 65923 nonzero bytes | Insert zeros AFTER quantization; do not send folder gaps through dither |
| Generated 48000-frame source encoded/decoded locally | MP348000; M4A48128; ADTS49152 decoded frames | Generic successful decode alone does not prove removal of final padding; exact metadata interval must be checked |

Primary references checked 14 October 2026:
- [ITU BS.1770](https://www.itu.int/rec/R-REC-BS.1770): BS.1770-5 (11/2023) is in force; measurement algorithm, not Product target selection.
- [EBU Tech3341 V4](https://tech.ebu.ch/docs/tech/tech3341.pdf), §§2.3/2.6: 400ms gated blocks, discard incomplete last block, true-peak meter accuracy requirements. Supports undefined short-source discussion, not C4's policy choice.
- [EBU loudness overview](https://tech.ebu.ch/loudness): −23 broadcast recommendation; Product deliberately chose −16.
- [FFmpeg loudnorm documentation](https://ffmpeg.org/ffmpeg-filters.html#loudnorm): linear requests can fall back to dynamic if conditions fail. Use a measured constant volume scalar rather than assuming this filter guarantees D4.
- [FFmpeg resampler options](https://ffmpeg.org/ffmpeg-resampler.html): SWR/SOXR/filter and triangular-dither options; no promised Product seed/reset contract.
- [FFmpeg MOV demuxer official source](https://www.ffmpeg.org/doxygen/trunk/mov_8c_source.html), edit-list/skip-sample handling: presentation intervals and decoder priming need interpretation. This is reference-library documentation, not Product source.
- [Xiph FLAC format](https://www.xiph.org/flac/format.html): STREAMINFO/format scope; metadata counts are not permission to ignore decoded errors.

## Post-issuance authoring plan / coverage census

**Zero issued assertions or Product cases today.** After PM issues a complete contract,
author these six coherent rows together before blind exact-head disposition. Counts
are minimum planned cases (34 total), not claimed coverage or a new CI gate.

| Proposed row | Cases | Fixture families / independent observation | Causal red control |
|---|---:|---|---|
| V16-A / I1,I2 | 8 | Generated equivalent mono/stereo WAV/AIFF/FLAC/MP3/AAC-LC forms; rates/precisions/profile selection; malformed/encrypted header and named refusal | Unsupported codec renamed .wav; silent source skip; conceal corrupt tail; mono gain metered before duplication |
| V16-B / I2,I3 | 6 | Sustained tone, stereo imbalance, crest pulse, silence, sub400ms, gated-out low-level source; independently calibrated LUFS/true-peak meter and constant-gain residual | Peak-limited source forced to target; inserted compressor; sample-only peak check; undefined loudness boosted |
| V16-C / I4,I6 | 6 | Isolated vs batch exact payload, split lossless/encoded matched tones with valid metadata, missing/conflicting metadata, two-folder gap | Shared resampler/PRNG state; double trim; lost tail; one inserted/deleted join frame; dithered folder gap |
| V16-D / I5,I6 | 5 | Natural 1/2/10, zero-padding/case ties, NFC collision, non-ASCII, swapped folder arguments; relocate logical roots and repeat cross-machine | Locale sort; global folder sort; timestamp/absolute path in manifest; neighbour-dependent seed |
| V16-E / I7 | 5 | Empty/refused folder, exact fit, one-frame over, rate-rounding+gaps, source mutation/output-failure transaction | Estimated bitrate length; omitted gap frames; write output before refusal; half-published pair |
| V16-F / I8 plus I2/I6 | 4 | Licence census; alternate filter/meters; repeat arithmetic profiles; forged manifest count/version | Unlicensed fixture; hash oracle that rejects alternate compliant filter; stale profile; manifest gain disagrees with PCM |

Do not derive a candidate oracle from the observed FFmpeg bytes. Build legal generated
integer/analytic tone families with exact frame provenance; separately encode lossy
fixtures once and pin encoder versions, hashes and explicit trim metadata. Include
sparse impulses, antiphase stereo, low-level ramps and near-Nyquist sources for filter,
quantization and peak discrimination. CC0/public-domain recordings are optional,
require original licence/source/hash ledger; no new WP11 golden regeneration.

The deliberately different positive path will use independently configured SWR and
SOXR with the **same issued gain/trim/count/quantizer contract**, each with its own
profile and no universal waveform-hash equality. First preflight both against PM's
passband/stopband/aliasing/error bounds and calibrated meter vectors; only then call
them conforming. Compare standalone/batch bytes within each path, exact frame counts,
constant-gain relationships and bounded fidelity across paths. If a checker rejects
one on undocumented library bytes alone, the checker fails preflight. Retain paired
control observations that alter one requirement while preserving others. Meter
calibration vectors establish sensitivity; acceptance from real candidate observations
remains a later blind stage on an immutable exact head.

## Return boundary

PM #384: issue one complete WP16 contract covering C1–C12 and numeric quality/meter
bounds, then authorize parallel host implementation/test authorship. This report
supplies no implementation or acceptance authority. WP14 full acceptance/real-card
WP16 integration remain held on final Windows C60/A9 and shipped-binary >4GiB evidence;
#146 gets current-package residual review priority. No accepted ten-pull, READ1,
native full-C60 or Phase1 campaign was rerun. WP15, hardware/media qualification,
atomicity, <30s target copy, write/async/recording and format freeze holds survive.
