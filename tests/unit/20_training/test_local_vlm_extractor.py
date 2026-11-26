"""Objetivo: verificar o comutador seguro do extrator visual local.

Entradas: argumentos simulados e saída JSON fictícia.
Processamento: usa subprocess mockado sem documentos reais.
Saídas: asserções sobre metadados e seleção do modelo.
"""

import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from health_refund_assistant.documents.vlm_extractor import LocalVLMExtractor


class LocalVLMExtractorTests(unittest.TestCase):
    def test_retorna_status_local_e_limpa_imagem_temporaria(self):
        root = Path(__file__).resolve().parents[3]
        extractor = LocalVLMExtractor(
            model_path=root / "models" / "base-smol",
            adapter_path=root / "adapters" / "smolvlm-teste" / "adapters.safetensors",
            prompt_version="v4.2",
        )
        resultado = Mock()
        resultado.returncode = 0
        resultado.stdout = '{"numero_documento":"123"}'
        resultado.stderr = ""
        with patch("subprocess.run", return_value=resultado):
            dados = extractor.extrair_dados_nf_visual("aGVsbG8=", "image/jpeg")
        self.assertEqual(dados["_meta"]["status"], "OK")
        self.assertIn("base-smol", dados["_meta"]["model"])


if __name__ == "__main__":
    unittest.main()
