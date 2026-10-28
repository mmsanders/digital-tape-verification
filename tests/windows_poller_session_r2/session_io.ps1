# Ordinary owned-file observation/retention only. No process launch or native API here.
function Read-LiveSession([string]$Control,[int]$AppPid,[string]$AppPath,[string]$AppHash,[decimal]$StartNs) {
  if (!(Test-Path -LiteralPath $Control)) { throw 'No new diagnostic folder after readiness' }
  [void](Ordinary-Path $Control $true)
  $dirs=@(Get-ChildItem -LiteralPath $Control -Force)
  if ($dirs.Count -ne 1 -or !$dirs[0].PSIsContainer -or $dirs[0].Name -cnotmatch '^diag-[0-9a-f]{32}$') { throw 'Expected exactly one fresh diagnostic session' }
  $dir=Ordinary-Path $dirs[0].FullName $true
  $sid=$dirs[0].Name.Substring(5)
  $marker=Ordinary-Path (Join-Path $dir '.digital-tape-diagnostic-session') $false
  if ((Get-Item -LiteralPath $marker).Length -gt 65536) { throw 'Live marker bound exceeded' }
  $m=Get-Content -LiteralPath $marker -Raw | ConvertFrom-Json
  if ($m.schema -ne 1 -or $m.session -cne $sid) { throw 'Session marker mismatch' }
  $path=Ordinary-Path (Join-Path $dir 'records.jsonl') $false
  $f=[IO.File]::Open($path,[IO.FileMode]::Open,[IO.FileAccess]::Read,[IO.FileShare]::ReadWrite)
  try {
    $length=$f.Length;if ($length -gt 16777216) { throw 'Live record bound exceeded' }
    $b=[byte[]]::new([int]$length);$at=0
    while ($at -lt $b.Length) { $n=$f.Read($b,$at,$b.Length-$at);if ($n -eq 0) { break };$at+=$n }
  } finally { $f.Dispose() }
  $end=$at;while ($end -gt 0 -and $b[$end-1] -ne 10) { $end-- }
  if ($at-$end -gt 65536) { throw 'Live partial line bound exceeded' }
  # A live last line may be torn, including inside UTF8: decode only complete lines.
  $text=[Text.UTF8Encoding]::new($false,$true).GetString($b,0,$end)
  $rows=@();foreach ($line in ($text -split "`n")) {
    if ($line.Length -eq 0) { continue }
    if ([Text.Encoding]::UTF8.GetByteCount($line)+1 -gt 65536) { throw 'Live line bound exceeded' }
    $rows+=@($line | ConvertFrom-Json)
  }
  $count=Get-TerminalCount $rows $sid $AppPid $AppPath $AppHash $StartNs
  $declared=@($rows|Where-Object {$_.kind -ceq 'cards-admit' -and $_.data.job_dir}|ForEach-Object {[string]$_.data.job_dir})
  return [pscustomobject]@{dir=$dir;session=$sid;terminal_count=$count;declared_jobs=$declared;complete_lines=$rows.Count;partial_tail=($end -lt $at);stopped=(@($rows|Where-Object {$_.kind -ceq 'incomplete'}).Count -gt 0)}
}
function Retain-Session([string]$Control,[string]$Out) {
  if (!(Test-Path -LiteralPath $Control)) { throw 'No diagnostic originals to retain' }
  [void](Ordinary-Path $Control $true)
  $dirs=@(Get-ChildItem -LiteralPath $Control -Force)
  if ($dirs.Count -ne 1 -or !$dirs[0].PSIsContainer -or $dirs[0].Name -cnotmatch '^diag-[0-9a-f]{32}$') { throw 'Ambiguous diagnostic roots; originals left untouched' }
  $dir=Ordinary-Path $dirs[0].FullName $true
  $marker=Ordinary-Path (Join-Path $dir '.digital-tape-diagnostic-session') $false
  if ((Get-Item -LiteralPath $marker).Length -gt 65536) { throw 'Marker too large' }
  $owner=Get-Content -LiteralPath $marker -Raw | ConvertFrom-Json
  if ($owner.schema -ne 1 -or $owner.session -cne $dirs[0].Name.Substring(5)) { throw 'Foreign session marker' }
  [void](Ordinary-Path ([IO.Path]::GetDirectoryName([IO.Path]::GetFullPath($Out))) $true)
  if ($Out.StartsWith('\\') -or $Out.Substring(2).Contains(':')) { throw 'Nonordinary retention output' }
  if (Test-Path -LiteralPath $Out) { throw 'Retention output exists; no overwrite' }
  [void](New-Item -ItemType Directory -Path $Out -ErrorAction Stop)
  $top=@(Get-ChildItem -LiteralPath $dir -Force)
  $items=@();foreach ($item in $top) {
    [void](Ordinary-Path $item.FullName $item.PSIsContainer)
    if ($item.PSIsContainer) {
      if ($item.Name -cne 'blobs') { throw 'Unexpected session directory' }
      $items+=@(Get-ChildItem -LiteralPath $item.FullName -Force)
    } else { $items+=@($item) }
  }
  $leaves=@();foreach ($item in $items) {
    $relative=$item.FullName.Substring($dir.Length+1).Replace('\','/')
    [void](Ordinary-Path $item.FullName $item.PSIsContainer)
    if ($item.PSIsContainer) { throw 'Unexpected nested session directory' }
    if ($relative -notin @('.digital-tape-diagnostic-session','records.jsonl') -and $relative -cnotmatch '^blobs/[0-9]{8}-(report|stdout|stderr|manifest)\.bin$') { throw 'Unexpected session file' }
    $leaves+=@(@{name=$relative;path=$item.FullName;bytes=$item.Length})
  }
  # Every directory is checked before listing its immediate children; never recurse.
  if (@($leaves | Where-Object {$_.name -ceq 'records.jsonl'}).Count -ne 1) { throw 'Missing original records' }
  [long]$total=0;foreach ($leaf in $leaves) { $total += [long]$leaf.bytes }
  if ($total -gt 16777216) { throw 'Session exceeds declared bound; originals retained in place' }
  [void](New-Item -ItemType Directory -Path (Join-Path $Out 'blobs') -ErrorAction Stop)
  $manifest=@();foreach ($leaf in $leaves) {
    $dest=Join-Path $Out $leaf.name.Replace('/','\')
    $sourceStream=[IO.File]::Open($leaf.path,[IO.FileMode]::Open,[IO.FileAccess]::Read,[IO.FileShare]::Read)
    try {
      $destStream=[IO.File]::Open($dest,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
      try { $sourceStream.CopyTo($destStream) } finally { $destStream.Dispose() }
    } finally { $sourceStream.Dispose() }
    $before=(Get-FileHash -LiteralPath $leaf.path -Algorithm SHA256).Hash.ToLowerInvariant()
    $after=(Get-FileHash -LiteralPath $dest -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($before -cne $after) { throw 'Retention hash mismatch; originals left untouched' }
    $manifest+=@(@{name=$leaf.name;bytes=$leaf.bytes;sha256=$before})
  }
  return $manifest
}

function Get-PostJobs([string]$Jobs,$Declared) {
  if (!(Test-Path -LiteralPath $Jobs)) { return @{status='absent';entries=@();scope='no cleanup-history claim'} }
  $full=Ordinary-Path $Jobs $true
  $entries=@();$unknown=$false
  foreach ($item in @(Get-ChildItem -LiteralPath $full -Force)) {
    $bound=$item.FullName -iin $Declared
    $reparse=(($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)
    if (!$bound -or $reparse -or !$item.PSIsContainer) { $unknown=$true }
    # List only the direct job entry. Never inspect/remove an unbound child.
    $entries+=@(@{name=$item.Name;path=$item.FullName;receipt_bound=$bound;directory=$item.PSIsContainer;reparse=$reparse})
  }
  $status='empty';if ($entries.Count) { $status='bound-leftover';if ($unknown) { $status='unbound-leftover' } }
  return @{status=$status;entries=$entries;scope='first-party declared paths plus direct file status; no independent ownership/cleanup-history proof'}
}
