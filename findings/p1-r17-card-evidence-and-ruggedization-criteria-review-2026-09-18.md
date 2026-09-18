# P1-R17-V card-evidence audit and ruggedization-criteria review

**Disposition: Part A is accepted only as arithmetic over the exact recorded rate
vectors and rejected as complete WP-05 A-2 physical evidence; Part B requires the
exact corrections below before Hardware resumes. READY FOR PM REVIEW.**

The two submissions are independent. Nothing in this return qualifies a card,
accepts a physical process or safety result, authorizes a print or trial, or opens
fabrication or charging.

## Authority and immutable inputs

- Assignment: `mmsanders/digital-tape-verification#13`, observed open with the
  `verification-lead` label; no scope-changing comment was present at start.
- Input verifier main: `392d6bb9c948a5924fe18728fab04202bc8e337e`.
- Product routing authority: `mmsanders/Digital-Tape@a277ee7d52b26a5cf100b6d3bd69e2b6f6638802`,
  tree `520d0233c398fb9ea3c7deda6df929d9ac89c646`.
- Card submission: commit `c0e6a83ae44c2370288594b75915a214ba25deb7`,
  tree `4421e11258690936f02734c176589ff0c3dad826`.
- Ruggedization/process submission: commit
  `7b8063182e0a335c1f8e3e9dfabfefe79e74fbc4`, tree
  `bedb241e712d18097d64f71da4022fe254ebcfa7`.

Fetched PR heads matched those exact commits at both activation and return. The
current Verification charter, issue workflow and P1-R17 PM disposition were read at
the routing commit. No Software tranche, product implementation or unrelated PR
content was inspected.

## Part A — exact card record

### Raw identity

All five issue-named Git blobs are present at the exact named paths:

| Run | Git blob | SHA-256 |
|---|---|---|
| onn V10 | `9825f13275138d57c8180a0ab07d5bf93a000253` | `60e9413cd87d6c022b3f5460f9c2d2c17083d50d7c3b676975513e4b226df4a5` |
| PNY 1 | `4313394aa630b08552335b01bb8a64760f28e3df` | `419f4c8010284822756daa8c8761b4fb1e2d3dbdc27da0dd4c2e62c802f9b8fb` |
| PNY 2 | `5358b6e22ef07db75d951ba41c72130828c2234c` | `61486d179d4fe7e1f7d50642ce9101b03cceef0301bfbabf39af134bd29b6547` |
| PNY 3, filled flag | `7c94bce8478e9da1d56ac27209ff21c7e8670381` | `abbe5706b4a5b5f9dad0103ca9165190aa327a8db85588161d80f8b1f3afc4e2` |
| PNY 3, unfilled | `8250c7d97619b88d23952c9eb9abbdd7c2814540` | `37a2b3d556dd16f3fdcc0340d54457a5a509759b63861749117eadeef557fc72` |

The packet README and `analyse.py` blobs are
`b9a3b2caba96676113c1c1992ca22504ab7f8cd3` and
`407fd7ba10a8a041ca3502fcfb5d3f7acee996d2`.

### Independent recomputation

Each file contains 19 recorded 64 MB-window rates. Independent traversal used the
rate vectors, `transfer_mb` and `elapsed_s`, not the stored worst, mean or verdict.
The elapsed-derived means agree with the stored two-decimal means within 0.006 MB/s.

| Run | Recorded-vector minimum | Maximum | Elapsed-derived mean | Recomputed result at 23.3 MB/s |
|---|---:|---:|---:|---|
| onn V10 | 15.34 | 25.72 | 19.13169 | FAIL |
| PNY 1 | 26.18 | 68.20 | 38.78826 | PASS |
| PNY 2 | 25.41 | 74.07 | 38.45633 | PASS |
| PNY 3 filled flag | 27.36 | 74.07 | 40.59004 | PASS |
| PNY 3 unfilled | 25.88 | 67.11 | 38.38594 | PASS |

Thus the exact recorded vectors support these narrow statements: the four PNY
vectors have minima above 23.3 MB/s; the onn-control vector has a 15.34 MB/s minimum
and makes the result go red; and the PNY-3 vector labeled `filled_to=0.8` has a
27.36 MB/s minimum. These are observations of the declared Windows 11 / Transcend
TS-RDF5R / mounted-filesystem path on 16 September 2026, not card-speed or SKU
claims.

