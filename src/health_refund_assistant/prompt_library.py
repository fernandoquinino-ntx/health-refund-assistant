"""Localiza e carrega versões de prompts Markdown."""

import re
from pathlib import Path

from .paths import PROMPTS_DIR


def prompt_versions(directory: Path) -> list[str]:
    versions = [
        path.stem
        for path in directory.glob("*.md")
        if re.fullmatch(r"v\d+\.\d+", path.stem)
    ]
    return sorted(versions, key=lambda version: tuple(map(int, version[1:].split("."))))


def carregar_prompt(component: str, versao: str | None = None) -> tuple[str, str]:
    if not re.fullmatch(r"[a-z][a-z0-9_]*", component):
        raise ValueError("Componente de prompt inválido.")
    directory = PROMPTS_DIR / component
    if not directory.is_dir():
        raise FileNotFoundError(f"Biblioteca de prompts não encontrada: {directory}")
    if versao is None:
        versions = prompt_versions(directory)
        if not versions:
            raise FileNotFoundError(f"Nenhum prompt versionado encontrado em {directory}")
        versao = versions[-1]
    if not re.fullmatch(r"v\d+\.\d+", versao):
        raise ValueError("Versão de prompt inválida.")
    path = directory / f"{versao}.md"
    if not path.is_file():
        raise FileNotFoundError(f"Prompt não encontrado: {path}")
    return path.read_text(encoding="utf-8").strip(), versao
