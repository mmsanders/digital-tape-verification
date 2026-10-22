# Verification269: both complete cardinality lemmas PROVED_CONDITIONAL

For frozen S1 b9f430c8c9b33532abf07eea0ed2653310639f2d, successful admitted
MP3 and AAC host decoding preserves P = count(buffer.spec.channels), and the
host copy/append path preserves P = host C. This closes the specific cardinality
dependency left by239/253 under the conditions below. It does not establish
global INTERNAL, numerical quality, termination/no-panic, S1/fullAPP or Product
integration clearance. No Product source changes, builds or decoder fixtures.

Reviewed Product main4ea89e8abd49ed93074132580512eaddaaa76cc3 and Verification
main4c84472d1c7b474a3a9e6ec679889e0d89a9a6fc at actual-review start; canonical
four and live269 read. Actual Software526 comment6323777063, PR530 evidence head
84d7ea664d2ba7dddb6da5bae33bdffe1414b541. Stage1 method4c84472d/tree
32bf7ed27b0384da6d08531ec0aef958f5df0973 imported8cd1784 before proof helper;
same method tree remains at exact evidence head. Independent review start
6330648726. The former six-body cap is superseded only for this invariant.

## Original evidence authentication

Durable Git ZIP docs/REVIEW/software526/software526-source-return.zip at exact
head:389287bytes SHA256366e6baca260d5489b461fdff9d1066b33655297fc497ea238de73f92cd44712,
Git blob27c2988941bab2dc5179efe58b23d74f8f5c44ff.229 unique members,228 FILES
entries authenticate. All44 full source files match SHA256/length/Git blob in
SOURCE-PINS AND an independently fetched untruncated recursive Git tree of S1.
Ingest subtree835078995d4e9cc2424f9ea8d6f11304b45f783f. All89 git-command
receipts/streams authenticate;44 git-show outputs equal packaged full sources,
44 rev-parse outputs equal computed blobs. Original Windows stream bytes retained.
No binary/host trace interpretation, decoder execution or Software proof-helper
execution by Verification. ARGUMENT.md at exact PR head (outside ZIP), Git
a3038bd7906a9f812ca1d0cb97d1ae91825b5534, is an explanation, not proof by itself.

The frozen independent checker accepts the46-node/24-obligation ledger shape;
16 abstract premise falsifiers reject, and remain invalid private-state models,
not production witnesses. These controls do not prove the invariant. The
following independent source induction supplies the disposition.

Software reports parent PID5224/parent20544,953125000ns parent CPU,5938000000ns
wall and600-second conservative total reserve including unmeasured git child
CPU. Do not substitute wall for CPU or call that reserve an exact measurement.
This was source-only work, zero codec builds/decoder runs; retained evidence is
small relative to512MiB. No new resource-intensive experiment was required.

## Independent induction and capability closure

Paths below are relative to host/ingest at S1. Exact44 file hashes and46
function/line nodes are retained in authenticated SOURCE-PINS.json/LEDGER.json.

AudioBuffer owns private AudioSpec, private SmallVec<Vec<S>>, frame count F and
capacity N (vendor/symphonia-core/src/audio/buf.rs). new78-98 computes C with
spec.channels().count(), resizes an empty outer vector to C and stores the same
owned spec. Successful valid allocation establishes P=C, independent of F/N.
AudioSpec owns its Channels value (audio/mod.rs49-71); Channels variants contain
values/owned storage, without interior mutable shared count. Positioned count
uses popcount, not raw mask (audio/channels.rs310-324). Accessors expose immutable
spec and fixed sample slices, never mutable owner spec or resizable outer vector.

clear, render_uninit, truncate and shift/trim alter F and/or existing sample
elements, not spec or outer length (buf110-118,389-433). grow/resize/render APIs
also operate on inner sample vectors/F; clone/default retain matching metadata.
The planes.push at595 belongs to a temporary vector of borrowed sample slices,
not AudioBuffer's owning planes. Iterator self.planes=rest similarly advances a
borrowed view. plane_mut480-482 returns only &mut[S]; helper functions receiving
outer slices cannot resize the owning SmallVec or mutate its separate spec.

MP3: src/mpeg.rs33-79 admits LayerIII;187-220 rejects changing version/rate/mono.
The direct CODEC_ID_MP3 constructor selects Layer3 (vendor/symphonia-bundle-mp3/
src/decoder.rs45-84). decode_inner85-138 replaces the unused/default buffer with
new(header.spec(),1152); later spec disagreement errors before decode. Header
spec/common.rs144-151 constructs mono/stereo from n_channels182-184. Whole-buffer
replacement reestablishes P=C; it is not assumed to preserve a previous spec.
Layer3 decode380-485 changes reservoir/state/sample arrays, calls render_uninit,
then plane_mut, and passes a sample subslice to synthesis. The numerical calls
receive header/frame/state/arrays and no buffer/spec/outer-owner capability.
Reset152-156 replaces codec state only; error decode_ref157-166 clears F and
returns Err, success returns a borrow of the same F32 buffer after trim. Partial
decode/error and later reuse cannot change P/spec. LayerI/II dispatch is outside
this admitted host path, justified by both host and decoder dispatch guards.

