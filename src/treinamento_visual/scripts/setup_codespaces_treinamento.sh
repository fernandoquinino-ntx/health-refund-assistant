#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT"

python -m venv .venv
.venv/bin/python -m pip install -r requirements/base.txt

python -m venv .venv-treinamento
.venv-treinamento/bin/python -m pip install -r requirements/treinamento.txt

mkdir -p models
if [[ ! -f models/base-smol/config.json ]]; then
  .venv-treinamento/bin/python - <<'PY'
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id="mlx-community/SmolVLM-Instruct-4bit",
    local_dir="models/base-smol",
    local_dir_use_symlinks=False,
)
PY
fi

if [[ ! -x .venv-conversao/bin/python ]]; then
  python -m venv .venv-conversao
  .venv-conversao/bin/python -m pip install -r requirements/conversao.txt
fi

if [[ ! -d tools/llama.cpp/.git ]]; then
  mkdir -p tools
  git clone --depth 1 https://github.com/ggerganov/llama.cpp tools/llama.cpp
fi

if [[ ! -f tools/llama.cpp/build/bin/llama-cli ]]; then
  cmake -S tools/llama.cpp -B tools/llama.cpp/build -DLLAMA_CURL=OFF -DGGML_NATIVE=OFF
  cmake --build tools/llama.cpp/build -j"$(nproc)"
fi
