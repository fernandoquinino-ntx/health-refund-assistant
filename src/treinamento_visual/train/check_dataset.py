"""Objetivo: verificar o dataset local de treinamento visual.

Entradas: JSONL por conjunto, imagens e OCR locais, prompt e processador do modelo.
Processamento: confere estrutura, separação por documento, origem OCR e tokens.
Saídas: contagens e divergências sem exibir dados dos documentos; erros retornam falha.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from anotacao_documentos.cli import ROTULOS
from treinamento_visual.ingest import config


ROOT = Path(__file__).resolve().parents[3]
PROMPT = ROOT / "prompts" / "treinamento_visual" / "extract_v1.txt"
DATASET = config.DATASET / "dataset"
MODELO = ROOT / "models" / "base"


def _intersecao(a: list[int], b: list[int]) -> bool:
    largura = max(0, min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0]))
    altura = max(0, min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1]))
    return 2 * largura * altura >= b[2] * b[3] > 0


def _normalizar_espacos(texto: str) -> str:
    return " ".join(texto.split())


def verificar_exemplo(
    exemplo: dict[str, Any], dataset: Path, paginas: Path, ocr: Path, prompt: str
) -> tuple[str, int, int]:
    """Valida um documento e conta campos verificados e divergentes no OCR."""
    imagens = exemplo.get("images")
    mensagens = exemplo.get("messages")
    if not isinstance(imagens, list) or not imagens or not all(isinstance(p, str) for p in imagens):
        raise ValueError("A lista de imagens é obrigatória.")
    if not isinstance(mensagens, list) or len(mensagens) != 3:
        raise ValueError("São necessárias mensagens de sistema, usuário e assistente.")
    for mensagem, papel in zip(mensagens, ("system", "user", "assistant")):
        if not isinstance(mensagem, dict) or mensagem.get("role") != papel or not isinstance(mensagem.get("content"), str):
            raise ValueError("Mensagem ou papel inválido.")
    if mensagens[0]["content"] != prompt:
        raise ValueError("O prompt de sistema não corresponde à versão registrada.")

    pasta_paginas = paginas.resolve()
    caminhos: list[Path] = []
    for imagem in imagens:
        caminho = dataset / imagem
        if caminho.is_symlink() or caminho.parent.is_symlink():
            raise ValueError("Imagens e suas pastas não podem ser links simbólicos.")
        caminho = caminho.resolve(strict=True)
        if caminho.parent.parent != pasta_paginas or not re.fullmatch(r"doc_[0-9a-f]{64}", caminho.parent.name):
            raise ValueError("A imagem não pertence à pasta local de páginas.")
        caminhos.append(caminho)
    identificador = caminhos[0].parent.name
    if any(caminho.parent.name != identificador for caminho in caminhos):
        raise ValueError("As imagens devem pertencer ao mesmo documento.")
    pasta_ocr = ocr / identificador
    if pasta_ocr.is_symlink() or not pasta_ocr.is_dir():
        raise ValueError("A pasta OCR do documento é inválida.")
    manifesto = json.loads((pasta_ocr / "manifest.json").read_text(encoding="utf-8"))
    total = manifesto["paginas"]
    if not isinstance(total, int) or isinstance(total, bool) or total <= 0:
        raise ValueError("Quantidade de páginas inválida.")
    esperadas = [pasta_paginas / identificador / f"pagina_{numero:04d}.png" for numero in range(1, total + 1)]
    if caminhos != esperadas:
        raise ValueError("As imagens não correspondem a todas as páginas, em ordem.")
    paginas_ocr = []
    textos = []
    for numero in range(1, total + 1):
        nome = f"pagina_{numero:04d}"
        paginas_ocr.append(json.loads((pasta_ocr / f"{nome}.json").read_text(encoding="utf-8")))
        textos.append((pasta_ocr / f"{nome}.txt").read_text(encoding="utf-8").rstrip("\n"))
    if mensagens[1]["content"] != "\n".join(textos):
        raise ValueError("O texto de entrada não corresponde ao OCR local.")

    resposta = json.loads(mensagens[2]["content"])
    if not isinstance(resposta, dict) or set(resposta) != ROTULOS:
        raise ValueError("O JSON de resposta deve conter exatamente os campos definidos.")
    verificados = divergentes = 0
    for campo, valor in resposta.items():
        if valor is None:
            continue
        if not isinstance(valor, dict) or set(valor) != {"valor", "pagina", "linha", "bbox"}:
            raise ValueError(f"Estrutura inválida no campo {campo}.")
        transcricao, numero, linha, bbox = valor["valor"], valor["pagina"], valor["linha"], valor["bbox"]
        if not isinstance(transcricao, str) or not transcricao.strip():
            raise ValueError(f"Transcrição vazia no campo {campo}.")
        if not isinstance(numero, int) or isinstance(numero, bool) or not 1 <= numero <= total:
            raise ValueError(f"Página inválida no campo {campo}.")
        if not isinstance(bbox, list) or len(bbox) != 4 or any(not isinstance(v, int) or isinstance(v, bool) for v in bbox):
            raise ValueError(f"Caixa inválida no campo {campo}.")
        pagina_ocr = paginas_ocr[numero - 1]
        x, y, largura, altura = bbox
        if not (0 <= x < x + largura <= pagina_ocr["largura"] and 0 <= y < y + altura <= pagina_ocr["altura"]):
            raise ValueError(f"Caixa fora da imagem no campo {campo}.")
        if linha is None:
            divergentes += 1
            continue
        if not isinstance(linha, str):
            raise ValueError(f"Linha inválida no campo {campo}.")
        linhas = {item["id"]: item for item in pagina_ocr["linhas"]}
        if linha not in linhas:
            raise ValueError(f"Linha inexistente no campo {campo}.")
        palavras = [
            item for item in pagina_ocr["palavras"]
            if item["linha"] == linha and _intersecao(bbox, item["bbox"])
        ]
        palavras.sort(key=lambda item: item["bbox"][0])
        reconhecido = " ".join(item["texto"] for item in palavras)
        if _normalizar_espacos(transcricao) == _normalizar_espacos(reconhecido):
            verificados += 1
        else:
            divergentes += 1
    return identificador, verificados, divergentes


def verificar(dataset: Path, paginas: Path, ocr: Path, prompt: str, modelo: Path) -> int:
    """Verifica os conjuntos e mede tokens usando o processador local do modelo."""
    conjuntos: dict[str, list[dict[str, Any]]] = {}
    documentos: set[str] = set()
    total_verificados = total_divergentes = 0
    for nome in ("train", "valid", "test"):
        arquivo = dataset / f"{nome}.jsonl"
        try:
            linhas = arquivo.read_text(encoding="utf-8").splitlines()
            if not linhas:
                raise ValueError("Conjunto vazio.")
            exemplos = []
            for linha in linhas:
                exemplo = json.loads(linha)
                if not isinstance(exemplo, dict):
                    raise ValueError("Exemplo deve ser um objeto JSON.")
                identificador, verificados, divergentes = verificar_exemplo(exemplo, dataset, paginas, ocr, prompt)
                if identificador in documentos:
                    raise ValueError("Documento repetido entre exemplos ou conjuntos.")
                documentos.add(identificador)
                total_verificados += verificados
                total_divergentes += divergentes
                exemplos.append(exemplo)
            conjuntos[nome] = exemplos
        except (OSError, ValueError, KeyError, TypeError, IndexError) as erro:
            detalhe = str(erro) if isinstance(erro, ValueError) else type(erro).__name__
            print(f"Falha no conjunto {nome}: {detalhe}.", file=sys.stderr)
            return 1
    print(
        f"Documentos: {len(documentos)}; treino: {len(conjuntos['train'])}; "
        f"validação: {len(conjuntos['valid'])}; teste: {len(conjuntos['test'])}; "
        f"campos conferidos com OCR: {total_verificados}; divergências para revisão: {total_divergentes}."
    )
    if not modelo.is_dir() or not (modelo / "config.json").is_file():
        print("Processador do modelo local indisponível; tokens não foram medidos.", file=sys.stderr)
        return 1

    from mlx_vlm.trainer.vlm.cross_entropy.dataset import VisionDataset
    from mlx_vlm.utils import load_config, load_processor

    try:
        configuracao = load_config(modelo)
        processador = load_processor(modelo, add_detokenizer=False, local_files_only=True)
        maximo = 0
        for exemplos in conjuntos.values():
            dados = VisionDataset(exemplos, configuracao, processador, base_path=dataset)
            for indice in range(len(dados)):
                maximo = max(maximo, int(dados[indice]["input_ids"].shape[0]))
    except (OSError, ValueError, KeyError, TypeError, RuntimeError) as erro:
        print(f"Falha ao medir tokens ({type(erro).__name__}).", file=sys.stderr)
        return 1
    print(f"Maior sequência, incluindo tokens visuais: {maximo}.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--modelo", type=Path, default=MODELO, help="Diretório local do modelo e processador.")
    args = parser.parse_args()
    try:
        prompt = PROMPT.read_text(encoding="utf-8")
    except OSError as erro:
        print(f"Não foi possível ler o prompt ({type(erro).__name__}).", file=sys.stderr)
        return 1
    return verificar(DATASET, config.PAGINAS, config.OCR, prompt, args.modelo)


if __name__ == "__main__":
    sys.exit(main())
