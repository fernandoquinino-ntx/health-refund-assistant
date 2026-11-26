"""Objetivo: iniciar o programa de anotação de documentos.

Entradas: argumentos do comando. Processamento: delega ao módulo CLI.
Saídas: mensagens, arquivos ou erros produzidos pelo comando escolhido.
"""

import sys

from .cli import main


if __name__ == "__main__":
    sys.exit(main())
