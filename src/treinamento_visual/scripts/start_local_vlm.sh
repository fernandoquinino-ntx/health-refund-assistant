#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT"

APPROVAL="json/training/visual/modelo_aprovado.json"
MODEL="models/gguf/smolvlm-256m-health-refund-Q4_K_M.gguf"
MMPROJ="models/gguf/smolvlm-256m-health-refund-mmproj.gguf"
LORA="models/gguf/smolvlm-256m-private-lora.gguf"
SERVER="tools/llama.cpp/build/bin/llama-server"

if [[ ! -f "$APPROVAL" ]]; then
  echo "Modelo local não ativado: aprovação inexistente." >&2
  exit 0
fi

python3 - <<PY
import json, sys
d=json.load(open("$APPROVAL"))
sys.exit(0 if d.get("aprovado") is True else 1)
PY
|| { echo "Modelo local não ativado: aprovação recusada." >&2; exit 0; }

if [[ ! -x "$SERVER" || ! -f "$MODEL" || ! -f "$MMPROJ" ]]; then
  echo "Modelo local não ativado: GGUF, mmproj ou servidor ausente." >&2
  exit 0
fi

SERVER_ARGS=(
  "$SERVER"
  --model "$MODEL" \
  --mmproj "$MMPROJ" \
  --host 127.0.0.1 \
  --port 8081
)
if [[ -f "$LORA" ]]; then
  SERVER_ARGS+=(--lora "$LORA")
fi
setsid -f "${SERVER_ARGS[@]}" >/tmp/health-refund-vlm.log 2>&1

echo "Servidor visual local iniciado em http://127.0.0.1:8081/v1"
