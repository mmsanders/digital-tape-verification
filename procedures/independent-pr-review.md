# Independent PR Review Procedure

## Purpose

Provide a separate, opt-in code-review lane for pull requests targeting the main development branch of `mmsanders/Digital-Tape`.

This lane is deliberately isolated from the Verification Lead's pre-test work. Implementation details learned by this reviewer must not be used to shape verification expectations or tests that have not yet been written.

## Trigger

Review an open PR targeting `main` when the exact phrase `Request Independent Review` appears in the PR title, body, or discussion.

The marker is opt-in. Unmarked PRs are ignored.

## Reviewer authority

The independent reviewer is advisory only.

It MUST NOT:

- approve the PR;
- request changes using GitHub's blocking review state;
- merge, close, retarget, relabel, or otherwise mutate the PR;
- push code or commits;
- resolve review threads;
- communicate review findings into the Verification Lead's pre-test workflow.

It MAY only submit a GitHub review with action `COMMENT`, including inline file comments when useful. These comments are for the Software Lead to evaluate and act on.

## Review method

For each marked PR:

1. Confirm the PR targets `main` and is still open.
2. Record the current head commit SHA.
3. Check prior independent-review comments. If that exact head SHA has already been reviewed, do nothing.
4. Read the PR description, changed-file list, full diff/patch, existing discussion, and relevant tests included in the PR.
5. Review adversarially. Prioritize concrete defects over style preferences. Look especially for:
   - correctness and edge cases;
   - data-loss or corruption paths;
   - unsafe ordering of persistent writes;
   - error handling and recovery;
   - state-machine inconsistencies;
   - bounds, overflow, lifetime, ownership, and resource bugs;
   - portability/C99 issues;
   - regressions against stated PR intent or accessible frozen specifications;
   - missing or ineffective tests for changed behavior;
   - concurrency/reentrancy hazards where applicable;
   - unnecessary complexity that creates a plausible failure mode.
6. Do not manufacture findings merely to appear critical. If no actionable defect is found, say so plainly and identify any residual uncertainty.
7. Submit one `COMMENT` review. Prefer inline comments for location-specific defects and a concise overall summary.

## Comment format

Every independent review begins with:

`Independent Review — head <FULL_HEAD_SHA>`

For each finding, state:

- **Severity:** blocker / major / minor / question
- **Location:** file and line/diff location when available
- **Claim:** one sentence describing the defect or concern
- **Reasoning:** concrete failure path or counterexample
- **Suggested action:** what the Software Lead should consider changing or checking

Use **blocker** only for credible cartridge loss/corruption or dangerous audio-output behavior. Avoid blocking language for style, maintainability, or speculative concerns.

## Re-review behavior

If new commits change the PR head while `Request Independent Review` remains present, review the new head again. The head-SHA marker prevents duplicate reviews of the same revision.

## Independence boundary

This code-review lane is not the Verification Lead. It may inspect implementation because it exists for post-authoring code critique. The Verification Lead must continue to obey the charter rule against seeing implementation before writing tests for that behavior.
