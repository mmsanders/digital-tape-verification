# V405 returned-head plan grammar review regressions

Review-discovered after the original plan5 binding, exact reviewed ancestor d8b004d251b21cdd3dd757118366d8f147b145dc. Expected behavior comes from POWER-CUT-SCHEMA-R1 §2 typed model/unit/time fields and ADR209 strict identity. These seven CLI fixtures deliberately recompute the canonical digest and row links so a checksum mismatch does not mask the grammar predicate. A digest binds bytes; it cannot turn an empty required identity into a valid identity.

Dependency: unchanged sibling tests/selfrun_plan5_r1 (published tree77fa80c6). One valid null-CID/unknown-part record must pass. Missing required photos, empty brand, empty unit label, a list for card_unit, zero or boolean t_sched must fail closed with exit2 and no traceback. No photo file is required again at judge time by this test; only declared shape/required identity is checked. No physical claims.

`python -B tests/selfrun_review_r1/run.py --judge PATH/media_atomicity.py --out NEW_DIRECTORY`

Current-head reproduction only adds --record-known-findings: SHA256 pinned c4ae0dc33f2e47299e10c2606aaf03b61c07dd5f5fb306f5ea7a65cd43520976 and the exact six failures must reproduce. That mode makes a reproducible HOLD report, never clearance. Corrective candidates run without it and need7/7. Import this new package unchanged before the corresponding fix, preserving original reviewed/import lineage and all old test bytes. Host-checker behavior only; no card/target/firmware authority.
