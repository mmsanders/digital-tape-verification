#!/usr/bin/env bash
set -euo pipefail
pkg=tests/wp16_ingest_r2
repo=mmsanders/Digital-Tape-Verification
tag=evidence-ingest1-r2-preflight2
asset=INGEST1-R2-PREFLIGHT2-SOURCES.tar.gz
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
if gh release view "$tag" --repo "$repo" >/dev/null 2>&1; then
  gh release download "$tag" --repo "$repo" --pattern "$asset" --dir "$work"
else
  python3 -B "$pkg/fixtures.py" "$work/generated" --seed "$pkg/encoded-seed.tar.gz"
  python3 -B "$pkg/asset.py" --build "$work/generated" --archive "$work/$asset"
  python3 -B "$pkg/asset.py" --archive "$work/$asset" --destination "$work/check"
  gh release create "$tag" "$work/$asset" --repo "$repo" --target "$GITHUB_SHA" --title 'INGEST-1 R2 independent preflight2 sources (not importable)' --notes-file "$pkg/ASSET-NOTES.md"
fi
# Durable download replay; local bootstrap alone does not establish availability.
python3 -B "$pkg/asset.py" --destination "$work/fetched"
