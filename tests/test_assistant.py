import os
import unittest
from datetime import date
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from health_refund_assistant import assistant
from health_refund_assistant.assessment import ExportPeriodError


class AssistantTests(unittest.TestCase):
    def test_assistant_uses_prompt_and_structured_evidence(self):
        response = SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content="O pedido está em análise.")
                )
            ]
        )
        with (
            patch.dict(os.environ, {"OPENAPI_TOKEN": "test-token"}),
            patch("health_refund_assistant.assistant.OpenAI") as openai_client,
        ):
            openai_client.return_value.chat.completions.create.return_value = response
            answer = assistant.create_assistant_answer(
                "Já foi pago?",
                {"documento": {"valor_total": 450.0}},
                "v1.0",
            )

        self.assertEqual(answer, "O pedido está em análise.")
        call = openai_client.return_value.chat.completions.create.call_args.kwargs
        self.assertIn("Não invente pedidos", call["messages"][0]["content"])
        self.assertIn('"valor_total": 450.0', call["messages"][1]["content"])

    def test_request_orchestrates_extraction_rules_and_response(self):
        extracted = {
            "prestador": "Clínica Sintética",
            "valor_total": 450.0,
            "_meta": {"status": "OK"},
        }
        assessment = {"situacao_pedido": "localizado"}
        request = assistant.AssistantRequest(
            pdf_bytes=b"%PDF-synthetic",
            question="O pedido foi pago?",
            export_paths=[Path("export.json")],
            extraction_prompt_version="v4.0",
            response_prompt_version="v1.0",
            reference_date=date(2026, 3, 20),
        )
        extractor = Mock()
        extractor.extrair_dados_nf_visual.return_value = extracted

        with (
            patch(
                "health_refund_assistant.assistant.load_selected_exports",
                return_value=[{"periodo": {}, "reembolsos": []}],
            ),
            patch(
                "health_refund_assistant.assistant.load_mapping",
                return_value={"version": "test"},
            ),
            patch(
                "health_refund_assistant.assistant.converter_pdf_bytes_primeira_pagina_base64",
                return_value="base64-image",
            ),
            patch(
                "health_refund_assistant.assistant.VLMExtractor",
                return_value=extractor,
            ),
            patch(
                "health_refund_assistant.assistant.avaliar_documento",
                return_value=assessment,
            ),
            patch(
                "health_refund_assistant.assistant.create_assistant_answer",
                return_value="Resposta",
            ) as answer,
        ):
            result = assistant.handle_request(request)

        self.assertEqual(result.document_fields["valor_total"], 450.0)
        self.assertEqual(result.assessment, assessment)
        self.assertEqual(result.answer, "Resposta")
        answer.assert_called_once()

    def test_request_does_not_call_vlm_without_plan_export(self):
        request = assistant.AssistantRequest(
            pdf_bytes=b"%PDF-synthetic",
            question="O pedido foi pago?",
            export_paths=[],
            extraction_prompt_version="v4.0",
            response_prompt_version="v1.0",
            reference_date=date(2026, 3, 20),
        )
        with patch("health_refund_assistant.assistant.VLMExtractor") as extractor:
            with self.assertRaises(ExportPeriodError):
                assistant.handle_request(request)
        extractor.assert_not_called()


if __name__ == "__main__":
    unittest.main()
