"""Objetivo: registrar trilhas auditáveis de interações do agente.

Entradas: usuário validado, tarefa, versões de prompt, anexos e saída.
Processamento: cria IDs, hashes e JSONL privado por usuário.
Saídas: evento persistido ou leitura de eventos locais.
"""

import hashlib
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from .paths import TRACE_LOG_DIR


def text_hash(text: str) -> str:
    """Gera hash SHA-256 para entrada ou saída sem armazenar texto bruto."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def trace_log_path(user_id: str) -> Path:
    """Resolve o arquivo JSONL privado de um usuário."""
    return TRACE_LOG_DIR / user_id / "eventos.jsonl"


def append_trace_event(
    user_id: str,
    event: dict[str, Any],
    base_dir: Path = TRACE_LOG_DIR,
) -> dict[str, Any]:
    """Append de evento JSONL com tipo e timestamp padronizados."""
    from ..auth.local_auth import _normalize_user_id

    normalized = _normalize_user_id(user_id)
    path = base_dir / normalized / "eventos.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **event,
    }
    descriptor = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
    with os.fdopen(descriptor, "a", encoding="utf-8") as file:
        file.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record


def load_trace_events(
    user_id: str,
    base_dir: Path = TRACE_LOG_DIR,
) -> list[dict[str, Any]]:
    """Lê os eventos locais de um usuário."""
    path = base_dir / user_id / "eventos.jsonl"
    if not path.exists():
        return []
    events: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(event, dict):
                events.append(event)
    return events
