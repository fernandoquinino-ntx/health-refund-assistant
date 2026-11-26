"""Objetivo: verificar autenticação local, isolamento e rastreamento privado.

Entradas: usuários, PINs e eventos sintéticos temporários.
Processamento: cria hashes, valida sessões e grava JSONL por usuário.
Saídas: asserções sobre autorização, segregação e trilha auditável.
"""

import tempfile
import unittest
from pathlib import Path

from health_refund_assistant.auth.local_auth import add_local_user, validate_local_user
from health_refund_assistant.core.trace import append_trace_event, load_trace_events


class LocalAuthTraceTests(unittest.TestCase):
    def test_pin_correto_autoriza_pin_incorreto_rejeita(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "usuarios.json"
            add_local_user("Fernando", "1234", path)
            self.assertEqual(validate_local_user("fernando", "1234", path), "fernando")
            self.assertIsNone(validate_local_user("fernando", "9999", path))
            self.assertIsNone(validate_local_user("desconhecido", "1234", path))

    def test_isolamento_por_usuario_nao_expoe_eventos(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            append_trace_event(
                "fernando",
                {"task": "consultar_status", "input_hash": "abc"},
                base,
            )
            append_trace_event(
                "maria",
                {"task": "confirmar_pagamento", "input_hash": "def"},
                base,
            )
            fernando = load_trace_events("fernando", base)
            maria = load_trace_events("maria", base)
            self.assertEqual(len(fernando), 1)
            self.assertEqual(len(maria), 1)
            self.assertEqual(fernando[0]["task"], "consultar_status")
            self.assertEqual(maria[0]["task"], "confirmar_pagamento")
            self.assertNotEqual(fernando[0]["event_id"], maria[0]["event_id"])


if __name__ == "__main__":
    unittest.main()
