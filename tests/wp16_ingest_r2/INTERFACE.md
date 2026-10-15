# Proposed observation files — incomplete checkpoint

Not a shipping adapter architecture or added Product CLI. Software owns the
external descriptor transport, native observation and observation extraction.
Use the real issued ingest command, never adapter-only success. Preserve raw
stdout/stderr, actual argv, exit, build/config/version and observed file bytes.
This checkpoint cannot confer candidate acceptance; review.py rejects pending
P2V16-002 cells and reports only CHECKED predicates after resolution.

## Census and packet

Each of Windows11x64/currentmacOSarm64/Linuxx64 returns the entire CENSUS.json,
including all codec/rate/channel/precision cells and refusal/native scenarios.
No missing/timeout/failed/slow result is PASS. Record exact OS/toolchain/binary
and library/configuration IDs and SHA256s. Inputs use the exact ASSET.json pack;
make folders from descriptor entries with names exactly as declared. Resolve
platform representability cases using actual native filesystem behavior; also
run the representable ordering subset on every OS. Never silently rename names.

Packet `INDEX.json` fields: candidate_sha,binary_sha256,tool_version,profile,
platform (`windows11`,`macos`,`linux`),architecture (`x64`,`arm64`),config_sha256,
cases (caseID→relative record.json). No evidence file may escape packet root.
Each case record: exit,argv,stdout_file,stderr_file,config_sha256,native_record;
success also wav,manifest,before (one little-endian float64 interleaved stereo
isolated pre-gain observation per source, in issued source order). Observations
are actual runtime evidence, not alternate expected outputs selected by adapter.

The pre-gain floats permit independent gain/TPDF residual and input meter checks.
At44100Hz lossless, independent fixture samples must equal them exactly. For SRC,
independently audit declared filter/latency/support/window and numerical vectors;
corroborate pre-gain observations with actual final PCM and reported scalar.
A fabricated/inferred pre-gain file alone cannot establish that conversion used
one scalar or correct source samples. No new shipping observability seam is
required: transport may extract diagnostic test observations externally; disclose
its binding and independently demonstrate it on causal bad outputs.

## Encoded intervals and quality

SOURCES.json's encoded presentation counts are independent facts. Its MP3 raw
origin is the disclosed FFmpeg6.1.1 synthesis convention: head=encoder_delay+529,
tail=encoder_padding−529; BMFF generated AAC uses1024-frame packets and its exact
integer edit interval. Those raw-origin numbers are not universal decoder
waveforms/skip semantics. A different decoder must expose actual raw count,
priming, already-applied skips and exact equivalent interval mapping; Verification
must independently approve that mapping before adapting reference-origin facts.
The current script intentionally accepts no arbitrary Software count override.

Validate Xing/Info/LAME-compatible count declarations against scanned frames,
BMFF exact rational endpoints, redundant declarations, complete decode, and apply
trim once. Missing declarations retain every decoded frame; no silence scan.
Original encoder-input length is not a substitute for declared presentation;
some12k MP3 encodes add a few declared presentation samples, retained explicitly.
Bounded fidelity/frequency/phase checks on matched generated sources are separate
from count/trim checks; no promise that independently encoded pieces match raw
source bits or become click-free. Final Stage1 must finish those observation
bindings and adversarial interval cases before import.

Profile declaration: pinned decoder/resampler/meter/build implementations and
versions/config hashes, reduction/FMA/SIMD/thread choices, scalar/gain refinement,
PRNG, FIR/reconstruction coefficients or exact mathematical design, support and
latency. The reference true-peak profile is16x Kaiser14 sinc,256 input-frame
half-support with zero extension; SRC A=(width48,cutoff.88,Kaiser10),
B=(width64,cutoff.90,Kaiser14), taps2*width*max(up,down)+1, compensated latency,
exact nearest/half-up output count. These declarations describe references only.

Use actual source and final PCM meter captures. Independent final integrated
loudness/peak and source scalar constraints are in audit.py. Calibrate the actual
candidate meter, not merely this reference. True-peak qualification includes
finite endpoints/impulses/random vectors with independent sinc reconstruction;
no sample-peak-only proof. Preserve final joined-peak measurement and named
unsafe-boundary refusal without changing neighbouring gains.

## Native transaction evidence

`native_record` fields: scenario,exit,complete,raw_trace_sha256,observer_selftest,
raw_review,events,dest_after,owned_stage_after plus scenario facts
(diagnostic_ok,competitor_unchanged,unrelated_unchanged). events have contiguous
seq and op; stage_create also exclusive/adjacent booleans. Dest snapshots are
sorted complete file lists. Normalized names include preflight_complete,
sources_revalidated,stage_create,output_open,audio_flush_close,
manifest_flush_close,publish_dir_noreplace,source_mutation_detected;
publish_file,device_open,preflight_disk_scratch are disallowed events as relevant.

These are normalized facts, never substitute logs. Bind raw complete native
observer output, process/tree identity, exit/readback/hash snapshots and operation
mapping. Demonstrate observer positive visibility and deliberate forbidden opens
before absence claims. Empty/truncated/BEGIN-END-only traces fail. Verification
independently reviews raw evidence; `raw_review=PASS` is a reviewed state, not a
Software self-certification. Keep raw-review decisions separately attributable.

Prove no output/stage open before FULL decode/order/trim/numeric/capacity
preflight, no preflight disk scratch/device open, per-pass source identity/SHA
binding/mutation refusal, exclusive adjacent stage containing only the two files,
both flushed/closed before exactly one no-replace directory publication. Existing
DEST and concurrent competitor remain unchanged. Inject each enumerated I/O
error; remove only owned unpublished stage. Kill at each cut, including after
publish: DEST is absent or COMPLETE pair consistent with boundary, never half;
identifiable orphan stage may remain. Preserve unrelated sentinel directories.
No power-loss durability claim. Native adapter cannot mark inaccessible evidence
PASS; no virtual/synthetic substitution for required native cases.

## Relations and remaining review

For EACH actual profile, compare repeated runs, relocation, per-source standalone
vs batch slices (including repeated source after different neighbours), different
target labels and folder splits. Changed target changes only corresponding
manifest options/counts; PCM/unchanged source records retain identity. Every
source resets decoder/trim/filter/meter/gain/dither. Cross-platform same-profile
full WAV+manifest equality is mandatory for identical logical inputs/options;
record source/profile/command identity before comparing bytes. Different profiles
are judged independently, not against each other's waveform hashes.

Stage2 checks complete census/raw/native/mapping/profile/licence/calibration and
relations alongside automated manifest/audio predicates. No self-reported summary
counts, profile strings, manual PASS flags or synthetic selftest establish shipping
behavior. Final success summary must visibly and truthfully report peak-limited,
unmeasurable and gapless-unknown source counts. This checkpoint preserves the
interface proposal; final Stage1 still needs those checks/control qualification
completed and frozen. Real-card/fullWP16/WP15 remain held on WP14 physical A6.
