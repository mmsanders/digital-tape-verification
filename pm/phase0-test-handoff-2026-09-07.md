# Digital Tape — PM handoff to Verification Lead

**Date:** 7 September 2026  
**From:** Temporary combined PM / Software Lead / Hardware Lead, via Michael  
**Priority:** Independent tests needed for the safe implementation merge; preserve all verification boundaries.

## 1. What I need from you

Please deliver the independently authored, spec-derived tests needed to release the **WP-06 read-path and WP-07 allocator implementation merge hold**, with a precise statement of what behaviour those tests cover and what remains uncovered.

Michael has temporarily combined PM, software and hardware authority for a Phase 0 freeze-and-cleanup push. He has **not** delegated your independent verification authority. I have paused to obtain your work through him. No repository changes were made during that intake.

This is a request for test source and an auditable coverage boundary, **not** permission to inspect the implementation, waive Structural Rule 1, or sign off untested behaviour. PR #20 remains held. Its existence identifies the PM’s merge dependency; **do not open its implementation, diff, implementation-derived tests, or discussion to decide what your tests should expect.**

## 2. Baseline and authority

Use the user-supplied **DRAFT-8 third-cut** files already authenticated in your independent review. Michael should pass the four files with this brief if they are not in your current context: `tapefs-v1.md`, `engine-api.md`, `acceptance.md`, and `VERSION.md`. Uploaded filenames may include a parenthesized suffix; authenticate their contents.

| Normative file | SHA-256 |
|---|---|
| `tapefs-v1.md` | `3bffa0ec46d7ba3779b02cbee6fac1edaf5094553f78270ee379759655147cbb` |
| `engine-api.md` | `537eadc423e1a7bde726d689206b8fe93bef164d57e48e8ff71e07eaf8a7e3a1` |
| `acceptance.md` | `7f78fba7b66b4fc6e96d15399c62468249bb30fbccbb59bf9f57b4532f56b6b7` |

At intake, `Digital-Tape/main` was commit `ed5efd834aa8f7a96bc8ef811569b2687d919526` and still published **DRAFT-7**. PR #25 carried review instructions, not the actual DRAFT-8 spec files. Do not assume merging that PR publishes the candidate.

**PM owns canonical issuance.** You may prepare and publish candidate-labelled tests against the authenticated attachments now. Do not wait for me to claim that issuance has already happened, and do not substitute the old canonical DRAFT-7 text silently. Before test integration/acceptance, we will re-authenticate against the actually issued canonical bundle. If any hashed file changes, identify the affected coverage and perform the necessary re-review; no automatic carry-over.

Your existing third-cut review found **zero blockers, zero majors, one documentation question**. That paper verdict already applies mechanically to byte-identical PM issuance. I am not asking you to repeat the entire adversarial pass. `V8R3-001` remains a documented, non-blocking wording question; do not quietly rewrite either the spec or the expected behaviour to dispose of it.

## 3. Deliver the smallest sound test tranche first

Derive expectations from the spec, not the current implementation’s capabilities. Start with independently testable **mount/read-path behaviour and allocation/ownership rules**. Use the existing verifier-owned infrastructure where suitable.

The coverage matrix should explicitly account for:

- TapeFS mount **phase 0 plus phases 1–4**: pre-read device-size refusals; superblock validity, selection and repair; version/state handling; geometry; index structural parsing versus full validity and selection; running cartridge sequence; both-side validation and degraded-B behaviour; stale promote-stage classification; and refusal-before-write ordering.
- Applicable WP-06a–WP-06h assertions, including callback/write accounting, disjoint versus overlapping physical-frame intervals, and read-only behaviour. Separate mount-only assertions from assertions requiring recording, reset, promotion, re-spool or other operations.
- TapeFS allocation/ownership rules and WP-07: allocation/write destinations versus lawful references below `a_high_water`, derived `free_next`, and interval disjointness. Distinguish a testable allocation rule from acceptance of an entire edit/reset workflow.

This list is a scope guide, **not a replacement oracle**. Use the precise errors, precedence, boundaries and invariants in DRAFT-8. Add any coverage needed for a sound boundary even if this list omits it.

