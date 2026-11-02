# WP-17 exact-candidate disposition (Software #642)

Authorized by Michael's 2 November manual continuation of the unavailable
Software Stage B of Verification #374. Candidate:
`ee478a913613a16a90e38c85112fb67cbbf53887` (Product PR #647).
Verifier input `3d616c14`; Product main `57c60582`.

This package adds execution/reporting around the already-published independent
`p3_r1_r374` predicates; it changes none of that package's bytes or expectations.
References come from the frozen WP-11 MANIFEST/WAVs and WP-14 fixtures.
Software's own assertion suite is not imported as an oracle.

Build the exact candidate's host modules and desktop cartridge producer, then:

```
python3 tests/wp17_candidate_r1/unpack_arm.py OUTPUT
python3 tests/wp17_candidate_r1/run.py --product PRODUCT --fwhost PRODUCT/build/fwhost/fwhost --tapectl PRODUCT/build/host/tapectl --arm OUTPUT --out RESULTS
```

The run confirms the current finding: the unchanged published partition gate
fails at `bootstrap`. A separate matrix records all twelve cases with the same
published expectations, without stopping on the first failed row. It asserts
that the sole disagreement is bootstrap; its successful exit means reproducible
**HOLD**, never firmware integration clearance.

The seven normal-rate golden cartridges are built from the published MANIFEST
preparation steps with the same P2 block count, UUID, epoch and audio edits inside
the WP-14 whole-card layout. Firmware `det` and `live` paths must produce the
exact reference PCM, zero underruns, zero reported writes and unchanged image
bytes. Both altered-sample and altered-rate outputs must mismatch, in each mode.
Generated PCM need not replace references: reports retain output hashes, counts,
first control mismatch bytes and the exact reproducible procedure.

ARM static accounting independently reads the actual ELF32 symbol table and the
linked map's retained engine input sections, authenticates every firmware blob
against SHA256SUMS, and applies the published `wp17.budget` predicate. The original
279011-byte CI ZIP is retained verbatim (below the 1 MiB evidence threshold).
The map's .rodata input contributions remain .rodata for the contract accounting
even though the Teensy linker places them into RAM. Stack acceptance remains
pending target measurement.

CI runs this independent package with GCC and Clang, plus the unchanged published
host golden package, on the exact candidate. No new engine campaign, firmware
change, physical operation or target acceptance is part of the run.
