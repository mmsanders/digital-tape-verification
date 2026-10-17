# Verification197 — retained any-subset operation rows

**Available selected-state operation judgments PASS within this report's bounds.
No new Software defect found. Overall443 remains HELD; no integration or batching
permission.** Missing coverage is separated below from completed evaluation.

Authority ADR185/Product449, live197 updated2026-10-17T14:27:10Z with no scope
updates at start. Product main input05315e2d464376400e122cd982dbb93dc084c1fb;
exact candidate443 `85b7c3fd0b123ae7e5d54cb9f7bb424fbc613542`. Verification original
input65dbd21f4dfd78ef3a1165074115535701efc7b5. First published196 Stage1 through
PR198/50091d0f8ce2edff3d56b13b6f090490f8337fd0, normal CI39041871250 SUCCESS,
freeing Software452. Its actual S1/S4 candidate is not returned yet;196 Stage2
remains pending, separate from this bounded197 disposition.

An own196 authoring correction accompanies this publication: the627-case parser
adapter now checks the generic message fallback on invalid reports, not just
rejection. No Product code was used to derive this correction. Original inputs,
valid outcomes and spec pins remain unchanged; old198 bytes stay in history.
Software452 should import the corrected package from this merged publication.

Individual Verification lead, no subworkers. Four required onboarding docs,
Michael447 and live196/197 read. No engine/Product implementation inspected or
modified; only original independent fixtures/raw parsers/state predicates used.
Imported model treec6cb573d654d337fef2f616f11cce0cee74e8968, A8 engined96b4245e04d74078f8938744b1394c3018516f7
and DRAFT10 pins unchanged (tapefs2a6a9f7b…9c17eba, APIaa042e41…c66b33a,
acceptance50aa63bd…9b9e547). Prior189/191/195 exact binding/model/input/PCM
facts, V186-01/V186-02/checksum PASS and585 specific pre-index-commit contexts
carry unchanged. The old model/durability campaigns were not rerun.

## Inputs, counts and meaning

The same13 retained ZIPs and1959 indexed members authenticate; IDs/full digests,
size/commit/expiry are in the immutable191 artifacts.json and new
authentication-result.json. Unpacked shard directories stay separate. Each
snapshot/remount already had byte-to-projection binding proved; this review adds
operation judgments rather than recomputing full projected-image hashes.

[coverage.csv](coverage.csv) enumerates every actual scenario with run count,
restored bases, deduplicated context count and uninterrupted fixture control.
Per-scenario permitted states and counts are in the four family result JSONs.
A context is scoped by shard/part, scenario, initial image, projection and remount;
these are not counts of distinct media, independent executions or new test cases.

| Family | Actual scenario rows | Run records evaluated | Selected contexts | Uninterrupted fixture controls |
|---|---:|---:|---:|---:|
| Core record/reset/stage callers and closures |20|1278|102992|20|
| Promote fresh/adopt/first-use,12 closures,11 resume seeds |26|1266|952|26|
| Format/dup,7 raw shapes each |14|938|633|14|
| Re-spool decline and v3 passes1/2 |3|513|20672|3|
| Corrected host load |1|Retained projected complete-history route|31216 command contexts|1|

Run records include retained duplicate/end boundaries and the superseded unfired
V186-02 coordinates; they are not asserted to be that many successful faults.
195 already closed the twelve missing coordinates. SAMPLED labels, multiplicity,
setup callbacks and missing actual fault executions retain their prior meaning.

## Coherent operation-row judgments

