"""Objetivo: verificar o gate que autoriza ativação de adaptadores.

Entradas: relatório fictício de avaliação.
Processamento: aplica limites mínimos sem usar modelos reais.
Saídas: aprovação ou rejeição determinística.
"""

import json
import tempfile
import unittest
from pathlib import Path

from treinamento_visual.train.approve_adapter import approve


class AdapterApprovalTests(unittest.TestCase):
    def test_rejeita_adaptador_sem_ganho(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            report = root / "report.json"
            output = root / "approved.json"
            report.write_text(json.dumps({
                "documentos_testados": 12,
                "base_taxa_acerto": 0.75,
                "adaptado_taxa_acerto": 0.76,
            }), encoding="utf-8")
            self.assertEqual(approve(report, output, 10, 0.10), 1)
            self.assertFalse(json.loads(output.read_text())["aprovado"])

    def test_aprova_adaptador_com_ganho_suficiente(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            report = root / "report.json"
            output = root / "approved.json"
            report.write_text(json.dumps({
                "documentos_testados": 20,
                "base_taxa_acerto": 0.50,
                "adaptado_taxa_acerto": 0.75,
            }), encoding="utf-8")
            self.assertEqual(approve(report, output, 10, 0.10), 0)
            self.assertTrue(json.loads(output.read_text())["aprovado"])


if __name__ == "__main__":
    unittest.main()
