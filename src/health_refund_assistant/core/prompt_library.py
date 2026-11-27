"""Objetivo: disponibilizar prompts versionados às tarefas de IA.

Entradas: componente e versão solicitada.
Processamento: localiza e lê arquivos Markdown da biblioteca.
Saídas: versões disponíveis, conteúdo selecionado ou erro de localização.
"""

import re
import json
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
    texto = path.read_text(encoding="utf-8").strip()
    componentes_estruturados = {
        ("agente_conversacional", "v1.0"),
        ("agente_conversacional", "v1.1"),
        ("reembolso_assistente", "v1.2"),
        ("reembolso_status", "v1.2"),
        ("revisao_documental", "v1.1"),
        ("estimativa_pagamento", "v1.0"),
        ("vlm_extractor", "v4.2"),
        ("avaliacao_visual", "v1.0"),
    }
    if (component, versao) in componentes_estruturados and not validar_prompt_padrao(texto):
        raise ValueError(
            f"Prompt não segue o padrão Tarefa/Entrada/Saída/Guardrails: {path}"
        )
    return texto, versao


def analisar_secoes_prompt(texto: str) -> dict[str, str]:
    """Separa um prompt versionado nas seções markdown simples."""
    secoes: dict[str, str] = {}
    secoes_abertas: list[str] = []
    atual: list[str] = []
    for linha in texto.splitlines():
        if linha.startswith("# Tarefa"):
            titulo = linha.removeprefix("# Tarefa").strip(" :")
            secoes["Tarefa"] = titulo
            secoes_abertas = ["Tarefa"]
            atual = secoes_abertas
        elif linha.startswith("## Entrada esperada"):
            secoes["Entrada esperada"] = ""
            secoes_abertas = ["Entrada esperada"]
            atual = secoes_abertas
        elif linha.startswith("## Saída esperada"):
            secoes["Saída esperada"] = ""
            secoes_abertas = ["Saída esperada"]
            atual = secoes_abertas
        elif linha.startswith("## Guardrails"):
            secoes["Guardrails"] = ""
            secoes_abertas = ["Guardrails"]
            atual = secoes_abertas
        elif atual:
            nome = atual[0]
            secoes[nome] = (secoes[nome] + ("\n" if secoes[nome] else "") + linha).strip()
    return secoes


def validar_prompt_padrao(texto: str) -> bool:
    """Confere somente os quatro blocos usados pelos prompts ativos."""
    secoes = analisar_secoes_prompt(texto)
    return all(nome in secoes and secoes[nome].strip() for nome in (
        "Tarefa",
        "Entrada esperada",
        "Saída esperada",
        "Guardrails",
    ))


def carregar_respostas_agente(versao: str = "v1.1") -> dict[str, str]:
    """Carrega respostas versionadas embutidas no prompt do agente."""
    prompt, _ = carregar_prompt("agente_conversacional", versao)
    matches = re.findall(r"```json\s*(\{.*?\})\s*```", prompt, flags=re.DOTALL)
    if not matches:
        raise ValueError("O prompt do agente não contém o catálogo JSON de respostas.")
    respostas = json.loads(matches[-1])
    if not isinstance(respostas, dict) or not respostas:
        raise ValueError("O catálogo de respostas do agente é inválido.")
    return respostas
