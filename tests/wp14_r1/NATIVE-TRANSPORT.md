# Mechanical native transport requested from Software #392

This is a verifier-owned request/observation protocol, not a claim that Software
already implements these interfaces. Binding does not move expectations into
Product. `native.py --platform OS TRANSPORT [ARGS...]` invokes
`TRANSPORT [ARGS...] request.json response.json` for every applicable case.

Use only temporary owned targets. Linux must execute actual loop-device cases in
Linux CI even when the local runner has no free loop. Production rejects loops;
test facts make them eligible. macOS/Windows must use their actual native port
on owned virtual backing with test facts; pair with actual production virtual
refusal. Never open physical user disks from this runner.

Each request identifies command, platform, backing path, target_bytes, facts,
binary_kind, optional control, and expected observations. The seed has a truthful
9-second TAPEFS cartridge. **Freshly provision a 64,000,000,000-byte sparse target
before normal cases**, then load the published quiet source where audio is needed;
the seed's small mirror is not a 64 GB formatted cartridge. Reset backing before
each case. Fixture requests already contain a complete whole-image layout: bind
those exact verifier bytes and their target_bytes, without reprovisioning. The
ceiling-equality case uses a 128 GiB sparse target. geometry_too_small requests
a 9-second label with partition 2 one sector short; preserve the existing target.
provision-order uses a nonzero old MBR and captures both LBA0 write payloads in
data_hex; mbr-first mutates only the publication order. unmount-error injects
failed unmount of an otherwise allowed own partition 1. suppress-finding is a
test-only host finding omission; do not change engine bytes for that mutant. Map commands mechanically using copied WP11/WP14 public syntax; use
UUID 00112233445566778899aabbccddeeff and epoch 315532800 for reproducible provision.
Use one-second overage source for capacity cases when added, and actual service
reads of referenced chunk data for the read injection, never mount metadata.

Facts map to the issued test-only facts file (`TAPECTL_TEST_FACTS`): whole,
removable, sd_bus, bytes, holds_os, layout_ok; repeated mounted=partition:where.
foreign_mount=true maps to a mounted foreign entry, otherwise none. `virtual`
is an actual target/probe setup, not a newly invented facts-file key. Erase
confirmation matches the logical target only when erase_matches is true; false
uses another explicit name. Facts apply only to device paths. Do not inject
facts into the production binary or assert that synthetic facts prove the OS
probe works. Required production symbols/string gate checks both real binaries.

Response fields:

- case, platform, request_sha256 (SHA-256 of sorted-key JSON **before** adding
  request_sha256), head_sha (40 lower hex), binary_sha256 (64 lower hex).
- capture_origin="native-candidate", control_applied matching requested control
  (null when absent), capture_artifacts: persistent raw artifact paths/URLs and
  hashes, including exact command/build/capture configuration and provenance.
- exit, stdout, stderr; trace for command cases. For symbols: binary_path and
  authentic native symbol-table output in symbols; binary_path must persist for
  immediate hash checking. Strip decoration only mechanically, never findings.
- trace: operation, platform, target_kind, target_bytes, success, events in
  observed order. Refusals additionally carry refusal, exit=3, engine_used=false
  when no engine call occurred. Do not fabricate a binding on a refused path.
- event kinds: write_open; engine_bind with write_is_null; read with offset,
  bytes, success, phase and referenced_chunk for failure injection; write with
  offset, bytes, issued_before_return and coalesced; flush with success,
  os_success, os_call, and fullfsync_unsupported for raw macOS fallback only.
  Offsets are actual **whole-target byte offsets**, not partition-relative.

No-op-flush means a real controlled candidate callback returns success without
its OS barrier; capture that omission. Non-NULL-binding means a real controlled
binding, even when it writes nothing. Each isolated bypass mutates only the
named safety rule; other rules stay valid. Flush-error injects actual barrier
failure and must propagate nonzero. Referenced-read-error injects a port failure
while verify services referenced audio. Controls/build changes must be test-only,
absent in shipped binary, and retained as patch/config/build provenance. An
unrelated process failure, missing record, forged JSON or wrong binary cannot
count as the intended control. Verification reviews that causal linkage.

Adapter stdout is not verdict input; write complete response.json and retain raw
captures outside the runner's temporary directory. All runs must bind the final
exact import/binding head announced in #146. No candidate accepted by this
transport alone; platform CI and A8 identity/replays are separate mandatory gates.