The one-path ceiling warning is warranted: PNY maxima span 67.11–74.07 MB/s and two
runs land on the same 74.07 MB/s maximum. No rate is attributed to the card alone.

### P1-R17-V-A01 — physical transfer and fill are not independently auditable

**Major; blocks accepting this packet as complete WP-05 A-2 evidence, but not the
recorded-vector arithmetic above.** The JSON preserves rounded MB/s values, not the
per-window byte counts and durations from which those values were calculated.
`measure_sustained_write.py` also ignores the return value of `os.write()`, increments
`written` by the requested byte count, and calculates the rate from that requested
count. A short write would therefore be silently counted as a full window. The
final temporary file is deleted and no final file size or byte-count trace remains.

The filled run records `filled_to: 0.8` because `--fill` was requested. It does not
record capacity/free-space before and after filling or a post-fill occupancy
measurement. The ballast loop has the same unchecked-write issue. The 20-minute gap
and Michael's reported fill are consistent with the claim but do not independently
establish the exact condition.

Smallest correction: on a fresh run, loop on `os.write()` until each requested range
is complete; retain requested and returned bytes plus monotonic start/end durations
for every window; record final file size; and record capacity/free bytes before fill,
after fill and after measurement. The analysis must derive rates and occupancy from
those retained primitive observations. Until then, the packet does not independently
prove a ≥1200 MB run on media measured at 80% occupancy.

### P1-R17-V-A02 — displayed mean trusts a stored summary

**Minor; non-blocking to the worst-window result.** `analyse.py` recomputes worst,
best, pair values and verdict from `windows_mb_s`, but displays `d["mean_mb_s"]`
directly. Changing PNY 1's stored mean from `38.79` to `999.0` still printed
`999.00`, reported all five verdicts in agreement and exited 0. A stored-verdict
mutation was correctly detected and exited 1; malformed JSON also failed nonzero.

Smallest correction: derive the displayed mean from `transfer_mb`, byte units and
`elapsed_s`, compare it with the stored summary under the declared rounding rule,
and exit nonzero on mismatch. Apply the same explicit comparison to every stored
summary field that the report claims to authenticate.

### P1-R17-V-A03 — “any adjacent pair” is not what the code computes

**Minor; non-blocking because pair rate is explicitly not an A-2 criterion.** The
README calls `pairmin` the minimum over “any adjacent pair.” The function evaluates
only fixed non-overlapping pairs `(0,1), (2,3), ...`, omitting `(1,2), (3,4), ...`.
For onn the reported 18.00776 MB/s fixed-pair minimum becomes 17.76235 MB/s over all
adjacent pairs; for PNY 2, 36.08881 becomes 35.93428. The pass/fail minima do not
change.

Smallest correction: either call and define this a fixed, phase-zero non-overlapping
pair statistic, including why that phase is chosen, or iterate every adjacent pair.
Do not retain the word “any” with the present implementation.

### Part A boundary

**Accepted:** immutable identity of the five blobs; arithmetic over all 95 recorded
window-rate values; the exact vector minima/pass-fail results; the fact that the
control vector goes red; path/host/reader labels as recorded.

**Rejected/not established:** complete WP-05 A-2 physical evidence, actual bytes
written per window, independently established 80% occupancy, manufacturer part
number, revision, per-sample CID, order/seller identity, host-caching state, ambient
conditions, reader temperature, attribution of speed to a card, exact-SKU or retail
family qualification, card atomicity, production end-to-end copy performance, or
C-90. No card or purchase is qualified.

## Part B — ruggedization and owned-printer criteria

The proposal is directionally useful: it separates design criteria from results,
uses inert dummies, bans live-cell destructive testing, preserves failures, keeps
WP-24 S-3 separate, and keeps fabrication/charging closed. It is **not acceptable as
an executable or auditable pre-test method as written**.

Relevant immutable blobs include:

- `spec/hw/ruggedization.md` `6f70996dcb2230547e2307c359ccdb3d63997ff6`;
- `hardware/printing/owned-printer-baseline.md`
  `250af3c3e4e7fce66ecbc7b189cf8b6684fe7bf1`;
