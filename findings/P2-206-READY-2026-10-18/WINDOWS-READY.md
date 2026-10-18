# Windows11 INGEST — one corrected-kit host collection

Verification206 collection-readiness PASS applies when this document is on merged
Verification/main with green normal CI. This authorizes one observation to return
for review, not acceptance of its results. Use this corrected kit/script; the old
6126d04 kit and original9d850667 script are historical and PAUSED.

If you already collected an older packet, preserve and return it first. No automatic
repeat is requested. Physical read-only A6 is a separate ready task: do it with its
own reviewed instructions, then remove the card and unplug the reader for INGEST.
Do not repeat earlier pulls, loads, dumps, README checks or off-card rehearsals.

## Before starting

- Windows11 x64 client desktop/laptop, build22000 or later.
- Remove every SD card and unplug every card reader for this host-only run.
- Open an Administrator PowerShell. Existing policy stays as it is. If it refuses
  the script, stop and return the exact error; do not change/override policy or
  run the script by another method.
- Python3.12 must already be available as `py -3.12` or `python`. If the script says
  it is missing, report that stop. No new installation is required by this brief.
- At least25GB free on the system drive, plus space for the returned ZIP. Internet
  access to GitHub/codeload/raw.githubusercontent.com, Microsoft Sysinternals and PyPI.
- Leave this run to finish. It creates a private Python environment, downloads the
  pinned sources/tools, and runs1927 host cases; it can take a while.

The existing Process Monitor selftest makes one deliberate read-nothing system-disk
handle open to establish visibility. It does not read/write/provision a cartridge.
No additional device probe or physical rehearsal is requested.

## 1. Download and authenticate

Paste this block in Administrator PowerShell. A failed command or mismatched hash
means STOP: preserve/report the error, do not proceed or retry with changed values.
The download and work folders must be new; do not delete earlier evidence to make
these checks pass.

```powershell
$ErrorActionPreference = 'Stop'
$d = Join-Path $env:USERPROFILE 'Downloads\DigitalTape-ingest-206'
$work = "$env:SystemDrive\DigitalTape-ingest-work-206"
if (Test-Path -LiteralPath $d) { throw "STOP: $d already exists; report this and preserve it." }
if (Test-Path -LiteralPath $work) { throw "STOP: $work already exists; report this and preserve it." }
New-Item -ItemType Directory -Path $d | Out-Null
$t = 'win11-kit-ingest-0.1.1-50bc4160f6da-r39104751447-1'
Invoke-WebRequest -UseBasicParsing -OutFile "$d\win11-kit.zip" `
  -Uri "https://github.com/mmsanders/Digital-Tape/releases/download/$t/win11-kit.zip"
Invoke-WebRequest -UseBasicParsing -OutFile "$d\win11_packet.ps1" `
  -Uri 'https://raw.githubusercontent.com/mmsanders/Digital-Tape/e1e06fc599177872b4f5d39d46f59c8952d1c108/tools/win11-kit/win11_packet.ps1'
if ((Get-Item -LiteralPath "$d\win11-kit.zip").Length -ne 2604482) { throw 'STOP: kit byte size differs.' }
$kitHash = (Get-FileHash -LiteralPath "$d\win11-kit.zip" -Algorithm SHA256).Hash
$scriptHash = (Get-FileHash -LiteralPath "$d\win11_packet.ps1" -Algorithm SHA256).Hash
Write-Host "KIT_SHA256: $kitHash"
Write-Host "SCRIPT_SHA256: $scriptHash"
if ($kitHash -ne 'ffb0f78ac3980fa1bb130f0aff22d53ebb100ed3323a8e50ba62a6ee1819c865') { throw 'STOP: kit SHA256 differs.' }
if ($scriptHash -ne '74e1af2cb91a3f9b418363941c48a60eee972481a32cbb9af22d8f3060318f9e') { throw 'STOP: script SHA256 differs.' }
```

## 2. Collect once

In the same window, paste this block. No `-Rehearsal` or policy override is used.
The console transcript and actual native exit code are kept alongside the download.

```powershell
Start-Transcript -Path "$d\collection-console.txt" -ErrorAction Stop
& powershell.exe -NoProfile -File "$d\win11_packet.ps1" `
  -Candidate 50bc4160f6da527da8c684d05264f99815aaa870 `
  -Kit "$d\win11-kit.zip" -Work $work -Out $d `
  -ShippingSha256 d923613badda95baeb387d5415d5212a5dedb7c5c7144b21874479babd178f5b `
  -ObserveSha256 d544b6f5c82e653842625080a87ac63cb52353aaeca62494dd5d08eedb844d9a
$collectionExit = $LASTEXITCODE
Write-Host "COLLECTION_EXIT: $collectionExit"
Set-Content -LiteralPath "$d\collection-exit.txt" -Value $collectionExit
Stop-Transcript
if ($collectionExit -ne 0) { throw 'STOP: collection failed. Preserve the work and return the console/error and exit code; do not retry.' }
```

Success requires actual exit0 and all three final script lines:

- `PACKET: ...\Downloads\DigitalTape-ingest-206\ingest-win11-packet-50bc4160f6da.zip`
- `SHA256: <digest from this run>`
- `Send this zip and its SHA256 to Verification. This run is an observation, not a PASS.`

Return that ZIP and its printed SHA256, plus collection-console.txt and
collection-exit.txt. The packet's digest is computed from your run; it is not the
kit or rehearsal digest. Keep all local evidence until review. If upload size
blocks delivery, report the exact size and digest so transport can be arranged;
do not rerun or discard it.

Any red error, nonzero exit, STOPPED message, missing success lines or missing ZIP
is a stop. Report the output as printed and preserve the work folder. Some errors
use PowerShell's own wording instead of STOPPED. Failed summarization now leaves
the uncompressed packet under the work folder and makes no ZIP/send instruction.
Never send a stale ZIP as the result of a failed attempt.

## Authenticated identities and boundary

| Item | Exact identity |
|---|---|
| Binary/profile/transport source | Product50bc4160f6da527da8c684d05264f99815aaa870, treeea0c9ae717a8478ca357fd01186f2a4d912a1193 |
| Script source | Producte1e06fc599177872b4f5d39d46f59c8952d1c108, tools/win11-kit/win11_packet.ps1 |
| Kit |2604482 bytes; ffb0f78ac3980fa1bb130f0aff22d53ebb100ed3323a8e50ba62a6ee1819c865 |
| Shipping exe |848384 bytes; d923613badda95baeb387d5415d5212a5dedb7c5c7144b21874479babd178f5b |
| Observation exe |956928 bytes; d544b6f5c82e653842625080a87ac63cb52353aaeca62494dd5d08eedb844d9a |
| Version/profile |ingest0.1.1 /INGEST1-AP4, Rust1.97.0 locked shipping/separate observe build39104751447 |
| Procmon ZIP |477754bf299c9e5b311c5666f7a4a48dfdb21265eaa8f0cca70ef9d9552e3a10; valid Microsoft signature required |

Actual packaged bytes are authenticated; rebuilding the same source is not a way
to recover these Windows binary hashes. ZIP/member/provenance review carries from
Verification204; Verification206 independently checks the returned transport fix.
Hosted Server rehearsal establishes mechanics only. Actual Windows11 observations
remain to be reviewed. No Product merge, overall436/WP16/APP/native/Mac/physical
qualification follows from collection readiness.
