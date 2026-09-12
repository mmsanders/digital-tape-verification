# P1-R5 Verification return — playback ramp schedule blocker

**Disposition:** Blocked before oracle/fixture authorship  
**Assignment:** `mmsanders/digital-tape-verification` issue #6  
**Issue update read:** `2026-09-12T22:59:16Z`  
**Product assignment input:** `b7f92dbb5ef4e59d9dd4ae268937ebbac31225ca`  
**Current product main read for charter/workflow:** `fd2b73fe50e3e5e8e2d02b8876256a6ed8f4b57b`  
**Verifier input:** `7a22cbb4447c40c51b7c8b2282a685ed30a46ba6`

## Finding P1-R5-V01 — the byte-exact scrub schedule is not issued

The frozen acceptance input says:

> Rate schedule driven into `tape_set_rate`: 4.0× at t=0, linear to 12.0× at t=1.5 s, hold. Reverse mirrors with negative rates. Scrub goldens drive this exact table.

That is the only occurrence of the scrub-ramp schedule in the authenticated
specification bundle. It defines a continuous envelope, but it does not contain
the “exact table” that WP-08 says the scrub goldens drive. In particular, it does
not specify:

- the timestamps/cadence at which firmware calls `tape_set_rate` between 0 and
  1.5 seconds;
- conversion of the non-integral intermediate values to signed Q16.16;
- the number of output frames rendered between successive calls; or
- how long the 12.0× hold contributes to the candidate output.

Those choices change the fixed-point positions sampled by `engine-api` §§6.2,
6.3 and 8, and therefore change the byte-exact PCM. For example, calls only at
0 and 1.5 seconds, calls every 250 ms, and calls every rendered frame all satisfy
the stated continuous envelope but yield different input positions and PCM. For
the mirrored reverse case, the unspecified segmentation likewise changes when
the playhead reaches the start and how many frames are emitted.

Verification cannot derive one uniquely correct candidate from the authenticated
specification, and choosing a table would create a new product/firmware requirement
outside Verification authority. The issue expressly requires all expectations to
come solely from the authenticated specification and forbids a frozen-spec change.
The missing table is therefore a blocking dependency, not an oracle tolerance.

## Evidence

Authenticated bytes read from `tests/playback_draft8/spec/`:

| File | SHA-256 |
|---|---|
| `tapefs-v1.md` | `3bffa0ec46d7ba3779b02cbee6fac1edaf5094553f78270ee379759655147cbb` |
| `engine-api.md` | `537eadc423e1a7bde726d689206b8fe93bef164d57e48e8ff71e07eaf8a7e3a1` |
| `acceptance.md` | `7f78fba7b66b4fc6e96d15399c62468249bb30fbccbb59bf9f57b4532f56b6b7` |

Search performed over all three authenticated files:

```text
rg -n -i 'scrub ramp|ramp table|rate schedule|12\.0' \
  tests/playback_draft8/spec/{tapefs-v1.md,engine-api.md,acceptance.md}
```

It finds the acceptance WP-08 requirement and the single firmware-criteria row
quoted above; it finds no timestamp/rate table or discretization rule.

## Work intentionally not performed

No product implementation, PR #20 source/diff/private test, or product adapter was
inspected or run. No fixture, candidate PCM, oracle, runner, saved P1-R4 evidence,
or frozen specification byte was changed. Verification did not invent a partial
package whose identity or future interpretation could be mistaken for the requested
complete tranche.

The non-ramp arithmetic and side-switch cases are independently authorable, but
issue #6 asks for one deliverable covering all five named groups and requires the
ramp's byte-exact candidate PCM. Splitting or narrowing that assignment without an
explicit PM update would be a scope change, so work stops at the dependency.

## Required next owner/action

PM must issue an authoritative scrub table (timestamp, signed Q16.16 value, and
rendered-frame count for every row, including the hold and mirrored reverse start
condition), then authenticate that input and open a fresh Verification assignment.
If PM instead authorizes a tranche excluding the ramp, that scope change must be
explicit. The signed Phase 0 hashes remain unchanged unless Michael separately
approves the required frozen-spec process.

All existing independence, PR #20, WP-11 listening/golden, hardware, purchase,
fabrication and charging holds remain in force. Closing issue #6 records only that
Verification stopped at this blocker; it is not acceptance of any package or product.