| Original row / predicate | Completed independent judgment | Remaining evidence or execution |
|---|---|---|
| Record overwrite/overdub/splice commit | Selected B is the original sequence20 or the exact original mode's sequence21 entries. A index and all A-owned chunks preserved. Original one-zero-frame setup payload checked; old source timeline protected. Complete fixture controls select21. | These are the published one-frame fixture shapes, not arbitrary record sessions; API/quarantine/torn controls retain their existing separate Phase1 bounds. |
| Reset healthy | Original B20 or reset B21/A references; A indices/all chunks unchanged. | No new full recording state-matrix claim. |
| Reset degraded/equal | Side A stays mountable; original degraded B, sole valid old B slot500 after entry invalidation, or new501/A references are all permitted. The third intermediate is not called corruption. All chunks unchanged. | Native callback/repair event detail beyond retained raw snapshots is not manufactured. |
| Stage-clear arm/reset/respool, healthy and4 closure seeds each | Current generation10/stage1/H3 or11/stage0/H3; no rollback below the actual restored candidate. A indices/chunks0..2 unchanged. Arm/reset retain the prescribed B timeline. Re-spool selected B may relocate to3/4, but its full chunk hash equals original live chunk2. Complete controls select cleared stage. | Long re-spool boundaries/persistence remain SAMPLED. The four stale/unfired old coordinate entries are not extra fault coverage. |
| Promote fresh / A fallback / mixed phase1 B | Stage0 keeps old H2/A and old or compacted B; first-use has H0/empty A. A audio is exactly old/promoted/empty as issued; B always renders the promoted source bytes. Structural sequences are unique. | Not every physical reader/cut or API-contract path executed here. |
| Promote RESUME rows1/2/3 | Exactly one raw row; H=S+len with expectedS0/3 and128 frames; corresponding step5/8/9 classification. Row2/3 actual operation traces contain no repeated chunk copy. Generations never fall below actual restored candidate, including closure seeds. | Canonical11 resume seeds and two distinct restored bases are executed bounds, not a new re-run of every possible projected image. |
| Promote decline / final | Stage0/H1 and A=B={0,0,128}, exact promoted audio. Every26 uninterrupted fixture control satisfies original terminal predicate. | Device-side position-clear and all original host API-state receipts remain their existing distinct criteria. |
| Format/dup invalidation and identity assignment | DRAFT10 raw classification derives step1 from the actual restored bytes, including fallback/blank/residue semantics where reached. Actual SB targets/bytes form the permitted prefix with successful barrier separation. No data/index work before step1; no identity before durable new A0/B0/standby state. Actual selected UUID and permitted mount result agree; old identity never coexists with changed/durably replaced index content. Complete14 controls select fresh identity. | Only7 supplied raw shapes; crafted DRAFT10 residue shapes/mirror-candidate exhaustion and broader arbitrary-subset residue re-runs are not supplied by this return. No full duplicate source-PCM/label/source-read-only proof is inferred from destination header/UUID snapshots. |
| Re-spool pass1/pass2 and decline | A metadata/SB unchanged; B layout and sequence follow actual restored base plus at most2 new commits. All raw tape_info/frontier facts match the original invariant. This includes legitimate703/704 on a second-interruption base; fixed original701/702 are not applied blindly. | Long-coordinate masks remain sampled; no comprehensive repeated-LBA operation coverage. |
| Re-spool copy/live-set/durability |323 distinct actual base/trace pairs:357241 attempted copy units match independently authored pattern bytes (decline only its normative40-byte prefix); never write below H or to current A/B live chunks. Every69 selected-index commit checked has complete correct data already durable. Initial live data is independently checked from actual restored bytes. | This is an operation causality proof over actual traces plus carried projection binding, not a new dump execution for all20672 contexts. Padding outside the decline's logical payload is deliberately unconstrained. |
| Host load supported audio states | Actual canonical WAV hashes match original empty or exact golden voice.wav;31216 corrected fresh command contexts yield31183 empty/empty,13 empty/new,20 new/new. Never new-A/empty-B. One complete route yields both voice sides. Verify is NULL-write, leaves image unchanged; ten NEEDS_REPAIR contexts remain lawful/bounded. |404 missing/unreachable host fault coordinates; cuts are projections of a complete actual trace. Full per-command seam JSON is absent, so event-level repair/zero-write proof cannot be regenerated from digest/summary alone. |

The re-spool trace check evaluates actual logical copy payloads/current live sets
and successful-barrier prerequisites. It does not repeat arbitrary-subset selection
or assume an error acknowledgement means no bytes can land. Failed barriers do not
become successful. Pending error writes remain eligible under the carried model.
All original logical-state rules are reused; the old ordinal-only persistence
planners are not reapplied as arbitrary-subset oracles. No universal unchanged-card
rule is imposed on destructive format/dup.

