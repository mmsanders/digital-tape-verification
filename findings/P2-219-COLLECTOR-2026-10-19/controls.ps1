param([Parameter(Mandatory=$true)][string]$Out)
$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Path $Out -ErrorAction Stop | Out-Null
$Out = (Resolve-Path $Out).Path
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
function Read-CollectorFunction([string]$Path) {
    $text = [IO.File]::ReadAllText($Path)
    $begin = $text.IndexOf('function Invoke-A6Native {')
    $end = $text.IndexOf("`nGet-Command wpr.exe", $begin)
    if ($begin -lt 0 -or $end -lt 0) { throw 'Missing exact collector function' }
    return $text.Substring($begin,$end-$begin)
}
$oldPath = Join-Path $here '../P2-R1-WP14-A6-R4-2026-10-17/WINDOWS-READY.md'
$old = Read-CollectorFunction $oldPath
$new = Read-CollectorFunction (Join-Path $here 'WINDOWS-READY.md')
$expected = $old.Replace('$LASTEXITCODE = $null','$global:LASTEXITCODE = $null').Replace('$nativeCode = $LASTEXITCODE','$nativeCode = $global:LASTEXITCODE')
# Ignore only comments: executable delta must be precisely the two scope qualifiers.
function ExecutableLines([string]$Text) {
    return (($Text -split "`r?`n" | Where-Object { $_.Trim() -and -not $_.Trim().StartsWith('#') }) -join "`n")
}
if ((ExecutableLines $new) -cne (ExecutableLines $expected)) { throw 'Unexpected wrapper delta' }
$rows = New-Object System.Collections.Generic.List[object]
. ([scriptblock]::Create($old))
foreach ($code in @(0,7)) {
    $global:LASTEXITCODE = 91
    $caught = $null
    try { $r = Invoke-A6Native -NativeTool $env:ComSpec -NativeArgs @('/d','/c',"exit $code") -Stem (Join-Path $Out "old-$code") }
    catch { $caught = $_.Exception.Message }
    if ($caught -notlike 'No actual native exit code*' -or $global:LASTEXITCODE -ne $code) { throw 'Original scope bug not reproduced' }
    $rows.Add([pscustomobject]@{case="old-$code";native_global=$global:LASTEXITCODE;stopped=$true;message=$caught})
}
. ([scriptblock]::Create($new))
foreach ($code in @(0,7)) {
    $global:LASTEXITCODE = 91
    $r = Invoke-A6Native -NativeTool $env:ComSpec -NativeArgs @('/d','/c',"echo stdout-$code & echo stderr-$code 1>&2 & exit $code") -Stem (Join-Path $Out "new-$code")
    if ($r -ne $code) { throw 'Wrong actual exit' }
    if ((Get-Content (Join-Path $Out "new-$code-out.txt") -Raw) -notmatch "stdout-$code") { throw 'stdout not retained' }
    if ((Get-Content (Join-Path $Out "new-$code-err.txt") -Raw) -notmatch "stderr-$code") { throw 'stderr not retained' }
    if ($ErrorActionPreference -ne 'Stop') { throw 'Caller preference not restored' }
    $rows.Add([pscustomobject]@{case="new-$code";exit=$r;stdout_retained=$true;stderr_retained=$true})
}
function NoNativeExit { Write-Output 'host-only missing-exit control' }
foreach ($tool in @('NoNativeExit',(Join-Path $Out 'does-not-exist.exe'))) {
    $global:LASTEXITCODE = 0 # A stale successful code must not be reused.
    $caught = $null
    try { $r = Invoke-A6Native -NativeTool $tool -NativeArgs @() -Stem (Join-Path $Out ('failure-' + $rows.Count)) }
    catch { $caught = $_.Exception.Message }
    if (-not $caught) { throw 'Missing/invocation exit did not stop' }
    if ($tool -eq 'NoNativeExit' -and $caught -notlike 'No actual native exit code*') { throw ('Missing exit was not detected: ' + $caught) }
    if ($ErrorActionPreference -ne 'Stop') { throw 'Caller preference not restored on failure' }
    $rows.Add([pscustomobject]@{case=$tool;stopped=$true;message=$caught})
}
# A terminating invocation failure must also propagate, never become zero.
$caught=$null
try { $r=Invoke-A6Native -NativeTool $env:ComSpec -NativeArgs @('/d','/c','exit 0') -Stem (Join-Path $Out 'absent-parent/output') }
catch { $caught=$_.Exception.Message }
if (-not $caught) { throw 'Redirection/invocation failure did not stop' }
$rows.Add([pscustomobject]@{case='invalid-output-parent';stopped=$true;message=$caught})
$wpr = Get-Command wpr.exe -CommandType Application -ErrorAction SilentlyContinue
if ($wpr) {
    $r=Invoke-A6Native -NativeTool $wpr.Source -NativeArgs @('-profiles') -Stem (Join-Path $Out 'wpr-profiles')
    $rows.Add([pscustomobject]@{case='host-wpr-profiles';exit=$r;scope='profiles only; no trace or card command'})
}
[ordered]@{powershell=$PSVersionTable.PSVersion.ToString();edition=$PSVersionTable.PSEdition;rows=@($rows.ToArray());disposition='PASS harmless process controls; physical collection remains paused'} | ConvertTo-Json -Depth 8 | Set-Content (Join-Path $Out 'RESULT.json')
Get-Content (Join-Path $Out 'RESULT.json')
