# WP-36 source-slot tranche — temporary Verification repair

Original surge scope: deterministic `write == NULL` core beneath WP-36; not package acceptance.

Temporary Verification review on 21 September 2026 repaired the draft without inspecting product implementation. The package now owns product-run disposition through `runner.py`; makes an otherwise-unloggable NULL-write failure observable through the frozen debug `dev_write` assertion and process status; rejects omitted playback calls; checks READ_ONLY/BUSY state-matrix precedence; exercises W-gated operations from both sides; adds the mount-time superblock-repair hazard; expands negative controls; defines the compact verifier-envelope semantics; and binds expectations to the canonical DRAFT-8 SHA-256 manifest.

Verifier branch base at review: `8ca23c6acfa9e3ec5e96d54f2ec93cb8c329f3c9`.

Still excluded: the required 100,000 random transport-sequence acceptance run, v1.1 WP-06a, raw format/dup gating, and product-source acceptance. Synthetic self-test success is not product evidence.

Next owner is Software for mechanical adapter linkage only. Verification dispositions the resulting exact product observation bundle. Do not merge or describe this draft as WP-36 acceptance merely because its self-tests are green.