## Positive and detecting controls

Honest baseline contexts pass before mutations. New controls all reject:

* Core: one-bit mutation of an actual protected chunk, with its real changed digest.
* Promote: changed retained live chunk bytes corrupt the permitted timeline.
* Format/dup: CRC-valid old UUID over newly committed indices cannot pass identity.
* Re-spool: destroyed actual A index; wrong actual copy byte; copy below H/live set.
* Host load: new A paired with empty B violates the permitted publication ordering.

Control outputs are in the result JSONs. They are deliberate mutations of retained
bytes/observations, not claims that Product emitted those failures. New actual
Software defects were not found. Initial reviewer assumptions about fixed resume
sequence numbers were corrected against the original contract/actual restored
bases before disposition; no Software correction is requested for703/704.

## Minimal next needs and exact acceptance stop

The195 map's independent evaluation is now complete for the **available scopes
above**. Remaining gaps are actual scope/input/execution limits, not an excuse to
rerun existing packets or demand a new runtime-ledger format:

1. For full duplication data/label/source safety beyond identity: bind the actual
   source raw bytes/label/read-only capability and rendered source/destination A/B
   observations for the distinct fresh selected destinations. Reuse existing
   traces/masks/images; a narrow remount/render supplement can supply this rather
   than replaying all format/dup or engine campaigns. Current destination headers
   alone do not prove those independent source properties.
2. For full arbitrary-subset coverage: PM must issue the bounded next coverage,
   including original DRAFT10 residue/mirror-candidate shapes and broader repeated-
   LBA/long-copy coordinates. Preserve Phase1's already accepted torn suites; this
   model remains512-byte atomic and does not qualify media. Do not launch175CPUh.
3. For host-load fault/repair-event claims: bind only the missing write/barrier
   fault route and retained/re-observed full per-command seam detail from pristine
   projections. Do not replace the existing fresh-image/audio PASS, pretend404
   missing coordinates ran or call projected host histories interrupted execution.
4. Media atomicity, target timing, batching/call-shape ruling, real hardware and
   physical/native/package criteria remain with their existing owners. These are
   not Software algorithm defects asserted by this report.

**Overall exact443 integration PASS is NOT licensed.** Software owns integration
only after an explicit overall exact-head PASS plus required CI. PM owns the next
coverage/Q-P2-1(b) ruling. Route this bounded disposition directly to Software's
443 thread with PM449 copy; close197 at this coherent published family/missing-
evidence stop.196 remains open only for its issued actual S1/S4 return. Nothing in
this report accepts436 or changes Michael447's ready Windows work/no Mac run.

## Reproduce only these new judgments

Fetch13 artifact ZIPs listed in191 artifacts.json, unpack each into its own
ROOT/<artifact-name>; no Product build/run needed. From Verification root:

```sh
python3 -B findings/P2-SUBSET-ROWS-2026-10-17/authenticate.py ROOT --out authentication-result.json
python3 -B findings/P2-SUBSET-ROWS-2026-10-17/rows.py ROOT core --out core-result.json
python3 -B findings/P2-SUBSET-ROWS-2026-10-17/rows.py ROOT promote --out promote-result.json
python3 -B findings/P2-SUBSET-ROWS-2026-10-17/rows.py ROOT dup --out dup-result.json
python3 -B findings/P2-SUBSET-ROWS-2026-10-17/rows.py ROOT respool --out respool-result.json
python3 -B findings/P2-SUBSET-ROWS-2026-10-17/respool_copy.py ROOT --out respool-copy-result.json
python3 -B findings/P2-SUBSET-ROWS-2026-10-17/load_rows.py ROOT --out load-result.json
```

One process per original verifier family avoids their bare module-name collisions.
All errors/controls/counts are retained. Raw packets remain outside git with full
digests and January2027 expiry; retain durably before expiry. All committed files
are under1MiB. Existing normal publication CI is selected by this report's path;
no new permanent gate or modified acceptance assertion.
