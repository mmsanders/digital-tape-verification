# Verification325 Stage B: Software585 / PR603

27 October 2026. **HELD for PM disposition; no Product integration clearance.**
The archive, source/import, child identity, pin and metadata checks pass. The
published one-final-build condition does not: two compilations are evidenced,
while the producer record says `final_build_count=1`. There is one uploaded
candidate. These are separate facts. No third build or unchanged runtime is requested.

## Current inputs

- Product main/app source: `1731f6ecef2d6cb72a228f2c88c297cf4b59553f`.
- Software603 head: `3bd470aeb059668733c5d0f91ea6f71d16e594d8`.
- Verification main: `fcad6b0cba06478a54294ea7298e7d3dc0da5819`.
- Import before packaging: `d9b27ab9e75cc14932b3afb0a5785b396816ca3d`.
- Packaging: `346c07cd53551cb53c543969b45fe7a0abb0a2b5`; final head fixes only
  the workflow's exit status after an intentionally failing negative judge.
- Live authority: [Verification325](https://github.com/mmsanders/digital-tape-verification/issues/325),
  [Software585 return](https://github.com/mmsanders/Digital-Tape/issues/585#issuecomment-6451921986),
  [PR603](https://github.com/mmsanders/Digital-Tape/pull/603), PM583 and PM593.
  Canonical four and live bodies/comments read before this review.

## Independent result

`AUDIT.json` records exact source/package trees, all five ZIP members and hashes,
compiled pins, transport identities and judgments. The archive SHA-256 is
`3f144cf565e0e195763898a446938c88bace85d9f60dceeb04622efdd3fe6076`.
The container SHA-256 is
`8f8772e9fb62d85e37d047706e839a9a39df9e1f73062c7f4e8b4d84a78fd037`.

Read-only Git/byte inspection independently establishes:

- The three published judges were imported unchanged before packaging; source
  trees match the cleared integrated source. PR603 changes no production host/app
  code. The old564 builder and workflow remain unchanged.
- Locked release build inputs and Cargo.lock match; all four expected pins occur
  in the new app bytes. Static PE checks show AMD64/PE32+, GUI subsystem, unsigned.
- The five archive members, external inventory/optional sheet and evidence agree.
  INGEST and tapectl match original independently downloaded transport members.
- Independent `REGISTRY.json` restricts claims to carried exact source/direct
  evidence. It does not trust the producer's draft registry as authority.
- Published r1 archive/meta check passes. Published r2 mechanically passes the
  producer count1 record; changed-tapectl-pin control refuses `tapectl.exe`.
  The truthful `CHECKED_RECORD.json` count2 passes r1 and is refused by r2 as intended.
- Diagnostics default OFF and production Make/elevation remain disabled. External
  optional human sheet contains no prefilled new-candidate PASS or launch authority.

## One bounded discrepancy and disposition request

[Run40570284830](https://github.com/mmsanders/Digital-Tape/actions/runs/40570284830)
compiled and packaged successfully, then failed because the expected negative
judge left PowerShell LASTEXITCODE=1. Candidate upload was skipped; evidence was
retained. Its app hash is `6c32a984ac6788310683c377d473ab68319284f45557011d1beec553c2e6fdb7`.
[Run40571246452](https://github.com/mmsanders/Digital-Tape/actions/runs/40571246452)
compiled again after the workflow-only correction and uploaded the reviewed ZIP.
Software disclosed this. The upload guard counts candidate artifacts, not completed
compilations; the producer hardcodes count1. It cannot authenticate that assertion.

PM must explicitly dispose the one-final-build scope for this existing exact ZIP
(including an explicit exception or count interpretation if intended). Verification
does not silently redefine the published repeat-build negative or waive the gate.
Preserve existing bytes and both records; no correction/rebuild loop is authorized
by this finding. Normal current-base CI/review/protection gates remain required.
CI snapshot during review:114 successful,2 in progress, no failures observed;
this is not a claim that pending checks passed.

## Evidence and byte-only replay

`ASSETS.json` pins all original Actions artifact transport bytes and IDs. All
raw transports, including both build records and candidate/INGEST bytes,
remain at the original Actions artifacts (expiry26 November2026);
durable release-asset upload was rejected by automatic approval review pending
explicit payload authorization. No release exists at the proposed tag yet.
Do not assume Actions retention is permanent. No signed download URLs are published.

With authenticated gh and both Git repositories containing the pinned commits:

```text
python -B fetch_verify.py LOCAL_EVIDENCE_DIRECTORY --fetch
python -B reproduce.py --data LOCAL_EVIDENCE_DIRECTORY --verification-git VERIFICATION_GIT --product-git PRODUCT_GIT
```

The scripts hash-check/fetch transports and inspect bytes/Git objects only. They
never execute Product source, packager, app, children, observer, UI or device routes.
`reproduce.py` writes independent JSON results only into the supplied evidence dir.
Existing local downloaded transports were audited; no build/runtime was repeated.

Actual UI, native window/quit/poller, app-driven child, own-HOST/CLI A6, session,
S3, fullINGEST/fullAPP, physical/card/Make and G2 remain HELD. Original564 partial
human evidence and all original STOPs retain their prior limits. No rung advances.
