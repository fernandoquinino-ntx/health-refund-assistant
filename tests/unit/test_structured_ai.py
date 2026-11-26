"""Testes dos contratos das tarefas de IA."""

import json
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from health_refund_assistant.conversation.structured_ai import request_structured_json
from health_refund_assistant.core.json_contracts import carregar_schema_json


class StructuredAITests(unittest.TestCase):
    def test_each_task_sends_its_prompt_and_registered_schema(self):
        examples = (
            ("document_review.schema.json", {
                "situacao_documental": "revisao_necessaria",
                "justificativa": "Revisar.",
                "campos_para_revisao": [],
                "orientacoes": [],
            }),
            ("assistant_answer.schema.json", {"resposta": "Resposta."}),
            ("payment_estimate.schema.json", {
                "data_submissao": "2026-03-20", "data_referencia": "2026-03-20",
                "data_estimada": "2026-03-27", "dias_uteis_restantes": 5,
                "dias_uteis_atraso": 0, "situacao": "dentro_do_prazo",
            }),
        )
        for schema_name, data in examples:
            with (
                self.subTest(schema=schema_name),
                patch.dict(os.environ, {"OPENAPI_TOKEN": "test-token"}),
                patch("health_refund_assistant.conversation.structured_ai.OpenAI") as client,
            ):
                client.return_value.chat.completions.create.return_value = SimpleNamespace(
                    choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(data)))]
                )
                self.assertEqual(request_structured_json("Prompt da tarefa", "entrada", schema_name), data)
                call = client.return_value.chat.completions.create.call_args.kwargs
                system = call["messages"][0]["content"]
                self.assertIn("Prompt da tarefa", system)
                self.assertIn(json.dumps(carregar_schema_json(schema_name), ensure_ascii=False, indent=2), system)
                self.assertIn("Template JSON correspondente", system)
                self.assertEqual(call["messages"][1]["content"], "entrada")
                schema = carregar_schema_json(schema_name)
                self.assertEqual(
                    call["response_format"]["json_schema"]["schema"],
                    {key: schema[key] for key in ("type", "properties", "required", "additionalProperties")},
                )

    def test_missing_schema_stops_before_api_call(self):
        with (
            patch.dict(os.environ, {"OPENAPI_TOKEN": "test-token"}),
            patch("health_refund_assistant.conversation.structured_ai.OpenAI") as client,
        ):
            with self.assertRaisesRegex(ValueError, "Schema não encontrado"):
                request_structured_json("Revisar", "entrada", "inexistente.schema.json")
            client.assert_not_called()

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
