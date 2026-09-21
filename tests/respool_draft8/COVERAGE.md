# WP-12 re-spool assertion matrix

| ID | Assertion | Basis | Control |
|---|---|---|---|
| WP12-A01 | Empty B is `TAPE_OK`, zero writes, index unchanged | TapeFS §9.4 V4-005 | empty-write mutation |
| WP12-A02 | Empty B `tape_promote` is `TAPE_ERR_INVALID_ARG` | TapeFS §9.3.0; acceptance WP-12 | scripted promote result |
| WP12-A03 | H=10 / B[10–11] pass 1 writes `[12,14)` and pass 2 writes `[10,12)` | TapeFS §9.4 V3-003 | missing pass-1 / stopped-after-pass-1 |
| WP12-A04 | Completed two-pass result is one entry `(10,0,2*CF)` at sequence 702 | TapeFS §9.4, §5.5 | stopped-after-pass-1 mutation |
| WP12-A05 | Chunk writes stay at or above `a_high_water` | TapeFS §7, §9.4 | write-below-H (implicit in A03) |
| WP12-A06 | No pass-1 destination is `TAPE_ERR_CARTRIDGE_FULL`, zero writes | TapeFS §9.4 | full-dest-accepted mutation |
| WP12-A07 | Degraded-B is `TAPE_ERR_NO_VALID_INDEX`, zero writes | TapeFS §9.4, §4.4 | fixture live-B premise |
| WP12-A08 | Ordinary respool does not write the superblock | TapeFS §8 / §9.4 | post/pre superblock identity |

Not covered: listened PCM, crash boundaries, WP-12a cells, stage clearing.
