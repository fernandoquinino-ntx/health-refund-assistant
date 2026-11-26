#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT"

if [[ ! -x .venv/bin/python ]]; then
  bash src/treinamento_visual/scripts/setup_codespaces_treinamento.sh
fi

setsid -f env PYTHONPATH=src \
  STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
  .venv/bin/python -m streamlit run app.py \
  --server.address 0.0.0.0 \
  --server.port 8501 \
  --server.headless true \
  >/tmp/health-refund-assistant.log 2>&1
