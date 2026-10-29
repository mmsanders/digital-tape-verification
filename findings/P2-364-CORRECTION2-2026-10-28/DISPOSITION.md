# Software624 correction2 — one unsafe NOT_READY exception remains

28 October 2026 PDT. Michael resumed: “Review software work.” Inputs Product main
`262466d354dac779b0fda9d712a2d75b73eeec33`, Verification main
`c8d137c61380bdc5f09b5fcc55e5ef7f533077c7`; Software
[return6487308640](https://github.com/mmsanders/Digital-Tape/issues/624#issuecomment-6487308640),
exact **`3963689230cd96e34dd0ee05e160bff6b172c774`**, PR626. Same Verification364
scope and independent context. No Product edits, physical card or native app run.

**FINDINGS: no integration/C2 clearance.** The earlier mount-path, extent and
enumeration error cases now fail closed. However, a new unconditional
ERROR_NOT_READY exception can still hide a volume on the target disk. F364-1 and
the shared A4/full-WP14 qualification remain open only at this narrowed issue.
Other accepted observations and WP-16 remain unchanged. No physical rerun.

## [P1] Do not equate ERROR_NOT_READY with confirmed absence of media

[probe_win.c:232](https://github.com/mmsanders/Digital-Tape/blob/3963689230cd96e34dd0ee05e160bff6b172c774/host/port/probe_win.c#L232)
skips a failed extent lookup whenever its error is ERROR_NOT_READY, **without**
checking whether that volume is on another device. `volume_elsewhere` is bypassed
by the short-circuit. That leaves `n_mounted` smaller and `query_error` empty even
for a volume on the selected disk.

Microsoft defines [ERROR_NOT_READY/21](https://learn.microsoft.com/en-us/windows/win32/debug/system-error-codes--0-499-)
as a device not being ready. It does not establish that media is absent or that
the volume cannot belong to the target. In contrast,
[ERROR_NO_MEDIA_IN_DRIVE/1112](https://learn.microsoft.com/en-us/windows/win32/debug/system-error-codes--1000-1299-)
expressly identifies no medium. The two are not interchangeable safety facts.
APP-1A §7 still requires an unresolved required query to fail closed.

### Independent control on this exact source

[CI40816448825](https://github.com/mmsanders/digital-tape-verification/actions/runs/40816448825)
compiled the covered probe with `tests/c1_volume_query_r2/prepare.py`'s controller.
The positive sees a real mounted NTFS volume on a freshly created hosted VHD.
The second run replaces **only that target-volume extent response** with a typed
ERROR_NOT_READY input. Its device number is obtained from an actual successful
IOCTL_STORAGE_GET_DEVICE_NUMBER on the same handle before the controlled failure.
Other queries remain real. This is a controlled error-code branch test, **not**
a claim that the OS spontaneously returned21 or that an empty reader was measured.

| Observed/control fact | Result |
|---|---|
| Baseline real mounted volumes | 1 |
| Target-volume extent response | Typed failure21, one call |
| Resulting mounted-volume count | **0** |
| Query error recorded | **false** |
| Pure removable-policy model, all other observed facts retained | REFUSE_FOREIGN_MOUNT (5) → REFUSE_NONE (0) |
| Required-query fail-stop | **FAIL** |

No Make, provision or raw write is invoked by the probe driver. The VHD setup
creates/formats only its own fresh file-backed disk. Removable=true is an explicit
pure-policy model input; the real VHD remains virtual/refused in shipping policy.
The workflow is green because it reproduces this known failed criterion, not
because the Product passed. The generated driver and RESULT are retained.

**Small correction, same task:** remove the unconditional NOT_READY bypass. On
that error, require affirmative other-device/non-disk evidence or fail the census
with the existing query-error/refusing-mount behavior. A successful independent
query can still exclude an unrelated empty reader, so this does not require
refusing every Make on a machine with such a reader. Add the same-target21
negative and other-device positive beside the existing controls. No physical
reader run, new observer or method round is requested.

## Explicit disposition of the other exclusions requested by Software

- **NO_MEDIA_IN_DRIVE/1112:** its documented meaning supports the limited inference
  that the queried drive currently has no medium, hence no mounted medium to
  preserve at that query point. It is not a claim of actual empty-reader testing,
  durable identity, or detection of a later insertion/swap; the existing query/open
  race limitation remains. This does not justify treating generic NOT_READY alike.
- **Affirmative other-device result:** a successful
  [IOCTL_STORAGE_GET_DEVICE_NUMBER](https://learn.microsoft.com/en-us/windows/win32/api/winioctl/ni-winioctl-ioctl_storage_get_device_number)
  response supplies device type/number. The helper's explicit different-device or
  non-disk test is a bounded positive exclusion, not permission to ignore a failed
  auxiliary query. If it cannot establish that exclusion for a possibly related
  volume, the existing fail-closed path must apply. No cross-restart identity or
  blanket proof about an unknown spanned/backing topology is granted.

The current blocker is specifically the unconditional21 case, which never even
attempts this positive exclusion. No additional physical qualification is imposed
to dispose these code/contract facts.

## What now passes

Independent offline `audit.py` uses the published validators, not producer-private
assertions. It authenticates original bundle files, real bridge reports/process
exits and candidate bytes. AUDIT.json contains the individual judgments.

| Coverage | Result |
|---|---|
| Old S3 suite | **31 Linux + 10 Windows PASS**, unchanged independent runner |
| Initial disk-length/open-geometry queries and known-policy neighbor | **3 per platform PASS**, with actual-query-failure-as-exit3 mutants rejected |
| Corrected census queries | Windows **4 PASS**: successful foreign-mounted neighbor exit3; actual mount-path/extent/enumeration OS faults → HOST_QUERY_FAILED/1 |
| Standalone census safety | **4 provision rows PASS**, REFUSE_FOREIGN_MOUNT/3, zero write-mode opens/writes/unmounts |
| Own-p1 and invalid-label supplement | PASS; failed-unmount negative still rejected |
| G3 real-child/bridge matrix | **28/28 PASS**, 16 child + 12 app-origin; exact original report/process/raw hashes independently checked |
| Import/source integrity | C1 tree `2401eac8980f0a9efddec2b301c335d6ee448dfc` and query-r1 tree `a25993fa18e4cf7d330937cc00a0a7b9af27662d` match Verification main; import083f7aaa predates code. Engine remains `d96b4245`. |

Software's CI also ran the unchanged real mount-path regression over old and new
probe source, reporting old omission versus new fail-stop; its original log is
retained. The distinct NOT_READY control above is independently run by Verification.
The production app source tree is unchanged from correction1; only the test import
and safety helper change. G3's `rows_not_matching:2` is stale producer diagnostic
counting of empty rejected-drop text; the actual corrected full `g3.check` and
independent replay both pass28. No native G4/Show-details/UAC claim follows.

## Exact rebuilt candidate

Make40810721775, G3 40810724483 and candidate40810718612 all completed SUCCESS on
the returned exact head. Captured PR check set:130 SUCCESS. These are authenticated
build/coverage facts, not clearance of the remaining exception.

| Item | Independently measured SHA-256 |
|---|---|
| ZIP | `4d415f99806a934f3429379befc9ad6e0bd50f1688fda4e448d5e48ed8d467c4` |
| digital-tape.exe | `5dda5d4a06d8a30c07f9bb61c7658d54ed3771ac2ffd35e275f6344f5319b809` |
| tapectl.exe | `2f348536912db67e930d6107a5a88b8d67094b717248cf3fa506a23b2b8c9e13` |
| ingest.exe | `3895f3f356c91b8a9fe870c33694da64bf2765df308bef118d657c1be4bb9a20` |

BUILD source/head/member identities agree. PE resources request no elevation;
the carried default-invoker boundary remains. Real Win11 UAC, reader/card and
person-triggerable outcomes remain C2 after clearance, not executed here.

The revised method note's census correction is supported for the measured fault
cases. Its statement grouping NOT_READY with “no medium” must be corrected with
the code. This is the only remaining blocking finding from this review.

## Replay and next owner

[Release evidence-364-correction2-2026-10-28](https://github.com/mmsanders/digital-tape-verification/releases/tag/evidence-364-correction2-2026-10-28),
asset `verification364-correction2-inputs.zip`, 51,162,284 bytes, SHA-256
`d5605a161bc0d669dab5293b5dbe989691f74651adce18db72ac395276941b3e`.
Only public project CI originals and review metadata/control bytes are retained;
no user music/private workspace data. `fetch.py DEST` authenticates before
extraction; `audit.py DEST --out RESULT` reproduces judgments without running Product.

Software624 makes the narrow exception correction and returns the next exact head,
CI controls and rebuilt candidate identities. Verification364 stays open. **Do not
integrate39636892 or run C2 with it.** A4/fullWP14 qualification remains limited
to this unresolved safety path; previous physical observations and WP16 stand.
