# Format / dup / empty-promote refusal matrix

| ID | Assertion | Basis | Control |
|---|---|---|---|
| FMT-A01 | format RO writes nothing | TapeFS §9.6; Engine API inv. 18 | format write mutation |
| FMT-A02 | format `block_count∈{0,1}` is GEOMETRY with zero callbacks | TapeFS §2.1, §9.6; V8C-001 | geom-0 callback |
| DUP-A01 | aliasing is INVALID_ARG before any write | TapeFS §9.5 item 1 | alias allowed |
| DUP-A02 | dest `write==NULL` is READ_ONLY, zero writes | TapeFS §9.5 item 2 | conforming |
| DUP-A03 | dest `block_count==0` is GEOMETRY, zero callbacks | TapeFS §9.5 item 3 | conforming |
| DUP-A04 | dest too small for source A is DEST_TOO_SMALL, zero writes | TapeFS §9.5 item 4 | too-small allowed |
| PR-A01 | empty Side B promote is INVALID_ARG, more_work false, zero writes | Engine API inv. 22 / 30; TapeFS §9.3 | empty promote wrote / succeeded |

Excluded: template/fallback step-1 writes, identity-assignment commits,
WP-10 crash tables, two-interruption partner-first, generation-exhausted
zeroing outcomes, destination remount classification, long-operation
continuation (WP-12a), product observations.
