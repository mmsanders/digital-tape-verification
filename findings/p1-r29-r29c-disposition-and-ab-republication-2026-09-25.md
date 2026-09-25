# P1-R29: PR #227 disposition and corrected R29 package republication

Date: 2026-09-25  
Verification issue: `mmsanders/digital-tape-verification#76`  
Verifier: Verification Lead

## Authority and authenticated inputs

- Product routing main: `3b740fa99e5f1bbeca8cc471bdadf05ecda7a555`
- Verification input main: `30b820b9e0c41396ceb9409a389fb73e66acc0fe`
- TapeFS SHA-256: `3bffa0ec46d7ba3779b02cbee6fac1edaf5094553f78270ee379759655147cbb`
- Engine API SHA-256: `537eadc423e1a7bde726d689206b8fe93bef164d57e48e8ff71e07eaf8a7e3a1`
- Acceptance SHA-256: `7f78fba7b66b4fc6e96d15399c62468249bb30fbccbb59bf9f57b4532f56b6b7`
- Verifier correction source commit: `7408f0aad4dff2284b2b3f56b39c3ea6e3da2dc7`
- Verifier correction source tree: `85e7689f2bdd07fd0cf37e1dc89170c7a11d3728`

The three frozen specification hashes were independently recomputed from the exact
product routing commit and match the issue authority. No product engine source was
inspected or executed for this return.

## Part 1 — exact PR #227 evidence disposition

Candidate identity:

- PR #227 head: `75b36a90cb72e3fa076e62baec1440f48afaf1b6`
- PR #227 tree: `efe5165bab8af07d4e919a0cd20637892b4d2cf6`
- Current verifier tree carried by the product evidence:
  `5637fbd3e89316889b4bbd52d2a72c95e3c278e1`
- Aggregate workflow run: `36101173027`
- Aggregate result: `4,209,696 / 48` shards PASS
- Aggregate SHA-256:
  `fdf477dc99cf55b54aa5dcfc314fcd607e5d2e3269859d9c16a95d58f410e78b`
- Aggregate artifact: `10849219575`
- Functional artifact: `10849462125`

The evidence identities, aggregate census, artifact, six clean cases, two
zero-needed cases, both state-matrix rows, zero-budget observations, own-device
write/flush failures, Faulted precedence, ring drain and abort observations are
mechanically authenticated. The retained raw results support only these bounded
public observations:

- the six named clean/headroom fixtures reach the recorded terminal media/results;
- both zero-needed counter-boundary cases perform no media work;
- the eleven in-progress BUSY cells return `TAPE_ERR_BUSY` with zero block
  operations, and the four allowed cells return `TAPE_OK` as recorded;
- zero budget returns `TAPE_ERR_INVALID_ARG` with zero block operations for both
  initiation and continuation;
- an ordinary continuation after BUSY advances the recorded public progress;
- destination write and flush failure each terminate with `TAPE_ERR_IO`,
  `more_work=false`, and recorded `FAULTED` state;
- the complete Faulted row, armed precedence, ring drain, underrun and abort results
  reproduce from the retained functional summary.

### Blocking evidence defect `P1-R29-V01`

The packet does **not** prove operation continuity/no restart. Its adapter assigns
constant strings (`R1`, `R2`, `R4`) rather than observing an engine-sourced identity,
and its progress value is a global callback count that remains monotonic even if the
engine restarts an operation. The old verifier therefore accepted its own adapter
labels as causal continuity evidence. Frozen WP-12a instead requires no-restart to
be established from the operation's observable work, including chunk-region writes.

The packet also does **not** exercise the required minimum positive budget. Its
small-budget campaign uses `block_budget=1024` for all nine calls; no
`block_budget=1` observation exists.

Disposition: the exact recorded public results above are narrowly accepted as raw
observations. PR #227's no-restart/continuity and minimum-positive-budget criteria
are **not accepted**, and PR #227 remains held. The aggregate green cannot be
credited against the corrected package tree below. Software must import that exact
tree and perform a fresh run before those criteria can be disposed.

