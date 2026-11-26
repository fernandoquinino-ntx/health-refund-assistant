"""Objetivo: verificar o OCR localizado e a preservação das saídas.

Entradas: respostas simuladas do OCR e documentos temporários de teste.
Processamento: confere agrupamento, renderização e repetição da ingestão.
Saídas: asserções para o runner de testes, sem uso de dados reais.
"""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from PIL import Image

from treinamento_visual.ingest import config
from treinamento_visual.ingest.ocr import processar, reconstruir


def resposta_ocr():
    return {
        "text": ["", "final", "valor", "data"],
        "left": [0, 140, 10, 10],
        "top": [0, 50, 50, 10],
        "width": [0, 40, 40, 40],
        "height": [0, 10, 10, 10],
        "block_num": [0, 1, 1, 1],
        "par_num": [0, 1, 1, 1],
        "line_num": [0, 2, 2, 1],
        "conf": [-1, 85.0, 90.0, 70.0],
    }


class IngestaoOcrTests(unittest.TestCase):
    def test_reconstroi_linhas_em_ordem_com_coordenadas_e_colunas(self):
        palavras, linhas = reconstruir(resposta_ocr(), 2)
        self.assertEqual([linha["id"] for linha in linhas], ["L001", "L002"])
        self.assertEqual([palavra["texto"] for palavra in palavras], ["data", "valor", "final"])
        self.assertEqual(linhas[1]["bbox"], [10, 50, 170, 10])
        self.assertEqual(palavras[1]["linha"], "L002")
        self.assertEqual(palavras[2]["bbox"], [140, 50, 40, 10])
        self.assertGreater(linhas[1]["texto"].index("final") - linhas[1]["texto"].index("valor"), 5)

    def test_gera_paginas_e_preserva_resultados_em_repeticao(self):
        with tempfile.TemporaryDirectory() as temporario:
            root = Path(temporario)
            entrada, paginas, ocr, log = root / "entrada", root / "paginas", root / "ocr", root / "logs" / "erro.log"
            entrada.mkdir()
            (entrada / "teste.pdf").write_bytes(b"pdf de teste")
            imagem = MagicMock(width=200, height=300)
            imagem.save.side_effect = lambda caminho: Path(caminho).write_bytes(b"imagem de teste")
            pagina = MagicMock()
            pagina.get_pixmap.return_value = imagem
            documento = MagicMock(needs_pass=False, page_count=1)
            documento.__iter__.return_value = iter([pagina])
            with patch("treinamento_visual.ingest.ocr.pymupdf.open") as abrir, \
                 patch("treinamento_visual.ingest.ocr.pytesseract.get_tesseract_version", return_value="5.5.4"), \
                 patch("treinamento_visual.ingest.ocr.pytesseract.image_to_data", return_value=resposta_ocr()) as tesseract:
                abrir.return_value.__enter__.return_value = documento
                self.assertEqual(processar(entrada, paginas, ocr, log), 0)
                pasta_ocr = next(p for p in ocr.iterdir() if p.name.startswith("doc_"))
                resultado = json.loads((pasta_ocr / "pagina_0001.json").read_text(encoding="utf-8"))
                origem = json.loads((pasta_ocr / "origem.json").read_text(encoding="utf-8"))
                self.assertEqual(origem["arquivo_entrada"], "teste.pdf")
                self.assertEqual(resultado["linhas"][1]["id"], "L002")
                self.assertIn("[p1 L002 y=50]", (pasta_ocr / "pagina_0001.txt").read_text(encoding="utf-8"))
                pagina.get_pixmap.assert_called_once_with(dpi=300, alpha=False)
                self.assertEqual(tesseract.call_args.kwargs["lang"], "por")
                self.assertEqual(tesseract.call_args.kwargs["config"], "--psm 6 -c preserve_interword_spaces=1")
                self.assertEqual(processar(entrada, paginas, ocr, log), 0)
                self.assertEqual(tesseract.call_count, 1)
                with patch.object(config, "DPI", 200):
                    self.assertEqual(processar(entrada, paginas, ocr, log), 1)
                self.assertTrue((pasta_ocr / "pagina_0001.json").exists())
                self.assertTrue(log.is_file())

    def test_processa_jpeg_com_orientacao_e_preserva_resolucao(self):
        with tempfile.TemporaryDirectory() as temporario:
            root = Path(temporario)
            entrada, paginas, ocr, log = root / "entrada", root / "paginas", root / "ocr", root / "logs" / "erro.log"
            entrada.mkdir()
            exif = Image.Exif()
            exif[274] = 6
            Image.new("RGB", (200, 300), "white").save(entrada / "foto.JPG", exif=exif)
            with patch("treinamento_visual.ingest.ocr.pytesseract.get_tesseract_version", return_value="5.5.4"), \
                 patch("treinamento_visual.ingest.ocr.pytesseract.image_to_data", return_value=resposta_ocr()) as tesseract:
                self.assertEqual(processar(entrada, paginas, ocr, log), 0)
                pasta_ocr = next(p for p in ocr.iterdir() if p.name.startswith("doc_"))
                manifesto = json.loads((pasta_ocr / "manifest.json").read_text(encoding="utf-8"))
                self.assertEqual(manifesto["tipo_entrada"], "imagem")
                self.assertIsNone(manifesto["dpi"])
                with Image.open(paginas / pasta_ocr.name / "pagina_0001.png") as pagina:
                    self.assertEqual(pagina.size, (300, 200))
                self.assertEqual(processar(entrada, paginas, ocr, log), 0)
                self.assertEqual(tesseract.call_count, 1)

    def test_png_transparente_e_renderizado_sobre_branco(self):
        with tempfile.TemporaryDirectory() as temporario:
            root = Path(temporario)
            entrada, paginas, ocr, log = root / "entrada", root / "paginas", root / "ocr", root / "logs" / "erro.log"
            entrada.mkdir()
            Image.new("RGBA", (200, 300), (0, 0, 0, 0)).save(entrada / "foto.png")
            with patch("treinamento_visual.ingest.ocr.pytesseract.get_tesseract_version", return_value="5.5.4"), \
                 patch("treinamento_visual.ingest.ocr.pytesseract.image_to_data", return_value=resposta_ocr()):
                self.assertEqual(processar(entrada, paginas, ocr, log), 0)
            pasta = next(p for p in paginas.iterdir() if p.name.startswith("doc_"))
            with Image.open(pasta / "pagina_0001.png") as pagina:
                self.assertEqual(pagina.size, (200, 300))
                self.assertEqual(pagina.getpixel((0, 0)), (255, 255, 255))


if __name__ == "__main__":
    unittest.main()
