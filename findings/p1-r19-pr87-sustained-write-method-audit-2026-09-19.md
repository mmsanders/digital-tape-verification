# P1-R19-V — PR #87 sustained-write method audit

**Disposition: BLOCKED. PR #87 is not ready for a future physical card rerun or
complete WP-05 A-2 evidence. READY FOR PM REVIEW.**

The corrected tool loops on short writes, the rate auditor recomputes every
adjacent pair, and the five legacy records remain explicit schema-1 evidence.
However, schema 2 does not retain the required per-call write trace and its auditor
accepts missing or corrupted mandatory primitives. A green synthetic suite therefore
does not establish that a future physical run would be independently auditable.

No physical rerun was performed. Nothing here accepts the prior card record as
complete A-2 evidence, qualifies a card or SKU, authorizes purchasing, fabrication,
charging or physical work, or dispositions PR #92.

## Authority and immutable inputs

- Assignment: `mmsanders/digital-tape-verification#15`, observed open with the
  `verification-lead` label. No scope-changing PM or Michael comment was present.
- Input verifier main: `15dd16eb499f5c148bff7c5b4b67ff75ae7a0f32`, tree
  `cc217c3947e2b96ab064beeb403c3a8b5c2a180d`.
- Product routing input: `fba51ad403ad0fcc20019b88a7f34beaeb3c389f`, tree
  `86852d6aba91045b061847c9fc24de3022d0a1cf`.
- Exact PR #87 input: `da97a8534ef6940f1cb8337e9c9fb7b403dc4804`, tree
  `62ce95dd951272167a4fb7fa1c676b190d9e1487`.

The current Verification charter, issue workflow, status/freeze documents and
`P1-R19-PM-DISPOSITION.md` were read from product main before the audit. Inspection
was limited to the issue-named PR #87 paths and five legacy raw JSON files.

### Prior-head provenance correction

The issue names prior head
`c0e6a83a474a0b01134ea64ea02a80c420979003`; that object does not exist in the
repository and cannot be fetched or resolved. The authenticated PR ancestry instead
contains `c0e6a83ae44c2370288594b75915a214ba25deb7`, tree
`4421e11258690936f02734c176589ff0c3dad826`. This audit does not silently replace
the frozen identifier: the mismatch is a provenance blocker, and the actual ancestor
comparison below is supplementary.

All five legacy files are byte-identical from that actual ancestor to the target:

| File | Git blob at both commits | SHA-256 |
|---|---|---|
| `onn-v10.json` | `9825f13275138d57c8180a0ab07d5bf93a000253` | `60e9413cd87d6c022b3f5460f9c2d2c17083d50d7c3b676975513e4b226df4a5` |
| `pny1.json` | `4313394aa630b08552335b01bb8a64760f28e3df` | `419f4c8010284822756daa8c8761b4fb1e2d3dbdc27da0dd4c2e62c802f9b8fb` |
| `pny2.json` | `5358b6e22ef07db75d951ba41c72130828c2234c` | `61486d179d4fe7e1f7d50642ce9101b03cceef0301bfbabf39af134bd29b6547` |
| `pny3-filled.json` | `7c94bce8478e9da1d56ac27209ff21c7e8670381` | `abbe5706b4a5b5f9dad0103ca9165190aa327a8db85588161d80f8b1f3afc4e2` |
| `pny3.json` | `8250c7d97619b88d23952c9eb9abbdd7c2814540` | `37a2b3d556dd16f3fdcc0340d54457a5a509759b63861749117eadeef557fc72` |

## Findings

### P1-R19-V01 — the required write-call trace is not retained

**Blocker.** `write_fully()` correctly continues after a short write, and an
independent partial-writer probe completed a 20-byte request as returns `7, 7, 6`.
But it returns only aggregate bytes and call count. Each window retains one starting
offset, total requested/returned bytes, call count and `calls - 1`; it does not
retain every write request length, return length and offset. The auditor therefore
cannot prove that a short-write continuation began at the correct offset, that every
request/return pair is represented, or that `write_calls` and `short_writes` are
truthful. Independent mutations removing `write_calls`, setting `short_writes` to
99, removing `offset_bytes`, or changing an offset to 7 all exited clean.

Smallest correction: retain an ordered call record for every write with window
index, absolute offset, requested bytes and returned bytes; hash-bind it to the raw
record; and require the auditor to prove exact contiguous coverage, positive bounded
returns, continuation offsets, aggregate counts and window totals. Add controls for
missing, duplicated, reordered, skipped, overlapping and over-return calls.

