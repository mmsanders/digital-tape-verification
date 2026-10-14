#!/bin/sh
# Off-card collection only. No device paths, load, pulls or physical stage.
set -eu
srcdir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
startdir=$PWD
tapectl_source=${1:?Usage: sh rehearse-macos.sh /absolute/path/to/shipped/tapectl}
[ "$(uname -s)" = Darwin ] && [ "$(uname -m)" = arm64 ] || { echo 'STOP: needs native macOS arm64'; exit 2; }
major=$(sw_vers -productVersion | cut -d . -f 1)
[ "$major" -ge 26 ] || { echo 'STOP: needs macOS 26 or later'; exit 2; }
for tool in zip sudo shasum; do command -v "$tool" >/dev/null || { echo "STOP: missing $tool"; exit 2; }; done
[ -f "$tapectl_source" ] && [ -x "$tapectl_source" ] || { echo 'STOP: executable source file required'; exit 2; }
check_hash() {
  actual=$(shasum -a 256 "$1" | awk '{print $1}')
  [ "$actual" = "$2" ] || { echo "STOP: hash mismatch: $1"; exit 2; }
}
check_hash "$tapectl_source" e7550d8bedbb0c784fd528c387a87cca2bad8d1b411c39217d25377329bb0beb
check_hash "$srcdir/a6check.py" 227ceed2f1ca8817447c4103983c72b16a060b1d3323de22c805289b621bd1ef
check_hash "$srcdir/a6-macos.d" c9764f11f7894fbe57dc08b0fb6248e70ce244b2f6137a9ee59d057397af7be8
free_kib=$(df -Pk . | awk 'END {print $4}')
[ "$free_kib" -ge 6291456 ] || { echo 'STOP: need 6 GiB free in the current folder'; exit 2; }
run=$(mktemp -d "$startdir/a6-rh-mac.XXXXXX")
finish() {
  status=$?
  trap - EXIT
  cd "$startdir"
  name=${run##*/}
  if zip -q -r "$run.zip" "$name" -x "$name/rehearsal.img"; then
    echo "Evidence: $run.zip"
  else
    echo "Zip failed; keep and send the logs in: $run"
  fi
  echo 'STOP here and send evidence to Verification. No card stage is authorized by this script.'
  echo "The disposable image remains at: $run/rehearsal.img"
  exit "$status"
}
trap finish EXIT
cp "$tapectl_source" "$run/tapectl"
cp "$srcdir/a6check.py" "$srcdir/a6-macos.d" "$run/"
cd "$run"
check_hash ./tapectl e7550d8bedbb0c784fd528c387a87cca2bad8d1b411c39217d25377329bb0beb
check_hash ./a6check.py 227ceed2f1ca8817447c4103983c72b16a060b1d3323de22c805289b621bd1ef
check_hash ./a6-macos.d c9764f11f7894fbe57dc08b0fb6248e70ce244b2f6137a9ee59d057397af7be8
{ sw_vers; uname -a; csrutil status; } > versions.txt 2>&1
df -Pk . > space.txt
shasum -a 256 tapectl a6check.py a6-macos.d > hashes-before.txt
if ./tapectl provision rehearsal.img --label A6-REHEARSAL --uuid 00112233445566778899aabbccddeeff --epoch 1760000000 --image-bytes 4296015872 > provision-out.txt 2> provision-err.txt; then
  echo 0 > provision-exit.txt
else
  result=$?; echo "$result" > provision-exit.txt; exit "$result"
fi
stat -f '%z' rehearsal.img > geometry.txt
[ "$(cat geometry.txt)" = 4296015872 ] || { echo 'STOP: unexpected image size'; exit 2; }
{ ls -ls rehearsal.img; du -k rehearsal.img; } > allocation.txt
if sudo /usr/sbin/dtrace -q -s a6-macos.d -o verify.trace -c './tapectl verify rehearsal.img' > verify-out.txt 2> dtrace-err.txt; then
  tracer_status=0
else
  tracer_status=$?
fi
echo "dtrace $tracer_status" > tracer-exits.txt
shasum -a 256 tapectl a6check.py a6-macos.d > hashes-after.txt
cmp hashes-before.txt hashes-after.txt || { echo 'STOP: source changed during collection'; exit 2; }
[ "$tracer_status" -eq 0 ] || exit "$tracer_status"
pid=$(awk '$1=="A6" && $2=="trace" && $3=="tool=dtrace" && $4 ~ /^target=[0-9]+$/ {split($4,a,"="); p=a[2]; n++} END {if(n==1) print p; else exit 2}' verify.trace)
echo "$pid" > verify-pid.txt
if ! command -v python3 >/dev/null; then
  echo 'Local checker not run: Python3 unavailable. Send raw evidence for independent review.' > checker-not-run.txt
  exit 0
fi
python3 --version > python-version.txt 2>&1
if python3 a6check.py --format dtrace --trace verify.trace --pid "$pid" --capacity 4296015872 --geometry geometry.txt --target rehearsal.img --exe tapectl --sha256 e7550d8bedbb0c784fd528c387a87cca2bad8d1b411c39217d25377329bb0beb --stdout verify-out.txt --diagnostics dtrace-err.txt --tracer-log tracer-exits.txt > checker.json 2> checker-err.txt; then
  echo 0 > checker-exit.txt
else
  result=$?; echo "$result" > checker-exit.txt; exit "$result"
fi
