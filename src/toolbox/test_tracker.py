"""Objetivo: executar a suíte unittest com registro opcional dos resultados.

Entradas: modo, seleção de testes e opções da linha de comando.
Processamento: executa unittest e registra a saída e o resultado observado.
Saídas: log, relatório JSON local e código de saída; não chama API diretamente.
"""

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

from .test_paths import EVALUATION_REPORTS_DIR


def executar_testes(comando: list[str], pasta: Path) -> int:
    """Executa unittest e registra o resultado sem mascarar falhas."""
    pasta.mkdir(parents=True, exist_ok=True)
    identificador = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    log = pasta / f"test_tracker_{identificador}.log"
    relatorio = pasta / f"test_execution_{identificador}.json"
    inicio = time.monotonic()
    try:
        resultado = subprocess.run(comando, capture_output=True, text=True, timeout=300)
        saida = resultado.stdout + resultado.stderr
        codigo = resultado.returncode
    except subprocess.TimeoutExpired:
        saida = "Os testes excederam o limite de 300 segundos.\n"
        codigo = 1
    except OSError as erro:
        saida = f"Não foi possível iniciar os testes: {erro}\n"
        codigo = 1
    log.write_text(saida, encoding="utf-8")
    relatorio.write_text(
        json.dumps(
            {
                "executado_em": datetime.now().isoformat(),
                "comando": comando,
                "codigo_saida": codigo,
                "duracao_segundos": round(time.monotonic() - inicio, 3),
                "log": str(log),
            },
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    print(saida, end="")
    print(f"Log: {log}\nRelatório: {relatorio}")
    return codigo


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m toolbox rastrear",
        description="Executa a suíte unittest e registra seus resultados.",
    )
    parser.add_argument("--mode", choices=("run", "test", "report", "help"), default="help")
    parser.add_argument("--name", help="Nome unittest completo para --mode test")
    parser.add_argument("--verbose", action="store_true", help="Exibe nomes dos testes")
    args = parser.parse_args(argv)
    if args.mode == "help":
        parser.print_help()
        return 0
    if args.mode == "report":
        reports = sorted(EVALUATION_REPORTS_DIR.glob("test_execution_*.json"))
        if not reports:
            parser.error("Nenhum relatório de execução encontrado.")
        print(reports[-1].read_text(encoding="utf-8"))
        return 0
    if args.mode == "test":
        if not args.name:
            parser.error("Use --name com o nome completo do teste unittest.")
        comando = [sys.executable, "-m", "unittest", args.name]
        if args.verbose:
            comando.append("-v")
    else:
        comando = [sys.executable, "-m", "unittest", "discover", "-s", "tests"]
        if args.verbose:
            comando.append("-v")
    return executar_testes(comando, EVALUATION_REPORTS_DIR)


if __name__ == "__main__":
    sys.exit(main())
