#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT"

if ! python3 - <<'PY'
import json
d=json.load(open("json/training/visual/modelo_aprovado.json"))
raise SystemExit(0 if d.get("aprovado") is True else 1)
PY
then
  echo "Conversão bloqueada: adaptador não aprovado."
  exit 0
fi

GGUF="models/gguf"

mkdir -p "$GGUF"

SOURCE="models/smolvlm-hf"

if [[ ! -f "$SOURCE/config.json" ]]; then
  .venv-conversao/bin/python - <<'PY'
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id="HuggingFaceTB/SmolVLM-256M-Instruct",
    local_dir="models/smolvlm-hf",
    local_dir_use_symlinks=False,
)
PY
fi

PYTHONPATH=tools/llama.cpp .venv-conversao/bin/python tools/llama.cpp/convert_hf_to_gguf.py \
  "$SOURCE" \
  --outfile "$GGUF/smolvlm-256m-health-refund-f16.gguf" \
  --outtype f16 \
  --model-name "smolvlm-health-refund"

PYTHONPATH=tools/llama.cpp .venv-conversao/bin/python tools/llama.cpp/convert_hf_to_gguf.py \
  "$SOURCE" \
  --outfile "$GGUF/smolvlm-256m-health-refund-mmproj.gguf" \
  --mmproj

if [[ -f tools/llama.cpp/build/bin/llama-quantize ]]; then
  tools/llama.cpp/build/bin/llama-quantize \
    "$GGUF/smolvlm-256m-health-refund-f16.gguf" \
    "$GGUF/smolvlm-256m-health-refund-Q4_K_M.gguf" \
    Q4_K_M
fi

if [[ -d models/adapters/smolvlm_ci ]]; then
  PYTHONPATH=tools/llama.cpp .venv-conversao/bin/python tools/llama.cpp/convert_lora_to_gguf.py \
    models/adapters/smolvlm_ci \
    --base "$SOURCE" \
    --outfile "$GGUF/smolvlm-256m-private-lora.gguf" \
    --outtype f32
fi
