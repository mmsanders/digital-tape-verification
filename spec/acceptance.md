# spec/acceptance.md — Acceptance criteria

**Revision:** DRAFT-4 · **Issued:** 2 Sep 2026 · **Owner:** Program Manager (frozen with the format at the Phase 0 gate)
**Supersedes:** DRAFT-3. Versioned in step with `tapefs-v1.md` and `engine-api.md` so the three cannot drift apart.
**Incorporates:** V3-003, V3-009, V3-011, V3-013, V3-014, V3-015 per PM Decisions 005, plus the hardware limit corrections from Decisions 002-A and 003 and the self-audit fixes recorded in the companion documents.

A work package is complete when its criterion below holds **and the Verification Lead has independently confirmed it** — not when the implementer says so. Criteria are stated so they can be checked, not argued.

---

## Stream 1 — Engine

| WP | Criterion |
|---|---|
| **WP-06** Block device, superblock, index commit | Format → mount → commit → unmount → mount round-trips on the file device. Every refusal path in `tapefs` §4.1 (all three phases) and §5.2/§5.3 has a test that exercises it, including: `version_major = 2` with one torn copy **writes nothing**; geometry at exact equality with the mirror block is **refused**; both slots valid with equal sequence is refused. `tape_commit` returns only after the final flush |
| **WP-07** Allocator, copy-on-write Side B | `tape_reset_side_b` completes in < 1 s and **moves no chunk**. Fuzzing over 10 000 random edit sequences never produces a Side B **allocation or write destination** below `a_high_water`. Side B *references* below the mark are correct and must not be flagged — the oracle identifies ownership by allocation, not by chunk id. `free_next` after remount equals invariant 12's derived value |
| **WP-08** Playback, seek, scrub | 1.0× playback bit-exact against `tests/golden/`. Every rate in the ramp table bit-exact. Seek to every run boundary ±1 frame lands on the specified frame. Reverse playback at the most negative rate does not wrap position; forward at the highest rate clamps at `max_pos`. The `engine-api` §8 formulas are the only implementation of the arithmetic |
| **WP-09** Record modes | Overwrite, overdub, splice each match their golden WAV. Overdub of full-scale against full-scale saturates at ±32767/−32768, never wraps. Splice at t=0, mid-run, exact run boundary and end all validate per `engine-api` §11. `tape_seek` and `tape_set_rate` while armed both return `TAPE_ERR_BUSY` |
| **WP-12** Re-spool | After a completed pass, the side is exactly one entry and renders bit-identically. **Invariant 10 holds at every write**, asserted by the simulator: no write destination ever intersects the live set of either side. The corrected V3-003 case — `a_high_water = 10`, one live B entry spanning chunks 10–11 so `len = 2` and `free_next = 12` — must send pass 1 to `[12, 14)` and then **run** pass 2 back into `[10, 12)`, reclaiming both chunks. A second case in which no lower run of `len` chunks exists must **decline** pass 2 and leave the cartridge compacted and intact. Both destinations must satisfy the `≥ a_high_water` floor as well as disjointness. Insufficient free space returns `TAPE_ERR_CARTRIDGE_FULL` and changes nothing |
| **WP-13** Embedded readiness | `.data + .bss + tape_instance_size()` ≤ 200 KiB summed — the same single gate `engine-api` §4 states, not a separate ceiling on the instance alone; `.rodata` ≤ 32 KiB; no allocator symbol links; stack ≤ 8 KiB by call-graph analysis; no indirect call outside `dev.h`; **no engine-owned state outside the caller's `mem` block** (invariant 19). All six as CI gates, green |
| **WP-36** Slot capability | Fuzzing over 100 000 random transport input sequences against a source-slot device with `write == NULL` produces zero calls to `dev_write` on that device. The debug assertion never fires |

## Stream 2 — Verification

### WP-10 — Crash injection

Power loss injected at **every** write boundary, and torn writes at every block write, across a scripted session covering format, load, play, overwrite, overdub, splice, commit, reset B, re-spool (both passes), promote (both phases) and duplicate. **Exhaustive, not sampled** — the injection-point count is reported.

**Universal assertions, after every injection:**

- No allocated chunk is unreachable from the live index **beyond what `tapefs` §7 permits**. Precisely: `free_next` equals `max(a_high_water, max over live-B entries of last + 1)`. **Chunks superseded by an overwrite are expected to be unreachable and must not be reported** — they are the format's only sanctioned leak and re-spool reclaims them. *(DRAFT-2's blanket reachability assertion contradicted the allocator and would have failed every ordinary overwrite; V3-014.)*
- The live index of each mountable side passes `tapefs` §5.2 in full.
- Referenced audio is intact for whatever generation is selected.

