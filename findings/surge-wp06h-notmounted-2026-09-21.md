# WP-06h not-mounted tranche — temporary Verification repair

Original surge scope: Engine API §10 Not mounted / acceptance WP-06h. Not package acceptance.

Temporary Verification review on 21 September 2026 repaired the tranche without inspecting product implementation. The package now gives **each ordinary call its own fresh process/case** before mount and after a successful mount→unmount transition, so one defective refusal cannot alter the state observed by later probes. It owns product execution/disposition through `runner.py`, supplies a verifier-owned public-API C probe, checks exact call presence and setup sequencing, exercises `tape_dup` specifically as an unmounted source with a distinct valid raw destination, and checks `tape_tell`'s output sentinel in both phases.

The original surge draft also treated zero writes/flushes as a WP-06h assertion. The issued WP-06h text requires the `TAPE_ERR_NOT_MOUNTED` result for every ordinary call and an untouched `tape_tell` output; it does not separately specify a zero-callback rule. The repaired probe records callback deltas for diagnosis, but Verification does not silently add that unstated acceptance condition.

Verifier branch base at review: `8ca23c6acfa9e3ec5e96d54f2ec93cb8c329f3c9`.

Still excluded: the behavior of `tape_init`, `tape_mount`, `tape_format`, and destination-side `tape_dup`, which are the explicit Not-mounted-row exceptions; crash/continuation behavior; and product-source/package acceptance. Synthetic self-tests are not product evidence.

Next owner is Software for mechanical compilation/linkage of the verifier-owned probe against the real public API. Verification dispositions the exact product observations.
