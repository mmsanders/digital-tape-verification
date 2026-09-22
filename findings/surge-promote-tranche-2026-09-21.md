# SURGE record — promote classification + uninterrupted metadata paths (21 Sep 2026)

Independent verifier coverage only. Not product acceptance and not authorization
to merge verification main.

Verification-lead repair found that the original surge fixture's high-sequence
A1 slot was semantically valid, so it became live Side A and invalidated several
claimed premises. The original adopt-in-place success oracle also consumed one
extra sequence, and the degraded-B adapter attempted to mount Side B even though
DRAFT-8 requires that mount request to fail.

The repaired `tests/promote_draft8/` package now keeps the high-sequence A
partner structurally valid but semantically invalid, mounts Side A for the
degraded-B case, uses DRAFT-8's branch-exact 3/1/4 sequence consumption, checks
two-generation FRESH paths, exercises exact counter boundaries, adds the missing
allocating-complete path, and proves counter-before-capacity refusal ordering.

A product runner plus hash-bound offline replay are included. The runner
authenticates retained DRAFT-8 spec bytes before execution.

Deliberate exclusions remain: RESUME, crash/torn-write boundaries,
two-interruption closure, copied-audio byte identity/rendered PCM, caller-owned
stored-position clearing integration, WP-12a continuation/re-entry, and broad
product acceptance.
