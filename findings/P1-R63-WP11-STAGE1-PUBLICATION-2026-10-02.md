# P1-R63: WP-11 Stage 1 independent publication

Verification #143, issued by PM Product #365 / ADR-158. Product input
`41d546f4d799dbe8642135cc228ac50de2869b9c`, verifier base
`ffaad65f2d5e6724e521545fbb9706dec145b163`, DRAFT-10. Onboarding and current role
scope refreshed against Product's role docs and charter. One context, no subworkers.
No engine implementation, Software candidate diff or Product output was read to
derive expectations. Only the normative spec, PM CLI contract, golden runner
shape and previously accepted verifier dispositions informed this publication.

## Published package

- `tests/golden`: ten independent references, four exact source excerpts,
  tapectl-only MANIFEST, source licence/conversion/hash provenance, model and
  eight causal controls. Every tree WAV is <= 970,244 bytes. Full source originals
  and canonical WAVs are published as checksum-verified fixture release assets.
- `tests/wp11_portability_r63`: test-only interpolation-hook harness, independent
  signed-division/floor oracle, 1,572,852 boundary pairs + 10,000,000 seeded PRNG
  pairs + 24 explicit extreme pairs. Seed `0x63d10a5e`. Synthetic conforming hook
  plus five arithmetic controls. Local GCC passes all 11,572,876 comparisons and
  kills all five controls; publication CI additionally requires Clang.
- `tests/wp11_ledgers_r63`: immutable evidence pins and 63-row paper delta. WP12/12a
  has 36 rows: 31 covered, two unreachable, three vacuous, zero open. WP08/09
  observable non-listening rows are covered. WP08-L01/L14 and WP09-L01 remain
  listening-held pending exact Product equality and Michael #367.

Sources downloaded successfully, original hashes checked, canonical conversion
rechecked byte-exact. Music recording licence matches PM's public-domain pin;
voice licence matches CC0. No silent source substitution or gain adjustment.
Overdub has 27 positive and five negative saturated samples. Model controls
catch advance-before-fetch, missing reverse frame zero, chunk wrap, omitted
splice tail, wrapping mix, retained overwrite tail, stale reset and stale promote.

## Required checks and handoff

Merge only after publication CI and the standing verifier CI are green. Publication
CI checks frozen reference/model equality, SHA256SUMS, GCC+Clang synthetic hook
tests and the ledger census. The source-assets workflow verifies exact source
and canonical hashes before creating the fixture archive. CI reports are attached
to the publication PR; #143's Stage 1 comment records immutable commit/subtree
identities and check results after merge. Michael #367 receives all ten direct WAV
links and listening cues after that merge.

Stage 2 is already routed in #143: wait for Software #366's returned exact PR
head, authenticate import/Structural Rule 1 ordering, run Product golden equality,
authenticate both toolchains including embedded/narrow-int and all seven specified
mutation patches and verifier kills. Leave #143 open between stages. Publication
and synthetic checks do not accept Product behavior or human listening.

Excluded: hardware, media qualification, Product release, and any new assertion
outside #143. Next owner after Stage 1: Verification, on Software #366's return;
Michael independently owns the listening sign-off.
