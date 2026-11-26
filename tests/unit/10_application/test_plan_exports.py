"""Objetivo: verificar a importação de exportações do plano.

Entradas: conteúdo JSON e diretórios temporários de teste.
Processamento: exercita importação, listagem e validação de períodos.
Saídas: asserções de sucesso ou falha para o runner de testes.
"""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from health_refund_assistant.plan.assessment import ExportPeriodError
from health_refund_assistant.plan import plan_exports


class PlanExportsTests(unittest.TestCase):
    def test_import_rejects_export_without_period_before_saving(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            with patch.object(plan_exports, "PLAN_EXPORTS_DIR", target):
                with self.assertRaisesRegex(
                    ExportPeriodError, "Análise não executada"
                ):
                    plan_exports.import_plan_export(
                        "export.json",
                        json.dumps({"reembolsos": []}).encode("utf-8"),
                    )

            self.assertEqual(list(target.iterdir()), [])

    def test_import_saves_valid_period_export_with_safe_filename(self):
        export = {
            "periodo": {"de": "01/03/2026", "ate": "31/03/2026"},
            "reembolsos": [],
        }
        content = json.dumps(export).encode("utf-8")
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(plan_exports, "PLAN_EXPORTS_DIR", Path(directory)):
                saved = plan_exports.import_plan_export("../plano.json", content)

            self.assertEqual(saved.parent, Path(directory))
            self.assertTrue(saved.name.endswith("_plano.json"))
            self.assertEqual(saved.read_bytes(), content)

    def test_import_rejects_non_object_reimbursement_records(self):
        export = {
            "periodo": {"de": "01/03/2026", "ate": "31/03/2026"},
            "reembolsos": [None],
        }
        content = json.dumps(export).encode("utf-8")
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            with patch.object(plan_exports, "PLAN_EXPORTS_DIR", target):
                with self.assertRaisesRegex(ExportPeriodError, "plan_export.schema"):
                    plan_exports.import_plan_export("plano.json", content)

            self.assertEqual(list(target.iterdir()), [])

    def test_assessment_round_trip_preserves_document_and_reconciliation(self):
        evidence = {
            "documento": {"numero_documento": "1049"},
            "conciliacao": {"situacao_pedido": "localizado"},
            "revisao_ia": {"situacao_documental": "revisao_necessaria"},
        }
        content = plan_exports.export_assessment_json(evidence)
        imported = plan_exports.import_assessment_json(content)
        self.assertEqual(imported, evidence)

    def test_assessment_round_trip_rejects_missing_sections(self):
        with self.assertRaisesRegex(ValueError, "dados documentais"):
            plan_exports.export_assessment_json({"conciliacao": {}})
        with self.assertRaisesRegex(ValueError, "documento"):
            plan_exports.import_assessment_json(b'{"conciliacao": {}}')


if __name__ == "__main__":
    unittest.main()
