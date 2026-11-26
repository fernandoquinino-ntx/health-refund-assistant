"""Objetivo: verificar o contrato do dataset visual.

Entradas: registros temporários com imagens e OCR simulados.
Processamento: confere origem, divergências e separação por documento.
Saídas: asserções para o runner de testes, sem uso de dados reais.
"""

import json
import tempfile
import unittest
from pathlib import Path

from anotacao_documentos.cli import ROTULOS
from treinamento_visual.train.check_dataset import verificar, verificar_exemplo


class CheckDatasetVisualTests(unittest.TestCase):
    def setUp(self):
        self.temporario = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporario.cleanup)
        root = Path(self.temporario.name)
        self.dataset, self.paginas, self.ocr = root / "dataset", root / "paginas", root / "ocr"
        self.dataset.mkdir()
        identificador = "doc_" + "a" * 64
        pasta_paginas, pasta_ocr = self.paginas / identificador, self.ocr / identificador
        pasta_paginas.mkdir(parents=True)
        pasta_ocr.mkdir(parents=True)
        (pasta_paginas / "pagina_0001.png").write_bytes(b"imagem de teste")
        (pasta_ocr / "manifest.json").write_text(json.dumps({"paginas": 1}), encoding="utf-8")
        pagina = {
            "pagina": 1, "largura": 200, "altura": 100,
            "linhas": [{"id": "L001", "texto": "150,00"}],
            "palavras": [{"linha": "L001", "texto": "150,00", "bbox": [20, 10, 50, 10]}],
        }
        (pasta_ocr / "pagina_0001.json").write_text(json.dumps(pagina), encoding="utf-8")
        texto = "[p1 L001 y=10] 150,00"
        (pasta_ocr / "pagina_0001.txt").write_text(texto + "\n", encoding="utf-8")
        resposta = {campo: None for campo in ROTULOS}
        resposta["valor_total"] = {"valor": "150,00", "pagina": 1, "linha": "L001", "bbox": [20, 10, 50, 10]}
        self.prompt = "prompt de teste"
        self.exemplo = {
            "images": [f"../paginas/{identificador}/pagina_0001.png"],
            "messages": [
                {"role": "system", "content": self.prompt},
                {"role": "user", "content": texto},
                {"role": "assistant", "content": json.dumps(resposta)},
            ],
        }

    def test_confirma_origem_exata_e_sinaliza_divergencias(self):
        _, verificados, divergentes = verificar_exemplo(
            self.exemplo, self.dataset, self.paginas, self.ocr, self.prompt
        )
        self.assertEqual((verificados, divergentes), (1, 0))
        resposta = json.loads(self.exemplo["messages"][2]["content"])
        resposta["valor_total"]["valor"] = "15"
        self.exemplo["messages"][2]["content"] = json.dumps(resposta)
        _, verificados, divergentes = verificar_exemplo(
            self.exemplo, self.dataset, self.paginas, self.ocr, self.prompt
        )
        self.assertEqual((verificados, divergentes), (0, 1))
        resposta["valor_total"]["valor"] = "150,00"
        resposta["valor_total"]["bbox"] = [69, 10, 1, 10]
        self.exemplo["messages"][2]["content"] = json.dumps(resposta)
        self.assertEqual(verificar_exemplo(self.exemplo, self.dataset, self.paginas, self.ocr, self.prompt)[1:], (0, 1))
        resposta["valor_total"]["linha"] = None
        self.exemplo["messages"][2]["content"] = json.dumps(resposta)
        self.assertEqual(verificar_exemplo(self.exemplo, self.dataset, self.paginas, self.ocr, self.prompt)[1:], (0, 1))

    def test_rejeita_caixa_fora_da_imagem(self):
        resposta = json.loads(self.exemplo["messages"][2]["content"])
        resposta["valor_total"]["bbox"] = [190, 10, 50, 10]
        self.exemplo["messages"][2]["content"] = json.dumps(resposta)
        with self.assertRaisesRegex(ValueError, "Caixa fora"):
            verificar_exemplo(self.exemplo, self.dataset, self.paginas, self.ocr, self.prompt)

    def test_rejeita_documento_repetido_entre_conjuntos(self):
        for nome in ("train", "valid", "test"):
            (self.dataset / f"{nome}.jsonl").write_text(json.dumps(self.exemplo) + "\n", encoding="utf-8")
        self.assertEqual(verificar(self.dataset, self.paginas, self.ocr, self.prompt, self.dataset / "modelo"), 1)


if __name__ == "__main__":
    unittest.main()
