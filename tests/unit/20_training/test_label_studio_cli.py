"""Objetivo: verificar a execução local do Label Studio.

Entradas: argumentos e variáveis de ambiente simulados.
Processamento: intercepta o início do processo externo.
Saídas: asserções sobre privacidade e passagem de argumentos.
"""

import json
import os
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from unittest.mock import patch

from anotacao_documentos.cli import ROTULOS
from treinamento_visual.label.cli import POLITICA_REDE, SANDBOX, main, preparar


class LabelStudioCliTests(unittest.TestCase):
    def test_prepara_tarefas_locais_e_preserva_arquivo_existente(self):
        with tempfile.TemporaryDirectory() as temporario:
            root = Path(temporario)
            paginas, ocr = root / "paginas", root / "ocr"
            identificador = "doc_" + "a" * 64
            (paginas / identificador).mkdir(parents=True)
            (ocr / identificador).mkdir(parents=True)
            (ocr / identificador / "manifest.json").write_text(json.dumps({"paginas": 2}), encoding="utf-8")
            for numero in (1, 2):
                (paginas / identificador / f"pagina_{numero:04d}.png").write_bytes(b"imagem de teste")
            destino = root / "privado" / "tarefas.json"
            self.assertEqual(preparar(paginas, ocr, destino), 0)
            original = destino.read_text(encoding="utf-8")
            tarefas = json.loads(original)
            self.assertEqual(len(tarefas), 2)
            self.assertEqual([tarefa["data"]["pagina"] for tarefa in tarefas], [1, 2])
            url = urlparse(tarefas[0]["data"]["image"])
            self.assertEqual(url.path, "/data/local-files/")
            self.assertEqual(parse_qs(url.query)["d"], [f"{identificador}/pagina_0001.png"])
            self.assertEqual(preparar(paginas, ocr, destino), 1)
            self.assertEqual(destino.read_text(encoding="utf-8"), original)

    def test_nao_cria_tarefas_quando_falta_uma_pagina(self):
        with tempfile.TemporaryDirectory() as temporario:
            root = Path(temporario)
            paginas, ocr = root / "paginas", root / "ocr"
            identificador = "doc_" + "b" * 64
            (paginas / identificador).mkdir(parents=True)
            (ocr / identificador).mkdir(parents=True)
            (ocr / identificador / "manifest.json").write_text(json.dumps({"paginas": 2}), encoding="utf-8")
            (paginas / identificador / "pagina_0001.png").write_bytes(b"imagem de teste")
            destino = root / "privado" / "tarefas.json"
            self.assertEqual(preparar(paginas, ocr, destino), 1)
            self.assertFalse(destino.exists())

    def test_configuracao_usa_os_campos_do_dataset_com_transcricao_por_regiao(self):
        config = Path(__file__).resolve().parents[3] / "src/treinamento_visual/label/config.xml"
        root = ET.parse(config).getroot()
        imagem = root.find("Image")
        caixas = root.find("RectangleLabels")
        transcricao = root.find("TextArea")
        self.assertIsNotNone(imagem)
        self.assertIsNotNone(caixas)
        self.assertIsNotNone(transcricao)
        self.assertEqual(imagem.get("value"), "$image")
        self.assertEqual(caixas.get("toName"), imagem.get("name"))
        self.assertEqual({label.get("value") for label in caixas.findall("Label")}, ROTULOS)
        self.assertEqual(transcricao.get("toName"), imagem.get("name"))
        self.assertEqual(transcricao.get("perRegion"), "true")
        self.assertEqual(transcricao.get("required"), "true")

    def test_desativa_telemetria_e_preserva_argumentos(self):
        variables = {
            "LABEL_STUDIO_SENTRY_DSN": "https://example.invalid",
            "LABEL_STUDIO_FRONTEND_SENTRY_DSN": "https://example.invalid",
            "LABEL_STUDIO_COLLECT_ANALYTICS": "true",
            "LABEL_STUDIO_BASE_DATA_DIR": "/outro/local",
            "LABEL_STUDIO_DATABASE_NAME": "/outro/banco",
            "LABEL_STUDIO_DJANGO_DB": "postgresql",
        }
        variables["HTTPS_PROXY"] = "http://127.0.0.1:8080"
        with patch.dict(os.environ, variables), patch(
            "sys.argv", ["cli", "--version"]
        ), patch("sys.platform", "darwin"), patch.object(Path, "is_file", return_value=True), \
                patch("os.execve") as execute:
            main()

        executable, arguments, environment = execute.call_args.args
        self.assertEqual(executable, SANDBOX)
        self.assertEqual(arguments[:3], [SANDBOX, "-p", POLITICA_REDE])
        self.assertEqual(arguments[-3:], ["version", "--internal-host", "127.0.0.1"])
        self.assertNotIn("HTTPS_PROXY", environment)
        self.assertEqual(environment["LABEL_STUDIO_SENTRY_DSN"], "")
        self.assertEqual(environment["LABEL_STUDIO_FRONTEND_SENTRY_DSN"], "")
        self.assertEqual(environment["LABEL_STUDIO_COLLECT_ANALYTICS"], "false")
        self.assertEqual(environment["LABEL_STUDIO_FEATURE_FLAGS_OFFLINE"], "true")
        self.assertEqual(environment["LABEL_STUDIO_LATEST_VERSION_CHECK"], "false")
        self.assertTrue(environment["LABEL_STUDIO_BASE_DATA_DIR"].endswith("/data/treinamento/label_studio"))
        self.assertEqual(environment["LABEL_STUDIO_DJANGO_DB"], "sqlite")
        self.assertEqual(
            environment["LABEL_STUDIO_DATABASE_NAME"],
            environment["LABEL_STUDIO_BASE_DATA_DIR"] + "/label_studio.sqlite3",
        )

    def test_servidor_fica_restrito_ao_localhost(self):
        with patch("sys.argv", ["cli", "start", "--internal-host", "0.0.0.0"]), \
                patch("sys.platform", "darwin"), patch.object(Path, "is_file", return_value=True), \
                patch("os.execve") as execute:
            main()

        arguments = execute.call_args.args[1]
        self.assertEqual(arguments[-2:], ["--internal-host", "127.0.0.1"])

    def test_nao_inicia_sem_sandbox_disponivel(self):
        with patch("sys.argv", ["cli", "start"]), patch("sys.platform", "linux"), \
                patch("os.execve") as execute:
            self.assertEqual(main(), 1)
        execute.assert_not_called()


if __name__ == "__main__":
    unittest.main()
