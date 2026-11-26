#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT"

if [[ ! -x .venv/bin/python ]]; then
  bash src/treinamento_visual/scripts/setup_codespaces_treinamento.sh
fi

if [[ -f json/training/visual/modelo_aprovado.json ]] &&
   python3 -c 'import json; raise SystemExit(0 if json.load(open("json/training/visual/modelo_aprovado.json")).get("aprovado") is True else 1)' &&
   [[ -f models/gguf/smolvlm-256m-health-refund-Q4_K_M.gguf ]]; then
  bash src/treinamento_visual/scripts/start_local_vlm.sh
  export LOCAL_VLM_BASE_URL="http://127.0.0.1:8081/v1"
  export LOCAL_VLM_MODEL="smolvlm-health-refund"
fi

setsid -f env PYTHONPATH=src \
  STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
  .venv/bin/python -m streamlit run app.py \
  --server.address 0.0.0.0 \
  --server.port 8501 \
  --server.headless true \
  >/tmp/health-refund-assistant.log 2>&1