### P1-R19-V02 — schema-2 validation fails open on mandatory evidence

**Blocker.** A clean synthetic record passes, but thirteen one-at-a-time mutations
also pass:

- missing or wrong `offset_bytes`, missing `write_calls`, and inconsistent
  `short_writes`;
- missing `fsync_ok` (treated as true), missing top-level first/last/elapsed timing,
  and an unchecked final fsync after `t_last`;
- missing requested total, returned total, or expected final size;
- missing or arithmetically corrupt `space_after_measurement`;
- an invented `target_kind`, which evades the mounted-filesystem final-size branch;
- an inserted false schema-2 summary (`worst_window_mb_s = 999.0`).

The auditor also does not require exact window indices/order, validate filesystem
`total/free/used/occupancy` arithmetic and before/after consistency, or prove the
declared raw-device applicability branch. Thus the record cannot yet authenticate
all required timing, fsync, final-size, capacity/free/used and raw-device facts.

Smallest correction: define a closed schema with required fields and allowed target
kinds; reject missing/unknown fields that affect the claim; validate index/offset and
all byte/timing/fsync/size/accounting identities; record the final fsync attempt and
outcome inside the measured span; and add retained positive/red controls for every
required primitive and branch. If schema 2 intentionally contains no summaries,
reject summary fields rather than silently ignore a contradictory value.

### P1-R19-V03 — the frozen prior-head identity is invalid

**Blocker to the issue's exact ancestry proof.** The required prior SHA is neither a
Git object nor a remote commit. The five files are identical against the actual PR
ancestor named above, but Verification cannot rewrite the assignment's immutable
identifier. PM must correct the exact prior head or explicitly accept the documented
provenance correction.

## Accepted narrow behavior

- The short-write loop completes a request and raises on a zero return.
- Rate calculation uses returned window bytes and monotonic window endpoints.
- `sliding_pair_rates` evaluates every adjacent `(i, i+1)` pair; an independent
  four-window vector produced exactly three expected pair rates.
- All five historical files audit explicitly as legacy schema 1 and state that they
  are not complete WP-05 A-2 evidence.
- The official card controls go red for their retained mutations, legacy analysis
  reproduces, and the broader product/verifier regression targets pass.

These facts do not cure V01–V03 and do not accept a physical method or result.

## Reproduction record

```text
git rev-parse / ls-tree / merge-base on exact refs and six issue-named paths
  -> product, verifier and PR target identities match; named prior SHA unresolved;
     actual ancestor c0e6a83ae44c... authenticated
git diff --no-index and sha256sum on five legacy JSON files
  -> byte-identical actual-ancestor-to-target; blobs and SHA-256 values above
make -C hardware card-test
  -> exit 0; 11 retained controls pass
make -C hardware card-audit
  -> exit 0; all five legacy records reproduce as schema 1
temporary independent schema-2 mutation probe
  -> clean fixture passes; all 13 missing/corrupt mutations above also pass;
     short-write continuation and every-adjacent-pair positive probes pass
hardware spec/thermal/mech/shell/solenoid/atomicity/fabrication-gate-test/
packet-check/packet-validate/packet-duplicates targets
  -> exit 0; retained controls pass
make -C hardware fabrication-gate
  -> exit 2; CLOSED with exactly five blockers
make -C tests check (verifier input)
  -> exit 0; fault device, crash, audio, ops, three-family playback and complete
     playback suites pass
```

The five fabrication blockers remain charger 45 °C enforcement, solenoid average
power, per-device transient temperatures, unqualified CD74HC221 timing, and the
resulting PROVISIONAL solenoid verdict. A green regression suite is not fabrication
or charging permission.

## Exclusions, holds and next dependency

No card/device was written, no physical evidence was created or accepted, and no
unrelated implementation or PR #92 material was inspected. Complete WP-05 A-2,
card/SKU identity and qualification, attribution, atomicity, production copy,
candidate PCM/listening, safety, fabrication, charging, physical work and purchasing
remain held. Frozen spec hashes and all Michael-reserved approvals remain unchanged.

Next owner is PM: correct or explicitly disposition the invalid prior-head identity,
then return the method to Hardware for the V01/V02 evidence-schema and auditor
corrections. Verification should re-audit fresh synthetic positive/red controls
before any separately authorized physical rerun.
