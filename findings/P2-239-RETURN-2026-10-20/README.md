# Verification239 — bounded actual return disposition

Independent review of Software499 / Product PR506 at
`69075205a31a2cbea4f00e142bc8b65d3437091c`. **PASS for the frozen scalar and
premise-discriminator comparisons, with useful conditional length lemmas below.
Global INTERNAL remains UNPROVED; no admitted production witness and no Product
integration permission.** This is the final actual disposition of the issued finite
method, not a claim that a successful proof model qualifies S1 or a full app.

Authority: live Verification239 and paired Software499 under PM497; Stage1 method
merge `a294ea88ca6bbe6d7a3dc0b660df3d6a7ae0faaa`, imported first at
`1fcb3bd971b69725abb70db4de6726516d61cad9`, unchanged eight-file method tree
`0b7d3c2f2b1550e9b778f634167d8b82f0eedf5e`. Expectations predate this new
implementation. Product/main `8f65b3d336727eec70fb6fe6d4dee6aafb7e0136` and
Verification/main `be9c02f1c862afafa1a89e9195790fc0e5535f29` were fetched before
disposition. Canonical AGENTS, full CLAUDE, STATUS and Verification charter and live
scope were read. Individual review; no subworkers or new uncovered campaign.

## Authenticated execution and limits

Hosted run39553865535/job119068957785 succeeded at tested
`8b689218dc06e68b6b09b6744e3e4f4e54c5ddf2`. Its workflow archives original S1
`b9f430c8c9b33532abf07eea0ed2653310639f2d`, ingest tree
`835078995d4e9cc2424f9ea8d6f11304b45f783f`, and adds only a test example calling
the production library. Locked Rust1.97.0, x86_64 Linux/usize64, native argv,
exit/stdout/stderr, compiler/host, adapter SHA256 and time receipts are retained.
No shipping source changed. All122 issued source/dependency Git blob/size pins and
returned SHA256 bindings match; this authenticates identities, not an audit of all
122 implementations. Manual review is limited to eight covered host sources and
three vendor audio dispatch/copy/buffer files. Engine tree d96b4245 is unchanged.
Tested-to-return changes add raw evidence and its byte-preserving attributes only;
the adapter, workflow and certificate sources are unchanged.

