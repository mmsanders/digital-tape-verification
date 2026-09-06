# Surge DRAFT-8 candidate — independent adversarial review

Review target: the four user-supplied surge-support files corresponding to Digital-Tape PR #25. The three hashed spec files authenticate exactly to the supplied DRAFT-8 manifest and to the final hashes advertised by surge support:

- TapeFS `a769c772ba9efd867badeaa6dbc4dd731913a31b01a5c296336686463093e792`
- engine API `d19c8f2453c258c582622c3447a792215debd3ec68df81c306d47ae5b57da836`
- acceptance `d2cf1f620f582df46bbcd736eed589aefe04512ca7953f15601850210d51ca81`

**Status boundary:** this is a review of the surge candidate bytes, not a claim that the PM has canonically issued DRAFT-8 on `Digital-Tape/main`. It is intentionally filed under a surge-candidate name rather than `spec-review-draft8.md`. If the PM later issues byte-identical files, these findings apply mechanically to that issued bundle; otherwise the issued bytes require their own authentication/review.

Method: clean pass from the actual three spec files, not from surge's claimed dispositions. The Verification Lead note was used only to preserve process boundaries (surge is not the PM; no implementation inspection; a paper pass is not WP-10) and not as evidence of correctness or as the review's attack list. After the clean pass, the candidate was cross-checked against the advertised V7 dispositions and the surge self-review. No `engine/` source, implementation branch/diff/issue, or unlanded implementation artifact was inspected.

Summary: **0 blockers, 3 majors.** Two majors (`V8C-001`, `V8C-002`) touch the Phase-0 freeze candidate; one (`V8C-003`) is in the later operations/WP-10 scope. Therefore the candidate **does not yet meet the standing zero-blocker/zero-major Phase-0 signature gate**, but it is a material convergence step: the DRAFT-7 cartridge-loss blocker V7-001 does not reproduce under DRAFT-8's partner-first/candidate-last rule, V7-002's zero-needed counter defect is corrected, and V7-004/V7-005 are singular and testable. The V7-003 raw-destination direction is substantially improved but its equal-generation-divergent crash oracle still has the later-scope acceptance mismatch in `V8C-003`.

Independent V7-001 trace result: from healthy, one-copy, and newer-partner/stale-candidate superblock shapes, an ordinary §4.6 update cannot begin its candidate write until the partner write has flushed successfully. If the partner write/flush fails or tears, the old selected candidate is untouched. Once the partner flush succeeds, the new generation is durable and selected; a torn/failed candidate write cannot roll selection below it. Repeating the argument from every resulting one-copy/stale-partner state preserves the same property. No repeated-interruption rollback was found.

Acceptance verdicts: **WP-11 remains testable as written. WP-12a remains testable as written. WP-10 is not final-testable as written until `V8C-003` is dispositioned**, because the exhaustive equal-generation-divergent raw-destination case has a permitted TapeFS crash state that the WP-10 per-operation allowed-state sets do not admit. Generic crash infrastructure and all non-disputed WP-10 cases may proceed.

---

FINDING: V8C-001
SEVERITY: major
AREA: `tapefs-v1.md` §2.1, §3, §4.1 phase 1/2, §9.5 preconditions, §13; `engine-api.md` §3; `acceptance.md` WP-06d / WP-10
CLAIM: `block_count` is explicitly untrusted, but mount and duplicate use it to address/read the mirror superblock before the geometry check that is stated to defend against it.
REPRO: Give `tape_mount` a device with `block_count = 0`. The mirror's normative LBA is `block_count - 1`; in the u32 API this is `0xFFFFFFFF`. §4.1 phase 1 requires “read both copies” before phase 2 evaluates `GEOMETRY_OK` or checks the stored mirror field. The engine therefore issues a read using the untrusted, already-underflowed address before the stated defense can run. Even for small nonzero impossible geometries, phase 1 performs media reads before the §2.1 line-2 rejection `block_count > LBA_CHUNK_BASE`. The same ordering defect exists in `tape_dup`: precondition 3 raw-classifies both destination superblocks before precondition 4 checks `GEOMETRY_OK`; `tape_format` correctly does geometry before raw classification.
IMPACT: A malformed/untrusted caller geometry can cause an out-of-range block callback or an I/O result before the normative `TAPE_ERR_GEOMETRY` refusal, so the claimed geometry defense and deterministic refusal order are false. This is not a cartridge-corruption blocker because the premature operation is a read, but it sits directly in candidate §4.1 and creates divergent observable behavior at the block-device boundary.
FIX: Add a pre-read device-size guard before mount phase 1, preferably the candidate-independent part of `GEOMETRY_OK` (`block_count > LBA_CHUNK_BASE`, or an explicitly equivalent minimum that makes both superblock reads addressable), then perform the full candidate-dependent geometry validation in phase 2. Move duplicate's geometry/capacity refusal checks ahead of raw-superblock classification, or define an equivalent pre-read guard before classification. Add WP-06/WP-10 cases for `block_count` 0, 1, and the minimum-invalid boundary asserting the specified error and zero out-of-range callbacks.

---

