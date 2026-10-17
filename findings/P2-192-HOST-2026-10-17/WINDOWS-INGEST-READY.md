# One Windows11 INGEST host packet — exact6126d04

**Ready to collect the missing actual Windows11 host observations.** This is
collection readiness, not full candidate/native acceptance. The known Windows
zero-access-open visibility limit and Mac shipping-exhaustion hold survive.
There is no need to repeat accepted numerical results on other platforms.

Use Windows11x64 and Administrator PowerShell, Python3.12,25GiB free on the
working drive, and an ordinary computer folder. Keep the card and reader out.
You may batch this with the separate short Windows physical A6 instructions from
Verification193 in one sitting. Neither procedure repeats any load, dump, pulls,
README or off-card A6 rehearsal.

## Download the one exact kit

Download [win11-kit from the reviewed run](https://github.com/mmsanders/Digital-Tape/actions/runs/38948012087/artifacts/12067900169)
as `win11-kit.zip` into Downloads. It is2,576,682 bytes; SHA256:
`32d6643c1cb782dcf6ac540f14b733be556a3b089b49fd53475076b9f5503eac`.
The exact shipping and observation binaries are already inside; do not build them.
The artifact is retained until14January2027. If unavailable, return the message;
do not substitute a later kit or change any pins.

## Run the pinned collection script once

Paste into Administrator PowerShell. It runs the reviewed script in a child
PowerShell with normal policy; no execution-policy or OS security change is made.
If policy or a tool refuses access, preserve the actual message and stop.

```powershell
$ErrorActionPreference = 'Stop'
$Candidate = '6126d04050133cacb9a1960a0bc13c9ee93130e5'
$Kit = (Resolve-Path (Join-Path $env:USERPROFILE 'Downloads\win11-kit.zip')).Path
if ((Get-FileHash $Kit -Algorithm SHA256).Hash -ne '32d6643c1cb782dcf6ac540f14b733be556a3b089b49fd53475076b9f5503eac') { throw 'Kit differs from the reviewed bytes; stop.' }
$Tag = Get-Date -Format 'yyyyMMdd-HHmmss'
$Base = Join-Path $env:LOCALAPPDATA ('DigitalTape-ingest-' + $Tag)
if (Test-Path $Base) { throw 'Existing folder; preserve it.' }
New-Item -ItemType Directory -Path $Base | Out-Null
$Script = Join-Path $Base 'win11_packet.ps1'
Invoke-WebRequest -UseBasicParsing -Uri ('https://raw.githubusercontent.com/mmsanders/Digital-Tape/' + $Candidate + '/host/ingest/stage1/win11_packet.ps1') -OutFile $Script
if ((Get-FileHash $Script -Algorithm SHA256).Hash -ne '9d8506670df30bbbc547c6c5757d9370e152ed55cfa4cd8378bd9e1f1337f502') { throw 'Collection script hash differs; stop.' }
$Work = Join-Path $Base 'work'
$Out = Join-Path $Base 'return'
New-Item -ItemType Directory -Path $Out | Out-Null
Write-Host ('Keep this folder: ' + $Base)
& powershell.exe -NoProfile -File $Script -Candidate $Candidate -Kit $Kit -ShippingSha256 '0e1ef2cb4f283eb876f08019222da5d3ac744ec30d49f020a2e87323f31bcac1' -ObserveSha256 '97918d4315955d54894918a24d98f7c8e2fdf3d0568634613f77cf4af1f0eaa6' -Work $Work -Out $Out
Write-Host ('Collector child exit: ' + $LASTEXITCODE)
Write-Host ('Evidence and any stopped work remain under: ' + $Base)
```

The script validates the client platform, architecture, administrator capability,
space, binaries and current transport pins. It authenticates the immutable sources
and package, uses pinned/signed Microsoft Process Monitor, and writes a ZIP64 packet
so the actual largest legal WAV fits. It records the real OS; do not use `-Rehearsal`.
If Python3.12 is missing, it prints that prerequisite rather than fabricating a run.
If Microsoft's downloadable Procmon bytes have changed, its pin check stops; return
that message to Software instead of overriding it.

The observer selftest deliberately attempts a read-only handle open of
PhysicalDrive0, with no device read, to test visibility. It performs no card work.
The actual INGEST cases use the private host folder and files. The shipped binary
is unmodified; the separate observation binary is identified truthfully.

When the script prints `PACKET:` and `SHA256:`, return that ZIP and digest on
Michael447 or in this chat. Also return any stopped-run message. Keep the whole
private folder until Verification disposes the packet; do not delete native
PML/CSV or re-run the full census to try to obtain PASS. A Software summary or
zero collector exit is not independent acceptance.

Reviewed readiness facts: exact kit authenticated; both PE hashes checked;
shipping binary contains no diagnostic seam markers while the observation binary
contains all nine (real negative control). Script SHA/transport pins independently
checked. The exact-head CI script rehearsal on Server is supplementary mechanics,
not the missing actual Windows11 observation. This Linux review did not execute
these PowerShell commands on your machine. No new physical/media/target claim.
