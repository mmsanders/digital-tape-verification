# Software642 — exact-head independent disposition

**HOLD pending PM's bootstrap-recognition decision. No integration clearance.**

Michael manually resumed the unavailable Software Stage B of Verification #374
on 2 November. Product main: `57c605829a402cb68be9d07ed2bcc99ee2d21103`;
Verification input: `3d616c14ca2770c0369dda6c3bfb66a60cce68ca`.
Final returned head: **`ee478a913613a16a90e38c85112fb67cbbf53887`**,
Product PR #647 / Software #642 addendum 6571202445. Earlier head `96d09ad3`
is superseded for this disposition. Completed Stage A and Hardware review carry.

## Independent results

| Criterion | Result | Evidence boundary |
|---|---|---|
| F6 | PASS | Entire `engine/`, including port/, equals tree d96b4245e04d74078f8938744b1394c3018516f7; original gate also rejects port-tree drift |
| F2 static | PASS | Independent ELF symbol-table read: `fw_engine_instance` reserve 191600 bytes. Linked engine .data/.bss/COMMON each 0; engine .rodata 1040 bytes (8+8+1024 retained input contributions). Published budget predicate passes |
| F2 target stack | PENDING | No painted-stack measurement; static success does not pass the 8192-byte target criterion |
| F1 host | PASS, 14/14 comparisons | Seven frozen normal-rate vectors through the firmware portable `det` and `live` paths, exact reference PCM, no tolerance; zero reported underruns/writes and unchanged cartridge bytes |
| F1 controls | PASS, 28/28 | Altered sample and rate 65537 instead of 65536 mismatch for each vector/mode; first mismatching bytes and hashes retained |
| Published host package | PASS, 10/10 | Unchanged `p3_r1_r374/wp17.py host` runs all frozen manifest outputs on this exact candidate. The three scrub vectors remain desktop/engine checks; no firmware scrub acceptance is claimed |
| Partition | 11 PASS / 1 disagreement | Original published gate fails at `bootstrap`. Separate twelve-case matrix retains the original expectations and exposes all rows; the failed expectation is not flipped, suppressed or counted PASS |
| F1 target / F3 / F5 | PENDING bench | No target PCM, I²S, wake timing, physical Play/Stop or removal observation |
| F4 | Deferred to WP-18/19 | No recording/commit-latency claim |

Windows execution is retained in [WINDOWS-RESULT.json](WINDOWS-RESULT.json);
the original ten-vector run is [PUBLISHED-HOST.json](PUBLISHED-HOST.json).
Independent Linux [CI 41464928020](https://github.com/mmsanders/digital-tape-verification/actions/runs/41464928020)
reproduces the same result under GCC and Clang: [GCC-RESULT](GCC-RESULT.json),
[CLANG-RESULT](CLANG-RESULT.json), [summary](SUMMARY.json). Each compiler passes
14 normal-rate firmware comparisons and detects 28 controls, plus the unchanged
ten-vector host package. Both retain the sole bootstrap expectation failure.
Windows source-hash guards required an LF export of the unchanged verifier bytes;
CRLF checkout conversion was not treated as candidate behavior. The local engine
Makefile's unquoted absolute path initially failed in this workspace with spaces;
overriding only its command-line `CURDIR` with an equivalent relative build path
allowed the normal GCC build. No Product source was edited.

The candidate-specific [execution package](../../tests/wp17_candidate_r1/README.md)
derives all expected PCM and fixture values from the previously published
Verification MANIFEST/references and WP-14 fixtures. Software's own `run_checks.py`
assertions were not imported or used to derive expectations. The reviewed fwhost
transport invokes the covered firmware `fw_part`/`fw_play` modules; it reports raw
PCM and view-I/O facts rather than supplying the independent verdict.

## V642-BOOTSTRAP — recognition and validation were conflated

The published Verification partition case changes only MBR byte 0 from zero to
one and expects refusal. Firmware accepts it, maps P2 correctly, and confines the
requested write to P2+1. This mismatch reproduces on the returned head.

The stricter expectation is verifier-owned; it is **not established as a firmware
defect**. WP-14 §2 defines recognition using signature plus partition entries,
without bootstrap bytes. Its §3.1 describes zero bootstrap for the provisioned
layout; §4.1 validation reports other layout mismatches. The existing desktop
`mbr_is_layout` examines bytes 446–511, whereas `mbr_findings` additionally checks
bootstrap and reserved bytes. Firmware reuses that unchanged recognition code.

FW-1 §4 simultaneously requires the partition view exactly as desktop tapectl
and refusal of a layout that is not §3. The published verifier case applied the
full-layout validation expectation to recognition. **Recommendation to PM:**
confirm WP-14 §2 recognition is authoritative for FW-1 card admission, and
authorize a new verifier correction publication accepting this recognition-only
case (with the full validation distinction explicit). Requiring stricter firmware
admission would instead be a Product contract decision and diverge from desktop
recognition. Neither change is silently made in this disposition.

The other eleven rows pass: clean, disk-signature-only change, damaged signature,
P1/P2 type, P1 start/size, P2 start/size, extra entry, and P2 status. Accepted views
return exact first/last block bytes, translate the legal write correctly, reject
before/after-view accesses, and leave every other byte unchanged. Refused cases
leave the entire image unchanged. These facts do not settle the disputed policy.

## Source evidence and static limits

Product firmware workflow **41401091513** is authenticated as a successful
pull-request run at `ee478a91`; all 117 exact-head check runs are success across
both API pages. This is supporting evidence, not independent acceptance by itself.
The exact original ARM artifact is [arm-evidence.zip](arm-evidence.zip), 279011
bytes, SHA-256 `16bb28c20b700318b95c1b22d9faed951218b2b7a1c377907ed29137337ede52`.
Its firmware SHA256SUMS, map, ELF, toolchain/package identities and negative-control
gate logs are retained verbatim. Every firmware blob is checked before parsing.

The reported ARM control gates reject RAM 207984 >204800 and .rodata
34832 >32768, each for the named reason. Their ELF files are not in this artifact;
those control-build observations remain authenticated CI evidence, distinct from
our independent parse of the retained production ELF/map. The existing independent
compiled-oversized-static gate qualification also carries from Stage A.

The target reserve is conservative storage spending, not a measured ARM
`tape_instance_size()` value. Boot refuses an insufficient reserve; actual target
instance/stack observations remain bench work. Engine read-only input sections
are identified separately even though the Teensy linker copies them into DTCM.

## Return and next owner

PM owns V642-BOOTSTRAP arbitration. Software must preserve this exact candidate
identity and the existing integration hold until an independent disposition
reflecting that decision exists. Do not change the firmware merely to satisfy an
unresolved verifier policy choice. A green finding-reproduction CI run means
this HOLD is reproducible, not that the candidate was cleared.

No Product or firmware edits, target/physical run, large-epoch completeness,
write-batching permission, card qualification, output-cap acceptance or DRAFT-11
issuance follows. Previous rig-method findings and all product holds stand.
