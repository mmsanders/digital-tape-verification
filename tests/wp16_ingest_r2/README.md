# INGEST-1 R2 independent authoring checkpoint — NOT IMPORTABLE

Verification #169; P2V16-002/#179 prevents complete Stage1 publication. This tree
preserves substantial unaffected work so it can be reviewed/replayed. It is not
a complete package or candidate acceptance. `review.py` deliberately refuses a
census containing unresolved ruling cells. Do not import it as the Stage1 release
or start a candidate acceptance rung from these synthetic results.

Product8f3c0f0eb3da74186ab8482e22e685c714a7a258 and Verification
66794e6e2fe5c66488ecfcdc5a8f9a23b0eedc2a were fetched. Required onboarding and live
assignment read; only issued contract/package documents used from Product. The
contract's exact bytes and blob pin are in authority/ and PINS.json. No Product
implementation/design/private tests inspected; individual lead, no subworkers.
The old cc50b720 checkpoint is retained unchanged.

P2V16-002 is in [the finding](../../findings/P2-R2-WP16-SOWT-2026-10-15/README.md).
No Michael test or PM acknowledgement blocks unaffected authoring. Physical A6,
real-card/fullWP16 and WP15 remain separate held scopes.

## Preserved scope

- 1704 generated source files: full proposed lossless precision/rate/channel
  cross-product (including every FLAC bit depth8..32), MPEG1/2/2.5 CBR/VBR,
  AAC-LC BMFF/ADTS, exact encoded presentation intervals and no-metadata positives,
  strict refusal headers/streams, ordinary/silent/short/gated/crest sources,
  dyadic dither, SRC passband/alias/endpoints, unsafe join and a sparse RIFF
  overflow source. 90 non16-bit sowt cells are PENDING_CONTRACT_RULING.
- `CENSUS.json`:1767 expanded descriptors in six coherent rows. Arithmetic loops
  are not inflated into candidate case counts. Descriptors include native paths,
  errors, kills, mutation, concurrency, capacity, identity and decoder cases.
  A descriptor is an expectation/setup, not an observed Product result.
- `model.py`: exact counts/zero-output refusal, natural Unicode/numeric ordering,
  xorshift/draw/round-even quantization, canonical WAV/manifest arithmetic.
- `numerics.py`, `calibrate.py`: independent BS1770/EBU gating,16x FIR true peak
  qualified against generated standard vectors and finite-sinc maximization;
  two different FIR references independently judged against issued bounds.
- `audit.py`, `selftest.py`:48 green-baseline/causal observations. Defects are
  caught by their intended audio/count/order/transaction predicate, not failed
  provenance or a broken baseline. Standalone/batch/repeat isolation is exercised
  separately for both reference profiles. These are not shipping Product runs.
- `INTERFACE.md`, `review.py`: proposed compact file/exit/PCM/meter/native interface.
  Native transport/adapter remains Software-owned outside this tree. Raw trace,
  filter/profile/decoder mapping, same-profile three-OS relations and full meter
  qualification require independent review; the script never emits acceptance.

This checkpoint is not represented as completion of all unaffected Stage1 gates.
Before full release: resolve/issue sowt cells; finish candidate-facing observation
qualification/control hardening, lossless/lossy fidelity and trim mapping review,
summary/native/relation checks, and freeze the final complete assertions/census.
Do not waive any row, slow case, platform or tolerance to finish that release.

## Replay and availability

Python3.12, numpy2.3.5, scipy1.17.0. Optional fixture decoder crosscheck used
FFmpeg6.1.1-3ubuntu5; its exact version/config/encoder commands are in the pack.
Lossy bytes are frozen in the small `encoded-seed.tar.gz`; they are not recreated
with an arbitrary encoder on candidate platforms. The seed contains93 small
encoded files plus authoring provenance, with no individual raw file>1MiB.
The full large-raw source pack is a durable release asset, not git raw audio.

```sh
python3 -m pip install -r tests/wp16_ingest_r2/requirements.txt
python3 -B tests/wp16_ingest_r2/check_pins.py
python3 -B tests/wp16_ingest_r2/selftest.py
python3 -B tests/wp16_ingest_r2/zero_boundary_selftest.py
python3 -B tests/wp16_ingest_r2/calibrate.py --out /tmp/ingest-calibration.json
python3 -B tests/wp16_ingest_r2/asset.py --destination /tmp/ingest-sources
python3 -B tests/wp16_ingest_r2/validate_fixtures.py /tmp/ingest-sources --out /tmp/ingest-fixtures.json
```

ASSET.json pins archive bytes/SHA256, member census and SOURCES.json hash; every
source record pins bytes/hash/rate/channels/raw/trim/effective frames, generator
and CC0 licence. Download/extraction authenticates all members. Candidate runs
use these exact downloaded bytes on all machines, never freshly encoded bytes.
A full source pack expands to roughly510MB, including a valid358MB sparse-source
capacity fixture; authoring decode crosscheck authenticates that source's exact
PCM layout/size/hash instead of retaining several GiB of decoded silence in RAM.
Actual candidate overflow preflight is still required; it is not waived as slow.

Rebuild for authoring availability only (not candidate-platform regeneration):

```sh
python3 -B tests/wp16_ingest_r2/fixtures.py /tmp/ingest-built --seed tests/wp16_ingest_r2/encoded-seed.tar.gz
python3 -B tests/wp16_ingest_r2/asset.py --build /tmp/ingest-built --archive /tmp/INGEST1-R2-PREFLIGHT2-SOURCES.tar.gz
python3 -B tests/wp16_ingest_r2/asset.py --archive /tmp/INGEST1-R2-PREFLIGHT2-SOURCES.tar.gz --destination /tmp/ingest-authenticated
```

The existing WP14 publication workflow adds bounded independent selfchecks and
source publication/download replay. No new permanent workflow or Product gate.
Recorded local calibration/fixture validation is distinguished from what CI runs.
Source asset tag/bytes are immutable; a later complete release gets a new identity.

Reference audio has no universal waveform-hash authority. Alternative filters
need distinct profiles and their own numerical/native/three-OS qualification.
The two reference paths prove limited feasibility and verifier control behavior,
not that Software's selected stack meets these requirements.
