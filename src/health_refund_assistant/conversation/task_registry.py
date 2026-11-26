"""Objetivo: centralizar tarefas reconhecidas pelo agente conversacional.

Entradas: nome da tarefa e texto livre do usuário.
Processamento: carrega o catálogo JSON e valida tarefas conhecidas.
Saídas: definição da tarefa ou erro para categoria inválida.
"""

import json
from pathlib import Path
from typing import Any

from ..core.paths import CONFIG_DIR


TASK_REGISTRY_PATH = CONFIG_DIR / "agent_tasks.json"


def load_task_registry(path: Path = TASK_REGISTRY_PATH) -> dict[str, Any]:
    """Carrega o catálogo único de tarefas e valida sua raiz."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError("Não foi possível carregar o catálogo de tarefas.") from error
    if not isinstance(data, dict) or not isinstance(data.get("tarefas"), dict):
        raise ValueError("O catálogo de tarefas não contém um objeto válido.")
    return data


def get_task_definition(task: str) -> dict[str, Any]:
    """Retorna a definição de uma tarefa conhecida ou da categoria não mapeada."""
    registry = load_task_registry()
    tasks = registry["tarefas"]
    if task in tasks:
        return tasks[task]
    return tasks["categoria_nao_mapeada"]
