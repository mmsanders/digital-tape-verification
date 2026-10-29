# Verification370 Stage A — obsolete global Make-disabled requirement superseded

29 October2026 PDT. Michael manually activated the open issue. Input Product main
`1d341573989d1d768a718371bd6af2b6c2b74b51`; Verification main
`3ff22aaea8a19b874ea65cea06056e99b3fd0b66`. Current AGENTS/agreement/STATUS/charter,
issue370 and its scope read. No scope comments. This is only Stage A, under
PM627/ADR-195; no Product edit, physical/native run, new method round or subworker.

**Stage A COMPLETE.** The earlier S2 “Make permanently disabled” wording is
superseded as a current acceptance requirement. APP-1 §2/§4 controls: a current
successful check, retained audio, valid nonempty label, exactly one offered card,
and no check/Make/confirmation in progress permit Make. Discovery alone does not.
The superseding contract and exact affected assertions are in
[c2_make_readiness_r1](../../tests/c2_make_readiness_r1/README.md).

## Why a note alone was not the chosen correction

These two older packages **are still called by Product CI** at the exact input:

| Affected package / old assertion | Current CI caller |
|---|---|
| `windows_discovery_r1`: `expected` includes false; `qualify` requires `valid_music_label_one_hint_make_enabled=False`; README's “permanently false Make” and “Hard hold” | `windows-discovery-578.yml`, including contract controls, emit and actual capture qualifier |
| `windows_interactions_r2`: `qualify` and `summary.py` require false in interaction snapshots, inheriting r1's earlier global-disabled wording | `windows-interactions-584.yml`, including contract controls, emit, summary and current/negative DOM qualifiers |

The targeted fixture/caller audit establishes **no retained audio in these old
captures**. Discovery's “valid music” setup directly supplies an Outcome to App;
it never retains an audio artifact. The interaction adapter likewise completes
checks with typed metadata through its worker closure, without publishing an
audio.wav for Bridge retention. It tests selection/editing/details/polling, not a
ready Make job. The historical field name omits that decisive precondition.

Consequently **their false observations and causal controls remain correct for
those specific no-audio inputs**. What is retired is treating those observations
or old README wording as a universal ban on Make. No live current requirement
prohibits Make when its full readiness conditions hold. A future full-ready
fixture must use the current predicate, not the legacy false-only assertion.

This is a superseding verifier correction outside the frozen old trees, with an
actual positive readiness test; it is not an assertion-value change or skip to
make Product pass. The existing Product CI invocations need no mechanical change
for their unchanged scoped fixtures. This interpretation does not waive their
unrelated assertions or make/elevation absence during **non-Make** actions.

## New independent readiness result

[CI40903502629](https://github.com/mmsanders/digital-tape-verification/actions/runs/40903502629)
checks the exact current Product head with a verifier-owned, test-only capture
inside the production Bridge module in a disposable checkout. The contract emits
72 combinations independently of Product; the Rust capture records actual
`Bridge::snapshot().make_enabled`, and Python qualifies every returned row.

| Outcome | Result |
|---|---|
| One card + nonempty valid label + successful current check + retained audio + idle | **Make enabled** |
| Other71 combinations: absent/multiple cards, empty label, failed check, absent artifact, confirmation or Making | **Make disabled** |
| Constant-false (“permanently disabled”) mutant | **Rejected** |
| Constant-true mutant | **Rejected** |
| Inversion of any individual snapshot outcome | **Rejected** |

The old no-retained-audio positive fixture is among the disabled neighbors; the
current fully ready case is now positively demonstrated. ROWS.json preserves the
actual small CI output. `contract.py --input .../ROWS.json` replays it and its
causal controls. No downloaded Product executable is run locally.

The inputs are controlled component facts (typed terminal outcome/artifact
availability), not a new actual audio/child/native/physical claim. Existing C1
real-child retention and Make evidence carries. This stage neither reopens C1
clearance nor accepts G1/G3/G4/G5/G2. No cleared candidate was changed or rebuilt.

## Identity and immutable-package preservation

Product merge `ea54a41850a37335ca857486b24d15ea1583caf1` and cleared5101e3f3 have
identical root tree `323207f0e3943efff809ff612dc26b580f3dbf90`. Current1d341573's
app tree equals the cleared app `fd7032d580e13d668c67c519508edcca25eb643f`.
The cleared candidate remains ZIP `b8a689cfbe926202b6d982dcdc5e5eaaa810d13a180556381d04811f9177ceab`.

The following package trees are identical in Product and Verification and are
unchanged by this publication:

- `windows_discovery_r1`: `ec9cda078291e24230302b732fe40d97b412a184`.
- `windows_interactions_r1`: `478499b20c603965d5cc6bc838c6e909c0a7c4c3`.
- `windows_interactions_r2`: `80ad54526d09ee763b04c4351d363831b8a39478`.

Only their Make-disabled scope was examined. No other package review or Product
CI edit is included. Old publications, validators, provenance and test bytes remain
reachable unchanged. Their global wording is now historical, not live authority.

## Stage B input and stop

At activation, [Michael628](https://github.com/mmsanders/Digital-Tape/issues/628)
has no comments/C2 return. Check once at Stage A completion. If it is still absent,
post this Stage A return and stop; keep370 open for the explicitly named Stage B.
Michael posts C2 evidence on Product628, not closed Verification364, and manually
resumes this issue. Missing observations remain unrun; G2 is not Verification's
to sign. No waiting/polling, lead wakeup, native session or physical test is started.
