# Pure controls shared by the parameterized recorder; never calls a native API.
function Get-TerminalCount($Rows,[string]$Session,[int]$AppPid,[string]$AppPath,[string]$AppHash,[decimal]$StartNs) {
  if ($Rows.Count -eq 0) { return 0 }
  $h=$Rows[0]
  if ($h.kind -cne 'session' -or $h.session -cne $Session -or $h.data.app_pid -ne $AppPid -or $h.data.app_path -ine $AppPath -or $h.data.app_sha256 -cne $AppHash -or [decimal]$h.data.app_os_start_ns -ne $StartNs) { throw 'Live session/parent identity mismatch' }
  if ($h.data.source_commit -cne 'fce1d644f03ed1220e40133be0c33bd30e519203') { throw 'Live source crosswalk mismatch' }
  if ($h.schema -ne 1 -or $h.seq -ne 0) { throw 'Bad header envelope' }
  if ($Rows.Count -eq 1) { return 0 }
  if ($Rows[1].kind -cne 'cards-contract' -or $Rows[1].data.cards_schema -ne 1) { throw 'Missing cards-1 contract' }
  $launch=@{};$terminal=@{};$admit=@{};$i=0
  foreach ($r in $Rows) {
    if ($r.schema -ne 1 -or $r.session -cne $Session -or $r.seq -ne $i) { throw 'Live envelope sequence/session mismatch' };$i++
    $k=[string]$r.kind;$d=$r.data
    if ($k -notin @('session','session-end','incomplete') -and !$k.StartsWith('cards-')) { throw 'Unexpected non-cards activity; stop session' }
    if ($k -ceq 'cards-admit') {
      if ($admit.ContainsKey([string]$d.run_id)) { throw 'Duplicate run admission' };$admit[[string]$d.run_id]=$d.ticket
    }
    if ($k -ceq 'cards-launch') {
      $id=[string]$d.run_id
      if (!$admit.ContainsKey($id) -or $admit[$id] -ne $d.ticket -or $launch.ContainsKey($id) -or $d.pid -le 0) { throw 'Unbound or duplicate launch' }
      $exe='C:\Users\mrtro\DigitalTape-618-kit\Digital-Tape\tapectl.exe'
      if ($d.exe -ine $exe -or $d.pin_sha256 -cne '44ef26869ba2d01a8a183660a2c7a050d0e7e9ff37c40b727131512739ea6ded' -or $d.exe_sha256_observed -cne $d.pin_sha256 -or $d.pin_version_label -cne 'tapectl-wp15-s2+f9306c2c5a42' -or @($d.argv).Count -ne 6 -or $d.argv[0] -ine $exe -or $d.argv[1] -cne 'cards') { throw 'Unexpected first-party child request; stop collection' }
      $launch[$id]=$d
    }
    if ($k -ceq 'cards-terminal') {
      $id=[string]$d.run_id
      if (!$launch.ContainsKey($id) -or $launch[$id].pid -ne $d.pid -or $launch[$id].ticket -ne $d.ticket -or $terminal.ContainsKey($id) -or $d.end -notin @('exited','timed_out','cancelled') -or $d.wait_kind -notin @('wait','try_wait-terminal')) { throw 'Unbound or duplicate terminal' }
      $terminal[$id]=$true
    }
  }
  # This count is only a FIRST-PARTY close trigger, never a complete-receipt verdict.
  return $terminal.Count
}
function Test-ManualConsent($Consent,[string]$CommandSha,[string]$Publication,[string]$MethodSha) {
  return ($Consent.human -ceq 'Michael' -and $Consent.route -ceq 'manual-software-resumption-existing-auto-mode' -and
    $Consent.permission_mode -ceq 'auto' -and $Consent.per_command_prompt -is [bool] -and $Consent.per_command_prompt -eq $false -and
    $Consent.command_sha256 -ceq $CommandSha -and $Consent.method_publication -ceq $Publication -and
    $Consent.method_sha256 -ceq $MethodSha -and $Consent.human_message_ref -and $Consent.human_message_text -and
    [DateTimeOffset]::Parse($Consent.manual_resumption_utc) -gt [DateTimeOffset]::Parse($Consent.publication_utc))
}
function Test-SessionBounds($Facts) {
  return ($Facts.native_window_ready -and $Facts.ready_elapsed_ms -ge 0 -and $Facts.ready_elapsed_ms -le 20000 -and $Facts.close_posted -and
    $Facts.close_elapsed_ms -ge $Facts.ready_elapsed_ms -and $Facts.close_elapsed_ms-$Facts.ready_elapsed_ms -le 15000 -and
    $Facts.close_elapsed_ms -le 60000 -and $Facts.graceful_exit -and !$Facts.forced_owned_cleanup -and
    $Facts.exit -eq 0 -and $Facts.capture_complete -and !$Facts.error -and !$Facts.capture_error -and !$Facts.collection_error -and !$Facts.retention_error -and !$Facts.cleanup_error -and
    $Facts.pid -gt 0 -and $Facts.normal_close_wait_ms -ge 0 -and $Facts.normal_close_wait_ms -le 10000 -and
    $Facts.normal_close_elapsed_ms -ge 0 -and $Facts.normal_close_elapsed_ms -le 10000 -and
    $Facts.final_elapsed_ms -ge $Facts.close_elapsed_ms -and $Facts.final_elapsed_ms -le 60000 -and
    $Facts.cleanup_elapsed_ms -ge 0 -and $Facts.cleanup_elapsed_ms -le 10000 -and
    $Facts.diagnostic_copy_complete -and $Facts.post_jobs_status -in @('empty','absent','bound-leftover') -and
    $Facts.parent_identity.image_path -ieq 'C:\Users\mrtro\DigitalTape-618-kit\Digital-Tape\digital-tape.exe' -and
    $Facts.parent_identity.os_start_ns -eq ([decimal]$Facts.process_start_ticks-[decimal]621355968000000000)*100 -and
    @($Facts.argv).Count -eq 2 -and $Facts.argv[0] -ieq $Facts.parent_identity.image_path -and $Facts.argv[1] -ceq '--diagnostic-receipts' -and
    $Facts.parent_identity.pid -eq $Facts.pid -and $Facts.parent_identity.start_ticks -eq $Facts.process_start_ticks -and
    $Facts.parent_identity.image_sha256 -ceq 'ccae0cf5098aed601fd17b4af1c0d62a33ad28dfb734add1c5df3a67df807c96')
}

# These pure deadline decisions are called by the generated recorder as well as tests.
function Get-WaitBudget([long]$Now,[long]$Deadline,[int]$Cap) {
  if ($Now -lt 0 -or $Deadline -lt 0 -or $Cap -lt 0) { throw 'Invalid clock budget' }
  return [int][Math]::Max(0,[Math]::Min([long]$Cap,$Deadline-$Now))
}
function Get-CloseDecision([long]$Ready,[long]$Now,[int]$Terminals,[bool]$Incomplete) {
  if ($Ready -lt 0 -or $Ready -gt 20000 -or $Now -lt $Ready -or $Terminals -lt 0) { throw 'Invalid readiness/time' }
  if ($Incomplete) { return 'incomplete' }
  if ($Terminals -ge 2) { return 'two-terminals' }
  if ($Now -ge [Math]::Min($Ready+15000,60000)) { return 'deadline' }
  return 'continue'
}
