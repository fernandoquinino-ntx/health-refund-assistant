"""Objetivo: verificar a estimativa de processamento de reembolso.

Entradas: datas, situações de pedidos e respostas de IA simuladas.
Processamento: testa limites, contagem de dias úteis e guardrails.
Saídas: asserções de sucesso ou falha para o runner de testes.
"""

import unittest
from datetime import date
from unittest.mock import patch

from health_refund_assistant.conversation.assistant import atualizar_estimativa
from health_refund_assistant.conversation.estimativa_pagamento import estimar_pagamento
from health_refund_assistant.core.json_contracts import validar_contrato_json


def assessment(**candidate_changes):
    candidate = {
        "strong": True,
        "request_date": "2026-03-20",
        "financial_status": "em_analise",
        "payment_date": None,
        "paid_amount": None,
        **candidate_changes,
    }
    return {"candidatos": [candidate], "erros_exportacao": [], "ids_com_registros_conflitantes": []}


class PaymentEstimateTests(unittest.TestCase):
    @patch("health_refund_assistant.conversation.estimativa_pagamento.request_structured_json")
    def test_friday_submission_weekend_due_date_and_delay(self, call):
        for reference, remaining, delay, status in (
            ("2026-03-20", 5, 0, "dentro_do_prazo"),
            ("2026-03-22", 5, 0, "dentro_do_prazo"),
            ("2026-03-27", 0, 0, "dentro_do_prazo"),
            ("2026-03-28", 0, 0, "prazo_ultrapassado"),
            ("2026-03-30", 0, 1, "prazo_ultrapassado"),
        ):
            expected = {
                "data_submissao": "2026-03-20",
                "data_referencia": reference,
                "data_estimada": "2026-03-27",
                "dias_uteis_restantes": remaining,
                "dias_uteis_atraso": delay,
                "situacao": status,
            }
            with self.subTest(reference=reference):
                validar_contrato_json(expected, "payment_estimate.schema.json", "teste")
                call.return_value = expected
                result = estimar_pagamento(assessment(), date.fromisoformat(reference))
                for field, value in expected.items():
                    self.assertEqual(result[field], value)
                self.assertIn("Feriados não foram considerados", result["aviso"])

    @patch("health_refund_assistant.conversation.estimativa_pagamento.request_structured_json")
    def test_weekend_submission_starts_monday(self, call):
        call.return_value = {
            "data_submissao": "2026-03-21", "data_referencia": "2026-03-23",
            "data_estimada": "2026-03-27", "dias_uteis_restantes": 4,
            "dias_uteis_atraso": 0, "situacao": "dentro_do_prazo",
        }
        result = estimar_pagamento(assessment(request_date="2026-03-21"), date(2026, 3, 23))
        self.assertEqual(result["data_estimada"], "2026-03-27")
        self.assertEqual(result["dias_uteis_restantes"], 4)

    @patch("health_refund_assistant.conversation.estimativa_pagamento.request_structured_json")
    def test_ai_contradiction_rejected(self, call):
        call.return_value = {
            "data_submissao": "2026-03-20", "data_referencia": "2026-03-20",
            "data_estimada": "2026-03-26", "dias_uteis_restantes": 5,
            "dias_uteis_atraso": 0, "situacao": "dentro_do_prazo",
        }
        with self.assertRaisesRegex(ValueError, "não corresponde"):
            estimar_pagamento(assessment(), date(2026, 3, 20))

    @patch("health_refund_assistant.conversation.estimativa_pagamento.request_structured_json")
    def test_missing_ambiguous_paid_invalid_and_future_are_not_estimated(self, call):
        valid = assessment()
        cases = [
            {"candidatos": []},
            {"candidatos": valid["candidatos"] * 2},
            assessment(strong=False),
            assessment(request_date=None),
            assessment(request_date="2026-02-30"),
            assessment(request_date="2026-03-21"),
            assessment(financial_status="pendencia_documental"),
            assessment(financial_status="nao_liberado"),
            assessment(financial_status="status_desconhecido"),
            assessment(financial_status="reembolsado_parcial"),
            assessment(payment_date="2026-03-19"),
            assessment(paid_amount=5),
            {**valid, "erros_exportacao": ["erro de coleta"]},
            {**valid, "ids_com_registros_conflitantes": [None]},
            {"candidatos": valid["candidatos"], "erros_exportacao": []},
        ]
        for case in cases:
            with self.subTest(case=case):
                result = estimar_pagamento(case, date(2026, 3, 20))
                self.assertEqual(result["situacao"], "nao_e_possivel_estimar")
                self.assertTrue(result["motivo"])
        call.assert_not_called()

    @patch("health_refund_assistant.conversation.assistant.estimar_pagamento")
    def test_old_evidence_is_refreshed_without_stale_submission_deadline(self, estimate):
        estimate.return_value = {"situacao": "nao_e_possivel_estimar"}
        old = {
            **assessment(),
            "situacao_prazo": "fora_do_prazo_simulado",
            "data_base_prazo": "2025-01-01",
            "dias_desde_atendimento_ou_emissao": 400,
        }
        updated = atualizar_estimativa(old, date(2026, 3, 30), "v1.0")
        self.assertEqual(updated["situacao_prazo"], "nao_aplicavel_pedido_localizado")
        self.assertIsNone(updated["data_base_prazo"])
        self.assertIsNone(updated["dias_desde_atendimento_ou_emissao"])
        estimate.assert_called_once_with(updated, date(2026, 3, 30), "v1.0")


if __name__ == "__main__":
    unittest.main()
