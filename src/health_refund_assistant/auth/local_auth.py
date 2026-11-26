"""Objetivo: autenticar usuários em ambiente local por usuário e PIN hash.

Entradas: identificador, PIN e arquivo local de usuários.
Processamento: gera hash PBKDF2 e compara de forma constante.
Saídas: usuário autorizado ou rejeição sem revelar se o usuário existe.
"""

import hashlib
import hmac
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any

from ..core.paths import USER_AUTH_PATH


USER_ID_PATTERN = re.compile(r"[a-zA-Z0-9_-]{3,32}")
PBKDF2_ITERATIONS = 120_000
DEFAULT_TEST_USER = "fernando-pimenta-quinino"
DEFAULT_TEST_NAME = "Fernando Pimenta Quinino"
DEFAULT_TEST_PIN = "123456"


def _normalize_user_id(user_id: str) -> str:
    """Normaliza e valida o identificador usado como nome de diretório."""
    normalized = user_id.strip().lower()
    if not USER_ID_PATTERN.fullmatch(normalized):
        raise ValueError("O usuário deve ter 3 a 32 caracteres alfanuméricos, _ ou -.")
    return normalized


def _load_users(path: Path) -> dict[str, Any]:
    """Lê o arquivo privado de usuários ou cria uma estrutura vazia."""
    if not path.exists():
        return {"schema_version": 1, "users": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError("Não foi possível carregar os usuários locais.") from error
    if not isinstance(data, dict) or not isinstance(data.get("users"), dict):
        raise ValueError("O arquivo de usuários locais é inválido.")
    return data


def _save_users(path: Path, data: dict[str, Any]) -> None:
    """Grava o arquivo de usuários com permissão restrita."""
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")


def add_local_user(
    user_id: str,
    pin: str,
    path: Path = USER_AUTH_PATH,
    display_name: str | None = None,
) -> str:
    """Cria ou atualiza um usuário local com PIN protegido por hash."""
    normalized = _normalize_user_id(user_id)
    if not re.fullmatch(r"[0-9]{4,8}", pin):
        raise ValueError("O PIN deve conter de 4 a 8 números.")
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", pin.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    data = _load_users(path)
    data["users"][normalized] = {
        "salt": salt.hex(),
        "pin_hash": digest.hex(),
        "iterations": PBKDF2_ITERATIONS,
        "display_name": display_name or normalized,
    }
    _save_users(path, data)
    return normalized


def validate_local_user(
    user_id: str,
    pin: str,
    path: Path = USER_AUTH_PATH,
) -> str | None:
    """Valida usuário sem informar se o identificador existe."""
    try:
        normalized = _normalize_user_id(user_id)
    except ValueError:
        return None
    if not re.fullmatch(r"[0-9]{4,8}", pin):
        return None
    data = _load_users(path)
    record = data["users"].get(normalized)
    if not isinstance(record, dict):
        return None
    try:
        salt = bytes.fromhex(record["salt"])
        iterations = int(record["iterations"])
        expected = bytes.fromhex(record["pin_hash"])
    except (KeyError, ValueError, TypeError):
        return None
    actual = hashlib.pbkdf2_hmac("sha256", pin.encode("utf-8"), salt, iterations)
    if not hmac.compare_digest(actual, expected):
        return None
    return normalized


def ensure_default_test_user(path: Path = USER_AUTH_PATH) -> str:
    """Cria o usuário sintético padrão se o arquivo local ainda não existir."""
    data = _load_users(path)
    if DEFAULT_TEST_USER not in data["users"]:
        add_local_user(
            DEFAULT_TEST_USER,
            DEFAULT_TEST_PIN,
            path,
            display_name=DEFAULT_TEST_NAME,
        )
    return DEFAULT_TEST_USER
