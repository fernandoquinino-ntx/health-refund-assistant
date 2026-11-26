# src/pdf_converter.py
"""Objetivo: preparar a imagem de um PDF para extração visual.

Entradas: caminho ou bytes de PDF.
Processamento: renderiza apenas a primeira página como JPEG.
Saídas: imagem codificada em Base64 ou erro de leitura/renderização.
"""

import base64
import pymupdf


def converter_primeira_pagina_pdf_base64(caminho_pdf: str) -> str:
  """Abre o PDF, renderiza a primeira página como imagem e devolve em Base64."""
  with pymupdf.open(caminho_pdf) as doc:
    pagina = doc.load_page(0)
    pix = pagina.get_pixmap(matrix=pymupdf.Matrix(2, 2))
    imagem_bytes = pix.tobytes("jpeg")
    return base64.b64encode(imagem_bytes).decode("utf-8")


def converter_pdf_bytes_primeira_pagina_base64(conteudo_pdf: bytes) -> str:
  """Renderiza a primeira página de um PDF carregado em memória."""
  with pymupdf.open(stream=conteudo_pdf, filetype="pdf") as doc:
    pagina = doc.load_page(0)
    pix = pagina.get_pixmap(matrix=pymupdf.Matrix(2, 2))
    imagem_bytes = pix.tobytes("jpeg")
    return base64.b64encode(imagem_bytes).decode("utf-8")