Do not reduce the full WP-07 requirement—such as its 10,000 random edit sequences—to a few allocator unit tests and call the package accepted. Similarly, a passing mount test does not accept the commit or recovery operation mentioned in the same WP-06 criterion.

Where the public API cannot expose a rule independently of later operations, state that limitation. Specify any required adapter as a contract derived from the spec, without inspecting private engine code or inventing a product API. I will handle mechanical integration. It is acceptable to conclude that a proposed behaviour must remain unmerged until broader tests exist.

## 4. Required return package

Publish your deliverables in `digital-tape-verification`, using your normal workflow, and return:

1. **An immutable commit SHA and file paths** for test source, fixtures/generators, runner instructions, and any adapter contract. Publish completed findings/status on that repo’s `main`; identify any test branch still awaiting integration.
2. **A coverage matrix:** spec section / acceptance item → test ID → assertion scope → dependency or uncovered remainder. State exactly which behaviours have independently authored tests ready to land, without claiming knowledge of the implementation’s contents.
3. **Reproduction details:** commands, toolchain/dependencies, deterministic seeds, fixture provenance, and expected outputs. Keep the handoff self-contained so we can carry it into `Digital-Tape` for future agents.
4. **Evidence, clearly separated:** what was authored; what harness/fixture checks actually ran; what ran against a conforming reference or deliberately faulty fixture, if applicable; and what has **not** run against the engine. Preserve failures and logs. Do not turn missing implementation into silent skips or green acceptance.
5. **A short disposition:** ready for test integration / blocked on named interface or spec question; remaining test work; and the next independent acceptance step after integration. Confirm which materials you inspected and that implementation blindness was preserved.

If blocked, return the smallest actionable finding with the established **FINDING / SEVERITY / AREA / CLAIM / REPRO / IMPACT / FIX** structure. Do not loosen assertions, remove cases, narrow input ranges, or negotiate an oracle against the implementation. Normative disagreements return to PM.

## 5. Sequence after your delivery

PM issues the canonical bundle and records the applicable paper-review evidence. Software then lands your authenticated tests **before** merging the corresponding implementation. Mechanical build/adapter changes must not alter correctness criteria and will be recorded. I will compare the implementation’s behaviour surface against your coverage matrix and retain any uncovered portion on the held branch.

Only after the relevant tests are independently authored and landed may implementation review cross that boundary. Permission for one covered behaviour is not permission to inspect still-untested neighbouring behaviour. Results against the engine must be reported separately from test authorship, and work-package acceptance remains yours.

## 6. What this request does not require or authorize

| Gate | Boundary |
|---|---|
| Phase 0 specification freeze | Existing zero-blocker/zero-major paper review, byte-identical canonical issuance, and the required recorded freeze sign-off. This test request is a separate implementation-merge dependency, not a new paper-freeze criterion. |
| WP-06 / WP-07 implementation merge | Verifier-authored tests on `main` before corresponding implementation; partial coverage does not authorize an entire package. |
| Operations/state freeze | Still requires the **actual green WP-10 run** against the issued contract. No paper review or narrow test tranche substitutes for it. |
| Hardware fabrication / cell charging | Remains held under the existing safety controls. No hardware acceptance is requested or implied by this handoff. |

Full WP-10 crash closure, WP-11 golden audio, WP-12a long-operation/state coverage and hardware audits remain important follow-on work. **Do not expand this immediate delivery into all of them before returning the smallest useful, independently sound tranche.** No surge-support work is requested.

## Source references

- [Working agreement and Structural Rule 1 — intake revision](https://github.com/mmsanders/Digital-Tape/blob/ed5efd834aa8f7a96bc8ef811569b2687d919526/CLAUDE.md). Its stale revision labels do not override the authenticated candidate above.
- [Independent third-cut review — reviewed publication](https://github.com/mmsanders/digital-tape-verification/blob/73b91475d50fbefc16df25f07e37b4481a8720be/findings/surge-draft8-third-cut-review.md).
- [Verification capability status — reviewed publication](https://github.com/mmsanders/digital-tape-verification/blob/73b91475d50fbefc16df25f07e37b4481a8720be/CAPABILITY-STATUS.md).

**Reply to PM through Michael with the commit, coverage matrix, run evidence and remaining holds. Do not merge or approve PR #20 merely on receipt of this brief.**
