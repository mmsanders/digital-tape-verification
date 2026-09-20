# P1-R23-V: repaired PR #87 sustained-write method re-audit

**Date:** 20 September 2026 UTC  
**Disposition:** **REJECTED / BLOCKED for a new physical acquisition**  
**Finding:** `P1-R23-V01` — the repaired auditor still fails open and can terminate by traceback

## Bound inputs

- Verification base: `391d6a8308edfca46f639c3a6567c220d7a7b95d`
  (tree `742d135b5d02850b69a8e34fb8a71db35012025d`)
- Product routing main, used only for charter and workflow:
  `8a7a8baed67c64a69d894daf6ce1ac5fbe268597`
- Exact held Hardware PR #87 repaired head:
  `e520c2c4de3fb917fb3e0e1bb72a91997cbe8333`
  (tree `deece322ca9001c95c002a3c0cf8d937b14f4d29`, sole parent rejected head
  `10471f37f432c44d6f5beac59d25b3771e057c38`)
- Controlling prior finding: `P1-R21-V01` at verifier commit
  `f00da3ffbaab62833cce52b29c4999934a37a9d2`, findings blob
  `659837ffd5ed5e8c59ba07f48863238f873b6404`
- Corrected legacy-record ancestor:
  `c0e6a83ae44c2370288594b75915a214ba25deb7`

The repaired commit changes only these three files:

| Path | Git blob | SHA-256 |
|---|---|---|
| `hardware/characterisation/audit_sustained_write.py` | `5a00b4b390492fce7cb110f93073676e69d7ea8b` | `a49d4c84994be54a88f092766d163b79def94664b214f25d56d35526735dc170` |
| `hardware/characterisation/test_sustained_write.py` | `b931d77635d01742fad06d0bdbf441abad7a9ee3` | `a5512ff72f25285a63e92c4f0c407a4b99ce00ed4cec317935cc230ca3a9c63b` |
| `hardware/measurements/2026-09-16-sustained-write/README.md` | `697faf36425cbec9c47db82253e3f81edd44107a` | `4ede954b564edc89d36a33d4f13e2898870a8c059a51121c1e7c31d7c1c1e0de` |

## Narrow closure of the prior forms

Every malformed or crashing form expressly listed by `P1-R21-V01` is corrected at
this exact head. A verifier-owned 1,200 MB / 19-window record was constructed
independently rather than imported from the product controls. Each mutation changed
only its named field; trace mutations were digest-rebound unless the digest itself
was the target. Both the mounted-filesystem baseline and a separately constructed
honest raw-device baseline pass.

The repaired auditor controlled-rejects and names the intended field for:

- reversed, missing, unknown, conflicting and ill-typed `final_fsync` members,
  including the former string-timestamp traceback;
- Boolean sequence/window identities and integral floats in trace, window,
  byte-total, final-size and capacity fields;
- false and zero `window_mb`, and false `required_mb_s`, `required_c90_mb_s` and
  `bar_mb_s` declarations;
- missing, unknown or ill-typed members in `fill`, its capacity children and
  `space_after_measurement`; and
- fabricated filesystem figures in a raw-device record.

The independent matrix also reconfirmed the earlier ordered-trace, digest, offset,
window timing, flush, total, final-size, target-kind, false-summary, occupancy and
capacity boundaries. In total, **55 one-field malformed controls reject by report
and name their intended boundary**. Thus `P1-R21-V01` is closed **only for its
enumerated forms and the rechecked prior boundaries**. It is not closed for the
method as a whole because the adjacent cases below remain.

## Blocking finding `P1-R23-V01`

The repaired auditor still does not safely establish that an input is a schema-2
record before arithmetic and acceptance. Eleven independent one-field neighbors
remain red for the method:

### Three malformed records terminate by traceback

1. `bytes_per_mb = 0` reaches a division by zero.
2. `space_after_measurement.total_bytes = 0` is noted as invalid, but the auditor
   then divides `used_bytes / total_bytes` and raises `ZeroDivisionError`.
3. `schema_version = "bogus"` is converted with `int(...)` before controlled type
   validation and raises `ValueError`.

These are not controlled audit rejections. A caller receives an exception rather
than a verifier-owned problem report, so the repaired method has not satisfied the
assignment's controlled-rejection boundary.

### Eight malformed identity/version records pass

- `schema_version = 3` is accepted as though it were schema 2. The method documents
  exactly schemas 1 and 2; no schema-3 contract exists.
