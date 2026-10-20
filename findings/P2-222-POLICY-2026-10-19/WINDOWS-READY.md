# Continue the INGEST collection after the policy-only refusal

Michael authorized **RemoteSigned for the collector's one child PowerShell process**
on19 October2026. No persistent CurrentUser/LocalMachine policy is changed. This
supersedes the policy pause in222 only after this publication's controls pass and
it is merged on Verification/main. Kit, collector and executable bytes stay the
same as206. This is readiness to collect one observation, not package acceptance.

Keep the failed attempt's logs and every existing folder. **Remove the card AND
unplug the reader.** Open Administrator PowerShell. Python3.12,25GB free on the
system drive plus packet space, and the original network prerequisites still apply.
Do not redownload the kit, unblock files, install missing tools, or repeat the
physical card test. If any check stops, preserve/report its exact message.

Paste the following block once. It finds the previously downloaded authenticated
kit in either known folder spelling, refuses existing work/packets, and places
new logs/ZIP in a fresh subfolder. It runs the original collector as a file, with
the specifically authorized process-only policy. Internet-marked unsigned script
refusal and managed-policy restrictions remain stops.

```powershell
function Invoke-Ingest206Child {
    param([string]$Shell,[string]$Script,[string[]]$CollectorArguments,[string]$ReceiptDirectory)
    if (Test-Path -LiteralPath $ReceiptDirectory) { throw 'STOP: receipt folder exists; preserve it.' }
    New-Item -ItemType Directory -Path $ReceiptDirectory -ErrorAction Stop | Out-Null
    $arguments = @('-NoProfile','-ExecutionPolicy','RemoteSigned','-File',('"{0}"' -f $Script)) + $CollectorArguments
    try {
        $process = Start-Process -FilePath $Shell -ArgumentList $arguments -Wait -PassThru -NoNewWindow `
            -RedirectStandardOutput (Join-Path $ReceiptDirectory 'collection-stdout.txt') `
            -RedirectStandardError (Join-Path $ReceiptDirectory 'collection-stderr.txt') -ErrorAction Stop
    } catch {
        $_.Exception.Message | Set-Content -LiteralPath (Join-Path $ReceiptDirectory 'launch-error.txt')
        'UNKNOWN' | Set-Content -LiteralPath (Join-Path $ReceiptDirectory 'collection-exit.txt')
        throw
    }
    $code = $process.ExitCode
    if ($null -eq $code) {
        'UNKNOWN' | Set-Content -LiteralPath (Join-Path $ReceiptDirectory 'collection-exit.txt')
        throw 'STOP: missing actual child exit; preserve the receipt folder.'
    }
    $code | Set-Content -LiteralPath (Join-Path $ReceiptDirectory 'collection-exit.txt')
    Get-Content -LiteralPath (Join-Path $ReceiptDirectory 'collection-stdout.txt')
    Get-Content -LiteralPath (Join-Path $ReceiptDirectory 'collection-stderr.txt')
    Write-Host ('COLLECTION_EXIT: ' + $code)
    Write-Host ('RECEIPT_DIRECTORY: ' + $ReceiptDirectory)
    if ($code -ne 0) { throw 'STOP: collection failed; preserve logs/work and do not retry.' }
}
$ErrorActionPreference = 'Stop'
$folders = @('DigitalTape-ingest-206','Digital-Tape-ingest-206') | ForEach-Object {
    Join-Path $env:USERPROFILE ('Downloads\' + $_)
} | Where-Object { Test-Path -LiteralPath (Join-Path $_ 'win11_packet.ps1') }
if (@($folders).Count -ne 1) { throw 'STOP: expected exactly one existing kit folder; report the folders found.' }
$d = @($folders)[0]
$script = Join-Path $d 'win11_packet.ps1'
$kit = Join-Path $d 'win11-kit.zip'
if ((Get-FileHash -LiteralPath $script -Algorithm SHA256).Hash -ne '74e1af2cb91a3f9b418363941c48a60eee972481a32cbb9af22d8f3060318f9e') { throw 'STOP: collector hash differs.' }
if ((Get-Item -LiteralPath $kit).Length -ne 2604482 -or (Get-FileHash -LiteralPath $kit -Algorithm SHA256).Hash -ne 'ffb0f78ac3980fa1bb130f0aff22d53ebb100ed3323a8e50ba62a6ee1819c865') { throw 'STOP: kit size/hash differs.' }
$work = "$env:SystemDrive\DigitalTape-ingest-work-206"
foreach ($oldWork in @($work,"$env:SystemDrive\ingest-win11-work")) {
    if (Test-Path -LiteralPath $oldWork) { throw ('STOP: existing work folder; preserve and report it: ' + $oldWork) }
}
if (Get-ChildItem -LiteralPath $d -Filter 'ingest-win11-packet-*.zip' -File) { throw 'STOP: older packet exists; return it before any new collection.' }
$receipt = Join-Path $d ('collection-approved-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '-' + [guid]::NewGuid().ToString('N').Substring(0,8))
$collectorArguments = @(
    '-Candidate','50bc4160f6da527da8c684d05264f99815aaa870',
    '-Kit',('"{0}"' -f $kit), '-Work',('"{0}"' -f $work), '-Out',('"{0}"' -f $receipt),
    '-ShippingSha256','d923613badda95baeb387d5415d5212a5dedb7c5c7144b21874479babd178f5b',
    '-ObserveSha256','d544b6f5c82e653842625080a87ac63cb52353aaeca62494dd5d08eedb844d9a'
)
Write-Host ('New receipt folder: ' + $receipt)
Invoke-Ingest206Child -Shell (Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe') `
    -Script $script -CollectorArguments $collectorArguments -ReceiptDirectory $receipt
```

The console may be quiet while the1927 host cases run. Wait for completion.
Success needs actual exit0 plus the collector's `PACKET:`, `SHA256:` and send lines,
and a new `ingest-win11-packet-50bc4160f6da.zip` inside the printed receipt folder.
Return that ZIP, its printed SHA256 and the new collection-stdout.txt,
collection-stderr.txt,collection-exit.txt to Michael473 or this chat. A zero launcher
exit without those packet/signoff lines is not a successful collection.

On refusal/nonzero/unknown exit: keep old AND new logs/work. Do not rerun, switch
to Bypass, change persistent policy, unblock a file, delete a folder or send an
older ZIP. Return the exact stop and printed receipt path. The child process's
RemoteSigned setting ends with that child and its descendants; it does not change
the parent shell or stored policies. Download marking can still prevent unsigned
scripts from running; that is an honest capability stop.
