# WP-36 source-slot assertion matrix

| ID | Assertion | Basis | Control |
|---|---|---|---|
| WP36-A01 | `tape_info.writable == false` on a `write == NULL` mount | Engine API §3.1 | conforming info field |
| WP36-A02 | Seek/rate/render/service succeed on both sides | Engine API §10 mounted-idle / playing | conforming playback path |
| WP36-A03 | arm / reset_b / promote / respool return `TAPE_ERR_READ_ONLY` | Engine API §3.1, §10 W cells | arm-succeeded mutation |
| WP36-A04 | Zero `dev_write` observations | Guardrail 06; acceptance WP-36 | source-slot write mutation |
| WP36-A05 | Final media byte-identical to input | TapeFS source-slot / no repair writes | encode identity |

Not covered: 100k random sequences, format/dup raw-device gating, v1.1 RO.
