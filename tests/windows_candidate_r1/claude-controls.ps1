$ErrorActionPreference='Stop'
# Pure synthetic receipt judgments. Never invoke Start-App, context.py or C# APIs.
$temp=Join-Path ([IO.Path]::GetTempPath()) ('synthetic307claude-'+[Guid]::NewGuid().ToString('N'))
[void][IO.Directory]::CreateDirectory($temp)
try {
  $prep=Join-Path $temp 'prepared'
  $env:CLAUDE_PREP=$prep
  python -B -c "import sys,pathlib;sys.path.insert(0,sys.argv[1]);import claude,prepare;p=pathlib.Path(sys.argv[2]);p.mkdir();[(p/n).write_bytes(b) for n,b in claude.prepared(prepare.fixture(),'2'*64).items()]" $PSScriptRoot $prep
  if ($LASTEXITCODE -ne 0) { throw 'Synthetic preparation failed' }
  # Run the exact inherited control corpus with only route/Python/path attribution updated.
  $source=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'controls.ps1') -Raw
  $source=$source.Replace(". (Join-Path `$PSScriptRoot '../windows_app_start_r2/window_gate.ps1')", ". (Join-Path '$prep' 'window_gate.ps1')")
  $source=$source.Replace("(Join-Path `$PSScriptRoot 'judge.ps1')", "(Join-Path '$prep' 'judge.ps1')")
  $source=$source.Replace('approved-exec-command-require-escalated','approved-claude-code-exact-command')
  $source=$source.Replace("`$good=@{", "`$good=@{tool_route='approved-claude-code-exact-command';python_path='C:\Program Files\Inkscape\bin\python.exe';python_sha256='fbaff2f38852ac61c5767a91d5efbd4d893fb8ca985a9fdc76cf6d88fb93a745';")
  $source=$source.Replace('context=@{', "context=@{python_executable='C:\Program Files\Inkscape\bin\python.exe';")
  $source=$source.Replace("`$mutations=@(", "`$mutations=@(@{key='tool_route';value='approved-exec-command-require-escalated'},@{key='python_sha256';value=('0'*64)},@{key='python_path';value='C:\other.exe'},")
  & ([scriptblock]::Create($source))
  'PASS Claude exact-route/Python negative controls plus inherited gate corpus; ZERO Product/Win32 calls'
} finally {
  foreach ($n in @('Start-App.ps1','context.py','judge.ps1','WindowNative.cs','window_gate.ps1')) {
    $file=Join-Path (Join-Path $temp 'prepared') $n
    if(Test-Path -LiteralPath $file){Remove-Item -LiteralPath $file}
  }
  $dir=Join-Path $temp 'prepared'
  if(Test-Path -LiteralPath $dir){[IO.Directory]::Delete($dir,$false)}
  [IO.Directory]::Delete($temp,$false)
}
