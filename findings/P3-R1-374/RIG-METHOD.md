# Stage B — Hardware atomicity rig method review

**Disposition: NOT CLEARED for a qualifying physical campaign.** No physical run
occurred. Scope is the design/method, not the parts order, acoustic-limit issuance
or hardware/media qualification. Stage A remains published at `41995965`.

Reviewed Hardware #641 / PR #646 head
`80d26364d84ddea4f42ee62a6222318d67d3b3d5`,
`hardware/characterisation/ATOMICITY-RIG.md` blob
`641dbfe22812faebead895b264a40966999068b3`.
Criteria/judge input is Product `3826018653e504217f37a16d8864fb0d597e22e6`:
WP-05 A-6, DRAFT-10 media atomicity, and the unchanged revision-3
`media_atomicity.py`. Hardware's return arrived before #374 stopped, so this is
the already-named Stage B, not a new assignment.

## What the design covers

The design identifies a single-block SPI transaction, accepted response, busy
entry, independent old-pattern readback, four separate neighbour baselines,
fresh post-power-cycle reads, CID checks and plan extensions. Those are suitable
method ingredients. Keeping misses and failed initialization visible, checking
back-power, and binding exact raw traces are appropriate. Judge self-tests pass
43/43; the always-NEW classifier mutation is caught (seven failures). These facts
do not qualify a card or establish an electrically clean cut.

## Findings requiring resolution

**R374-1 — an observed tear on a late-cut trial can disappear from PASS.**
The judge calls `qualifies` and skips target/neighbour classification for
non-qualifying rows. The published synthetic probe supplies 1,000 qualifying NEW
rows and one fully formed late-cut row whose target is a mixture of its exact old
and new patterns. With the unchanged **production** threshold of 1,000, the judge
returns PASS with an empty `torn_iterations`; direct classification of that row
is TORN. All identity/plan/precondition fields are valid synthetic values. This is
a method counterexample, not an observed card defect.

Exclude a miss from the qualifying count, but audit every otherwise valid returned
target/neighbour observation for corruption. Preserve and escalate any observed
tear/corruption; do not allow the summary verdict to erase it. Hardware/PM must
resolve the verdict path before campaign clearance; Verification changes no
Product judge here. Reproduce with `rig_qualifier_probe.py` and the pinned judge.

**R374-2 — the row does not itself prove busy at the actual rail-opening edge.**
Step 8 uses the last completed 0x00 byte and a timestamp of writing the GPIO.
`qualifies` accepts any older busy sample, however stale, if no deassertion time
was supplied: the probe's sample at 120 µs and cut at 1,000,000 µs still qualifies.
The proposed firmware reduces that interval to roughly one SPI byte, but busy
can end inside that interval and the switch has an unmeasured delay. A row's
software timestamp is not an independently measured switch-opening event.

Specify how actual switch opening is aligned to wire-level busy, bound the
sampling/switch uncertainty, and mark ambiguous/finished-before-opening cases
non-qualifying. Qualify that method with busy-ending-between-sample-and-cut and
delayed/no-cut controls, in addition to the existing obvious late-cut control.
Retain per-trial evidence sufficient for the qualified method; sampled analyser
captures alone cannot rescue rows whose qualifying state is otherwise unproven.
The raw data schema must preserve both CID reads and flag disagreement explicitly.

**R374-3 — U3 is not a specified 1.5-V rail comparator.**
The design assigns an always-powered SN74LVC125A an approximately 1.5-V falling
threshold and drives it directly from a slow RC-decaying rail. TI specifies
VIL ≤0.8 V / VIH ≥2.0 V at a 2.7–3.6-V supply, and an 8 ns/V maximum input
transition time; it does not supply the asserted calibrated threshold. The
proposed 10 Ω × 10 µF discharge has a 100-µs time constant. Using that edge as
quantitative rail timing is therefore unqualified. Use a suitable specified
threshold/hysteresis measurement path or demonstrate a properly calibrated
waveform method; retain analogue evidence for the off interval and back-power
control. Also specify /OE and unused-input wiring. [TI SN74LVC125A datasheet,
§§5.3, 8.1.2](https://www.ti.com/lit/ds/symlink/sn74lvc125a.pdf).

**R374-4 — the claimed 2-µs non-overlap is not established by the circuit.**
The 22-nF gate capacitor, 10-kΩ/100-kΩ paths and fast-off diode need a worst-case
turn-off analysis and measurement before Q2 is enabled. A diode charges the gate
toward a diode drop below the GPIO rail; the remaining gate-voltage tail is not
the MOSFET datasheet's fast-driver test. The DMG2305UX threshold spans -0.5 to
-0.9 V at a small test current, so threshold alone does not prove Q1 is safely
off in 2 µs. Simultaneous supply/discharge conduction is a risk to be resolved,
not a measured failure asserted here. Bound dead time and current using the
actual driver/capacitance before energizing the discharge sequence.
[Diodes DMG2305UX datasheet, p.2](https://www.diodes.com/datasheet/download/DMG2305UX.pdf).

**R374-5 — SPI data has no demonstrated transfer to the production SD4 bus.**
The judge allowing `spi`/MISO establishes a supported protocol field, not a
physical equivalence theorem. Retain bus mode, SCK and rail/switch configuration
in the result. Treat SPI results as bounded characterization until PM disposes
the exact qualification scope or a representative native-mode campaign exists.
Do not silently extend this design to SDR50/card-system qualification.

## Required clarifications, without a new acceptance criterion

- A minimum of 100 sampled busy durations is not a guaranteed lower bound on a
  future write. Retain actual qualifying evidence and extend the plan when short;
  remove the assertion that every fraction below 1 must land in busy.
- Bind the committed calibration, firmware binary, bus settings, switch revision
  and analysis method to an immutable manifest referenced with the run. The
  existing plan digest binds the identity/schedule, not all these extra fields.
- `PNM/PRV` can be a recorded revision string, but retain raw CID, decoded fields,
  capacity and photographed manufacturer part number per sample. Do not infer
  unreported silicon/controller equivalence or substitute a retail speed label.
- Keep the rig as characterization tooling under `hardware/characterisation/`;
  PM owns any placement/scope decision. There is no need to put card-rig code in
  Product `firmware/` or `engine/` to satisfy this review.

The next owners are Hardware for the method/circuit/evidence corrections and PM
for the SPI qualification boundary. The existing 1,000-cut threshold, zero-tear/
zero-neighbour-damage requirement and all fabrication/charging gates stand.
Software #642 exact-head disposition remains unavailable until its return exists.