AAC: src/aac.rs59-100 admits LC/config1/2/1024; ADTS179-244 rejects configuration
changes, MP4 uses a single admitted ASC and fresh decoder. Vendor AAC constructor
aac/mod.rs62-119 clones/owns ASC channels, creates AudioBuffer with that spec,
rejects unsupported profile/SBR/count/size. No later ASC/buffer/spec replacement
occurs in reachable decode/reset. decode_inner251-268 clears and renders F, then
decode_ga135-243 changes pair/ICS/CRC state. set_pair120-134 validates pair/index
against owned ASC count; malformed/unsupported routes return errors or panic,
not successful frames. synth_audio(cpe.rs165-185) receives the buffer but only
extracts plane_mut slices into ICS synth_channel449-467 and DSP synth57-157.
ICS/DSP own coefficients/delay/windows, not buffer metadata. Error decode_ref
284-293 clears F; reset269-274 resets pairs only. Even retained partially changed
pair state cannot resize owner planes or spec; later successful reuse retains
P=C. A new stream constructs a fresh decoder, rather than silently changing C.

This is a complete projection onto authority to mutate the owned buffer/spec/
outer plane count. It is not a complete numerical call-graph audit. Whole-buffer
receivers were followed through mutation and success/error exits. At sample-only
cuts the audited call sites and types pass no owner/metadata alias; safe Rust
privacy/borrowing prevents a callee from recovering that authority. The relevant
core/codec crates forbid unsafe_code. The ledger's PROVED_UNREACHABLE means an
unreachable metadata write, not that synthesis/bitstream functions are uncalled.
An arbitrary unaudited callee is not declared preserving by name. Imdct/numeric
callees have only their own state and sample arrays/slices; conditional memory
safety/contracts are explicit. Their accuracy and possible panic remain outside
the claimed successful-return property.

Host: MP3src/mpeg.rs312-358 and AACsrc/aac.rs142-176 allocate exactly host C outer
vectors. On every successful decoder return, the host checks spec-count==host C
and expected frame count before copy. Concrete num_planes is owning planes.len
(buf441-442); GenericAudioBufferRef F32 dispatch returns the same borrowed buffer.
Audio::copy_to_vecs_planar(audio/mod.rs307-319) resizes destination outer vector
to P; inner resizing and copy do not change outer length. Therefore tmp.len=P=C
and host iter_mut.zip(tmp) is exhaustive; append changes only inner vectors.
finish(src/common.rs191-213) validates declared channel/rate, frame lengths,
finite samples and trim, returning the same object. It does NOT check outer
count and is NOT used as a substitute for this missing premise.

## Each complete codec obligation

Both columns are independently PROVED_CONDITIONAL at the exact source above.

| Obligation | MP3 argument | AAC argument |
|---|---|---|
| admission | LayerIII, stable mono/version/rate guards | LC/config1/2/1024 host ASC, stable ADTS/MP4 config |
| constructor | first unused replacement calls new | constructor calls new with owned cloned ASC |
| ownership_alias | private owned buffer; slice-only mutation | private owned buffer/ASC; no mutable metadata alias |
| spec_count | positioned popcount, not mask value | same count with stable owned Channels |
| dispatch | direct MP3 selects Layer3 | direct AAC constructor and LC branch |
| mutable_decode | Layer3 render/plane slices only | decode_ga/pair synth extracts sample slices only |
| clear_trim_render | F/sample-only methods | F/sample-only methods |
| reuse_reset | state reset/error clear leaves P/spec | pair reset/error clear leaves P/spec |
| replacement_transition | unused replacement proves anew; mismatch rejects | fresh stream creates new decoder; no in-place spec replacement |
| success_error | Err/panic excluded; success same buffer | Err/panic excluded; success same buffer |
| returned_frame | exact borrowed F32 dispatch | exact borrowed F32 dispatch |
| host_copy_finish | spec guard plus P=C makes copy/zip exhaustive | same, including ADTS/MP4 decode_units |

Conditions: valid successful allocations; Rust privacy, borrow and memory safety;
no UB/foreign fabricated private state; Vec/SmallVec clone/length/resize/iteration
and slice contracts at locked dependency versions; representable mono/stereo
count arithmetic; exact admitted successful host path. Stable spec is supported
by the owned representation and audited mutation closure, not merely assumed
because an accessor has a familiar name. We do not prove compiler/library
implementation correctness or numerical callees free of defects. A panic, error,
unsupported stream or allocation failure is not promoted to a successful frame.

## Disposition and surviving limits

MP3 lemma PROVED_CONDITIONAL. AAC lemma PROVED_CONDITIONAL. Host cardinality
correspondence through copy/append/finish PROVED_CONDITIONAL. No unresolved
capability edge remains for this invariant in the admitted source graph.
No substantive correction return needed. Close269 at this actual disposition.

Carry239 PCM/FLAC/count/copy bridges unchanged. Global INTERNAL remains UNPROVED:
finite-precision peak/repetition and !limited gated-loudness ranking are separate
unclosed obligations. No full S1/INGEST/fullAPP/HOST/Mac/native/443 acceptance,
Product merge permission or expanded fixture campaign. A268 and C270 retain
their own OPEN dependencies and budgets; this result does not clear them.

replay.py authenticates immutable original bytes, provenance/ledger/control
consistency only; it NEVER runs Software proof helpers or a decoder and DOES
NOT mechanically prove the manual source induction. Normal Verification CI
compares the deterministic result. Optional --archive uses the retained ZIP;
--root selects the Verification checkout.
