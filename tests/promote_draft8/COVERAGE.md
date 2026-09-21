# Promote classification and completed-path matrix

| ID | Assertion | Basis | Control |
|---|---|---|---|
| PR-A01 | Empty B is `INVALID_ARG`, `more_work` false, zero writes | TapeFS §9.3.0 | empty wrote / succeeded |
| PR-A02 | Degraded-B is `NO_VALID_INDEX`, zero writes | TapeFS §9.3.0 / §4.4 | fixture live-B premise |
| PR-A03 | A≡B entry arrays is NOTHING TO DO: `TAPE_OK`, zero writes | TapeFS §9.3.0 | nothing-to-do wrote |
| PR-A04 | `cartridge_sequence == 0xFFFFFFFD` is `SEQUENCE_EXHAUSTED`, zero writes | TapeFS §4.5 / §9.3.0 | conforming |
| PR-A05 | No staging room and not adopt-in-place is `CARTRIDGE_FULL`, zero writes | TapeFS §9.3.1 | full allowed |
| PR-A06 | Adopt-in-place + disjoint `[0,len)` completes at `[0,len)`, `H=len`, stage 0 | TapeFS §9.3.1–§9.3.2 | skipped phase-2 copy |
| PR-A07 | Adopt-in-place + overlapping `[0,len)` declines; `H=S+len`, stage 0 | TapeFS §9.3.2 step 5 | decline wrote chunk 0 |
| PR-A08 | Completed path increments `sb_generation` and issues four index commits' sequences | TapeFS §5.5, §9.3 | sequence |

Excluded: RESUME rows, crash boundaries, two-interruption partner-first,
WP-12a continuation identity, listened PCM, 10k-edit histories.
