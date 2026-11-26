#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

FUSED="models/smolvlm-fused"
GGUF="models/gguf"

mkdir -p "$GGUF"

if [[ -d "$FUSED" ]]; then
  echo "Modelo fusionado já existe: $FUSED"
else
  PYTHONPATH=src .venv-treinamento/bin/python -m treinamento_visual.train.export_adapter
fi

SOURCE="models/smolvlm-hf"
if [[ ! -f "$SOURCE/config.json" ]]; then
  .venv-treinamento/bin/python - <<'PY'
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id="HuggingFaceTB/SmolVLM-Instruct",
    local_dir="models/smolvlm-hf",
    local_dir_use_symlinks=False,
)
PY
fi

PYTHONPATH=tools/llama.cpp .venv-conversao/bin/python tools/llama.cpp/convert_hf_to_gguf.py \
  "$SOURCE" \
  --outfile "$GGUF/smolvlm-base-f16.gguf" \
  --outtype f16 \
  --model-name "smolvlm-health-refund-base"

PYTHONPATH=tools/llama.cpp .venv-conversao/bin/python tools/llama.cpp/convert_hf_to_gguf.py \
  "$SOURCE" \
  --outfile "$GGUF/smolvlm-base-mmproj.gguf" \
  --mmproj
