"""Objetivo: preparar e conferir anotações para um dataset visual privado.

Entradas: PDFs locais, imagens, anotações LabelMe e argumentos do comando.
Processamento: renderiza páginas, registra revisões e valida anotações.
Saídas: imagens, JSONs locais e mensagens de validação; não treina modelos.
"""

import argparse
import hashlib
import json
import math
import re
import sys
import tempfile
from pathlib import Path

import pymupdf


ROOT = Path(__file__).resolve().parents[2]
DATASET = ROOT / "data" / "treinamento"
ENTRADA = DATASET / "entrada"
PAGINAS = DATASET / "paginas"
ROTULOS = {
    "numero_documento", "prestador", "cnpj_cpf_prestador", "valor_total",
    "data_emissao", "data_atendimento", "nome_profissional",
    "descricao_servico", "registro_profissional",
}


def preparar(entrada: Path, paginas: Path) -> int:
    """Renderiza cada PDF uma vez, sem substituir imagens ou anotações."""
    entrada.mkdir(parents=True, exist_ok=True)
    paginas.mkdir(parents=True, exist_ok=True)
    arquivos = sorted(p for p in entrada.iterdir() if p.suffix.lower() == ".pdf")
    novos = existentes = falhas = 0
    for arquivo in arquivos:
        try:
            if arquivo.is_symlink() or not arquivo.is_file():
                raise ValueError("A entrada deve ser um arquivo regular, não um link.")
            conteudo = arquivo.read_bytes()
            identificador = "doc_" + hashlib.sha256(conteudo).hexdigest()
            destino = paginas / identificador
            if destino.exists() or destino.is_symlink():
                print(f"{identificador}: já preparado; preservado.")
                existentes += 1
                continue
            with pymupdf.open(stream=conteudo, filetype="pdf") as documento:
                if documento.needs_pass:
                    raise ValueError("PDF protegido por senha.")
                if documento.page_count == 0:
                    raise ValueError("PDF sem páginas.")
                with tempfile.TemporaryDirectory(prefix=".preparando_", dir=paginas) as temporario:
                    pasta = Path(temporario)
                    for numero, pagina in enumerate(documento, start=1):
                        imagem = pagina.get_pixmap(matrix=pymupdf.Matrix(2, 2), alpha=False)
                        imagem.save(str(pasta / f"pagina_{numero:04d}.png"))
                    (pasta / "total_paginas.txt").write_text(
                        str(documento.page_count), encoding="utf-8"
                    )
                    pasta.rename(destino)
            print(f"{identificador}: preparado.")
            novos += 1
        except (OSError, ValueError, RuntimeError) as erro:
            print(f"Falha ao preparar um PDF ({type(erro).__name__}): {erro}", file=sys.stderr)
            falhas += 1
    print(f"Preparados: {novos}; já existentes: {existentes}; falhas: {falhas}.")
    return 1 if falhas else 0


def erros_anotacao(imagem: Path, anotacao: dict) -> list[str]:
    """Confere estrutura e geometria, sem comprovar a correção humana."""
    erros = []
    if anotacao.get("imagePath") != imagem.name:
        erros.append("imagePath não corresponde à imagem")
    pixmap = pymupdf.Pixmap(str(imagem))
    largura, altura = pixmap.width, pixmap.height
    if anotacao.get("imageWidth") != largura or anotacao.get("imageHeight") != altura:
        erros.append("dimensões não correspondem à imagem")
    shapes = anotacao.get("shapes")
    if not isinstance(shapes, list):
        return erros + ["shapes deve ser uma lista"]
    for indice, shape in enumerate(shapes, start=1):
        prefixo = f"região {indice}"
        if not isinstance(shape, dict):
            erros.append(f"{prefixo}: estrutura inválida")
            continue
        rotulo = shape.get("label")
        if not isinstance(rotulo, str) or rotulo not in ROTULOS:
            erros.append(f"{prefixo}: rótulo desconhecido")
        descricao = shape.get("description")
        if not isinstance(descricao, str) or not descricao.strip():
            erros.append(f"{prefixo}: transcrição ausente em description")
        pontos = shape.get("points")
        if (
            shape.get("shape_type") != "rectangle"
            or not isinstance(pontos, list)
            or len(pontos) != 2
            or any(
                not isinstance(p, list) or len(p) != 2
                or any(isinstance(v, bool) or not isinstance(v, (int, float))
                       or (isinstance(v, float) and not math.isfinite(v)) for v in p)
                for p in pontos
            )
        ):
            erros.append(f"{prefixo}: retângulo inválido")
            continue
        (x1, y1), (x2, y2) = pontos
        if not (0 <= x1 <= largura and 0 <= x2 <= largura
                and 0 <= y1 <= altura and 0 <= y2 <= altura
                and x1 != x2 and y1 != y2):
            erros.append(f"{prefixo}: retângulo vazio ou fora da imagem")
    return erros