- `hardware/test_spec_manifest.py`
  `87f5ae1ee9ba4addf48ce8379fcc386bbb77688c`;
- WP-04 / WP-24 / WP-25
  `bf040839086c13538bf86c55de80063de0c04af3` /
  `2d0e7fae4c5e5e4d6859bd9ea14fa28a3a3d296a` /
  `87fac0db9eee5164f38ded22d185abd56b4b910c`.

### P1-R17-V-B01 — abuse inputs are not yet repeatable

**Blocker.** The drop family names six faces, four selected corners and two selected
edges but does not identify the exact corners/edges on a datum drawing, define the
order within each group, specify a release fixture and attitude tolerance, or give a
height tolerance. Cumulative severity makes order part of the method. “Chest height”
is a rationale for an internal 1.0 m screen, not external qualification; that narrow
status should remain explicit. The two-unit plan is acceptable only as the stated
screen, with any failure failing the screen, not as a statistical claim.

The shake definition does not say whether 150 mm is peak-to-peak, one-way travel or
amplitude; where it is measured; what motion profile/tolerance is required; how the
unit is gripped; or how travel is verified. Audible metronome video proves cadence,
not displacement. A manual 3 Hz motion for 120 seconds per axis must be shown feasible
or replaced by a fixture.

The tumble definition omits box material/internal surface, apparatus, article
loading, release method, what counts as one tumble, and how 0.4 m impact height and
end-over-end motion are obtained.

Smallest correction: issue a datum/orientation drawing and complete ordered sequence;
declare release, height and attitude tolerances; define shake travel unambiguously
with grip, waveform, measurement and tolerances; and fully specify the tumble
apparatus and counting rule. Preserve n=2 as a screen and say explicitly that one
failure rejects the stage.

### P1-R17-V-B02 — inspection thresholds, instruments and baselines are missing

**Blocker.** The method calls for connector unmate force, fastener torque, seam gap,
cell “hand-load,” hidden transport motion/datum, audio reference level, cartridge
force and magnified inspection without specifying instruments, resolution/accuracy,
baseline procedure or pass deltas. A torque or unmate-force measurement can itself
turn a fastener or disconnect/disturb the article. “Any opening,” “normal force,”
“as before” and “same reference level” are not auditable thresholds.

Smallest correction: for every D/FC check, define instrument, range/resolution,
calibration/check, baseline value, allowed delta and observation sequence. Identify
which checks are non-disturbing checkpoints and which require opening/disassembly;
do not return a disturbed article to a cumulative sequence unless the protocol
explicitly defines that branch and its effect on acceptance.

### P1-R17-V-B03 — C-1 and C-2 do not yet prove the checks can go red

**Major.** An omitted retainer fastener need not produce audible cell motion if
friction or another feature still captures the dummy, and D-01's hand-load is
undefined. A fastener backed out two turns has no bound to a measured gap or torque
loss; D-17's method is undefined and a seam gap is only expected after the entire
drop family. These are candidate faults, not retained sensitivity proofs.

Smallest correction: define safe injected defects in measured terms just beyond the
eventual acceptance limits, prove the corresponding instrumented check detects each
defect before abuse, and retain the raw baseline/control readings. A control that
does not go red invalidates that check before a qualifying article is exposed.

### P1-R17-V-B04 — internal child-safety criteria lack sourced test methods

**Major.** R-3 appropriately says it is an internal design criterion rather than a
regulatory/compliance claim, and R-4 gives a 31.7 × 57.1 mm cylinder. But neither
criterion cites the adopted source/method or defines the sharp-edge tape/test tool,
sharp-point probe, accessibility rule, cylinder insertion/orientation and force, or
how fragments are handled. “Criteria used for children's products” is not executable
provenance.

Smallest correction: cite the exact edition/section adopted as the internal design
source, reproduce the operative method and instrument requirements in the controlled
protocol, and keep the explicit non-compliance disclaimer. This remains an internal
screen unless separately authorized competent compliance work occurs.

### P1-R17-V-B05 — stage gates and restart/retention rules are incomplete

