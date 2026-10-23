# Pure gate shared by the real recorder and causal observation controls.
function Test-OwnedWindow($Sample, [int]$OwnedPid, [long]$StartTicks) {
  return ($Sample.pid -eq $OwnedPid -and $Sample.start_ticks -eq $StartTicks -and
    $Sample.handle -ne 0 -and $Sample.title -ceq 'Digital Tape' -and
    $Sample.top_level -and $Sample.owner_handle -eq 0 -and $Sample.visible -and
    $Sample.responding -and !$Sample.ambiguous)
}
function Get-ReadyWindow($Samples, [int]$OwnedPid, [long]$StartTicks) {
  if ($Samples.Count -lt 3) { return $null }
  $tail=@($Samples | Select-Object -Last 3)
  $previous=$null
  foreach ($s in $tail) {
    if (!(Test-OwnedWindow $s $OwnedPid $StartTicks) -or $s.elapsed_ms -lt 0 -or $s.elapsed_ms -gt 20000) { return $null }
    if ($null -ne $previous) {
      $gap=$s.elapsed_ms-$previous.elapsed_ms
      if ($s.seq -ne $previous.seq+1 -or $gap -lt 250 -or $gap -gt 1500 -or $s.handle -ne $previous.handle) { return $null }
    }
    $previous=$s
  }
  if ($tail[2].elapsed_ms-$tail[0].elapsed_ms -lt 1000) { return $null }
  return $tail[2]
}
function Test-NormalQuit($Facts) {
  return ($Facts.native_window_ready -and $Facts.close_posted -and $Facts.graceful_exit -and
    !$Facts.forced_owned_cleanup -and $Facts.exit -eq 0 -and $Facts.capture_complete -and !$Facts.error -and !$Facts.capture_error)
}