**Per-operation allowed-state sets.** DRAFT-2 required "remount succeeds, Side A byte-identical to session start" for every injection, which contradicts what duplicate, format and promote are specified to do (V3-013). Each operation now has its own oracle:

| Operation | Permitted outcomes after any injection |
|---|---|
| Play, seek, scrub | No change to either side |
| Overwrite, overdub, splice, commit | Side A unchanged (referenced frames). Side B is **exactly** the pre-operation or post-operation generation, never between |
| Reset B | Side A unchanged. Side B is the pre- or post-reset generation |
| Re-spool | Side A unchanged. Side B renders bit-identically to before, in either the pre-pass or post-pass layout. **Never a layout referencing overwritten chunks** |
| Promote | Side A and Side B are each one of the enumerated generations in `tapefs` §9.3's recovery table, **including the legitimately mixed pair** (A at its previous generation, B at phase-1) that arises from a crash between steps 3 and 4. All referenced audio intact in whichever generation is selected. **Side A is not required to be byte-identical to session start; a completed promote changes it by design.** Promote of an empty Side B must return `TAPE_ERR_INVALID_ARG` having written nothing |
| Duplicate | **Source unchanged, always** — absolute. Destination is the pre-copy cartridge, `TAPE_ERR_INCOMPLETE`, `TAPE_ERR_BAD_MAGIC` if it was blank and crashed before the final superblock, or the completed copy with its fresh UUID and a Side B mirroring its new Side A. Rejection for aliasing or capacity writes nothing at all (invariant 18). **The re-run path must be exercised**: after an interrupted copy, calling `tape_dup` again on the same destination *device* must complete it — which is only possible because the destination is a `tape_dev`, not a mount |
| Format, reusable media | The old cartridge unchanged, `TAPE_ERR_INCOMPLETE`, or the new empty cartridge |
| Format, blank media | The above, **or `TAPE_ERR_BAD_MAGIC`** — before step 4 no valid superblock has ever existed and remount cannot succeed. This is the single permitted "does not mount" case in the whole suite |

### WP-11 — Golden suite and runner

One command runs everything. Comparison byte-exact, **no tolerance** (ADR-016). A failure emits an audible-difference WAV plus first differing frame, channel, both values, delta, count and peak. Fixtures are generated once, listened to by a human, and committed; regeneration requires logged PM approval.

**Mutation testing before each phase gate.** Seven mutations, each caught:

