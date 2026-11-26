"""Testes dos cenários sintéticos de conciliação."""
import json
import unittest
from datetime import date
from pathlib import Path

from health_refund_assistant.plan.assessment import avaliar_documento
from scripts.test_paths import SYNTHETIC_DATA_DIR
from health_refund_assistant.plan.reconciliation import DEFAULT_MAPPING, load_json


def read_json(path: Path):
    with path.open(encoding="utf-8") as file:
        return json.load(file)


class SyntheticReimbursementScenariosTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = read_json(SYNTHETIC_DATA_DIR / "casos_teste.json")["casos"]
        cls.gold = read_json(SYNTHETIC_DATA_DIR / "gabarito.json")["casos"]
        cls.export = read_json(SYNTHETIC_DATA_DIR / "exportacao_ficticia.json")
        cls.mapping = load_json(DEFAULT_MAPPING)

    def test_all_fifteen_scenarios_match_deterministic_assessment(self):
        self.assertEqual(len(self.cases), 15)
        self.assertEqual(len(self.gold), 15)
        self.assertEqual(
            {case["id"] for case in self.cases},
            set(self.gold),
        )

        for case in self.cases:
            with self.subTest(case_id=case["id"]):
                expected = self.gold[case["id"]]["avaliacao"]
                result = avaliar_documento(
                    self.gold[case["id"]]["campos"],
                    [self.export],
                    self.mapping,
                    date.fromisoformat(case["data_referencia"]),
                )

                for field, value in expected.items():
                    if field == "status_financeiro":
                        statuses = {
                            candidate["financial_status"]
                            for candidate in result["candidatos"]
                        }
                        self.assertEqual(
                            statuses,
                            set() if value is None else {value},
                        )
                    else:
                        self.assertEqual(result[field], value, field)

    def test_deadline_cases_distinguish_existing_and_missing_requests(self):
        overdue_with_request = self.gold["C06"]["avaliacao"]
        self.assertIsNone(overdue_with_request["dias_desde_atendimento_ou_emissao"])
        self.assertEqual(overdue_with_request["situacao_prazo"], "nao_aplicavel_pedido_localizado")
        self.assertEqual(overdue_with_request["situacao_pedido"], "localizado")

        overdue_without_request = self.gold["C07"]["avaliacao"]
        self.assertEqual(
            overdue_without_request["dias_desde_atendimento_ou_emissao"],
            32,
        )
        self.assertEqual(
            overdue_without_request["situacao_pedido"],
            "nao_localizado_nas_exportacoes",
        )
        self.assertTrue(
            overdue_without_request["periodo_dos_datasets_cobre_data_base"]
        )

        missing_dates = self.gold["C13"]["avaliacao"]
        self.assertEqual(missing_dates["situacao_pedido"], "data_documento_indeterminada")
        self.assertIsNone(missing_dates["dias_desde_atendimento_ou_emissao"])
        case_13 = next(case for case in self.cases if case["id"] == "C13")
        self.assertFalse(case_13["falha_critica"])

    def test_paid_status_requires_confirmed_payment_evidence(self):
        paid = self.gold["C02"]["avaliacao"]
        approved_without_payment = self.gold["C15"]["avaliacao"]
        self.assertEqual(paid["status_financeiro"], "reembolsado_integral")
        self.assertEqual(
            approved_without_payment["status_financeiro"],
            "liberado_integral_aguardando_pagamento",
        )


if __name__ == "__main__":
    unittest.main()
