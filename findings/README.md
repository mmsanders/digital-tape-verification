# Verification findings index

**Phases 1 and 2 complete; Phase 3 open.** Current acceptance boundaries are in
[CAPABILITY-STATUS](../CAPABILITY-STATUS.md). Findings retain their original input,
coverage, exclusions and immutable publication identities.

| Current Phase 3 record | Scope |
|---|---|
| [Hardware18852b5 HOLD review](HW651-18852B5/DISPOSITION.md) | Published27/71/229 pass; two reproduced code findings and unresolved Product CI |
| [Hardware651 remaining binding](HW651-RECORDS/DISPOSITION.md) | Saved records, plan4 and qualified completed-write rollback tests; no Product or physical clearance |
| [Software652 IF/3 binding](SW652-IF3/DISPOSITION.md) | 53 checker/47 fake-port cases; ready for import, no implemented-head or target clearance |
| [V382 executable bindings/return](P3-R2-V382/DISPOSITION.md) | Ready BE1 and rig row tests; exact R374-1 PASS; whole kit/rig review pending corrected declarations/implementations |
| [V380 Stage A](P3-R2-V380/DISPOSITION.md) | Rig expectations and revised DRAFT11/BE1 preflight; interface dependencies, no new candidate clearance |
| [V378 correction and exact-head clearance](P3-R1-V378/DISPOSITION.md) | ADR-202: ee478a91 cleared for authorized off-target integration; 28 admission cases pass, 4 controls reject, prior evidence authenticated and carried |
| [Software642 exact-head disposition](P3-R1-SW642/DISPOSITION.md) | ee478a91: host PCM/static budgets pass; bootstrap-recognition spec/test disagreement held for PM; target checks pending |
| [#374 Stage B rig-method review](P3-R1-374/RIG-METHOD.md) | Not cleared: reproduced non-qualifying-tear blind spot, cut/busy and electrical proof gaps; no physical run |
| [#374 Stage A disposition](P3-R1-374/DISPOSITION.md) | 365 actual faults PASS; six long requests proved unavailable; ten host goldens PASS; target/candidate acceptance excluded |
| [#374 inputs](P3-R1-374/INPUTS.json) | Exact Product/Verification refs and authoritative document hashes |
| [DRAFT-11 / FW-1 preflight](P3-R1-374/PREFLIGHT.md) | Independent consistency, testability and golden-preservation findings; proposed revision remains not in force |
| [P3-R1 package](../tests/p3_r1_r374/README.md) | Authored expectations and reproduction commands |

The [complete pre-Phase3 findings index](https://github.com/mmsanders/digital-tape-verification/blob/1938e65130d338a11404ba5dedae0b1c471203da/findings/README.md)
links all older dated dispositions. Its exact bytes are also retained in
[the archive](../archive/FINDINGS-INDEX-PRE-P3-374.md), with SHA-256 recorded in
[the archive index](../archive/README.md). Later accepted boundaries supersede
older HOLD/pending wording; old issue chatter is not an active assignment.

Phase 2 closed with G2 deferred, not waived. Hardware/media/target qualification,
fabrication/charging gates and Michael's reserved decisions remain separate.

[V388 exact Software kit HOLD](V388/DISPOSITION.md): Hardware publication; Software deadline/confinement/type findings; absent CI658 and Hardware correction dependencies.

[V390 CI/HW review](V390/DISPOSITION.md): required supported-platform census removed; original Hardware defects corrected, two outer-loader exceptions remain.

[V392 Hardware correction](V392/DISPOSITION.md): c55e5ad bounded artifact-consistency correction cleared; current-base required CI and physical holds remain.

[V394 laneA](V394-KIT/DISPOSITION.md): corrected kit0db6ce5c clears bounded behavioral findings; required ordering-policy CI remains blocked.

[V394 independent policy bindings](V394-POLICY/DISPOSITION.md): census companion and real history fixtures/provenance contract ready; corrected Product adapter/gate candidates pending.

[V397 runner restoration](V397-RUNNER/DISPOSITION.md): bounded Ubuntu24.04 restoration clears, existing differential/control identities retained.

[V397 complete census replay](V397-CENSUS/DISPOSITION.md): 25 actual-adapter cases, complete original retained artifacts, companion/DAG/A8 controls pass; current-base Product CI remains required.

[V397 ordering correction](V397-ORDER/DISPOSITION.md): narrow provenance route disposed on actual histories/kit lineage, current-base Product CI remains required.

[V398 ADR208 preflight delta](V398-PREFLIGHT/PREFLIGHT.md): hands-on method, strict facts, four wording findings and unchanged frozen bundle; no retired lab gates.

[V398 hands-on semantic tests](V398-METHOD-TESTS/DISPOSITION.md):41 fixtures/10 controls; actual serial binding needs Software declaration.

[V398 self-run Hardware method](V398-HARDWARE-METHOD/DISPOSITION.md):11 actual production-judge cases and planted-tear control pass; optional-CID/new-route, policy and implementation dependencies remain.

[V405 self-run bindings](V405-SELFRUN/DISPOSITION.md): settled ADR209 decisions bound before implementation; no physical/candidate clearance.
