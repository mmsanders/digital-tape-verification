# Software652 IF/3 — independent bindings published

Authority is Michael's direct instruction "Please bind the IF/3 cases for software"
on4November2026. No open verifier issue existed; activation/return is logged on the
existing Software652 pair. Closed V382 is not reopened or represented as complete.
Product main51d0f8f and verifier main7df60b14 are the exact input baselines.

Received Software declaration f9db5832194f95d886ad19a9855348c00f5a2da9,
blob20ddc4448f532725b64db639f1b7a98faa8696c4, SHA256
e572cb1f72ae591980c2345fa16f06f6494fa0b595659048227ae460174619de. IF/3 fixes
all four Software IF/2 declaration conflicts returned by V382. The new package
tests/be1_if3_r1 binds them without inspecting held local implementation/private
tests. Previous tests/be1_binding_r1 remains unchanged and is a declared dependency.

**53 checker cases and47 fake-port capture cases.** Ten checker controls and eleven
capture mutations detect. Windows harness results retained; Linux CI runs only
these new bindings. No Product checker/helper execution or exact-head clearance
is claimed. Harness doubles qualify the method, never substitute for the candidate.

Checker bindings cover F5 all-check precedence, witness/card/verify combinations,
retained/superseded errors and aggregate/exit state, and exact firmware.hex declared/
measured identity. Capture bindings cover modes, framing, send/reset/flush, exclusive
output, all declared exits, partial-byte retention, clocks/deadlines, interruptions,
port errors, usage and no devices/network. See the package README for exact coverage.

Synthetic marker probes test declared report fields, not authenticity: no real
Michael witness or physical session is asserted. Publication/task reports always
remain nonphysical. No target criterion or whole-kit acceptance follows.

The previous import-only Software586abc12 treeb094d319 is authentic. The new import
and subsequent implementation commits, Michael-owned IMPORTS approval and required
CI remain Software's next steps. No Product file, import manifest or implementation
was edited in Verification. No Hardware lane changes, previous golden/fault/target
campaigns, purchases, serial/device connection, flashing or physical action.

Ready for unchanged import. Exact source/tree/merge/final CI is returned on652 after
merge-commit publication. Stop at the binding handoff; later candidate disposition
requires its exact returned implemented head and the independent packages.
