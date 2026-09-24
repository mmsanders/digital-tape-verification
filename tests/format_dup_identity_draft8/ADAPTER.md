# R29 format/duplicate identity + duplicate long-operation binding contract

This directory is an independent verifier-owned package. A later Software round may bind the exact publication tree to the Digital-Tape public API, but must not change fixtures, planner order/count/digest, durability semantics, expected bytes, parser, or oracle.

The product adapter is mechanical only. It may report raw bytes and public API observations. It may not report an authoritative semantic classification such as old, new, safe, unchanged, candidate, or completed. Those classifications belong to this package's media.py and oracle.py.

## Blindness boundary

This package was authored from frozen DRAFT-8 specifications only. Product implementation must not be used to alter the verifier package. A later binding may inspect product implementation only after importing the publication tree byte-for-byte.

## Streaming protocol

Run one adapter process. Its initial JSON handshake must contain:

- format: FMTDUP-ID-ADAPTER-1
- adapter_kind: product
- stable adapter_id
- caseset_sha256: c493e77dff948df48d9c67c51ef4b68f0a61d2e02615b2d08760a594e79dc4e3
- raw_observation_only: true

The verifier streams every canonical case and expects one FMTDUP-ID-OBSERVATION-1 object per case. Production has no sampling, case-count, torn-length, durability-mode, or scenario override. EOF, timeout, malformed JSON, case drift, or process failure is failure.

## Raw crash observations

For scope=crash, return the verifier case index, injection_fired=true, verifier-format pre_snapshot and post_snapshot, target_baseline from the clean execution, actual_remount_result from a fresh product instance initialized from durable bytes only, and actual_selected_uuid when that mount succeeds.

A raw snapshot contains exact hex for primary superblock, mirror superblock, A0 block-0 header, and B0 block-0 header, each 512 bytes. Do not replace those bytes with decoded claims. The verifier independently checks magic/CRC, primary/mirror selection, version/state admission, UUID, sb_generation, A0/B0 identity, and final sequence numbers.

### Clean target baseline

For every operation/shape prove these four one-block superblock targets and bytes:

1. step-1 partner;
2. step-1 candidate/other copy;
3. final identity mirror;
4. final identity primary.

Each baseline entry reports only phase, copy, LBA, and SHA-256 of the exact target block. An extra, missing, reordered, or byte-different target fails before remount outcomes are considered.

All non-superblock writes required to prepare new indices/audio happen between the step-1 pair and the final identity pair as DRAFT-8 specifies. They are not additional superblock crash targets in this tranche. Before final identity begins, final A0/B0 headers must already be durable.

## Dual working/durable device

Maintain independent working and durable byte images.

- Reads observe working bytes.
- A successful write updates working bytes.
- In write_through, a successful write also updates durable bytes immediately.
- In flush_required, a successful write is not durable until a successful flush.
- A successful flush copies all preceding working writes to durable bytes.
- A fresh remount after injection uses durable bytes only; discard working state and all engine state.

For every targeted 512-byte superblock write, run before-write with 0 bytes landed, every torn prefix 1 through 511, after-write with the complete 512 bytes landed before its following flush, and a fault/power cut at the following target flush.

A torn prefix is copied into both working and durable media and then the write fails. after_write is not a 512-byte torn write: in flush_required the completed block remains non-durable at that cut.

## Mandatory destination shapes

Use the raw bytes from fixture.py, not product helpers:

- healthy byte-identical pair;
- structurally-valid mirror only;
- CRC-correct generation 0;
- only valid copy has version_major=2;
- equal-generation divergent CRC-correct pair;
- generation-exhausted candidate plus lower-generation partner;
- generation-exhausted equal-generation divergent pair.

The first five exercise the ordinary WIP-template path. The last two exercise the zeroing fallback. Equal-divergent geometry/capacity refusals are separate contract cases and must show no destination-superblock read/write before refusal.

## Duplicate WP-12a mechanical scripts

Contract observations report only public call results and state/counter facts requested by oracle.py.

### Small-budget continuation

Start duplicate with a budget smaller than the work and repeatedly call tape_dup until more_work=false. Do not advance through tape_service. Show at least one non-terminal continuation and a terminal call with no restart.

### Complete duplicate in-progress row

Exercise all fifteen Engine API state-matrix columns against a duplicate in progress:

seek, set_rate, render, service, status/info/tell, arm, feed, commit, abort, set_side, reset_b, promote, respool, dup, unmount.

Allowed: render, service, status/info/tell, and matching dup continuation. The other eleven return TAPE_ERR_BUSY. Every BUSY probe is followed by an ordinary continuation proving the same operation still advances without restart.

### Budget and argument stability

Exercise zero budget on initiation and continuation. On continuation separately change destination ctx, new_uuid, epoch, and destination nominal length. Each mismatch is TAPE_ERR_INVALID_ARG, does no work, and leaves the operation running. Separately prove only block_budget, more_work, cb, and user may vary.

### Callback re-entry

From inside a duplicate progress callback exercise the same fifteen columns. render and status/info/tell remain allowed. Every other tested same-instance call, including matching duplicate continuation and service, returns BUSY with no state change and no recursion. The next ordinary continuation must still advance the original operation.

### Destination failure while Playing

Start duplicate while the source is Playing at non-zero rate and fail a destination dev_write. Show that duplicate returns TAPE_ERR_IO and terminates with more_work=false; the source is not FAULTED; source rate, position, and ring are unchanged; transport remains Playing; and audio continues.

### Already-FAULTED source

The source-FAULTED duplicate behavior in this tranche is the state-matrix result: on an instance already in FAULTED, tape_dup returns TAPE_ERR_FAULTED and performs zero block operations. Do not invent a duplicate-specific source-write failure path; duplicate writes the destination.

## Failure retention

On first failure retain failure-reproducer.json. Crash reproductions contain exact pre/post primary and mirror blocks, exact case/injection parameters, actual fresh-remount result, and the verifier independently parsed result.

Success evidence retains canonical census/digest, adapter/build/source provenance, package hashes, and stderr. A Software green is evidence, never self-acceptance.
