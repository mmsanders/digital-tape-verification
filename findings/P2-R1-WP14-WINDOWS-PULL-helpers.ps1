# Independent witness helpers only. No Product build, repair, or test facts.
# Paste these definitions into the Administrator PowerShell session.
function Invoke-Tape {
    param([string[]]$TapeArgs, [string]$Stem)
    $savedPreference = $ErrorActionPreference
    $PSNativeCommandUseErrorActionPreference = $false
    $code = $null
    $global:LASTEXITCODE = $null
    $started = [DateTime]::UtcNow
    Write-Host ('Started {0:u}: {1}' -f $started, ($TapeArgs -join ' '))
    $clock = [Diagnostics.Stopwatch]::StartNew()
    try {
        # Windows PowerShell wraps native stderr as NativeCommandError text.
        # Preserve it without treating a diagnostic as a failing exit code.
        $ErrorActionPreference = 'Continue'
        & $Exe @TapeArgs *> ($Stem + '.txt')
        $code = $global:LASTEXITCODE
    } finally {
        $clock.Stop()
        $ErrorActionPreference = $savedPreference
    }
    if ($null -eq $code) { throw 'No native process exit code; stop and inspect.' }
    [IO.File]::WriteAllText($Stem + '-exit.txt', [string]$code + "`r`n")
    [IO.File]::WriteAllText($Stem + '-seconds.txt', $clock.Elapsed.TotalSeconds.ToString('R', [Globalization.CultureInfo]::InvariantCulture) + "`r`n")
    @{ started_utc=$started.ToString('o'); ended_utc=[DateTime]::UtcNow.ToString('o'); args=$TapeArgs; exit=$code; seconds=$clock.Elapsed.TotalSeconds } |
        ConvertTo-Json -Depth 4 | Set-Content -Encoding UTF8 ($Stem + '-command.json')
    return [int]$code
}

function Save-WavRecords {
    param([string[]]$Paths, [string]$Output)
    $rows = foreach ($path in $Paths) {
        if (Test-Path -LiteralPath $path -PathType Leaf) {
            @{ path=$path; bytes=(Get-Item -LiteralPath $path).Length; sha256=(Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash }
        } else { @{ path=$path; missing=$true } }
    }
    ConvertTo-Json -InputObject @($rows) -Depth 4 | Set-Content -Encoding UTF8 $Output
}

function Assert-Wav {
    param([string]$Path, [long]$Bytes, [string]$Hash)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw ('Missing WAV: ' + $Path) }
    if ((Get-Item -LiteralPath $Path).Length -ne $Bytes -or (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash -ne $Hash) {
        throw ('Unexpected WAV length/hash: ' + $Path + '; preserve the card.')
    }
}

function Save-ReadOnlyRange {
    param([string]$Source, [long]$Offset, [int]$Count, [string]$Output)
    if ($Offset -lt 0 -or $Offset % 512 -ne 0 -or $Count -le 0 -or $Count % 512 -ne 0) { throw 'Unaligned read range.' }
    $stream = $null
    try {
        # Default File.Open buffering may request 4096 bytes for a 512-byte
        # final-sector read. Bound the buffer to one logical sector so a raw
        # device read cannot prefetch beyond the declared disk end.
        $stream = [IO.FileStream]::new($Source, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::ReadWrite, 512, [IO.FileOptions]::None)
        [void]$stream.Seek($Offset, [IO.SeekOrigin]::Begin)
        $buffer = New-Object byte[] $Count
        $done = 0
        while ($done -lt $Count) {
            $got = $stream.Read($buffer, $done, $Count - $done)
            if ($got -eq 0) { throw 'Short metadata read; retain refusal and card.' }
            $done += $got
        }
        [IO.File]::WriteAllBytes($Output, $buffer)
    } finally { if ($null -ne $stream) { $stream.Dispose() } }
}
