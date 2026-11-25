import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from health_refund_assistant.pdf_processing import processar_pdfs


class ProcessarPdfsTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.incoming = self.root / "incoming"
        self.processed = self.root / "processed"
        self.failed = self.root / "failed"
        self.status_path = self.root / "notas_extraidas.json"
        self.incoming.mkdir()
        self.result = {
            "numero_documento": "NF-123",
            "prestador": "Clínica Exemplo",
            "cnpj_cpf_prestador": "12.345.678/0001-90",
            "valor_total": 375.0,
            "data_emissao": "15/01/2025",
            "descricao_servico": "Consulta médica",
            "registro_profissional": "CRM 12345",
            "imagem_legivel": True,
            "observacao_visual": None,
            "_meta": {"status": "OK"},
        }

    def tearDown(self):
        self.temp_dir.cleanup()

    def criar_pdf_falso(self, nome: str, conteudo: bytes) -> Path:
        caminho = self.incoming / nome
        caminho.write_bytes(conteudo)
        return caminho

    def criar_extrator(self, resultados=None):
        extrator = Mock()
        extrator.model = "modelo-teste"
        extrator.prompt_version = "v1.1"
        extrator.extrair_dados_nf_visual.side_effect = resultados or [
            self.result
        ]
        return extrator

    def processar(self, extrator, **kwargs):
        with (
            patch("health_refund_assistant.pdf_processing.VLMExtractor", return_value=extrator),
            patch(
                "health_refund_assistant.pdf_processing.converter_primeira_pagina_pdf_base64",
                return_value="imagem-base64",
            ),
        ):
            return processar_pdfs(
                pasta_pdfs=self.incoming,
                caminho_status=self.status_path,
                model="modelo-teste",
                pasta_processadas=self.processed,
                pasta_falhas=self.failed,
                **kwargs,
            )

    def ler_status(self):
        return json.loads(self.status_path.read_text(encoding="utf-8"))

    def test_success_renames_and_moves_pdf_with_unique_id(self):
        self.criar_pdf_falso("nota original.pdf", b"%PDF-1")
        status = self.processar(self.criar_extrator())

        self.assertEqual(len(status["pdfs"]), 1)
        registro = next(iter(status["pdfs"].values()))
        self.assertRegex(
            registro["nome_arquivo"],
            r"^2025-01-15_NF-123_[0-9a-f]{8}\.pdf$",
        )
        self.assertTrue(Path(registro["caminho"]).is_file())
        self.assertFalse((self.incoming / "nota original.pdf").exists())
        self.assertEqual(status["schema_version"], 3)

    def test_identical_pdf_is_recorded_as_duplicate_without_second_vlm_call(self):
        original = self.criar_pdf_falso("nota.pdf", b"%PDF-same")
        extrator = self.criar_extrator()
        self.processar(extrator)

        (self.incoming / "copia.pdf").write_bytes(
            next(self.processed.glob("*.pdf")).read_bytes()
        )
        status = self.processar(extrator)

        (self.incoming / "nota.pdf").write_bytes(b"%PDF-same")
        status = self.processar(extrator)

        self.assertEqual(extrator.extrair_dados_nf_visual.call_count, 1)
        self.assertEqual(len(status["pdfs"]), 1)
        self.assertEqual(len(status["duplicatas"]), 2)
        self.assertEqual(
            status["duplicatas"][0]["tipo_duplicidade"], "arquivo_identico"
        )
        self.assertTrue(
            Path(status["duplicatas"][0]["caminho"]).is_file()
        )
        self.assertFalse(original.exists())

    def test_same_provider_and_invoice_number_is_flagged_as_duplicate(self):
        self.criar_pdf_falso("nota-a.pdf", b"%PDF-first")
        extrator = self.criar_extrator([self.result, self.result])
        self.processar(extrator)

        self.criar_pdf_falso("nota-b.pdf", b"%PDF-different")
        status = self.processar(extrator)

        self.assertEqual(len(status["pdfs"]), 1)
        self.assertEqual(len(status["duplicatas"]), 1)
        self.assertEqual(
            status["duplicatas"][0]["tipo_duplicidade"],
            "mesmo_prestador_e_numero_documento",
        )
        self.assertIn("resultado", status["duplicatas"][0])

    def test_missing_provider_tax_id_does_not_make_logical_duplicate(self):
        resultado = {**self.result, "cnpj_cpf_prestador": None}
        extrator = self.criar_extrator([resultado, resultado])
        self.criar_pdf_falso("nota-a.pdf", b"%PDF-first")
        self.processar(extrator)

        self.criar_pdf_falso("nota-b.pdf", b"%PDF-second")
        status = self.processar(extrator)

        self.assertEqual(len(status["pdfs"]), 2)
        self.assertEqual(status["duplicatas"], [])

    def test_existing_status_without_hash_still_detects_identical_pdf(self):
        pasta_legada = self.root / "notas_pdf"
        pasta_legada.mkdir()
        nota_legada = pasta_legada / "nota-antiga.pdf"
        nota_legada.write_bytes(b"%PDF-legacy")
        status_antigo = {
            "schema_version": 2,
            "model": "modelo-teste",
            "prompt_version": "v1.1",
            "pdfs": {
                "nota-antiga.pdf": {
                    "nome_arquivo": "nota-antiga.pdf",
                    "caminho": str(nota_legada),
                    "processado": True,
                    "sucesso": True,
                    "model": "modelo-teste",
                    "prompt_version": "v1.1",
                    "resultado": self.result,
                }
            },
        }
        self.status_path.write_text(
            json.dumps(status_antigo), encoding="utf-8"
        )
        self.criar_pdf_falso("copia.pdf", b"%PDF-legacy")
        extrator = self.criar_extrator()

        status = self.processar(extrator)

        self.assertEqual(extrator.extrair_dados_nf_visual.call_count, 0)
        self.assertEqual(len(status["pdfs"]), 1)
        self.assertEqual(len(status["duplicatas"]), 1)
        self.assertEqual(
            status["pdfs"]["nota-antiga.pdf"]["sha256"],
            status["duplicatas"][0]["sha256"],
        )

    def test_failed_pdf_moves_to_failed_and_can_be_retried(self):
        resultado_falha = {
            **self.result,
            "_meta": {"status": "ERRO_CONEXAO"},
        }
        extrator = self.criar_extrator([resultado_falha, self.result])
        self.criar_pdf_falso("nota.pdf", b"%PDF-retry")
        primeiro_status = self.processar(extrator)
        caminho_falha = Path(next(iter(primeiro_status["pdfs"].values()))["caminho"])
        self.assertTrue(caminho_falha.is_relative_to(self.failed))

        with (
            patch("health_refund_assistant.pdf_processing.VLMExtractor", return_value=extrator),
            patch(
                "health_refund_assistant.pdf_processing.converter_primeira_pagina_pdf_base64",
                return_value="imagem-base64",
            ),
        ):
            segundo_status = processar_pdfs(
                pasta_pdfs=self.incoming,
                caminho_status=self.status_path,
                model="modelo-teste",
                pasta_processadas=self.processed,
                pasta_falhas=self.failed,
                reprocessar_falhas=True,
            )

        self.assertEqual(len(segundo_status["pdfs"]), 1)
        registro = next(iter(segundo_status["pdfs"].values()))
        self.assertTrue(registro["sucesso"])
        self.assertTrue(Path(registro["caminho"]).is_relative_to(self.processed))
        self.assertEqual(extrator.extrair_dados_nf_visual.call_count, 2)


if __name__ == "__main__":
    unittest.main()
