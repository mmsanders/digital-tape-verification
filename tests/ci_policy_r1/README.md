# V390 CI policy review r1

Independent checks under PM657/ADR205: parse workflow YAML with PyYAML BaseLoader,
trace mandatory aggregate dependencies, verify nonempty aggregates, Windows/Linux
legs, retained golden/member coverage, manual-only event and original commands,
and require the supported-platform retained-artifact census to remain mandatory.
Moving the three-platform census to manual CI must not silently remove its
Windows/Linux completeness and post-upload retained-byte authentication coverage.
The current check recognizes the declared census.py entry point; a new interface
must be declared/bound rather than disguised to satisfy a string predicate.

The actual Product lane-verdict CLI runs21 cases (positive and failed, cancelled,
missing, skipped and uncertain classifier contexts over each real parsed lane).
The actual classifier CLI runs4 uncertainty/full-event cases. Five workflow mutants
are rejected. These are structural/selection checks, not a simulated GitHub runner
or evidence that any physical/macOS job ran.

```
python -B tests/ci_policy_r1/run.py --product PRODUCT --base BASE_EXPORT --out RESULT.json
```

Requires PyYAML6.0.3. Base is Product aa3b87f9 canonical .github/workflows/ci.yml.
`--record-known-finding` pins all four changed e0b6bb02 files and requires exactly
the missing required supported-platform census finding; it never grants clearance.
Default strict mode exits1 on that head. This review-discovered expectation does
not claim to predate that implementation. Original verifier packages are unchanged.
