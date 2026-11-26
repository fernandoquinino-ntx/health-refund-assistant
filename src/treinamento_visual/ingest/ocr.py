"""Objetivo: preparar imagens e OCR localizado para treinamento visual.

Entradas: PDFs e imagens locais e configuração de renderização e Tesseract.
Processamento: prepara páginas, reconhece palavras e reconstrói linhas.
Saídas: imagens, JSONs e textos privados; erros detalhados ficam em log local.
"""

import hashlib
import json
import os
import statistics
import sys
import tempfile
import traceback
from pathlib import Path
from typing import Any

import pymupdf
import pytesseract
from PIL import Image, ImageOps

from . import config


def reconstruir(dados: dict[str, list[Any]], pagina: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Agrupa palavras por linha do Tesseract e preserva suas posições em pixels."""
    grupos: dict[tuple[int, int, int], list[dict[str, Any]]] = {}
    for indice, texto_bruto in enumerate(dados["text"]):
        texto = str(texto_bruto).strip()
        if not texto:
            continue
        x, y = int(dados["left"][indice]), int(dados["top"][indice])
        largura, altura = int(dados["width"][indice]), int(dados["height"][indice])
        if x < 0 or y < 0 or largura <= 0 or altura <= 0:
            raise ValueError("O Tesseract retornou coordenadas inválidas.")
        bloco = int(dados["block_num"][indice])
        paragrafo = int(dados["par_num"][indice])
        linha = int(dados["line_num"][indice])
        palavra = {
            "texto": texto,
            "bbox": [x, y, largura, altura],
            "bloco": bloco,
            "paragrafo": paragrafo,
            "linha_tesseract": linha,
            "confianca": float(dados["conf"][indice]),
        }
        grupos.setdefault((bloco, paragrafo, linha), []).append(palavra)

    linhas_ordenadas = sorted(
        grupos.values(),
        key=lambda palavras: (
            min(p["bbox"][1] for p in palavras),
            min(p["bbox"][0] for p in palavras),
        ),
    )
    larguras = [
        p["bbox"][2] / len(p["texto"])
        for palavras in linhas_ordenadas for p in palavras
    ]
    largura_caractere = max(1.0, statistics.median(larguras)) if larguras else 1.0
    palavras_saida: list[dict[str, Any]] = []
    linhas_saida: list[dict[str, Any]] = []
    for numero, palavras in enumerate(linhas_ordenadas, start=1):
        palavras.sort(key=lambda palavra: palavra["bbox"][0])
        identificador = f"L{numero:03d}"
        x_min = min(p["bbox"][0] for p in palavras)
        y_min = min(p["bbox"][1] for p in palavras)
        x_max = max(p["bbox"][0] + p["bbox"][2] for p in palavras)
        y_max = max(p["bbox"][1] + p["bbox"][3] for p in palavras)
        texto_linha = ""
        for palavra in palavras:
            posicao = round(palavra["bbox"][0] / largura_caractere)
            espacos = max(1 if texto_linha else 0, posicao - len(texto_linha))
            texto_linha += " " * espacos + palavra["texto"]
            palavra["linha"] = identificador
            palavras_saida.append(palavra)
        linhas_saida.append({
            "id": identificador,
            "pagina": pagina,
            "bbox": [x_min, y_min, x_max - x_min, y_max - y_min],
            "texto": texto_linha,
        })
    return palavras_saida, linhas_saida


def _identificador(arquivo: Path) -> str:
    resumo = hashlib.sha256()
    with arquivo.open("rb") as entrada:
        for trecho in iter(lambda: entrada.read(1024 * 1024), b""):
            resumo.update(trecho)
    return "doc_" + resumo.hexdigest()


def _registrar_erro(log: Path, erro: Exception) -> None:
    log.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    descritor = os.open(log, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    with os.fdopen(descritor, "a", encoding="utf-8") as arquivo:
        traceback.print_exception(type(erro), erro, erro.__traceback__, file=arquivo)


def _salvar_origem(pasta_ocr: Path, nome_arquivo: str) -> None:
    origem = pasta_ocr / "origem.json"
    if origem.is_symlink():
        raise ValueError("O registro de origem não pode ser um link simbólico.")
    if origem.exists():
        registro = json.loads(origem.read_text(encoding="utf-8"))
        if not isinstance(registro, dict) or not isinstance(registro.get("arquivo_entrada"), str):
            raise ValueError("O registro de origem existente é inválido.")
        return
    with origem.open("x", encoding="utf-8") as arquivo:
        json.dump({"arquivo_entrada": nome_arquivo}, arquivo, ensure_ascii=False, indent=2)


def _ja_preparado(paginas: Path, ocr: Path, versao: str, tipo: str) -> bool:
    if not paginas.exists() and not ocr.exists() and not paginas.is_symlink() and not ocr.is_symlink():
        return False
    if paginas.is_symlink() or ocr.is_symlink() or not paginas.is_dir() or not ocr.is_dir():
        raise ValueError("Saída existente incompleta ou inválida; não será substituída.")
    manifesto_path = ocr / "manifest.json"
    if manifesto_path.is_symlink():
        raise ValueError("O manifesto não pode ser um link simbólico.")
    manifest = json.loads(manifesto_path.read_text(encoding="utf-8"))
    total = manifest["paginas"]
    dpi = config.DPI if tipo == "pdf" else None
    if manifest.get("tipo_entrada", "pdf") != tipo or (
        manifest["dpi"], manifest["psm"], manifest["idioma"]
    ) != (dpi, config.PSM, config.IDIOMA):
        raise ValueError("A configuração da saída existente é diferente; não será substituída.")
    if manifest["tesseract"] != versao:
        raise ValueError("A versão do Tesseract é diferente; a saída não será substituída.")
    if not isinstance(total, int) or isinstance(total, bool) or total <= 0:
        raise ValueError("Manifesto de páginas inválido.")
    for numero in range(1, total + 1):
        nome = f"pagina_{numero:04d}"
        if not all(p.is_file() and not p.is_symlink() for p in (
            paginas / f"{nome}.png", ocr / f"{nome}.json", ocr / f"{nome}.txt"
        )):
            raise ValueError("Saída existente incompleta; não será substituída.")
        resultado = json.loads((ocr / f"{nome}.json").read_text(encoding="utf-8"))
        if resultado["pagina"] != numero or not isinstance(resultado["palavras"], list) or not isinstance(resultado["linhas"], list):
            raise ValueError("Resultado OCR existente inválido; não será substituído.")
    return True


def _processar_pagina(imagem: Path, tamanho: tuple[int, int], numero: int, pasta_ocr: Path) -> bool:
    dados = pytesseract.image_to_data(
        str(imagem),
        lang=config.IDIOMA,
        config=f"--psm {config.PSM} -c preserve_interword_spaces=1",
        output_type=pytesseract.Output.DICT,
    )
    palavras, linhas = reconstruir(dados, numero)
    resultado = {
        "pagina": numero,
        "largura": tamanho[0],
        "altura": tamanho[1],
        "palavras": palavras,
        "linhas": linhas,
    }
    nome = f"pagina_{numero:04d}"
    (pasta_ocr / f"{nome}.json").write_text(
        json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    texto = "\n".join(
        f"[p{numero} {linha['id']} y={linha['bbox'][1]}] {linha['texto']}"
        for linha in linhas
    )
    (pasta_ocr / f"{nome}.txt").write_text(texto + ("\n" if texto else ""), encoding="utf-8")
    return not palavras


def processar(entrada: Path, paginas: Path, ocr: Path, log: Path) -> int:
    """Processa documentos locais sem substituir resultados anteriores."""
    for caminho in (entrada, paginas, ocr, log.parent):
        if caminho.is_symlink():
            raise ValueError("As pastas de entrada e saída não podem ser links simbólicos.")
        caminho.mkdir(mode=0o700, parents=True, exist_ok=True)
    if log.is_symlink():
        raise ValueError("O log não pode ser um link simbólico.")
    arquivos = sorted(p for p in entrada.iterdir() if p.suffix.lower() in {".pdf", ".jpg", ".jpeg", ".png"})
    if not arquivos:
        print("Nenhum PDF ou imagem JPG/PNG encontrado na pasta de entrada.", file=sys.stderr)
        return 1
    versao = str(pytesseract.get_tesseract_version())
    novos = existentes = falhas = paginas_sem_texto = 0
    for numero_documento, arquivo in enumerate(arquivos, start=1):
        etapa = "validação"
        try:
            if arquivo.is_symlink() or not arquivo.is_file():
                raise ValueError("A entrada deve ser um arquivo regular, não um link.")
            identificador = _identificador(arquivo)
            tipo = "pdf" if arquivo.suffix.lower() == ".pdf" else "imagem"
            destino_paginas, destino_ocr = paginas / identificador, ocr / identificador
            if _ja_preparado(destino_paginas, destino_ocr, versao, tipo):
                _salvar_origem(destino_ocr, arquivo.name)
                existentes += 1
                continue
            etapa = "renderização e OCR"
            with tempfile.TemporaryDirectory(prefix=".preparando_", dir=paginas) as temp_paginas, \
                 tempfile.TemporaryDirectory(prefix=".preparando_", dir=ocr) as temp_ocr:
                pasta_paginas, pasta_ocr = Path(temp_paginas), Path(temp_ocr)
                sem_texto_documento = 0
                if tipo == "pdf":
                    with pymupdf.open(str(arquivo)) as documento:
                        if documento.needs_pass:
                            raise ValueError("PDF protegido por senha.")
                        if documento.page_count <= 0:
                            raise ValueError("PDF sem páginas.")
                        total_paginas = documento.page_count
                        for numero, pagina in enumerate(documento, start=1):
                            imagem = pagina.get_pixmap(dpi=config.DPI, alpha=False)
                            imagem_path = pasta_paginas / f"pagina_{numero:04d}.png"
                            imagem.save(str(imagem_path))
                            sem_texto_documento += _processar_pagina(
                                imagem_path, (imagem.width, imagem.height), numero, pasta_ocr
                            )
                else:
                    with Image.open(arquivo) as original:
                        if original.format not in {"JPEG", "PNG"} or getattr(original, "n_frames", 1) != 1:
                            raise ValueError("A imagem deve ser um JPEG ou PNG de um único quadro.")
                        imagem = ImageOps.exif_transpose(original).convert("RGBA")
                        fundo = Image.new("RGBA", imagem.size, "white")
                        fundo.alpha_composite(imagem)
                        imagem_rgb = fundo.convert("RGB")
                        imagem_path = pasta_paginas / "pagina_0001.png"
                        imagem_rgb.save(imagem_path, format="PNG")
                        sem_texto_documento += _processar_pagina(imagem_path, imagem_rgb.size, 1, pasta_ocr)
                    total_paginas = 1
                manifesto = {
                    "tipo_entrada": tipo,
                    "paginas": total_paginas,
                    "dpi": config.DPI if tipo == "pdf" else None,
                    "psm": config.PSM,
                    "idioma": config.IDIOMA,
                    "tesseract": versao,
                }
                (pasta_ocr / "manifest.json").write_text(
                    json.dumps(manifesto, ensure_ascii=False, indent=2), encoding="utf-8"
                )
                _salvar_origem(pasta_ocr, arquivo.name)
                etapa = "publicação das saídas"
                pasta_paginas.rename(destino_paginas)
                pasta_ocr.rename(destino_ocr)
            paginas_sem_texto += sem_texto_documento
            novos += 1
        except (
            OSError, ValueError, RuntimeError, KeyError, TypeError, IndexError,
            Image.DecompressionBombError, pytesseract.TesseractError,
        ) as erro:
            _registrar_erro(log, erro)
            print(
                f"Documento {numero_documento}: falha em {etapa} ({type(erro).__name__}); "
                "detalhes no log privado de ingestão.",
                file=sys.stderr,
            )
            falhas += 1
    print(
        f"Documentos preparados: {novos}; preservados: {existentes}; falhas: {falhas}; "
        f"páginas novas sem texto OCR: {paginas_sem_texto}."
    )
    return 1 if falhas else 0


def main() -> int:
    if any(caminho.is_symlink() for caminho in (
        config.DATASET.parent, config.DATASET, config.PAGINAS.parent
    )):
        raise ValueError("As pastas do dataset não podem ser links simbólicos.")
    return processar(config.ENTRADA, config.PAGINAS, config.OCR, config.LOG)
