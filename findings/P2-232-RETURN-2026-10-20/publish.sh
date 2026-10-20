#!/usr/bin/env bash
set -euo pipefail
out=/tmp/verification232
mkdir -p "$out"
python3 -B findings/P2-232-RETURN-2026-10-20/selftest.py
python3 -B findings/P2-232-RETURN-2026-10-20/replay.py --fetch --archive "$out/software485-exact-shipping-return.zip" --out "$out/RESULT.json"
cmp "$out/RESULT.json" findings/P2-232-RETURN-2026-10-20/RESULT.json
python3 -B findings/P2-232-RETURN-2026-10-20/fetch_sources.py --archive "$out/software485-exact-shipping-return.zip" --out "$out/source"
python3 -c "import shutil;shutil.make_archive('/tmp/verification232/source232-reviewed','zip','/tmp/verification232/source')"
cp "$out/source/SOURCE-PINS.json" "$out/SOURCE-PINS.json"
cp findings/P2-232-RETURN-2026-10-20/AUTHORITY.json "$out/AUTHORITY.json"
cd "$out"
sha256sum software485-exact-shipping-return.zip source232-reviewed.zip RESULT.json SOURCE-PINS.json AUTHORITY.json > SHA256SUMS
tag="evidence-232-disposition-$SOURCE_HEAD"
gh release create "$tag" --repo "$GITHUB_REPOSITORY" --target "$SOURCE_HEAD" --title "Verification232 exact shipping and S1 bounded disposition" --notes "Original approved Software485 archive retained unchanged; independent raw/import replay and pinned reviewed source bytes. Exact recorded Windows11 shipping result only. INTERNAL/global JOINED_PEAK unproved; all wider holds remain." software485-exact-shipping-return.zip source232-reviewed.zip RESULT.json SOURCE-PINS.json AUTHORITY.json SHA256SUMS
mkdir fetched
gh release download "$tag" --repo "$GITHUB_REPOSITORY" --dir fetched
(cd fetched && sha256sum -c SHA256SUMS)
for f in software485-exact-shipping-return.zip source232-reviewed.zip RESULT.json SOURCE-PINS.json AUTHORITY.json SHA256SUMS; do cmp "$f" "fetched/$f"; done
