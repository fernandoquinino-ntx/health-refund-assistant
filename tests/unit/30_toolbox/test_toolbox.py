"""Objetivo: verificar o rastreamento de testes da toolbox.

Entradas: diretórios temporários e resultados simulados de unittest.
Processamento: confere comandos, relatórios e códigos de falha.
Saídas: asserções de sucesso ou falha para o runner de testes.
"""

import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from toolbox.__main__ import main as toolbox_main
from toolbox.test_tracker import main


class ToolboxTrackerTests(unittest.TestCase):
    def test_build_extension_creates_chrome_zip_and_sha256(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "src" / "extension"
            source.mkdir(parents=True)
            (source / "manifest.json").write_text(
                json.dumps({
                    "manifest_version": 3,
                    "name": "Teste",
                    "version": "1.2.3",
                    "background": {"service_worker": "20_background/background.js"},
                    "action": {"default_popup": "10_popup/popup.html"},
                    "content_scripts": [{"js": ["30_content/bridge.js"]}],
                }),
                encoding="utf-8",
            )
            for origem in (
                "10_popup/popup.html",
                "10_popup/popup.js",
                "20_background/background.js",
                "30_content/bridge.js",
                "40_collector/collector.js",
                "60_schemas/export.schema.json",
            ):
                destination = source / origem
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_text("teste", encoding="utf-8")
            with patch("toolbox.operacoes.ROOT", root):
                from toolbox.operacoes import build_extension
                self.assertEqual(build_extension(), 0)
            package = root / "build" / "care-plus-reembolsos-1.2.3.zip"
            checksum = root / "build" / "care-plus-reembolsos-1.2.3.sha256"
            self.assertTrue(package.is_file())
            self.assertTrue(checksum.is_file())
            with zipfile.ZipFile(package) as archive:
                names = set(archive.namelist())
            self.assertIn("manifest.json", names)
            self.assertIn("20_background/background.js", names)
            self.assertIn("30_content/bridge.js", names)
            self.assertIn("40_collector/collector.js", names)

    def test_toolbox_restart_assistant_calls_restart_operation(self):
        with (
            patch("sys.argv", ["toolbox", "restart_assistant"]),
            patch("toolbox.operacoes.restart_assistant", return_value=0) as executar,
        ):
            self.assertEqual(toolbox_main(), 0)
            executar.assert_called_once_with()

    def test_toolbox_build_extension_calls_operation_without_arguments(self):
        with (
            patch("sys.argv", ["toolbox", "build_extension"]),
            patch("toolbox.operacoes.build_extension", return_value=0) as executar,
        ):
            self.assertEqual(toolbox_main(), 0)
            executar.assert_called_once_with()

    def test_toolbox_propagates_tracker_exit_code(self):
        with (
            patch("sys.argv", ["toolbox", "rastrear", "--mode", "run"]),
            patch("toolbox.test_tracker.main", return_value=3),
        ):
            self.assertEqual(toolbox_main(), 3)

    def test_run_uses_unittest_and_propagates_failure(self):
        with tempfile.TemporaryDirectory() as diretorio:
            pasta = Path(diretorio)
            falha = subprocess.CompletedProcess([], 3, stdout="saída\n", stderr="falha\n")
            with (
                patch("toolbox.test_tracker.EVALUATION_REPORTS_DIR", pasta),
                patch("toolbox.test_tracker.subprocess.run", return_value=falha) as executar,
                contextlib.redirect_stdout(io.StringIO()),
            ):
                self.assertEqual(main(["--mode", "run", "--verbose"]), 3)
                self.assertEqual(main(["--mode", "report"]), 0)
            comando = executar.call_args.args[0]
            self.assertEqual(comando, [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"])
            relatorio = json.loads(next(pasta.glob("test_execution_*.json")).read_text())
            self.assertEqual(relatorio["codigo_saida"], 3)
            self.assertEqual(next(pasta.glob("*.log")).read_text(), "saída\nfalha\n")

    def test_timeout_returns_failure_and_writes_report(self):
        with tempfile.TemporaryDirectory() as diretorio:
            pasta = Path(diretorio)
            with (
                patch("toolbox.test_tracker.EVALUATION_REPORTS_DIR", pasta),
                patch("toolbox.test_tracker.subprocess.run", side_effect=subprocess.TimeoutExpired("unittest", 300)),
                contextlib.redirect_stdout(io.StringIO()),
            ):
                self.assertEqual(main(["--mode", "run"]), 1)
            relatorio = json.loads(next(pasta.glob("test_execution_*.json")).read_text())
            self.assertEqual(relatorio["codigo_saida"], 1)


if __name__ == "__main__":
    unittest.main()
