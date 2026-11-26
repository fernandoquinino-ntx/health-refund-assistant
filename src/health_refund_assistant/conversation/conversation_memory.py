"""Memória local de uma conversa para uso individual e privado."""

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from ..core.paths import CONVERSATION_STATE_PATH
from ..core.json_contracts import validar_contrato_json


MAX_MESSAGES = 50


def load_conversation(path: Path = CONVERSATION_STATE_PATH) -> dict[str, Any]:
    if not path.exists():
        return {"messages": [], "evidence": None}
    try:
        with path.open(encoding="utf-8") as file:
            data = json.load(file)
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Não foi possível carregar a memória local: {error}") from error
    if (
        not isinstance(data, dict)
        or not isinstance(data.get("messages"), list)
        or not all(
            isinstance(message, dict)
            and message.get("role") in ("user", "assistant")
            and isinstance(message.get("content"), str)
            for message in data["messages"]
        )
        or not (
            data.get("evidence") is None
            or (
                isinstance(data.get("evidence"), dict)
                and isinstance(data["evidence"].get("documento"), dict)
                and isinstance(data["evidence"].get("conciliacao"), dict)
            )
        )
    ):
        raise ValueError("A memória local tem formato inválido; não foi carregada.")
    if data["evidence"] and "revisao_ia" in data["evidence"]:
        validar_contrato_json(
            data["evidence"]["revisao_ia"], "document_review.schema.json", "memória local"
        )
    return data


def save_conversation(
    messages: list[dict[str, str]],
    evidence: dict[str, Any] | None,
    path: Path = CONVERSATION_STATE_PATH,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, delete=False
        ) as file:
            temporary_path = Path(file.name)
            json.dump(
                {"messages": messages[-MAX_MESSAGES:], "evidence": evidence},
                file,
                ensure_ascii=False,
            )
        os.replace(temporary_path, path)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def clear_conversation(path: Path = CONVERSATION_STATE_PATH) -> None:
    path.unlink(missing_ok=True)
