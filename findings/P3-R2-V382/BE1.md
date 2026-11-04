# V382 — ready BE1 binding publication

Receipt: public BE1-IF/2 at97a5502216d1822d1708edad922e856b08dc909b;
authority Product51d0f8f812fe6ffbba71c2bf9a7426ee5d23ed78 (PM655/ADR204),
issue382 updated2026-11-04T03:17:51Z. Prior V380d23a90f7 carries unchanged.

Published package: tests/be1_binding_r1. 109 deterministic bundle cases and four
fake-port capture cases, plus nine checker-harness and two capture mutations.
Windows self-test results accompany this record; Linux CI runs the same harness.
Self-tests exercise fixture generation, exact reference authentication, result
predicates and confinement with explicit test doubles. **No Product checker/helper
execution or clearance:** those implementations are absent in the declared input.
No reference regeneration, engine render, golden/fault/target campaign repeated.

The exact remaining dependencies were returned to Software652 in
https://github.com/mmsanders/Digital-Tape/issues/652#issuecomment-6623537388 :
F5 precedence, file-role schema, superseded-error exits, capture timeout/info/send
semantics. Ready subset may be imported unchanged for its documented boundary.
Uncovered behaviors remain held pending a corrected declaration and additional
independent binding. This is not a repeated blanket absent-schema dependency.

Every generated fixture is simulated. No physical witness is fabricated; false
actual/witness markers are negative parser controls only. Target F1/F2/F5, timing,
output caps, media qualification and independent raw/witness audit remain pending.
No physical session, purchase, DRAFT11 issuance, batching, fabrication or charging.