**Major.** Stages are listed, but the gate from Stage 1 to Stage 2 is not stated. An
inert dummy is matched only by mass and outline, not center of mass, mounting
interface or stiffness/load transfer. “Restart the affected sequence” does not say
whether a redesign restarts the full 12-drop cumulative sequence, both units, rough
play, controls, or only one orientation. The record retains failures, but physical
failed-article retention and post-failure handling are not defined.

Smallest correction: require both Stage-1 articles and controls to meet every stated
gate before Stage 2; define dummy mass, center of mass, envelope, attachment and
load-transfer equivalence; retain and quarantine failed articles; and state that a
repair/redesign begins the entire affected cumulative family on fresh articles, with
the applicable controls rerun. Keep the absolute ban on live-cell destructive tests.

### P1-R17-V-B06 — process coupons and split-plate controls need exact binding

**Major.** K-2 says five cubes in five jobs on different days, but does not hold bed
position constant or repeat the five-position layout. It can therefore confound
between-job variation with position. The 0.01 mm recording increment is not an
instrument accuracy/uncertainty requirement. Material conditioning/profile controls
and an analysis that separates within-job, bed-position and between-job effects are
not specified. K-3 is a hand fit/no-fit result and K-4 lacks a fixture, force/known-
mass tolerance and deflection instrument.

PM's contingent split-plate direction is acceptable only as a direction. Before a
print, the rebuilt packet must bind the machine-confirmed usable build volume; keep
all four WP-24 bases and their matching lids in the same job/plate; retain the full
0.10/0.18/0.26/0.34 mm sweep; retain blind mapping; and preserve the complete WP-04
sweep plus spread M/D/H bed-position controls, source generation, packet validation
and immutable packet revision. The current rev-5 plate remains held and no print is
authorized.

Smallest correction: repeat the same multi-position K-1 layout across at least five
separate K-2 jobs under a fixed recorded process, use a calibrated dimensional
instrument with uncertainty, and report within-position, bed-position and
between-job variation separately. Define quantitative K-3/K-4 methods. Then issue a
new split packet satisfying every binding above after usable volume is physically
confirmed.

## Reproduction record

Commands were run on clean extractions/worktrees of the exact commits:

```text
git rev-parse / show -s / ls-tree <exact refs and paths>
  -> both commit/tree pairs and all five raw Git blobs match the assignment
sha256sum raw/*.json
  -> SHA-256 values in Part A
python3 analyse.py
  -> exit 0; four PNY PASS, onn FAIL; all five stored verdicts agree
python3 independent_card_audit.py raw/
  -> exit 0; all 95 rates traversed; table above independently reproduced
analyse.py with PNY-1 verdict changed PASS -> FAIL
  -> exit 1, mismatch named
analyse.py with malformed JSON
  -> exit 1
analyse.py with PNY-1 mean changed 38.79 -> 999.0
  -> exit 0 and 999.00 displayed (P1-R17-V-A02)
make -C hardware check
  -> exit 0; regeneration/check suites pass; retained mutations go red;
     DRC/ERC explicitly SKIP because KiCad/no board are absent
make -C hardware spec-test
  -> exit 0; 6 retained controls, 4 spec files tracked
make -C hardware fabrication-gate-test
  -> exit 0; 8 checks and CLI controls pass, gate proven able to open and go red
make -C hardware fabrication-gate
  -> exit 2; CLOSED with exactly five blockers
```

The five fabrication blockers remain the charger 45 °C response, solenoid average
power response, per-device transient temperatures, unqualified CD74HC221 timing,
and the resulting PROVISIONAL solenoid verdict. A green regression suite is not
fabrication or charging permission.

## Holds and smallest next dependency

All frozen spec hashes, implementation blindness, VT8 exclusions, WP-11
golden/listening hold, PR #20/#64 holds, card atomicity and qualification, production
copy, fabrication, charging, physical trial, safety, purchasing and Michael-reserved
approvals remain unchanged. Machine facts and usable build volume are unconfirmed
physical inputs, not assumptions.

**Smallest next dependency: Hardware must publish a corrected ruggedization/process
proposal resolving B01–B06 for a fresh independent criteria review.** Separately, a
future card rerun with retained primitive byte/time/occupancy observations is needed
before WP-05 A-2 physical evidence can be accepted. PM owns routing; issue closure
records only that this Verification pass stopped.
