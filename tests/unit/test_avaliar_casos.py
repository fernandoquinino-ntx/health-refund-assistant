"""Testes do avaliador de casos sintéticos."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from scripts.case_evaluation import (
    _validar_manifesto,
    comparar_valor,
    executar_avaliacao,
)
from scripts.test_paths import TEST_FIXTURES_DIR


class AvaliarCasosTests(unittest.TestCase):
    def test_legacy_command_does_not_fabricate_report_without_api_key(self):
        project_root = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / "avaliacao.json"
            environment = {**os.environ, "OPENAPI_TOKEN": ""}
            result = subprocess.run(
                [
                    sys.executable,
                    str(project_root / "scripts" / "case_evaluation_v3.py"),
                    "--saida",
                    str(report),
                ],
                cwd=project_root,
                env=environment,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("OPENAPI_TOKEN", result.stderr)
            self.assertFalse(report.exists())

    def test_catalog_covers_fifteen_reimbursement_assistant_scenarios(self):
        catalog_path = TEST_FIXTURES_DIR / "casos_teste.template.json"
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        cases = catalog["casos"]

        self.assertEqual(len(cases), 15)
        self.assertEqual(len({case["id"] for case in cases}), len(cases))
        self.assertEqual([case["id"] for case in cases], [f"C{i:02}" for i in range(1, 16)])
        self.assertTrue(all(case["executar_vlm"] for case in cases))
        criticos = {
            case["id"] for case in cases if case["falha_critica"]
        }
        self.assertEqual(criticos, {"C14", "C15"})
        self.assertTrue(all(case["pergunta"].strip() for case in cases))
        self.assertTrue(all(case["data_referencia"] for case in cases))
        self.assertEqual(
            {case["categoria"] for case in cases},
            {
                "pedido",
                "pagamento",
                "prazo",
                "completude",
                "data_ausente",
                "seguranca",
            },
        )

    def test_money_uses_cent_tolerance_and_null_is_exact(self):
        self.assertTrue(comparar_valor("valor_total", 100.0, 100.01, 0.01))
        self.assertFalse(comparar_valor("valor_total", 100.0, 100.02, 0.01))
        self.assertTrue(comparar_valor("registro_profissional", None, None, 0.01))
        self.assertFalse(
            comparar_valor("registro_profissional", None, "CRM 123", 0.01)
        )

    def test_comparison_does_not_treat_boolean_as_number(self):
        self.assertFalse(comparar_valor("valor_total", 1.0, True, 0.01))
        self.assertFalse(comparar_valor("imagem_legivel", True, 1, 0.01))

    def test_gabarito_rejects_fields_not_returned_by_extractor(self):
        cases = {
            "casos": [
                {
                    "id": "C01",
                    "arquivo": "C01.pdf",
                    "executar_vlm": True,
                }
            ]
        }
        gold = {
            "casos": {
                "C01": {"campos": {"status_esperado": "BAIXA_CONFIRMADA"}}
            }
        }
        with self.assertRaisesRegex(ValueError, "Campos não extraídos"):
            _validar_manifesto(cases, gold)

    def test_legacy_prompt_compares_only_its_nine_field_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            cases_path, gold_path, documents, report_path = self._prepare_suite(root)
            gold = json.loads(gold_path.read_text(encoding="utf-8"))
            gold["casos"]["C01"]["campos"].update(
                {
                    "data_atendimento": "10/03/2026",
                    "nome_profissional": "Profissional Sintético",
                }
            )
            gold_path.write_text(json.dumps(gold), encoding="utf-8")
            extractor = self._mock_extractor([100.0 + index for index in range(15)])

            with (
                patch("scripts.case_evaluation.VLMExtractor", return_value=extractor),
                patch(
                    "scripts.case_evaluation.converter_primeira_pagina_pdf_base64",
                    return_value="imagem",
                ),
            ):
                report = executar_avaliacao(
                    cases_path,
                    gold_path,
                    documents,
                    report_path,
                    prompt_version="v1.1",
                )

        self.assertTrue(report["resumo"]["aprovado"])
        self.assertEqual(
            set(report["resultados"][0]["campos"]),
            {"valor_total"},
        )

    def test_v4_prompt_compares_professional_and_service_date_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            cases_path, gold_path, documents, report_path = self._prepare_suite(root)
            gold = json.loads(gold_path.read_text(encoding="utf-8"))
            outputs = []
            for index in range(15):
                expected_fields = {
                    "valor_total": 100.0 + index,
                    "data_atendimento": "10/03/2026",
                    "nome_profissional": "Profissional Sintético",
                }
                gold["casos"][f"C{index + 1:02}"]["campos"] = expected_fields
                outputs.append(
                    {**expected_fields, "_meta": {"status": "OK"}}
                )
            gold_path.write_text(json.dumps(gold), encoding="utf-8")
            extractor = self._mock_extractor([100.0 + index for index in range(15)])
            for version in ("v4.0", "v4.1", "v4.2"):
                with self.subTest(version=version):
                    extractor.prompt_version = version
                    extractor.extrair_dados_nf_visual.side_effect = outputs
                    with (
                        patch("scripts.case_evaluation.VLMExtractor", return_value=extractor),
                        patch(
                            "scripts.case_evaluation.converter_primeira_pagina_pdf_base64",
                            return_value="imagem",
                        ),
                    ):
                        report = executar_avaliacao(
                            cases_path,
                            gold_path,
                            documents,
                            report_path,
                            prompt_version=version,
                        )
                    self.assertTrue(report["resumo"]["aprovado"])
                    self.assertEqual(
                        set(report["resultados"][0]["campos"]),
                        {"valor_total", "data_atendimento", "nome_profissional"},
                    )

    def test_suite_with_fifteen_successful_cases_can_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            cases_path, gold_path, documents, report_path = self._prepare_suite(root)
            extractor = self._mock_extractor([100.0 + index for index in range(15)])

            with (
                patch("scripts.case_evaluation.VLMExtractor", return_value=extractor),
                patch(
                    "scripts.case_evaluation.converter_primeira_pagina_pdf_base64",
                    return_value="imagem",
                ),
            ):
                report = executar_avaliacao(
                    cases_path,
                    gold_path,
                    documents,
                    report_path,
                    prompt_version="v1.1",
                )

            self.assertTrue(report["resumo"]["suite_completa"])
            self.assertTrue(report["resumo"]["aprovado"])
            self.assertEqual(report["resumo"]["casos_executados"], 15)
            self.assertTrue(report_path.is_file())

    def test_out_of_scope_case_prevents_passing_incomplete_suite(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            cases_path, gold_path, documents, report_path = self._prepare_suite(
                root, skipped=1
            )
            extractor = self._mock_extractor([100.0 + index for index in range(14)])

            with (
                patch("scripts.case_evaluation.VLMExtractor", return_value=extractor),
                patch(
                    "scripts.case_evaluation.converter_primeira_pagina_pdf_base64",
                    return_value="imagem",
                ),
            ):
                report = executar_avaliacao(
                    cases_path, gold_path, documents, report_path
                )

            self.assertFalse(report["resumo"]["suite_completa"])
            self.assertFalse(report["resumo"]["aprovado"])
            self.assertEqual(report["resumo"]["casos_fora_do_escopo"], 1)

    def test_critical_case_mismatch_fails_even_above_accuracy_threshold(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            cases_path, gold_path, documents, report_path = self._prepare_suite(root)
            outputs = [100.0 + index for index in range(15)]
            outputs[-1] += 10
            extractor = self._mock_extractor(outputs)

            with (
                patch("scripts.case_evaluation.VLMExtractor", return_value=extractor),
                patch(
                    "scripts.case_evaluation.converter_primeira_pagina_pdf_base64",
                    return_value="imagem",
                ),
            ):
                report = executar_avaliacao(
                    cases_path, gold_path, documents, report_path
                )

            self.assertGreaterEqual(
                report["resumo"]["acuracia_por_caso"], 0.85
            )
            self.assertEqual(report["resumo"]["falhas_criticas"], 1)
            self.assertEqual(report["resultados"][-1]["caso_id"], "C15")
            self.assertTrue(report["resultados"][-1]["falha_critica"])
            self.assertFalse(report["resumo"]["aprovado"])

    def _prepare_suite(self, root: Path, skipped: int = 0):
        documents = root / "documentos"
        documents.mkdir()
        cases = []
        gold_cases = {}
        for index in range(15):
            case_id = f"C{index + 1:02}"
            execute = index >= skipped
            filename = f"{case_id}.pdf"
            if execute:
                (documents / filename).write_bytes(b"%PDF-test")
                gold_cases[case_id] = {
                    "campos": {"valor_total": 100.0 + index}
                }
            cases.append(
                {
                    "id": case_id,
                    "arquivo": filename,
                    "executar_vlm": execute,
                    "falha_critica": index == 14,
                    "motivo_fora_escopo": "Teste",
                }
            )

        cases_path = root / "casos.json"
        cases_path.write_text(
            json.dumps({"schema_version": 1, "casos": cases}),
            encoding="utf-8",
        )
        gold_path = root / "gabarito.json"
        gold_path.write_text(
            json.dumps({"schema_version": 1, "casos": gold_cases}),
            encoding="utf-8",
        )
        return cases_path, gold_path, documents, root / "resultado.json"

    @staticmethod
    def _mock_extractor(values):
        extractor = Mock()
        extractor.model = "modelo-teste"
        extractor.prompt_version = "v1.1"
        extractor.extrair_dados_nf_visual.side_effect = [
            {"valor_total": value, "_meta": {"status": "OK"}}
            for value in values
        ]
        return extractor


if __name__ == "__main__":
    unittest.main()
