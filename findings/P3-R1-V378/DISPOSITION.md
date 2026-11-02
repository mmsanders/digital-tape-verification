# Verification378 — ADR-202 correction and exact-head clearance

**CLEARED:** `ee478a913613a16a90e38c85112fb67cbbf53887` for the authorized
**off-target Software642 integration scope**, subject to Software's required
current-base CI and existing merge authority. This is not WP-17 target/package,
physical, media or safety acceptance and does not clear another Product head.

Authority: Product ADR-202 / PM648, merged via PR #649 at
`b07d8d4832fb6c4213efa950d47e827c34e6ea65`; live Verification #378, updated
2026-11-02T16:44:15Z, manually activated by Michael. Verification input was
`d7540127aa982df5f8716bcc7732f53b171c0386`. Candidate PR #647 still identified
the exact unchanged `ee478a91` at the final source check.

## New versioned correction

[`wp17_admission_r2`](../../tests/wp17_admission_r2/README.md) implements only
the explicitly issued recognition correction and its bounded coverage/controls.
[AUTHORITY.json](../../tests/wp17_admission_r2/AUTHORITY.json) pins PM document
hashes, source trees, predecessor merge identities and 32 carried-file hashes.
Original `p3_r1_r374`, `wp17_candidate_r1`, their expectations, every prior
disposition and all frozen goldens remain byte-unchanged. The old bootstrap HOLD
remains the truthful historical result under its predecessor expectation; this
new publication supersedes that admission hold for **this exact candidate**.

Admission follows WP-14 §2/E-1 recognition. Bootstrap, disk-signature and
reserved-prefix-only variation does not itself refuse admission. Signature,
all specified partition-table fields, extents, extra-entry exclusion and view
bounds remain mandatory. This correction neither changes provisioned bytes nor
relaxes full WP-14 §4.1 validation or write confinement.

## New execution and controls

| Check | Result |
|---|---|
| Admitted cases | 9/9 PASS: clean; bootstrap first/last/all; disk signature; reserved 444/445/both; combined prefix |
| Refused cases | 19/19 PASS: either signature byte, P1/P2 status/CHS/type/start/count, extra entries 3/4, zero/overflow/past-card extents |
| View behavior | Every admitted image gives exact first/last P2 reads, correct P2+1 write, refusal of before/after-view I/O, and no changed byte elsewhere |
| Refused image preservation | All refused images remain byte-identical |
| Desktop diagnostic distinction | Clean and disk-signature variation verify OK. All seven admitted bootstrap/reserved-prefix variants still return exit 1 with `MBR_LAYOUT`; verify changes no image byte |
| Controls | All 4 rejected: blanket acceptance, wrong reported write offset, actual raw bytes modified outside P2 despite plausible metadata, and false bounds handling |

Windows results: [WINDOWS-RESULT.json](WINDOWS-RESULT.json).
Independent Linux [CI 41485606006](https://github.com/mmsanders/digital-tape-verification/actions/runs/41485606006)
at authoring commit `3858da0bf2dc0cd38e602fbdc9a9498987898154` reproduced the
same 28 passing cases and four rejecting controls:
[LINUX-RESULT.json](LINUX-RESULT.json). The harness exercised the returned
firmware's actual `fw_part` view through its partition adapter, not a substitute
recognizer. Images were verifier-generated regular files; no physical card ran.

Only partition/view/diagnostic cases executed anew. Building the unchanged host
transport is preparation, not another engine/golden/fault campaign.

## Authenticated evidence carried without re-execution

| Published predecessor | Facts carried |
|---|---|
| `41995965873e96a76139ffa57f17549d858a759a` | Stage A/package/preflight: 365 actual deferred load faults pass (404 with earlier receipts); six long-cut coordinates unavailable on the three-unit fixture, zero new executed cuts |
| `3d616c14ca2770c0369dda6c3bfb66a60cce68ca` | Rig method remains NOT CLEARED; no physical tear claimed or method re-review performed |
| `d7540127aa982df5f8716bcc7732f53b171c0386` | Same ee478a91: seven normal-rate F1 vectors through det/live, 14 exact PCM comparisons and 28 controls per platform; original ten desktop regressions pass; F2 static RAM 191600 and engine .rodata 1040; F6 engine/port tree d96b4245 |

Ancestry, all 32 pinned publication files, exact candidate HEAD and clean scoped
worktree are checked. Firmware subtree remains
`cf46ed64eac396e750fce3a2ba9ff1a30520cf9c`; entire engine remains
`d96b4245e04d74078f8938744b1394c3018516f7`. No behavior/evidence identity
difference was found. The prior original ARM artifact and result JSON identities
are preserved, not replaced with fresh runs.

The F1 clarification is consistent with those retained facts: the seven named
normal-rate vectors are compared as PCM payloads; retained PCM hashes and frame
counts match the data extracted from the unchanged reference WAVs. Whole-WAV
hashes separately authenticate the reference files. This was offline identity
checking, not rendering another frame. The three scrub vectors retain their
actual published MANIFEST commands/rates and prior desktop results; they are
not represented as firmware-at-1.0x vectors. No golden regeneration occurred.

## Integration and remaining holds

Software #642 owns integration under its existing pre-routed authority, only
with required current-base CI. This clearance names **ee478a91 only**: PM-only
documentation/site changes do not justify repeating accepted campaigns, and
they do not authorize unrelated behavior changes or blanket clearance of a new
head. A changed candidate/evidence identity must be identified and disposed
within its applicable scope before relying on this publication.

Target F1 PCM/I²S, actual target instance and painted-stack measurements, wake
timing, physical Play/Stop/removal and F4 recording/commit latency remain pending.
Rig R374-1…5 remains NOT CLEARED; SPI-only characterization does not qualify native
SD4/SDR50 or the product. Large-epoch/repeated-LBA boundaries and the historical
#443 hold carry. **Batching remains disabled.** Six unavailable cut coordinates
are never renamed executed cuts. Fabrication/charging CLOSED, output-cap/safety,
purchase, card/media/release, G2/macOS and unissued DRAFT-11 boundaries stand.

No Product implementation/spec, prior package/report byte or physical state was
changed. Return the correction publication and exact-head disposition on V378
and Software #642, then stop and close V378. PM maintains Product status/ledger.
