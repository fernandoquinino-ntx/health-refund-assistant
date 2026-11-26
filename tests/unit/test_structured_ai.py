"""Testes dos contratos das tarefas de IA."""

import json
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from health_refund_assistant.conversation.structured_ai import request_structured_json


class StructuredAITests(unittest.TestCase):
    def test_valid_review_uses_strict_schema(self):
        data = {
            "situacao_documental": "nao_e_possivel_avaliar",
            "justificativa": "Data não identificada.",
            "campos_para_revisao": ["data_emissao"],
            "orientacoes": ["Solicite uma imagem legível."],
        }
        response = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(data)))])
        with (
            patch.dict(os.environ, {"OPENAPI_TOKEN": "test-token"}),
            patch("health_refund_assistant.conversation.structured_ai.OpenAI") as client,
        ):
            client.return_value.chat.completions.create.return_value = response
            result = request_structured_json("Revisar", "entrada", "document_review.schema.json")
        self.assertEqual(result, data)
        call = client.return_value.chat.completions.create.call_args.kwargs
        self.assertTrue(call["response_format"]["json_schema"]["strict"])

    def test_invalid_review_is_rejected(self):
        data = {
            "situacao_documental": "aprovado",
            "justificativa": "OK",
            "campos_para_revisao": [],
            "orientacoes": [],
        }
        response = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(data)))])
        with (
            patch.dict(os.environ, {"OPENAPI_TOKEN": "test-token"}),
            patch("health_refund_assistant.conversation.structured_ai.OpenAI") as client,
        ):
            client.return_value.chat.completions.create.return_value = response
            with self.assertRaisesRegex(ValueError, "JSON incompatível"):
                request_structured_json("Revisar", "entrada", "document_review.schema.json")

    def test_refusal_does_not_produce_a_success_result(self):
        response = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=None))])
        with (
            patch.dict(os.environ, {"OPENAPI_TOKEN": "test-token"}),
            patch("health_refund_assistant.conversation.structured_ai.OpenAI") as client,
        ):
            client.return_value.chat.completions.create.return_value = response
            with self.assertRaisesRegex(ValueError, "tarefa não concluída"):
                request_structured_json("Responder", "entrada", "assistant_answer.schema.json")
