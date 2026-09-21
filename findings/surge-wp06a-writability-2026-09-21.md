# WP-06a v1.1 effective-writability tranche — temporary Verification repair

Original surge scope: the WP-06a mounted-mutator and repair-skip rows that the existing mount package deferred. Not package acceptance.

Temporary Verification review on 21 September 2026 repaired the draft without inspecting product implementation. The package now separates healthy v1.1 mutator cases from repair-required media; covers both structurally invalid and valid-stale superblock partners; owns product execution/disposition through `runner.py`; supplies a verifier-owned public-API probe with a genuinely non-NULL write callback; rejects omitted/wrong-side calls; checks the exact READ_ONLY/BUSY precedence; compares final media byte-for-byte; and binds expectations to the canonical DRAFT-8 SHA-256 manifest.

The original package also required zero flushes. That was stronger than issued WP-06a, which requires **zero `dev_write` calls**. Flush callbacks remain recorded as evidence but are not an invented acceptance failure by themselves.

Verifier branch base at review: `8ca23c6acfa9e3ec5e96d54f2ec93cb8c329f3c9`.

Still excluded: source-slot `write == NULL` (WP-36), raw format/dup gating, crash/continuation coverage, and product-source/package acceptance. Synthetic self-test success is not product evidence.

Next owner is Software for mechanical compilation/linkage of the verifier-owned probe against the real public API. Verification dispositions the exact resulting product observations. Do not merge or describe this draft as acceptance merely because self-tests are green.
