# P3-R1 independent acceptance / Verification #374

Authority: issue #374, Product `3826018653e504217f37a16d8864fb0d597e22e6`,
FW-1, DRAFT-10. Engine tree `d96b4245e04d74078f8938744b1394c3018516f7`.
Authored without reading firmware. Old packages and golden bytes are unchanged.

`python tests/p3_r1_r374/wp17.py selftest` qualifies the independent comparison,
resource and partition expectations. This is method evidence, not firmware acceptance.

`python tests/p3_r1_r374/wp17.py host --product PATH --out PATH` runs the ten
published WP-11 manifest commands, authenticates frozen references, compares exact
WAV/PCM and rejects an altered sample. Seven normal-rate results are F1 host
references; the three scrub results retain their issued rates, not a false 1x claim.
It also compares the entire engine tree, including port/, with the pinned tree.

Target F1: use the seven non-scrub manifest cartridges at 1x, correct side and
frame count. Retain the cartridge hash, firmware SHA, raw PCM (no WAV header),
sample count and rate. `wp17.py pcm REFERENCE.wav CAPTURE.pcm` compares all bytes;
short/long captures and changed samples fail. The three scrub cases remain
additional rate-vector checks; FW-1's all-ten-at-1x wording needs PM clarification.
Never compare a raw PCM hash with a whole-WAV hash in SHA256SUMS.

F2: `wp17.py budget DATA BSS INSTANCE RODATA STACK` takes measured bytes from
the candidate map and painted-stack result. DATA/BSS are engine-owned statics,
excluding the separately counted caller instance. Print the map, instance symbol,
section accounting and arithmetic; reject missing sections and double counting.
The `--static-only` mode leaves stack acceptance pending. This scope follows
guardrail 08 / engine-api §4; board-core memory must be reported separately.
The self-test compiles an actual oversized static object in CI, reads `size -A`,
and proves the same budget predicate rejects its measured .bss.

Partition adapter protocol, for Software's host-built firmware binding: one JSON
request per process on stdin with `image`, `sectors`, `reads` and `writes` in view
LBAs. JSON stdout: `accepted`, `start`, `blocks`, `read_hex`, `write_absolute_lba`,
`out_of_range_refused`. `wp17.py partition --adapter COMMAND --out DIR` sends
WP-14 independently built whole-image fixtures and mutated MBRs; checks the
actual first/last partition bytes, write translation, unchanged outside bytes and
refusal of before/after-view operations. A host CLI alone cannot qualify the
firmware binding. The adapter must exercise that binding, not duplicate its parser.
The expected layout is the issued WP-14 layout (FAT16 0x0e), applying the
Michael-approved E-1 normative overlay to the frozen TAPEFS §3 base row.

Q-P2-1: `crash.py PRODUCT OUTPUT` runs exactly PLAN.json's 365 deferred faults
using the prior test transport and immutable oracles, plus six no-lower-run cuts.
No engine/port changes; prior 39 fault receipts carry. For a coordinate beyond
the actual trace, retain the full trace and classify unavailable on this fixture;
never replace it with a different fixture. Finite large-epoch sampling and absence
of repeated-LBA epochs remain explicit. These runs alone grant no batching permission.
CPU admission includes children, prior reported upper bound 608.49 seconds and
current measured process costs; 7200 CPU seconds / 2 GiB compressed ceiling.

Target F3/F5 and pending F2 stack: see BENCH.md. No physical run is authorized here.
