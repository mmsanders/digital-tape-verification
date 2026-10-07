# Proposed source-independent observation boundary (not final package schema)

This paper definition precedes Product changes. PM's P2READ-001 ruling is still needed.
It chooses no buffer layout, watermark or implementation algorithm.

## Device transport

Verifier-built fixtures own TAPEFS geometry and logical-to-physical frame mappings.
The adapter calls the public API, never imports the oracle or emits expected values.
Record every callback unfiltered: operation, LBA, block count, return code, API-call
ordinal and injection identity. A successful multi-block read copies actual fixture
bytes; a failing callback poisons its destination and reports failure. Errors carry
zero completed blocks unless the device contract separately provides a completion
count; the public callback provides none. Count requested blocks even on failure.

The independent replay classifies each requested block by the fixture's geometry:
payload, metadata/reserved or out of extent. It checks mapping-run boundaries, total
requested blocks per service call, zero render I/O and literal NULL source-slot write
binding. Nothing in the port may cache or coalesce away engine requests.

## Narrow test-only engine observations

Per-call uint64 monotonic counters, reset after cold mount, report:

| Counter | Increment at the actual operation |
|---|---|
| refill_copy_bytes | Each byte copied from successful device-read storage into play PCM storage |
| warm_adoption_copy_bytes | Each byte copied from an accepted warm descriptor into play PCM storage |
| retained_move_bytes | Each already valid PCM byte relocated within/between retained ranges |
| mapping_entry_visits | Every actual entry inspection for playback mapping, prefix construction/search or lookup |

Direct reads into the final play ring incur no extra copy bytes. Counters count all
intermediate copies, including scalar loops, not only calls named memcpy/memmove.
Output stores are excluded. Copy events must distinguish new PCM from relocation;
an operation doing both increments both categories for their actual bytes. Metadata
copies and recording stores are not playback-copy evidence.

Use direct compile-time test instrumentation, with caller-owned/test-owned counters;
no new public device callback, fifth funnel, private-state snapshot, runtime consumer
API or shipping state. Observations must never drive a Product branch or change PCM.
The final schema will include the PM-issued work inequality and its reset boundaries.

## Required causal and absence evidence for the complete package

The eventual package must detect actual candidate whole-window rereads, single-block
large-budget amplification, stale invalidation/warm coverage, retained-window movement,
missing interpolation lookahead and sum-of-counts budget overrun. Schema mutation
selftests alone are not these Product controls.

For each seam counter, execute a bounded test-build control that deliberately performs
the observed copy/move/entry inspections; require the independently known nonzero
delta. Include zero-work controls. A constant-zero invented seam must fail. Deliberate
work must occur at the same observation path used by real Product operations.

Compare instrumented and shipping runs for exact PCM/results/status and device traces.
Check shipping preprocessor/object/link evidence for absence of the seam definitions,
references and storage, including static/inlined sites; symbol absence alone cannot
prove compiled-out instrumentation. Audit actual increment sites after the matching
independent behavior tests are authored, preserving the independence order.
