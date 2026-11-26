"""Objetivo: oferecer uma entrada única para as ferramentas do projeto.

Entradas: comando e respectivos argumentos.
Processamento: encaminha a execução à ferramenta escolhida.
Saídas: mensagens, arquivos e erros gerados pela ferramenta.
"""

import argparse


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("comando", choices=("avaliar", "gerar_fixtures", "rastrear"))
    parser.add_argument("argumentos", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    if args.comando == "avaliar":
        from .case_evaluation import main as executar
    elif args.comando == "gerar_fixtures":
        from .gerar_fixtures_sinteticas import main as executar
    else:
        from .test_tracker import main as executar
    resultado = executar(args.argumentos)
    return resultado if resultado is not None else 0


if __name__ == "__main__":
    raise SystemExit(main())