1. Off-by-one in a chunk boundary calculation.
2. Index commit written *before* the chunks are flushed.
3. `sequence` not incremented on commit.
4. CRC computed over the wrong byte range.
5. A Side B **allocation** permitted one chunk below `a_high_water` *(the allocation, not a reference — see WP-07)*.
6. Saturating clamp replaced with a plain cast, so overdub wraps.
7. **Warm-start buffer accepted for the wrong `(uuid, side, frame range)`.** *(Replaces DRAFT-2's preroll-cache mutation, which targeted a feature DRAFT-3 deleted; V3-015.)*

Any mutation the suite does not catch is a coverage gap and a finding of equal weight to an engine bug.

---

## Firmware criteria referenced by the specs

| Behaviour | Criterion |
|---|---|
| **Instant-on, warm** | Wake from sleep with a mounted cartridge to first rendered non-silent frame: **< 100 ms**, measured on the bench build with a logic analyser on I²S |
| **Warm-start validity** | The retained ring is passed as a `tape_warm_start` descriptor with correct `uuid`, `side`, `start_frame` and `valid_frames`. A deliberately mismatched descriptor must produce `warm_start_used = false` and a correct, silent-free mount — **not** audio from the wrong cartridge |
| **Instant-on, cold** | Card init begins within 20 ms of the cartridge-detect switch closing. Play pressed 1 s after insert produces audio within 100 ms of the press |
| **Resume position** | Checkpoint to device flash every 10 s of playback and on every transport state change. After abrupt removal, resume lands in `[T − 12 s, T − 2 s]` where **T is the true position at the moment of removal** — not the checkpoint. Measuring against the checkpoint would admit a 10 s error the specified algorithm cannot produce and would fail to catch a cadence regression. Table holds 64 `(uuid, side)` entries, LRU. Promote clears both entries for that UUID; reset B clears `(uuid, B)` |
| **Scrub ramp** | Rate schedule driven into `tape_set_rate`: 4.0× at t=0, linear to 12.0× at t=1.5 s, hold. Reverse mirrors with negative rates. Scrub goldens drive this exact table |
| **Record light** | Colour from `tape_status().entries_free` as a fraction of `TAPE_MAX_ENTRIES`: **green** ≥ 25 % free, **yellow** < 25 %, **red** at 0 — and at 0 the record button does not hold. Off while not armed |
| **End of tape** | `at_end` releases the play button within 50 ms |
| **Cartridge full mid-record** | On `TAPE_ERR_CARTRIDGE_FULL`, firmware stops the transport, releases the buttons, and commits. The recording up to that point is present on the next mount |
| **Output cap** | Codec output limited in the volume register to the level producing 85 dB SPL on the specified reference headphones, re-asserted every boot, unreachable from any user control. SPL meter and coupler, **witnessed by Michael** |
| **Copy progress** | LED row position reflects `blocks_done / blocks_total` from the progress callback; never a timer |

---

## Media atomicity — the format's one physical assumption

`tapefs` §8 and §13 rest on a 512-byte SD block write being atomic under power loss. It is true of essentially every card in practice and is not universally guaranteed, and DRAFT-4's first cut cited a work package (WP-19) that does not exist in this document — so the format's single load-bearing physical assumption had no acceptance criterion at all.

**Criterion.** On each candidate card SKU, with the card powered from a switched supply: write a known 512-byte pattern to a fixed block, cut power at randomised offsets inside the write window, then re-read. Across at least 1 000 cuts per SKU, every read must return **either** the previous content **or** the new content in full — never a mixture. A single torn block is a blocker finding and forces a format change, not a firmware workaround.

Run during WP-05 card characterisation (this criterion replaces the dangling WP-19 reference in DRAFT-4's first cut), on the same cards bought for the sustained-write measurement. Results recorded per SKU with revision, alongside the write-speed numbers.

---

## Hardware safety limits (PM-owned; measurements live in `spec/hw/`)

**These state limits, not mechanisms.** DRAFT-1 named the charger's NTC input as the means of enforcing the charge window, which over-constrained a limit into an implementation no candidate part could meet. How a limit is met is the Hardware Lead's choice; *that* it is met, in hardware and not defeatable by firmware, is not.

| Limit | Value |
|---|---|
| **Charge window** | Charging suspended below 0 °C or above **45 °C** cell temperature. Enforced in hardware; firmware cannot override. Mechanism is the Hardware Lead's — a TS network designed so 45 °C maps to the charger's hot-suspend threshold, a part with a suitable threshold, or a series cutoff. **Note:** a BQ25896's native hot *suspend* is T5 ≈ 60 °C; T3 ≈ 45 °C only drops charge voltage 200 mV ([TI datasheet](https://www.ti.com/lit/ds/symlink/bq25896.pdf)). Verified by sweeping cell temperature across both thresholds |
| **Solenoid — single pulse** | Bounded in hardware to the shortest duration that reliably releases the latch, plus stated margin. **The number comes from WP-04/WP-22 measurement, not from this document.** Verified by holding the gate high and measuring coil current |
| **Solenoid — sustained power** | **Average coil power ≤ 0.25 W over any rolling 10 s window**, enforced in hardware, not defeatable by firmware. Stated as power because power is what damages a coil. The limit must sit above the fastest legitimate use — a child alternating stop and play about twice a second — and below the coil's continuous rating; if those do not leave a gap the answer is a shorter pulse or a lower-power coil, not a looser limit. Verified by driving the gate at 100 Hz continuously: average coil power must fall to and stay at or below the limit within 2 s. Component values and worst-case tolerance are part of the deliverable before WP-26; a PPTC is a third-layer backstop and may not be the element establishing this bound |
| **Worst-case thermal** | Charge at full rate + copy + all LEDs for one hour: no external surface above ambient + 15 K; cell surface below 45 °C. **Junction temperatures of the charger, regulator and MCU reported individually**, not inferred from a lumped enclosure model — a 30 s copy is a transient the lumped model does not resolve. Witnessed by Michael |
| **Deep-discharge latch** | Hardware load switch disconnects the cell below ~3.2 V, released by charger insertion. Must not add perceptible latency to wake-from-sleep; if it does, escalate rather than trading against instant-on |
