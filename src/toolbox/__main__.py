"""Objetivo: oferecer uma entrada única para as ferramentas do projeto.

Entradas: comando e respectivos argumentos.
Processamento: encaminha a execução à ferramenta escolhida.
Saídas: mensagens, arquivos e erros gerados pela ferramenta.
"""

import argparse


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "comando",
        choices=(
            "avaliar",
            "gerar_fixtures",
            "rastrear",
            "setup_app",
            "setup_training",
            "setup_conversion",
            "setup_label",
            "setup_codespace",
            "build_extension",
            "start_local_vlm",
            "start_assistant",
            "converter_modelo",
        ),
    )
    parser.add_argument("argumentos", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    if args.comando == "avaliar":
        from .case_evaluation import main as executar
    elif args.comando == "gerar_fixtures":
        from .gerar_fixtures_sinteticas import main as executar
    elif args.comando == "rastrear":
        from .test_tracker import main as executar
    elif args.comando == "setup_app":
        from .operacoes import setup_app as executar
    elif args.comando == "setup_training":
        from .operacoes import setup_training as executar
    elif args.comando == "setup_conversion":
        from .operacoes import setup_conversion as executar
    elif args.comando == "setup_label":
        from .operacoes import setup_label as executar
    elif args.comando == "setup_codespace":
        from .operacoes import setup_codespace as executar
    elif args.comando == "build_extension":
        from .operacoes import build_extension as executar
    elif args.comando == "start_local_vlm":
        from .operacoes import start_local_vlm as executar
    elif args.comando == "converter_modelo":
        from .operacoes import converter_modelo as executar
    else:
        from .operacoes import start_assistant as executar
    if args.comando in {
        "setup_app",
        "setup_training",
        "setup_conversion",
        "setup_label",
        "setup_codespace",
        "build_extension",
        "start_local_vlm",
        "start_assistant",
        "converter_modelo",
    }:
        resultado = executar()
    else:
        resultado = executar(args.argumentos)
    return resultado if resultado is not None else 0


if __name__ == "__main__":
    raise SystemExit(main())
