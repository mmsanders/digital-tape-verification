# P1-R21-V: sustained-write method repair re-audit

**Date:** 19 September 2026 UTC  
**Disposition:** **REJECTED / BLOCKED for a new physical acquisition**  
**Finding:** `P1-R21-V01` — schema-2 remains incompletely closed and type-unsafe

## Bound inputs

- Verification base: `e77b61fe420e48444cf0791c74fc7e296ef0ccf6`
  (tree `2e96e8d4e30357944ed4a3efbffacd7356a94cb2`)
- Exact Hardware PR #87 head: `10471f37f432c44d6f5beac59d25b3771e057c38`
  (tree `3d8e134e4673a2fffa4cd7df9763d7541383c8a8`, sole parent
  `fb937b163b1f6fece3b6e0bd8c67d229196e85d8`)
- Product main used only for charter, workflow and PM routing:
  `86a1ba0874812ef4ca052a4dbc6baad2b16addb6`
- Corrected legacy-record ancestor:
  `c0e6a83ae44c2370288594b75915a214ba25deb7`

The exact method commit changes only:

| Path | Git blob | SHA-256 |
|---|---|---|
| `hardware/characterisation/audit_sustained_write.py` | `3676cd8bfed171a465d9876f8ab855df7992f27e` | `c50a3a0f53d9698f6b609ed85ff82517bb9502eff7ebe5357a852aa751c27782` |
| `hardware/characterisation/measure_sustained_write.py` | `6388333d253b08d96403e895a4aa5be26bf491b1` | `32404b0cf3006fd4d398e64a0ba14527a3028534a279aeef467863be19eff851` |
| `hardware/characterisation/test_sustained_write.py` | `a5ed1f5dd89b603bbb374267f6f5b092062896d2` | `ed393496bdf0eb5edfda78554424af826508213c75ac6928395c335b9a1ca261` |
| `hardware/measurements/2026-09-16-sustained-write/README.md` | `2f9d43eacbd35371c9855324038ab847a5690694` | `f88addb13e486b325d3ba7d1de21e949f3e94278954a49f834bbbf43906c9948` |

## What the repair closes

The acquisition path now loops short writes and retains every call in an ordered,
digest-bound trace containing sequence, window, absolute offset, requested bytes and
returned bytes. The auditor reconstructs window call counts, short writes, offsets,
totals and continuity from that trace. Window timing includes its `fsync`; the final
`fsync` is retained inside the top-level measured span. Mounted-file and raw-device
final-size branches are distinct.

The exact prior thirteen-mutation corpus was replayed independently. Every mutation
now rejects: missing/wrong window offset, missing `write_calls`, false
`short_writes`, missing `fsync_ok`, missing top-level timing, missing requested or
returned total, missing expected size, missing post-run capacity, corrupted post-run
capacity, unknown target kind and inserted false summary. The new trace controls also
reject missing, duplicated, reordered, mis-windowed, discontinuous, negative-offset
and over-return calls, including mutations whose digest was recomputed.

Accordingly, the substantive defects previously reported as `P1-R19-V01` and
`P1-R19-V02` are corrected in this exact method head. This does not make the complete
repair acceptable because the additional required malformed-field controls expose a
new fail-open boundary.

## Blocking finding `P1-R21-V01`

The top-level record, windows and calls are partly closed, but the complete schema is
not closed or safely typed. An independently generated schema-2 fixture at 40 MB/s
was mutated one property at a time. Thirteen malformed forms were accepted and one
caused an uncaught exception:

- a closing `fsync` whose end timestamp precedes its start timestamp is accepted;
- removing `final_fsync.error` or adding an unknown `final_fsync` field is accepted;
- a string `final_fsync.t_start_monotonic_s` raises an uncaught `TypeError` instead
  of producing a controlled audit rejection;
- Boolean `write_trace.seq` and Boolean window `index` values pass as their integer
  equivalents;
- integral-valued floats pass for byte offsets, byte counts and capacity counts;
- a false `window_mb` is accepted even though the retained windows contradict it;
- false `required_mb_s`, `required_c90_mb_s` and `bar_mb_s` values are accepted;
- unknown fields inside `fill` and `space_after_measurement` are accepted.

These are not cosmetic presentation failures. The assignment expressly requires a
strict closed schema, monotonic sequence/window identity, a closing flush inside the
timed span, target bounds and rejection of malformed fields. In particular, accepting
a reversed closing-flush interval does not establish that the final durability event
was observed in order, and accepting Boolean sequence/index values defeats strict
identity typing. A malformed record can also terminate the audit by traceback rather
than by a verifier-owned problem report.

Before a new physical card acquisition, the method needs exact nested schemas and
primitive types for `final_fsync`, `fill` and every capacity object; finite,
non-negative integer byte/identity fields; ordered final-flush timestamps; validation
or removal of all declared window/criterion metadata; and retained controls that make
each of these mutations go red without crashing.

## Legacy record identity

All five legacy JSON files are byte-identical between corrected ancestor
`c0e6a83ae44c2370288594b75915a214ba25deb7` and the exact PR head:

| Record | Git blob at both revisions | SHA-256 |
|---|---|---|
| `onn-v10.json` | `9825f13275138d57c8180a0ab07d5bf93a000253` | `60e9413cd87d6c022b3f5460f9c2d2c17083d50d7c3b676975513e4b226df4a5` |
| `pny1.json` | `4313394aa630b08552335b01bb8a64760f28e3df` | `419f4c8010284822756daa8c8761b4fb1e2d3dbdc27da0dd4c2e62c802f9b8fb` |
| `pny2.json` | `5358b6e22ef07db75d951ba41c72130828c2234c` | `61486d179d4fe7e1f7d50642ce9101b03cceef0301bfbabf39af134bd29b6547` |
| `pny3-filled.json` | `7c94bce8478e9da1d56ac27209ff21c7e8670381` | `abbe5706b4a5b5f9dad0103ca9165190aa327a8db85588161d80f8b1f3afc4e2` |
| `pny3.json` | `8250c7d97619b88d23952c9eb9abbdd7c2814540` | `37a2b3d556dd16f3fdcc0340d54457a5a509759b63861749117eadeef557fc72` |

This closes the prior ancestry/provenance discrepancy only. The five records remain
schema-1 legacy observations and are not complete WP-05 A-2 evidence.

## Executed checks

- `make -C hardware card-test card-audit` — pass: 15 retained control families,
  legacy audit and legacy analysis reproduction.
- Independent prior thirteen-mutation corpus — 13/13 rejected.
- Independent extended adversarial corpus — required trace/bounds/summary mutations
  rejected; 13 malformed records accepted and one malformed record crashed as listed
  in `P1-R21-V01`.
- `make -C tests check` at verifier base — pass, including the retained ops,
  playback and complete-playback suites.
- `make -C hardware fabrication-gate-test` — pass.
- Real fabrication gate — **CLOSED with five blockers**.

## Preserved boundary

No physical card was accessed or rerun. No card, reader, SKU, WP-05 A-2 result,
atomicity behavior, production-copy path or qualification result is accepted. PR #87
is neither approved nor merged. Frozen specifications and verifier fixtures were not
changed. Fabrication, charging, purchasing, physical-work and all Michael-reserved
approvals remain held. Hardware may repair only the method; PM decides any later route
back to independent Verification.
