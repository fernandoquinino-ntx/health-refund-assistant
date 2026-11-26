"""Objetivo: iniciar o OCR local de apoio ao treinamento visual.

Entradas: PDFs e imagens locais e configuração de ingestão. Processamento: chama o pipeline.
Saídas: imagens e OCR locais ou erro de execução.
"""

import sys

from .ocr import main


if __name__ == "__main__":
    sys.exit(main())
