"""Objetivo: verificar o catálogo central das tarefas do agente.

Entradas: arquivo JSON versionado de tarefas.
Processamento: carrega nomes, schemas e entradas mínimas.
Saídas: asserções sobre catálogo completo e categoria não mapeada.
"""

import unittest

from health_refund_assistant.conversation.task_registry import (
    get_task_definition,
    load_task_registry,
)


class TaskRegistryTests(unittest.TestCase):
    def test_catalog_contains_required_tasks_and_unknown_category(self):
        registry = load_task_registry()
        tasks = registry["tarefas"]
        self.assertTrue({
            "analisar_documento",
            "consultar_status",
            "confirmar_pagamento",
            "verificar_prazo",
            "revisar_completude",
            "categoria_nao_mapeada",
        }.issubset(tasks))

    def test_unknown_task_returns_safe_definition(self):
        definition = get_task_definition("qualquer_coisa")
        self.assertEqual(definition["deterministic_tools"], [])
        self.assertIn("pedido_esclarecimento", definition["allowed_outputs"])


if __name__ == "__main__":
    unittest.main()
