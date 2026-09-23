# P1-R25 Verification return — deterministic WP-36 source-slot evidence

Date: 23 September 2026  
Authority: independent Verification, issue #51

## Disposition

**PASS for the five-case deterministic WP-36 precursor.**

Exact Digital-Tape PR #191 head
`bce469b517636a39a08ce718137fc72230d8332f` may proceed to PM routing for
this narrow deterministic tranche with **no product behavior change requested**.

This is **not WP-36 acceptance**. The separately required 100,000-sequence
transport-input run remains outstanding and explicitly excluded.

## Immutable identities

- product base: `e3c90e09dae7b4210d03daaf1cd3d125a219479e`
- product head: `bce469b517636a39a08ce718137fc72230d8332f`
- candidate tree: `7c03f8b443ae3da95e29a39fc173566b01c64c36`
- verifier publication: `6fc4014a4afa088cbba49c8306f72a77bd3291d8`
- verifier/product `tests/slot_draft8` tree:
  `14860665f297d03867cc1098a02d3f6495a6d935`
- exact adapter source Git blob:
  `b30cb6b853676d603899ca1fcc7790715c6e7e79`
- independently recomputed adapter source SHA-256:
  `869fc3926ecb83fb2406c2412eab39ede4036ba3313aa7323e42bf6d9d162d37`

PR #191 changes only CI and Software-owned slot adapter/runner files. It changes
no engine file and no verifier-owned package byte.

## Exact product evidence

- Actions run/job: `35873349423` / `107222846601`
- artifact: `p1-r25-slot-product-evidence`
- artifact ID: `10756185178`
- downloaded artifact ZIP SHA-256:
  `b956c7906130a5190cb832eb3c2b15b32fc50937ef914d46f71bcded51e2aa06`
- `observations.jsonl` SHA-256:
  `d395bce4e4f8daff7e73a13d13d6b6ac4e1a88d51be5e56069f66d4ebf33378a`
- `PROVENANCE.md` SHA-256:
  `088d8629d6f26f677f8a99c2c99e2ecc85350150ff803bb7b60bcd183e8d882c`
- linked debug product probe SHA-256:
  `e2b7bd8fbe98eff2798c37e1341866be0ae539dcaf850146cca5c6295d8d9bdf`

The downloaded artifact contains one verifier-runner provenance row and exactly
five case rows.

## NULL-source / debug-trap boundary

This evidence does not rely merely on a JSON
`"debug_assertions": true` claim.

### Literal NULL capability

The exact adapter source constructs the public `tape_dev` with:

`dev.write = NULL`

There is no write callback wrapper that could swallow or count an attempted
write. The adapter supplies only source read and flush callbacks.

The adapter itself contains:

```c
#ifdef NDEBUG
#error "WP-36 product evidence requires debug assertions enabled"
#endif
```

and its Makefile includes `-UNDEBUG`.

### Exact internal trap

Verification performed a narrow instrumentation-only inspection of the frozen
`engine/src/dev.h` helper at the exact candidate head. The sanctioned engine
write wrapper is:

```c
static inline int dev_write(const tape_dev *d,
                            uint32_t lba, uint32_t count, const void *buf)
{
    TAPE_TRAP_IF(d->write == NULL);
    return d->write(d->ctx, lba, count, buf);
}
```

with:

```c
#ifndef NDEBUG
# define TAPE_TRAP_IF(cond) do { if (cond) { __builtin_trap(); } } while (0)
#else
# define TAPE_TRAP_IF(cond) ((void)0)
#endif
```

Therefore, when `NDEBUG` is absent, an internal `dev_write` attempt against
this source slot terminates at the wrapper before any callback can occur.

### Engine really built with the trap active

The exact-head Actions log shows the slot job rebuilding the engine with:

`make -C engine all CFLAGS=-UNDEBUG`

and the actual compiler commands for engine objects include `-UNDEBUG`.
The adapter compile command also includes `-UNDEBUG`.

