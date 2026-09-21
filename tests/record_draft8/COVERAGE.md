# WP-09 record assertion and exclusion matrix

This matrix is the acceptance boundary for this package. “Covered” means the
verifier has an independent assertion and a negative control. It does not imply
whole-work-package acceptance, golden PCM acceptance, or product-engine acceptance.

| Assertion ID | Case | Independent assertion | Normative basis | Control |
|---|---|---|---|---|
| WP09-A01 | OW-MID | Overwrite at frame 128 for 64 frames leaves `[(0,0,128),(3,0,64)]`, total 192 | TapeFS §9.1 overwrite trim | kept-tail mutation |
| WP09-A02 | OW-END | Overwrite at exact end appends; `[(0,0,256),(3,0,64)]`, total 320 | Engine API §11; TapeFS §9.1 | conforming synthetic |
| WP09-A03 | OD-MID | Overdub mid keeps timeline length 256 and splits around the edit | TapeFS §9.1 overdub | truncated-timeline mutation |
| WP09-A04 | SP-T0 | Splice at 0 inserts a new first entry | TapeFS §9.1; Engine API §11 | conforming synthetic |
| WP09-A05 | SP-MID | Splice mid splits the live run and keeps the suffix | TapeFS §9.1 splice | dropped-suffix mutation |
| WP09-A06 | SP-END | Splice at exact end appends | Engine API §11 | live-only sequence-base mutation |
| WP09-A07 | EMPTY | Zero-accepted commit is `TAPE_OK`, zero writes/flushes, unchanged index and sequence | Engine API §7.1 V5-008 | empty-commit write mutation |
| WP09-A08 | BUSY | `tape_seek` and `tape_set_rate` while armed return `TAPE_ERR_BUSY` with zero writes | Engine API §7, §10 | armed-seek-allowed mutation |
| WP09-A09 | non-empty | Allocation starts at derived `free_next==H==3`; service writes stay in chunk 3 | TapeFS §7 | service-write-below-H mutation |
| WP09-A10 | non-empty | B1 commit is entries → flush → header → flush; exactly two commit flushes; sequence 701 | TapeFS §8; Engine API §7.1 | flush-count mutation |
| WP09-A11 | non-empty | Ordinary stage-0 record does not update the superblock | TapeFS §8–§9.1 | fixture/result identity |
| WP09-A12 | all | `tape_feed` issues no block I/O | Engine API §7 | feed `events_from_call` |
| WP09-A13 | arithmetic | Overdub full-scale + full-scale saturates at ±32767/−32768 and never wraps | Engine API §8 | seven clamp vectors |

## Deliberate exclusions

Not covered here: golden WAV / human listening (WP-11); PCM byte identity of
overwrite/overdub/splice against a listened fixture; stage-1 clearing;
`TAPE_ERR_INDEX_FULL` / `SEQUENCE_EXHAUSTED` / `CARTRIDGE_FULL` short-accept;
zero-frame timelines; multi-chunk edits; random 10 000-edit sequences; promote;
re-spool; duplicate; format; long-operation continuation; FAULTED; crash
injection; WP-36 source-slot write isolation; hardware/media atomicity.

This package does not establish complete WP-09, WP-07, WP-10, WP-11 or
WP-12a acceptance. A synthetic green run proves the verifier package only.
