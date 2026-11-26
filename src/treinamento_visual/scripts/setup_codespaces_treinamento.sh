#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT"

python -m venv .venv
.venv/bin/python -m pip install -r requirements/base.txt

python -m venv .venv-treinamento
.venv-treinamento/bin/python -m pip install -r requirements/treinamento-ci.txt

mkdir -p models

.venv-treinamento/bin/python - <<'PY'
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id="HuggingFaceTB/SmolVLM-256M-Instruct",
    local_dir="models/smolvlm-hf",
    local_dir_use_symlinks=False,
)
PY

if [[ ! -x .venv-conversao/bin/python ]]; then
  python -m venv .venv-conversao
  .venv-conversao/bin/python -m pip install -r requirements/conversao.txt
fi

if [[ ! -d tools/llama.cpp/.git ]]; then
  mkdir -p tools
  git clone --depth 1 https://github.com/ggerganov/llama.cpp tools/llama.cpp
fi
git -C tools/llama.cpp checkout --detach a8ad690ca9239ea35db4de47e00cf632d01895fd

if [[ ! -f tools/llama.cpp/build/bin/llama-cli ]]; then
  cmake -S tools/llama.cpp -B tools/llama.cpp/build -DLLAMA_CURL=OFF -DGGML_NATIVE=OFF
  cmake --build tools/llama.cpp/build -j"$(nproc)"
fi
