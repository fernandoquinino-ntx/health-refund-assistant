"""Testes da orquestração do assistente."""
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import Mock, patch

from health_refund_assistant.conversation import assistant
from health_refund_assistant.plan.assessment import ExportPeriodError


class AssistantTests(unittest.TestCase):
    def test_assistant_uses_prompt_and_structured_evidence(self):
        with patch(
            "health_refund_assistant.conversation.resposta_assistente.request_structured_json",
            return_value={"resposta": "O pedido está em análise."},
        ) as structured:
            answer = assistant.create_assistant_answer(
                "Já foi pago?",
                {"documento": {"valor_total": 450.0}},
                "v1.0",
            )

        self.assertEqual(answer, "O pedido está em análise.")
        self.assertIn("Não invente pedidos", structured.call_args.args[0])
        self.assertIn('"valor_total": 450.0', structured.call_args.args[1])

    def test_follow_up_passes_bounded_history_as_untrusted_context(self):
        history = [{"role": "user", "content": str(i)} for i in range(12)]
        with patch(
            "health_refund_assistant.conversation.resposta_assistente.request_structured_json",
            return_value={"resposta": "Resposta"},
        ) as structured:
            assistant.create_assistant_answer("E agora?", {}, "v1.0", history)
        content = structured.call_args.args[1]
        self.assertIn('"content": "2"', content)
        self.assertNotIn('"content": "1"', content)
        self.assertIn("não confiável", content)

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
                "health_refund_assistant.conversation.assistant.load_selected_exports",
                return_value=[{"periodo": {}, "reembolsos": []}],
            ),
            patch(
                "health_refund_assistant.conversation.assistant.load_mapping",
                return_value={"version": "test"},
            ),
            patch(
                "health_refund_assistant.conversation.assistant.converter_pdf_bytes_primeira_pagina_base64",
                return_value="base64-image",
            ),
            patch(
                "health_refund_assistant.conversation.assistant.VLMExtractor",
                return_value=extractor,
            ),
            patch(
                "health_refund_assistant.conversation.assistant.avaliar_documento",
                return_value=assessment,
            ),
            patch(
                "health_refund_assistant.conversation.assistant.create_assistant_answer",
                return_value="Resposta",
            ) as answer,
            patch(
                "health_refund_assistant.conversation.assistant.review_document",
                return_value={"situacao_documental": "revisao_necessaria"},
            ) as review,
        ):
            result = assistant.handle_request(request)

        self.assertEqual(result.document_fields["valor_total"], 450.0)
        self.assertEqual(result.assessment["situacao_pedido"], assessment["situacao_pedido"])
        self.assertEqual(result.assessment["estimativa_pagamento"]["situacao"], "nao_e_possivel_estimar")
        self.assertEqual(result.answer, "Resposta")
        self.assertEqual(result.assessment["elegibilidade"]["status"], "nao_e_possivel_avaliar")
        review.assert_called_once()
        answer.assert_called_once()

    def test_review_cannot_accept_missing_essential_fields(self):
        with patch(
            "health_refund_assistant.conversation.revisao_documental.request_structured_json",
            return_value={
                "situacao_documental": "sem_inconsistencias_identificadas",
                "justificativa": "Parece completo.",
                "campos_para_revisao": [],
                "orientacoes": [],
            },
        ):
            with self.assertRaisesRegex(ValueError, "contradiz"):
                assistant.review_document("É elegível?", "imagem", {"imagem_legivel": True}, {})

    def test_review_reports_insufficient_document_evidence(self):
        review = {
            "situacao_documental": "nao_e_possivel_avaliar",
            "justificativa": "Data de emissão ausente.",
            "campos_para_revisao": ["data_emissao"],
            "orientacoes": ["Confira a data de emissão."],
        }
        with patch(
            "health_refund_assistant.conversation.revisao_documental.request_structured_json",
            return_value=review,
        ) as structured:
            result = assistant.review_document("É elegível?", "imagem", {"imagem_legivel": True}, {})
        self.assertEqual(result["situacao_documental"], "nao_e_possivel_avaliar")
        self.assertIn("image_url", structured.call_args.args[1][1])

    def test_review_failure_stops_response(self):
        request = assistant.AssistantRequest(
            pdf_bytes=b"%PDF", question="É elegível?", export_paths=[Path("export.json")],
            extraction_prompt_version="v4.0", response_prompt_version="v1.0",
            reference_date=date(2026, 3, 20),
        )
        extractor = Mock()
        extractor.extrair_dados_nf_visual.return_value = {"_meta": {"status": "OK"}}
        with (
            patch("health_refund_assistant.conversation.assistant.load_selected_exports", return_value=[{}]),
            patch("health_refund_assistant.conversation.assistant.load_mapping", return_value={}),
            patch("health_refund_assistant.conversation.assistant.converter_pdf_bytes_primeira_pagina_base64", return_value="image"),
            patch("health_refund_assistant.conversation.assistant.VLMExtractor", return_value=extractor),
            patch("health_refund_assistant.conversation.assistant.avaliar_documento", return_value={}),
            patch("health_refund_assistant.conversation.assistant.review_document", side_effect=ValueError("revisão inválida")),
            patch("health_refund_assistant.conversation.assistant.create_assistant_answer") as answer,
        ):
            with self.assertRaisesRegex(ValueError, "revisão inválida"):
                assistant.handle_request(request)
            answer.assert_not_called()

    def test_request_does_not_call_vlm_without_plan_export(self):
        request = assistant.AssistantRequest(
            pdf_bytes=b"%PDF-synthetic",
            question="O pedido foi pago?",
            export_paths=[],
            extraction_prompt_version="v4.0",
            response_prompt_version="v1.0",
            reference_date=date(2026, 3, 20),
        )
        with patch("health_refund_assistant.conversation.assistant.VLMExtractor") as extractor:
            with self.assertRaises(ExportPeriodError):
                assistant.handle_request(request)
        extractor.assert_not_called()


if __name__ == "__main__":
    unittest.main()
