param([Parameter(Mandatory=$true)][string]$Out)
$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Path $Out | Out-Null
$Out = (Resolve-Path $Out).Path
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$text = [IO.File]::ReadAllText((Join-Path $here 'WINDOWS-READY.md'))
$begin = $text.IndexOf('function Invoke-Ingest206Child {')
$end = $text.IndexOf("`n`$ErrorActionPreference = 'Stop'",$begin)
if ($begin -lt 0 -or $end -lt 0) { throw 'Missing exact instruction function' }
$fn = $text.Substring($begin,$end-$begin)
if ($fn -notmatch "'-ExecutionPolicy','RemoteSigned'" -or $fn -match 'Bypass|Set-ExecutionPolicy|Unblock-File') { throw 'Unexpected policy authority' }
. ([scriptblock]::Create($fn))
$before = Get-ExecutionPolicy -List | ConvertTo-Json -Compress
$shell = Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe'
$child = Join-Path $Out 'harmless child.ps1'
@'
param([int]$ExpectedExit=0)
Write-Output 'BODY_STARTED'
Write-Output ('EFFECTIVE_POLICY: ' + (Get-ExecutionPolicy))
[Console]::Error.WriteLine('CHILD_STDERR')
exit $ExpectedExit
'@ | Set-Content -LiteralPath $child -Encoding ascii
$old = Join-Path $Out 'old-collection-stderr.txt'
'OLD_EVIDENCE_MUST_SURVIVE' | Set-Content -LiteralPath $old
$oldHash = (Get-FileHash $old -Algorithm SHA256).Hash
$rows = New-Object System.Collections.Generic.List[object]
foreach ($code in @(0,7)) {
    $receipt = Join-Path $Out ("exit-$code with spaces")
    $caught=$null
    try { Invoke-Ingest206Child -Shell $shell -Script $child -CollectorArguments @('-ExpectedExit',"$code") -ReceiptDirectory $receipt | Out-Null }
    catch { $caught=$_.Exception.Message }
    $got=(Get-Content (Join-Path $receipt 'collection-exit.txt') -Raw).Trim()
    if ($got -ne "$code" -or ($code -eq 0 -and $caught) -or ($code -eq 7 -and -not $caught)) { throw 'Actual exit/stop control failed' }
    $stdout=Get-Content (Join-Path $receipt 'collection-stdout.txt') -Raw
    $stderr=Get-Content (Join-Path $receipt 'collection-stderr.txt') -Raw
    if ($stdout -notmatch 'BODY_STARTED' -or $stdout -notmatch 'EFFECTIVE_POLICY: RemoteSigned' -or $stderr -notmatch 'CHILD_STDERR') { throw 'Child policy or logs not retained' }
    $rows.Add([pscustomobject]@{case="actual-exit-$code";exit=$got;stopped=[bool]$caught;stdout=$true;stderr=$true;child_policy='RemoteSigned'})
}
$marked=Join-Path $Out 'internet-marked.ps1'
Copy-Item -LiteralPath $child -Destination $marked
"[ZoneTransfer]`r`nZoneId=3`r`nHostUrl=https://example.invalid/harmless.ps1" | Set-Content -LiteralPath $marked -Stream Zone.Identifier -Encoding ascii
$receipt=Join-Path $Out 'policy-refusal';$caught=$null
try { Invoke-Ingest206Child -Shell $shell -Script $marked -CollectorArguments @() -ReceiptDirectory $receipt | Out-Null }
catch { $caught=$_.Exception.Message }
$got=(Get-Content (Join-Path $receipt 'collection-exit.txt') -Raw).Trim()
$err=Get-Content (Join-Path $receipt 'collection-stderr.txt') -Raw
if (-not $caught -or $got -eq '0' -or $err -notmatch 'PSSecurityException|not digitally signed|UnauthorizedAccess') { throw 'RemoteSigned refusal control failed' }
if ((Get-Content (Join-Path $receipt 'collection-stdout.txt') -Raw) -match 'BODY_STARTED') { throw 'Blocked child body ran' }
$rows.Add([pscustomobject]@{case='marked-unsigned-refusal';exit=$got;stopped=$true;body_ran=$false})
$receipt=Join-Path $Out 'missing-exit';$caught=$null
function Start-Process { [pscustomobject]@{ExitCode=$null} }
try { Invoke-Ingest206Child -Shell $shell -Script $child -CollectorArguments @() -ReceiptDirectory $receipt | Out-Null }
catch { $caught=$_.Exception.Message }
finally { Remove-Item Function:\Start-Process }
if (-not $caught -or (Get-Content (Join-Path $receipt 'collection-exit.txt') -Raw).Trim() -ne 'UNKNOWN') { throw 'Missing exit became success' }
$rows.Add([pscustomobject]@{case='missing-exit-mock';exit='UNKNOWN';stopped=$true})
$receipt=Join-Path $Out 'invocation-failure';$caught=$null
try { Invoke-Ingest206Child -Shell (Join-Path $Out 'absent.exe') -Script $child -CollectorArguments @() -ReceiptDirectory $receipt | Out-Null }
catch { $caught=$_.Exception.Message }
if (-not $caught -or (Get-Content (Join-Path $receipt 'collection-exit.txt') -Raw).Trim() -ne 'UNKNOWN' -or -not (Test-Path (Join-Path $receipt 'launch-error.txt'))) { throw 'Invocation failure was not preserved' }
$rows.Add([pscustomobject]@{case='invocation-failure';exit='UNKNOWN';stopped=$true;launch_error_retained=$true})
$caught=$null
try { Invoke-Ingest206Child -Shell $shell -Script $child -CollectorArguments @() -ReceiptDirectory $Out | Out-Null }
catch { $caught=$_.Exception.Message }
if (-not $caught -or (Get-FileHash $old -Algorithm SHA256).Hash -ne $oldHash) { throw 'Existing evidence was modified' }
$rows.Add([pscustomobject]@{case='existing-receipt';stopped=$true;old_evidence_unchanged=$true})
$after = Get-ExecutionPolicy -List | ConvertTo-Json -Compress
if ($before -cne $after) { throw 'Parent/stored policies changed' }
[ordered]@{powershell=$PSVersionTable.PSVersion.ToString();before_policy=$before;after_policy=$after;rows=@($rows.ToArray());scope='Harmless Windows Server process controls; no collector, kit campaigns or physical device execution'} | ConvertTo-Json -Depth 8 | Set-Content (Join-Path $Out 'RESULT.json')
Get-Content (Join-Path $Out 'RESULT.json')
