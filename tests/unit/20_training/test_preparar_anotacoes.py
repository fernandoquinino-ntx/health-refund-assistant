"""Objetivo: verificar a preparação e conferência de anotações visuais.

Entradas: arquivos temporários, anotações e renderização simulada.
Processamento: testa preparação, preservação e validação de páginas.
Saídas: asserções de sucesso ou falha para o runner de testes.
"""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from anotacao_documentos.cli import erros_anotacao, marcar_sem_campos, preparar, verificar


class PrepararAnotacoesTests(unittest.TestCase):
    def test_prepara_todas_as_paginas_e_preserva_anotacoes(self):
        with tempfile.TemporaryDirectory() as temporario:
            root = Path(temporario)
            entrada, paginas = root / "entrada", root / "paginas"
            entrada.mkdir()
            (entrada / "arquivo.pdf").write_bytes(b"conteudo de teste")
            documento = MagicMock()
            documento.needs_pass = False
            documento.page_count = 2
            pagina = MagicMock()
            pagina.get_pixmap.return_value.save.side_effect = (
                lambda caminho: Path(caminho).write_bytes(b"imagem de teste")
            )
            documento.__iter__.return_value = iter([pagina, pagina])
            with patch("anotacao_documentos.cli.pymupdf.open") as abrir:
                abrir.return_value.__enter__.return_value = documento
                self.assertEqual(preparar(entrada, paginas), 0)
                pasta = next(paginas.iterdir())
                self.assertEqual(
                    sorted(p.name for p in pasta.iterdir()),
                    ["pagina_0001.png", "pagina_0002.png", "total_paginas.txt"],
                )
                anotacao = pasta / "pagina_0001.json"
                anotacao.write_text("anotação preservada", encoding="utf-8")
                self.assertEqual(preparar(entrada, paginas), 0)
                self.assertEqual(anotacao.read_text(encoding="utf-8"), "anotação preservada")
                self.assertEqual(abrir.call_count, 1)

    def test_falha_na_renderizacao_nao_deixa_documento_parcial(self):
        with tempfile.TemporaryDirectory() as temporario:
            root = Path(temporario)
            entrada, paginas = root / "entrada", root / "paginas"
            entrada.mkdir()
            (entrada / "arquivo.pdf").write_bytes(b"conteudo de teste")
            documento = MagicMock()
            documento.needs_pass = False
            documento.page_count = 1
            documento.__iter__.side_effect = RuntimeError("erro de renderização")
            with patch("anotacao_documentos.cli.pymupdf.open") as abrir:
                abrir.return_value.__enter__.return_value = documento
                self.assertEqual(preparar(entrada, paginas), 1)
            self.assertEqual(list(paginas.iterdir()), [])

    @patch("anotacao_documentos.cli.pymupdf.Pixmap")
    def test_valida_rotulos_transcricao_e_caixas(self, pixmap):
        pixmap.return_value.width = 100
        pixmap.return_value.height = 200
        imagem = Path("pagina_0001.png")
        anotacao = {
            "imagePath": imagem.name,
            "imageWidth": 100,
            "imageHeight": 200,
            "shapes": [{
                "label": "valor_total",
                "description": "123,45",
                "shape_type": "rectangle",
                "points": [[5, 6], [70, 80]],
            }],
        }
        self.assertEqual(erros_anotacao(imagem, anotacao), [])
        anotacao["shapes"][0].update(label="desconhecido", description="", points=[[0, 0], [101, 2]])
        self.assertEqual(len(erros_anotacao(imagem, anotacao)), 3)
        anotacao["shapes"][0]["label"] = []
        self.assertIn("região 1: rótulo desconhecido", erros_anotacao(imagem, anotacao))

    @patch("anotacao_documentos.cli.pymupdf.Pixmap")
    def test_verifica_sidecar_ausente_e_pagina_sem_campos(self, pixmap):
        pixmap.return_value.width = 100
        pixmap.return_value.height = 200
        with tempfile.TemporaryDirectory() as temporario:
            pasta = Path(temporario) / "doc_teste"
            pasta.mkdir()
            (pasta / "total_paginas.txt").write_text("2", encoding="utf-8")
            imagem = pasta / "pagina_0001.png"
            imagem.write_bytes(b"imagem de teste")
            self.assertEqual(verificar(Path(temporario)), 1)
            (pasta / "total_paginas.txt").write_text("1", encoding="utf-8")
            self.assertEqual(verificar(Path(temporario)), 1)
            self.assertEqual(marcar_sem_campos(imagem, Path(temporario)), 0)
            self.assertEqual(verificar(Path(temporario)), 0)
            self.assertEqual(marcar_sem_campos(imagem, Path(temporario)), 1)
            self.assertEqual(json.loads(imagem.with_suffix(".json").read_text())["shapes"], [])


if __name__ == "__main__":
    unittest.main()