FINDING: V8C-002
SEVERITY: major
AREA: `tapefs-v1.md` §4/§4.6, §5, §9.5 step 4, §9.6 steps 4–5; `engine-api.md` invariant 7 (§12); `acceptance.md` WP-10 counter assertions
CLAIM: The candidate simultaneously requires `sb_generation` to strictly increase on format/duplicate commits and requires those exact identity-assignment commits to reset `sb_generation` to 1, so the frozen invariant is unsatisfiable literally.
REPRO: Start `tape_dup` on reusable media whose selected old superblock is generation 100. Step 1 writes the WIP barrier at generation 101. Step 4 explicitly commits the new cartridge with `sb_generation = 1`, and §4.6 explicitly excludes that identity-assignment commit because “this generation goes backwards.” `tape_format` says the same for its final mirror/primary writes. Yet TapeFS §5 says `sb_generation` advances on logical superblock updates including “the commits of format and duplicate,” and engine invariant 7 says it “strictly increases on every logical superblock update” including “format's and duplicate's commits,” before later saying format/duplicate reset it to 1 and the rule does not span them.
IMPACT: The byte-exact algorithms are clear, but the candidate's normative invariant/property suite cannot be implemented or independently asserted as written. A literal invariant-7 verifier rejects every reusable-media format/duplicate; one that silently applies the later exception violates the preceding enumerated rule. Both TapeFS §5 and engine §12 are in the Phase-0 freeze candidate.
FIX: Define the identity boundary explicitly and consistently. For example: `sb_generation` strictly increases for every ordinary update of an existing cartridge, including format/duplicate **step-1 WIP barriers**; the final format/duplicate identity-assignment commit establishes a new cartridge and resets `sb_generation = 1`, so monotonicity does not span that commit. Remove “the commits of format and duplicate” from the strict-increase list (or rename it to the step-1 barriers), and make invariant 7/acceptance use the same wording.

---

FINDING: V8C-003
SEVERITY: major
AREA: `tapefs-v1.md` §9.5/§9.6 raw classification and crash tables; `acceptance.md` WP-10 raw-admission cases and per-operation allowed-state sets
CLAIM: TapeFS explicitly permits a “surviving primary” state after the first zero in the equal-generation-divergent zero-both path, but WP-10's exhaustive per-operation allowed-state sets do not admit that state/result family.
REPRO: Supply a raw destination whose primary and mirror are both CRC-valid at the same generation but byte-divergent, as WP-10 explicitly requires. Classification chooses zero-both. Tear or power-cut after the mirror zero becomes durable and before the primary is zeroed. TapeFS's duplicate table says the primary is now the sole candidate; the format table says the same. That surviving primary can carry any admission prefix that structural validity alone allowed: `version_major = 2` (remount → `TAPE_ERR_VERSION`), `state = WRITE_IN_PROGRESS` (→ `TAPE_ERR_INCOMPLETE`), unsupported state/stage, invalid geometry, bad indices, or a fully mountable old logical state. A zero-byte tear can also leave the original equal-generation divergence and therefore `TAPE_ERR_INCONSISTENT`. WP-10 nevertheless gives Duplicate only pre-copy cartridge / `INCOMPLETE` / blank `BAD_MAGIC` / completed copy, and Format reusable only old cartridge unchanged / `INCOMPLETE` / new empty. It separately mandates exhaustive torn writes on the equal-generation-divergent shape.
IMPACT: A conforming implementation following TapeFS can fail the literal WP-10 oracle, so the first-green WP-10 operations-freeze gate is not singular. This is not a new cartridge-loss blocker: format/duplicate are explicitly destructive raw-destination operations and TapeFS does enumerate the intermediate bytes. It is an acceptance/spec consistency defect in the later behavior scope.
FIX: Either (a) extend WP-10's format/duplicate allowed-state sets with the exact “surviving primary” outcome at the zero-both boundary, including the error/result derived by mounting that surviving copy and the original `INCONSISTENT` state when no bytes landed; or (b) redesign the equal-generation-divergent first step to install a fully specified higher-generation v1 WIP barrier rather than exposing one arbitrary former copy, where headroom permits. In either case, make the exhaustive oracle byte/state based rather than compressing this boundary into the ordinary reusable-media set.

---

## Clean-pass notes (no finding)

- **V7-001:** fixed in the candidate. §4.1 now records stale lower-generation partners for repair, phase 4 repairs them without incrementing generation, and §4.6 preserves the selected candidate until the replacement generation is durable. The promote step bodies themselves cite §4.6; the fix is not only in a reading note.
- **V7-002:** fixed. §4.5 consults each counter only when that branch's `needed != 0`; empty re-spool and NOTHING-TO-DO promote remain legal at stored `0xFFFFFFFE`/`0xFFFFFFFF`.
- **V7-003:** the v1 WIP template, classification-as-plan, refusal-before-write rule, and foreign-major handling are mechanically much better. The remaining issue found is `V8C-003`, not the DRAFT-7 ambiguity.
- **V7-004:** fixed. Duplicate copies the source's 32-byte label byte-for-byte and WP-10 asserts it.
- **V7-005:** fixed. `tape_service` is allowed in every mounted row except Faulted, consistent with the table and WP-12a.
- The DRAFT-7 running `next_sequence`, promote/re-spool branch counts, degraded-B override, FAULTED override, callback re-entry rules, interpolation/transport arithmetic, and WP-11 portability gate did not produce a new finding in this pass.

**Freeze recommendation:** do not sign Phase 0 on these bytes yet because `V8C-001` and `V8C-002` are majors inside the candidate. This is nevertheless a credible near-freeze candidate: no blocker survived the independent pass, and the DRAFT-7 cartridge-survival blocker is materially resolved. After the two candidate majors are corrected, re-review the exact issued bytes; operations/state still require a green, singular WP-10 after `V8C-003` is fixed.