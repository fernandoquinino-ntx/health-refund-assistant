"""Objetivo: verificar a proteção do exportador de datasets visualmente anonimizados.

Entradas: diretórios temporários e consentimento falso.
Processamento: chama o exportador sem criar arquivos reais.
Saídas: asserções sobre bloqueio explícito.
"""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from treinamento_visual.train.export_public_dataset import export_public


class ExportPublicDatasetTests(unittest.TestCase):
    def test_bloqueia_sem_consentimento(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with patch.dict("os.environ", {}, clear=True):
                self.assertEqual(export_public(root / "privado", root / "publico"), 1)


if __name__ == "__main__":
    unittest.main()