Thus both the adapter compile-time attestation and the engine's internal
`dev_write` trap are active in the exact linked product binary.

### Crash/assertion failure cannot be accepted

The unchanged verifier self-test runs a fake adapter that exits 134 and confirms
the verifier runner reports:

`adapter process failed; assertion/crash is a WP-36 failure`

and exits nonzero.

The real verifier runner likewise treats nonzero exit, signal/abort, timeout,
missing output or malformed observation as case failure.

Combining:
1. literal `write = NULL`;
2. active `dev_write` trap in the exact engine build; and
3. fail-closed process-exit handling

means normal completion of these public API scripts is genuine evidence that no
forbidden internal `dev_write` path was reached. It is not merely a
self-reported debug flag.

## Adapter / runner mechanical audit

No material observation defect was found.

The adapter:
- maps the five exact verifier case IDs to the intended A/B/playback/mutator/
  repair scripts;
- logs every actual source read callback before range refusal;
- logs every source flush callback;
- has no source write callback because `dev.write == NULL`;
- carries an event-overflow flag and exits nonzero on overflow;
- uses bounded scripted call counts well below its call array capacity;
- records the actual public results, info fields, service continuation,
  rendered count, feed accepted count and mutator continuation flags.

The Software wrapper:
- authenticates the imported verifier subtree;
- invokes the unchanged verifier-owned `runner.py`;
- retains the complete JSONL;
- records product/tree/source/binary hashes;
- does not synthesize expected product observations.

## Independent raw-observation replay

Verification ignored the retained Software/verifier-runner
`status=PASS` / `errors=[]` fields and independently applied the unchanged
oracle's observable requirements to all five raw JSON observations.

Common facts across all five:
- observation format is `WP36-SLOT-OBSERVATION-2`;
- `adapter_kind=product`;
- `debug_assertions=true`;
- `event_overflow=false`;
- one successful init, mount, info and unmount;
- `tape_info.writable=false`;
- zero write callbacks;
- zero flush callbacks;
- normal process exit.

### Case dispositions

| Case | Independent disposition |
|---|---|
| WP36-SRC-A | PASS — Side A playback path completes, service terminates, render returns 8 |
| WP36-SRC-B | PASS — Side B playback path completes, service terminates, render returns 8 |
| WP36-SRC-MUTATORS-B | PASS — arm/reset/promote/respool READ_ONLY; feed/commit BUSY |
| WP36-SRC-MUTATORS-A | PASS — same writability gating from Side A |
| WP36-SRC-REPAIR-A | PASS — mount succeeds, writable=false, needs_repair=true, no write/flush |

**Result: 5/5 PASS.**

## Media-identity evidence

The unchanged verifier runner checked the actual OUTPUT.vo08 from each process
against the verifier fixture during the exact-head run.

The retained artifact preserves the observation JSONL and provenance, but not
the per-case OUTPUT.vo08 bytes themselves. Verification therefore does not
pretend to re-hash absent output files.

Independently, the exact adapter dataflow was audited:
- `media_load` is the only code that populates/modifies the tracked
  `g_media` superblock/index envelope;
- after load, the source callback surface exposes reads and flush only;
- `dev.write` is literal NULL;
- the adapter contains no post-load mutation of `g_media`;
- `media_store` serializes that same `g_media` object.

Together with the exact-run verifier result, this supports the published
byte-identical-media assertion without relying on a hidden write-swallowing
callback.

## Routing

PM may route exact product PR #191 onward for this deterministic precursor.
Verification requests no product behavior change for these five cases.

## Explicit exclusion / acceptance boundary

Still **unaccepted and required separately**:
- the WP-36 100,000 random transport-input sequence run.

Also excluded:
- complete WP-36 acceptance;
- broader source/helper acceptance;
- WP-11 golden/listening acceptance.

Issue #51 may close as completed.
