"""Objetivo: verificar a memória local da conversa.

Entradas: mensagens e arquivos temporários de teste.
Processamento: exercita gravação, leitura, validação e remoção do estado.
Saídas: asserções de sucesso ou falha para o runner de testes.
"""

import tempfile
import unittest
from pathlib import Path

from health_refund_assistant.conversation.conversation_memory import (
    MAX_MESSAGES,
    clear_conversation,
    load_conversation,
    save_conversation,
)


class ConversationMemoryTests(unittest.TestCase):
    def test_persistence_limit_and_clear(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "conversa.json"
            messages = [
                {"role": "user", "content": str(i)}
                for i in range(MAX_MESSAGES + 2)
            ]
            evidence = {"documento": {"valor_total": 100}, "conciliacao": {}}
            save_conversation(messages, evidence, path)
            loaded = load_conversation(path)
            self.assertEqual(loaded["messages"], messages[-MAX_MESSAGES:])
            self.assertEqual(loaded["evidence"], evidence)
            self.assertEqual(path.stat().st_mode & 0o077, 0)
            clear_conversation(path)
            self.assertEqual(load_conversation(path), {"messages": [], "evidence": None})

    def test_corrupted_memory_is_not_silently_discarded(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "conversa.json"
            path.write_text("{", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "memória local"):
                load_conversation(path)
            self.assertTrue(path.exists())

    def test_invalid_evidence_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "conversa.json"
            path.write_text('{"messages": [], "evidence": {}}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "formato inválido"):
                load_conversation(path)