## Part 2 — corrected R29-C observation contract

Published package: `tests/respool_full_draft8`  
Tree: `7e98b40c6aceb0a5759bfb1499091a4c9f541927`  
Observation schema: `WP10-RESPOOL-OBSERVATION-2`

The corrected contract:

- requires `block_budget=1` for every call in the minimum-positive-budget campaign;
- retains the cumulative chronological chunk-region write LBA list before and after
  every relevant call;
- requires BUSY to leave the raw trace unchanged;
- requires continuation traces to preserve the prior trace as an exact prefix and
  forbids repeated copied chunk LBAs;
- treats adapter labels as non-causal metadata;
- retains the exact terminal media checks and every prior crash/state criterion.

The canonical planner remains exactly 4,209,696 cases with SHA-256
`02c52de7a7c51a6ffafe5c9d5afad9c23032b72fc11aaf206bb27a9c9506d3e1`.
A constant-label repeated-copy control now goes red. Where no raw chunk write is
observable, no private engine-identity claim is made.

## Part 3 — corrected R29-A and R29-B packages

### R29-A promote

- Package: `tests/promote_draft8`
- Tree: `e99ba0f2cf3f9e8cdd22199cbd9cc502cc5638a3`
- Observation schema: `PROMOTE-OBSERVATION-2`
- Cases: 44,311
- Case-set SHA-256:
  `8732af9434437d0411731b3e4909a2ca9a1278778e5d9c8947642cec7b793442`

The four-chunk fixtures now carry a truthful 9-second nominal label and the
eight-chunk fixtures a truthful 21-second label. The independent parser performs
phase-0 device-capacity admission, then ordered version/state/geometry admission
before index selection. It enforces the frame cap, stored-versus-derived chunk
equality, fixed fields, mirror LBA, capacity and Side-A waterline.

Stored positions are now explicitly a caller-owned model. The verifier preserves
them on nonterminal calls and models caller clearing only after terminal
`TAPE_OK && !more_work`; it no longer claims a device-side position table absent
from the frozen public API. Long-operation continuity uses `block_budget=1` and
cumulative raw chunk-write traces rather than adapter-label equality.

### R29-B format/duplicate

- Package: `tests/format_dup_identity_draft8`
- Tree: `f76ab23d17beb9212f8ee1d17d3d1875b74abc7d`
- Observation schema: `FMTDUP-ID-OBSERVATION-2`
- Cases: 57,611
- Case-set SHA-256:
  `c493e77dff948df48d9c67c51ef4b68f0a61d2e02615b2d08760a594e79dc4e3`

The compact fixture now carries truthful 9-second/four-chunk geometry. The raw
snapshot includes device capacity and the parser applies the same ordered phase-0
and phase-2 geometry admission before index selection. Duplicate continuation now
requires `block_budget=1`, trace-prefix continuity, and no repeated copied chunk
LBA; adapter labels are non-causal.

PR #229 and PR #230 evidence predates these changed package trees and observation
schemas. None of it is credited here. Each product owner must import the exact new
tree and produce fresh raw evidence.

## Independent verification

All three corrected package self-tests pass, including the new geometry,
admission-precedence, caller-ownership, budget-1, trace-prefix and repeated-copy red
controls. Every `tests/*_draft8` verifier package in the repository also passes.
Planner membership, ordering, censuses and digests are unchanged.

## Holds and exclusions

This return does not approve or merge product PR #227, #229 or #230 and does not
accept any product engine source. No hardware, listening, fabrication, charging,
purchasing, wallet or regulatory work occurred. All existing safety, physical-work,
purchase, merge and Michael-reserved approvals remain active. The only blocker for
the next product round is fresh evidence bound to the exact corrected package tree
for that product tranche.
