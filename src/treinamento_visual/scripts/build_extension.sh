#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
SOURCE="$ROOT/src/extension"
OUTPUT="$ROOT/build/extension"

python3 -m json.tool "$SOURCE/manifest.json" >/dev/null
rm -rf "$OUTPUT"
mkdir -p "$OUTPUT"

cp "$SOURCE/manifest.json" "$OUTPUT/manifest.json"
cp "$SOURCE/10_popup/popup.html" "$OUTPUT/popup.html"
cp "$SOURCE/10_popup/popup.js" "$OUTPUT/popup.js"
cp "$SOURCE/20_background/background.js" "$OUTPUT/background.js"
cp "$SOURCE/30_content/bridge.js" "$OUTPUT/bridge.js"
cp "$SOURCE/40_collector/collector.js" "$OUTPUT/collector.js"
cp "$SOURCE/60_schemas/export.schema.json" "$OUTPUT/export.schema.json"

echo "Extensão construída em: $OUTPUT"