- Non-string values in each of `sku`, `revision`, `cid`, `sample`, `reader`,
  `measured_at` and `host` are accepted without a finding.

Those seven fields are required top-level members but are not type-checked. They bind
the record to the card/SKU/revision, physical sample, reader, acquisition time and
host; accepting objects, lists, numbers, Booleans or null in their place defeats the
closed-schema and provenance claim on which a later qualification would depend.

The minimum repair is to validate the top-level JSON value as an object; validate
`schema_version` without coercion and require exactly version 2 on this path; require
positive `bytes_per_mb` and positive capacity denominators before division; and
validate every required provenance/identity member against its declared primitive
type before any arithmetic. Retained controls must make each case reject with its
own field named and no traceback. Whether any identity string must also be nonempty
is a PM/WP-05 policy question and is not decided by this finding.

## Unchanged acquisition writer and legacy records

The acquisition writer is byte-identical between the rejected parent and repaired
head: `hardware/characterisation/measure_sustained_write.py` remains Git blob
`6388333d253b08d96403e895a4aa5be26bf491b1`, SHA-256
`32404b0cf3006fd4d398e64a0ba14527a3028534a279aeef467863be19eff851`.
No physical writer path was exercised.

All five schema-1 records are byte-identical between corrected ancestor
`c0e6a83ae44c2370288594b75915a214ba25deb7` and the exact repaired head:

| Record | Git blob at both revisions | SHA-256 |
|---|---|---|
| `onn-v10.json` | `9825f13275138d57c8180a0ab07d5bf93a000253` | `60e9413cd87d6c022b3f5460f9c2d2c17083d50d7c3b676975513e4b226df4a5` |
| `pny1.json` | `4313394aa630b08552335b01bb8a64760f28e3df` | `419f4c8010284822756daa8c8761b4fb1e2d3dbdc27da0dd4c2e62c802f9b8fb` |
| `pny2.json` | `5358b6e22ef07db75d951ba41c72130828c2234c` | `61486d179d4fe7e1f7d50642ce9101b03cceef0301bfbabf39af134bd29b6547` |
| `pny3-filled.json` | `7c94bce8478e9da1d56ac27209ff21c7e8670381` | `abbe5706b4a5b5f9dad0103ca9165190aa327a8db85588161d80f8b1f3afc4e2` |
| `pny3.json` | `8250c7d97619b88d23952c9eb9abbdd7c2814540` | `37a2b3d556dd16f3fdcc0340d54457a5a509759b63861749117eadeef557fc72` |

They remain schema-1 legacy observations, not complete WP-05 A-2 evidence.

## Executed checks

- Independent 66-case adversarial matrix: mounted and raw-device conforming
  baselines pass; 55 intended malformed controls reject with the intended marker;
  11 unresolved adjacent cases reproduce `P1-R23-V01` (three traceback, eight
  fail-open). The matrix returned nonzero by design. Scratch script SHA-256:
  `b0d04689e35413bc13d4517bdfd60fcb008ec69f9e08c25cbbbb2468a599ac3e`;
  result JSON SHA-256:
  `2f6918d27ef22736f03a0cee1b22fb57498a6e21461d6963bff9966a051fe92f`.
- `make -C hardware card-test card-audit` — pass: 26 retained controls, legacy
  audit and legacy arithmetic reproduction.
- `make -C tests check` at the exact verifier base — pass, including retained ops,
  playback and complete-playback packages and evidence replay.
- `make -C hardware spec-check thermal-check mech-check shell-test solenoid-test
  atomicity-test fabrication-gate-test packet-check packet-validate
  packet-duplicates` — pass.
- Real `make -C hardware fabrication-gate` — **CLOSED, exit 2, with five blockers**.

The scratch mutation program and JSON are execution aids, not repository inputs or
new acceptance sources; the cases, identities and outcomes needed for durable review
are recorded above.

## Preserved boundary and next owner

No card, reader or physical acquisition was accessed or run. No card, sample, SKU,
WP-05 A-2 record, atomicity behavior, production path or qualification result is
accepted. PR #87 is not approved or merged. The signed DRAFT-8 hashes, verifier
fixtures and product files are unchanged. Fabrication, charging, purchasing, safety,
wallet, physical-work, regulatory and all Michael-reserved approvals remain held.

PM may route a bounded auditor repair to Hardware. A new physical acquisition remains
blocked until an exact repaired head closes `P1-R23-V01` under fresh independent
re-audit. Verification stops at publication of this exact-head finding.