def verificar(paginas: Path) -> int:
    """Verifica páginas e sidecars LabelMe sem imprimir os valores anotados."""
    documentos = sorted(paginas.glob("doc_*"))
    if not documentos:
        print("Nenhum documento encontrado. Execute primeiro o comando preparar.", file=sys.stderr)
        return 1
    falhas = 0
    imagens = []
    for documento in documentos:
        try:
            if documento.is_symlink() or not documento.is_dir():
                raise ValueError("diretório inválido")
            total = int((documento / "total_paginas.txt").read_text(encoding="utf-8"))
            if total <= 0:
                raise ValueError("quantidade de páginas inválida")
            esperadas = {f"pagina_{numero:04d}.png" for numero in range(1, total + 1)}
            encontradas = {imagem.name for imagem in documento.glob("pagina_*.png")}
            if encontradas != esperadas:
                raise ValueError("páginas ausentes ou inesperadas")
            imagens.extend(documento / nome for nome in sorted(esperadas))
        except (OSError, ValueError) as erro:
            print(f"{documento.name}: {erro}", file=sys.stderr)
            falhas += 1
    for imagem in imagens:
        sidecar = imagem.with_suffix(".json")
        try:
            if not sidecar.is_file():
                raise ValueError("anotação JSON ausente")
            with sidecar.open(encoding="utf-8") as arquivo:
                anotacao = json.load(arquivo)
            if not isinstance(anotacao, dict):
                raise ValueError("anotação não é um objeto JSON")
            erros = erros_anotacao(imagem, anotacao)
            if erros:
                raise ValueError("; ".join(erros))
        except (OSError, ValueError, RuntimeError) as erro:
            print(f"{imagem.parent.name}/{imagem.name}: {erro}", file=sys.stderr)
            falhas += 1
    print(f"Páginas verificadas: {len(imagens)}; documentos ou páginas com problemas: {falhas}.")
    return 1 if falhas else 0


def marcar_sem_campos(imagem: Path, paginas: Path) -> int:
    """Registra uma página revisada sem campos, sem sobrescrever anotações."""
    try:
        if imagem.is_symlink() or imagem.parent.is_symlink():
            raise ValueError("links simbólicos não são permitidos")
        relativa = imagem.resolve().relative_to(paginas.resolve())
        if (len(relativa.parts) != 2 or not relativa.parts[0].startswith("doc_")
                or not re.fullmatch(r"pagina_\d{4,}\.png", relativa.name)):
            raise ValueError("a imagem deve ser uma página do dataset")
        pixmap = pymupdf.Pixmap(str(imagem))
        anotacao = {
            "version": "5.0.1", "flags": {}, "shapes": [],
            "imagePath": imagem.name, "imageData": None,
            "imageHeight": pixmap.height, "imageWidth": pixmap.width,
        }
        with imagem.with_suffix(".json").open("x", encoding="utf-8") as arquivo:
            json.dump(anotacao, arquivo, ensure_ascii=False, indent=2)
        print("Página revisada sem campos registrada.")
        return 0
    except (OSError, ValueError, RuntimeError) as erro:
        print(f"Não foi possível registrar a página: {erro}", file=sys.stderr)
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("comando", choices=("preparar", "verificar", "sem_campos"))
    parser.add_argument("imagem", nargs="?", type=Path, help="Página revisada sem campos")
    args = parser.parse_args()
    if DATASET.parent.is_symlink() or DATASET.is_symlink() or ENTRADA.is_symlink() or PAGINAS.is_symlink():
        parser.error("As pastas do dataset não podem ser links simbólicos.")
    if (args.comando == "sem_campos") != (args.imagem is not None):
        parser.error("Informe uma imagem somente para o comando sem_campos.")
    if args.comando == "preparar":
        DATASET.mkdir(mode=0o700, parents=True, exist_ok=True)
        return preparar(ENTRADA, PAGINAS)
    if args.comando == "sem_campos":
        assert args.imagem is not None
        return marcar_sem_campos(args.imagem, PAGINAS)
    return verificar(PAGINAS)


if __name__ == "__main__":
    sys.exit(main())
