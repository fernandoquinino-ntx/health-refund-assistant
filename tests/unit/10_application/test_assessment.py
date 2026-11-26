"""Objetivo: verificar a avaliação determinística dos documentos.

Entradas: campos e exportações de teste.
Processamento: exercita avaliação, correspondência e regras de prazo.
Saídas: asserções de sucesso ou falha para o runner de testes.
"""
import unittest
import json
import tempfile
from datetime import date
from pathlib import Path
from unittest.mock import patch

from health_refund_assistant.plan.assessment import (
    ExportPeriodError,
    avaliar_documento,
    validar_periodo_exportacao,
)
from health_refund_assistant.plan import assessment as assessment_module
from health_refund_assistant.plan.reconciliation import DEFAULT_MAPPING, load_json


class AssessmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mapping = load_json(DEFAULT_MAPPING)

    def setUp(self):
        self.document = {
            "numero_documento": "NFS-e 1001",
            "prestador": "Clínica Fictícia Horizonte",
            "cnpj_cpf_prestador": "00.000.000/0001-00",
            "valor_total": 450.0,
            "data_emissao": "02/03/2026",
            "data_atendimento": "02/03/2026",
            "nome_profissional": "Dra. Fictícia Ana",
            "descricao_servico": "Consulta médica",
            "registro_profissional": "CRM 100001/SP",
        }
        self.export = {
            "periodo": {"de": "01/03/2026", "ate": "31/03/2026"},
            "reembolsos": [],
        }

    def test_deadline_boundary_includes_day_30_and_excludes_day_31(self):
        at_day_30 = avaliar_documento(
            self.document,
            [self.export],
            self.mapping,
            date(2026, 4, 1),
        )
        self.assertEqual(at_day_30["dias_desde_atendimento_ou_emissao"], 30)
        self.assertEqual(at_day_30["situacao_prazo"], "dentro_do_prazo_simulado")

        at_day_31 = avaliar_documento(
            self.document,
            [self.export],
            self.mapping,
            date(2026, 4, 2),
        )
        self.assertEqual(at_day_31["dias_desde_atendimento_ou_emissao"], 31)
        self.assertEqual(at_day_31["situacao_prazo"], "fora_do_prazo_simulado")

    def test_uses_service_date_before_issue_date_and_marks_fallback(self):
        self.document["data_atendimento"] = "01/03/2026"
        result = avaliar_documento(
            self.document, [self.export], self.mapping, date(2026, 4, 1)
        )
        self.assertEqual(result["data_base_prazo"], "2026-03-01")
        self.assertEqual(result["origem_data_base_prazo"], "data_atendimento")

        self.document["data_atendimento"] = None
        result = avaliar_documento(
            self.document, [self.export], self.mapping, date(2026, 4, 1)
        )
        self.assertEqual(result["data_base_prazo"], "2026-03-02")
        self.assertEqual(result["origem_data_base_prazo"], "data_emissao")

    def test_deadline_notice_matches_selected_simulation(self):
        result = avaliar_documento(
            self.document, [self.export], self.mapping, date(2026, 4, 1), 365
        )
        self.assertIn("365 dias", result["aviso_prazo"])
        self.assertIn("simulada", result["aviso_prazo"])

    def test_missing_export_period_stops_assessment(self):
        with self.assertRaisesRegex(ExportPeriodError, "Análise não executada"):
            avaliar_documento(
                self.document,
                [{"reembolsos": []}],
                self.mapping,
                date(2026, 4, 1),
            )

        with self.assertRaisesRegex(ExportPeriodError, "período"):
            validar_periodo_exportacao({"reembolsos": []}, "sem-periodo.json")

    def test_missing_data_is_reported_as_incomplete_without_inference(self):
        self.document["data_atendimento"] = None
        self.document["data_emissao"] = None
        self.document["nome_profissional"] = None
        self.document["registro_profissional"] = None
        self.document["descricao_servico"] = None
        result = avaliar_documento(
            self.document, [self.export], self.mapping, date(2026, 4, 1)
        )
        self.assertIsNone(result["data_base_prazo"])
        self.assertEqual(result["situacao_prazo"], "indeterminado")
        self.assertEqual(
            result["situacao_pedido"], "data_documento_indeterminada"
        )
        self.assertEqual(
            result["campos_incompletos"],
            [
                "nome do profissional de saúde",
                "registro profissional",
                "descrição do serviço",
                "data do atendimento",
                "data de emissão",
            ],
        )

    def test_export_not_covering_note_does_not_claim_request_missing(self):
        old_export = {
            "periodo": {"de": "01/01/2026", "ate": "31/01/2026"},
            "reembolsos": [],
        }
        result = avaliar_documento(
            self.document, [old_export], self.mapping, date(2026, 4, 1)
        )
        self.assertEqual(result["situacao_pedido"], "periodo_nao_coberto")
        self.assertFalse(result["periodo_dos_datasets_cobre_data_base"])

    def test_payment_and_portal_statuses_require_matching_evidence(self):
        examples = (
            ("Reembolsado Integral", 450.0, "12/03/2026", "reembolsado_integral"),
            ("Reembolsado Parcial", 200.0, "12/03/2026", "reembolsado_parcial"),
            ("Em Análise", None, None, "em_analise"),
            ("Não Liberado", None, None, "nao_liberado"),
            (
                "Liberado Integral",
                450.0,
                None,
                "liberado_integral_aguardando_pagamento",
            ),
        )
        for status, paid_amount, payment_date, expected in examples:
            with self.subTest(status=status):
                claim = {
                    "numeroSinistro": "SIN-SINT-001",
                    "prestador": self.document["prestador"],
                    "beneficiario": "Beneficiário Sintético",
                    "status": status,
                    "valorSolicitadoNum": 450.0,
                    "valorFinalReembolsadoNum": paid_amount,
                    "dataRealizacao": self.document["data_atendimento"],
                    "dataSolicitacao": "05/03/2026",
                    "dataPagamento": payment_date,
                    "procedimento": self.document["descricao_servico"],
                }
                export = {
                    **self.export,
                    "reembolsos": [claim],
                }
                result = avaliar_documento(
                    self.document,
                    [export],
                    self.mapping,
                    date(2026, 3, 20),
                )
                self.assertEqual(
                    result["candidatos"][0]["financial_status"],
                    expected,
                )

    def test_conflicting_exports_are_not_collapsed_into_one_candidate(self):
        claim = {
            "numeroSinistro": "SIN-SINT-001",
            "prestador": self.document["prestador"],
            "beneficiario": "Beneficiário Sintético",
            "status": "Em Análise",
            "valorSolicitadoNum": 450.0,
            "dataRealizacao": self.document["data_atendimento"],
            "dataSolicitacao": "05/03/2026",
            "procedimento": self.document["descricao_servico"],
        }
        earlier = {**self.export, "reembolsos": [claim]}
        paid = {
            **claim, "status": "Reembolsado Integral",
            "valorFinalReembolsadoNum": 450.0, "dataPagamento": "12/03/2026",
        }
        later = {**self.export, "reembolsos": [paid]}
        result = avaliar_documento(self.document, [earlier, later], self.mapping, date(2026, 3, 20))
        self.assertEqual(len(result["candidatos"]), 2)
        self.assertEqual(result["ids_com_registros_conflitantes"], ["SIN-SINT-001"])
        identical = avaliar_documento(self.document, [earlier, earlier], self.mapping, date(2026, 3, 20))
        self.assertEqual(len(identical["candidatos"]), 1)

    def test_confirmed_d2_and_365_rules_are_opt_in(self):
        with tempfile.TemporaryDirectory() as directory:
            config_path = Path(directory) / "prazos_reembolso.json"
            config_path.write_text(json.dumps({
                "schema_version": 1,
                "regras_confirmadas": True,
                "d2": {"ativo": True, "dias": 2},
                "365": {"ativo": True, "dias": 365},
            }), encoding="utf-8")
            with patch.object(assessment_module, "PRAZO_CONFIG_PATH", config_path):
                result = avaliar_documento(
                    self.document,
                    [self.export],
                    self.mapping,
                    date(2026, 4, 1),
                )
            self.assertTrue(result["regras_prazo_confirmadas"])
            self.assertTrue(result["corte_d2"]["ativo"])
            self.assertEqual(result["corte_d2"]["corte_exportacao"], "2026-03-30")
            self.assertTrue(result["prazo_365"]["ativo"])
            self.assertEqual(result["prazo_365"]["situacao"], "dentro_do_prazo_para_novo_pedido")

    def test_d2_only_confirms_absence_two_days_after_import(self):
        export = {
            **self.export,
            "_importado_em": "2026-03-20",
        }
        recent_document = {**self.document, "data_atendimento": "2026-03-19"}
        recent = avaliar_documento(
            recent_document,
            [export],
            self.mapping,
            date(2026, 3, 20),
        )
        self.assertNotEqual(
            recent["corte_d2"]["situacao"],
            "ausencia_confirmada_na_exportacao",
        )

        old_document = {**self.document, "data_atendimento": "2026-03-16"}
        old = avaliar_documento(
            old_document,
            [export],
            self.mapping,
            date(2026, 3, 20),
        )
        self.assertEqual(
            old["corte_d2"]["situacao"],
            "ausencia_confirmada_na_exportacao",
        )

    def test_365_days_blocks_only_new_request_without_candidate(self):
        old_document = {**self.document, "data_atendimento": "2025-01-01"}
        no_candidate = avaliar_documento(
            old_document,
            [self.export],
            self.mapping,
            date(2026, 3, 20),
        )
        self.assertEqual(
            no_candidate["prazo_365"]["situacao"],
            "prazo_expirado_sem_pedido",
        )
        self.assertFalse(no_candidate["pode_abrir_novo_pedido"])


if __name__ == "__main__":
    unittest.main()
