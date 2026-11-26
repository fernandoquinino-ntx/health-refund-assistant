"""Objetivo: centralizar a configuração do OCR de apoio.

Entradas: nenhuma. Processamento: define parâmetros comuns para renderização e OCR.
Saídas: constantes usadas pelo programa de ingestão.
"""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DATASET = ROOT / "data" / "treinamento"
ENTRADA = DATASET / "entrada"
PAGINAS = DATASET / "paginas" / "ocr_300dpi"
OCR = DATASET / "ocr"
LOG = DATASET / "logs" / "ingestao.log"
DPI = 300
PSM = 6
IDIOMA = "por"