The original11 raw files total41,441 bytes. Authoritative outer inventory
`docs/REVIEW/software499/run1-FILES.json` has Git blob
`96824d42155572f805d6e9237187e2824dfc75b3` (1,374 bytes). The inner hash list
was written before `/usr/bin/time` finalized run-time.txt: exactly that one entry
has the empty-file hash. The original is preserved; the outer inventory binds the
actual915-byte final timing file. This disclosed ordering defect does not alter
any input, answer or command. Original transport remains at the immutable candidate
[raw evidence directory](https://github.com/mmsanders/Digital-Tape/tree/69075205a31a2cbea4f00e142bc8b65d3437091c/docs/REVIEW/software499).

Independent replay matches all25 frozen inputs/results and binds16 native command
records to their returned fields: five actual dsp::output_frames calls, eleven
guard/shape discriminators and nine explicit proof-model rows. Four valid PCM rows
call deinterleave; the partial-frame row checks the extracted WAV caller guard.
Four trim rows call actual finish on deliberately empty-plane constructed states,
including enormous counts; these are impossible admitted decoder states. Two
quantize calls combine actual output length with an explicit equal-plane/count
predicate. Nine append/pass/convergence rows execute a separate model. All25
mutations of actual returned answer values are detected by the unchanged comparator.
Metadata and exact labels are checked separately; no model row is promoted to a
production invocation. Coefficient tuple assertions in Software run.py are tiny
model checks, **not a mechanized verification of the production loops**.

Software build19.02 CPU-seconds and run0.06 CPU-seconds are authenticated. Independent
work performs byte/JSON/hash/source checks only, conservatively bounded60 CPU-seconds
and less than2MiB downloaded/source material, within2CPU-hours/512MiB; no Product
rerun, codec/audio/native or census execution. Existing normal required CI is
unchanged apart from adding this replay to it.

## Independently assessed conditional subdomains

Every length lemma concerns successful normal returns under valid slices, successful
allocation/copy/push and representable indices/arithmetic. Error, panic or allocation
abort is not silently proved impossible; this is no whole-process resource theorem.

1. **PCM WAV/AIFF length correspondence.** wav.rs checks channels/width/align,
   positive admitted rate and data divisibility. AIFF checks positive declared
   frames and exact u128 offset+frames*channels*width equality before selecting the
   payload suffix. common.rs starts C empty planes and pushes once into every
   plane per complete frame; after k iterations each length is k. Both callers
   supply exactly F complete frames and raw=F. Error returns do not return a
   successful Decoded object. This closes the conditional successful length path;
   the inner floor division alone would not reject a partial block.
2. **FLAC length correspondence.** flac.rs starts C empty planes/raw0; each successful
   frame has positive B, matching channel count, exactly C subframes and verified
   body/CRC before append. Constant/verbatim forms produce B samples. Fixed/LPC
   warmups contribute order and residual contributes B-order: divisibility by
   P=2^porder and order<=B/P are checked, so partition lengths sum to B-order.
   Prediction pushes once per residual; decorrelation/conversion preserve count.
   Extending every C plane by B and advancing raw by B preserves equal lengths.
   Final count/MD5 checks may refuse, not shorten a successful return. Refusal/?
   exits are unsuccessful; arithmetic and allocation success remain explicit.
3. **MP3/AAC copied-length bridge, still conditional.** The pinned generic audio
   dispatcher reaches concrete copy_to_vecs_planar. It resizes the outer vector to
   num_planes and each inner to samples_planar, whose default is frames(); concrete
   AudioBuffer frames=num_frames and plane slices use that same count. This closes
   the copied-vector-length bridge conditional on num_planes==admitted spec channels.
   That equality is **not established for every MpaDecoder/AacDecoder constructor/
   reserve/render return** here. Metadata frames/spec checks and zip append alone
   cannot close it. The prior accepted fixed-codec MP3 constructor conditional
   result carries; no invented runtime-wide or native-rate refusal requirement.
4. **Finish/trim.** finish checks existing plane lengths/finiteness, not outer
   plane count. Given constructor cardinality and valid raw state, checked head+tail
   below raw yields positive effective count. Empty-plane success in the frozen
   discriminator demonstrates the missing premise; it is no admitted source or
   production INTERNAL witness. No general constructor claim is inferred from it.
5. **Output and channel counts.** output_frames uses checked u128 multiplication/
   rounding then u64 conversion. For u64 N and admitted positive rate<=192000 the
   intermediate is below2^80; a u64 intermediate restriction would be wrong.
   The actual wide-valid and overflow neighbours distinguish these cases. On
   usize64 with valid effective slices, the44100 path copies out elements and the
   other-rate loop pushes once per k in0..out. Main checks positive output and
   RIFF total before pass2 conversion; each source count is bounded by total<2^30.
   Mono quantize emits2L; stereo zip emits2min(L,R). L=R=out is essential: actual
   L3/R2 emits4 and the frozen predicate rejects it. Silent writer output is a
   distinct explicit zero-byte-count path. These statements do not prove every
   allocation/index/panic outcome unreachable on all targets.

Pass1/pass2 byte identity needs the same deterministic decoder/configuration and
matching metadata/trim/planes. Hash equality alone does not prove determinism. The
three frozen model rows detect missing premises and add no runtime-wide proof.

## Exact remaining obligations and final stop

The new vendor bridge narrows the codec obligation to constructor plane/spec
cardinality. convert.rs has two continuing branches. The peak branch updates
g by p_out+GUARD_DB-CEILING_DBTP+0.001 and sets limited; a uniform finite-precision
bound on the next quantized/refined peak and number of repeats is still missing.
The !limited measured-loudness branch feeds back target-lo and may clamp to the
peak bound; a finite bound covering cancellation/no-change, gating and branch
transitions is also missing. Real-arithmetic decrease and three literal coefficient
checks cannot establish convergence by32. The abstract32-continue row rejects an
unsupported rank claim but is not a codec witness. Global INTERNAL therefore stays
UNPROVED; no original INTERNAL guard is newly witnessed by an admitted source.

This closes239 at a useful bounded actual disposition and the finite-method proof
stop, without another unchanged campaign or a demand for new human/codec work.
Software499/PM497 own any future specifically authorized constructor-cardinality
or finite-precision ranking method. No454/459/fullAPP/S1 integration permission is
earned. Existing234 exactd923 Win11 resource PASS,2301640-byte/nativeCSV, S2
integration10faee5 and originalRED access stop carry. Closed observer235/491 privilege
stop is absolute; no token/security/helper/provider retry. Native/Mac/PML/A6/S3/G2
and E242 own-HOST holds survive at their original scopes. No acceptance by closure.

Reproduce with `python3 -B findings/P2-239-RETURN-2026-10-20/replay.py --out /tmp/239`
(GH_TOKEN optional for public API quota), then compare REVIEW.json to RESULT.json.
Local `--offline verification-work` uses the previously authenticated raw/source
snapshots and yields the same result; it does not bypass a network approval.
