"""Objetivo: converter anotações do Label Studio em exemplos de treinamento visual.

Entradas: banco SQLite do Label Studio, páginas OCR e prompt registrado.
Processamento: associa caixas e transcrições e separa exemplos por documento.
Saídas: JSONL local em data/treinamento/dataset.
"""

import argparse
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any

from anotacao_documentos.cli import ROTULOS
from treinamento_visual.ingest import config


ROOT = Path(__file__).resolve().parents[3]
DATABASE = ROOT / "data" / "treinamento" / "label_studio" / "label_studio.sqlite3"
PROMPT = ROOT / "prompts" / "treinamento_visual" / "extract_v1.txt"
DATASET = ROOT / "data" / "treinamento" / "dataset"


def _percentual_para_pixels(value: dict[str, Any], largura: int, altura: int) -> list[int]:
    return [
        round(value["x"] * largura / 100),
        round(value["y"] * altura / 100),
        round(value["width"] * largura / 100),
        round(value["height"] * altura / 100),
    ]


def _linha_ocr(palavras: list[dict[str, Any]], bbox: list[int]) -> str | None:
    x, y, width, height = bbox
    direita, inferior = x + width, y + height
    candidatos = []
    for palavra in palavras:
        px, py, pw, ph = palavra["bbox"]
        inter_width = max(0, min(direita, px + pw) - max(x, px))
        inter_height = max(0, min(inferior, py + ph) - max(y, py))
        if inter_width * inter_height > 0:
            candidatos.append(palavra)
    linhas = {palavra["linha"] for palavra in candidatos}
    return next(iter(linhas)) if len(linhas) == 1 else None


def build(dataset: Path = DATASET, database: Path = DATABASE) -> int:
    if dataset.exists():
        raise ValueError("O diretório do dataset já existe.")
    if database.is_symlink():
        raise ValueError("O banco do Label Studio não pode ser link simbólico.")
    dataset.mkdir(mode=0o700)

    prompt = PROMPT.read_text(encoding="utf-8")
    connection = sqlite3.connect(database)
    try:
        rows = connection.execute(
            "SELECT id, data FROM task WHERE project_id = 1 ORDER BY id"
        ).fetchall()
        if len(rows) != 6:
            raise ValueError("São necessárias exatamente seis tarefas.")

        examples = []
        for task_id, task_data in rows:
            data = json.loads(task_data)
            documento = data["documento"]
            pagina = data["pagina"]
            if not isinstance(pagina, int) or pagina != 1:
                raise ValueError("Somente páginas únicas são suportadas.")

            source = config.PAGINAS / documento / f"pagina_{pagina:04d}.png"
            ocr_dir = config.OCR / documento
            if source.is_symlink() or not source.is_file():
                raise ValueError("Imagem não encontrada.")
            annotation_rows = connection.execute(
                "SELECT result FROM task_completion WHERE task_id = ? ORDER BY id",
                (task_id,),
            ).fetchall()
            if not annotation_rows:
                raise ValueError("A tarefa não possui anotação.")

            ocr_page = json.loads((ocr_dir / f"pagina_{pagina:04d}.json").read_text(encoding="utf-8"))
            ocr_text = (ocr_dir / f"pagina_{pagina:04d}.txt").read_text(encoding="utf-8").rstrip("\n")
            boxes = {}
            texts = {}
            for (result_json,) in annotation_rows:
                for item in json.loads(result_json):
                    item_id = item["id"]
                    if item["type"] == "rectanglelabels":
                        boxes[item_id] = (item["value"]["rectanglelabels"][0], item["value"])
                    elif item["type"] == "textarea":
                        texts[item_id] = item["value"]["text"][0]

            answer = {field: None for field in ROTULOS}
            for item_id, (label, value) in boxes.items():
                text = texts.get(item_id)
                if not text:
                    continue
                bbox = _percentual_para_pixels(
                    value, ocr_page["largura"], ocr_page["altura"]
                )
                answer[label] = {
                    "valor": text,
                    "pagina": pagina,
                    "linha": _linha_ocr(ocr_page["palavras"], bbox),
                    "bbox": bbox,
                }

            image_target = dataset / "paginas" / documento / f"pagina_{pagina:04d}.png"
            image_target.parent.mkdir(mode=0o700, parents=True)
            if not image_target.exists():
                image_target.write_bytes(source.read_bytes())
            examples.append({
                "images": [f"paginas/{documento}/pagina_{pagina:04d}.png"],
                "messages": [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": ocr_text},
                    {"role": "assistant", "content": json.dumps(answer, ensure_ascii=False)},
                ],
            })
    finally:
        connection.close()

    for name, items in (("train", examples[:4]), ("valid", examples[4:5]), ("test", examples[5:6])):
        with (dataset / f"{name}.jsonl").open("x", encoding="utf-8") as output:
            for example in items:
                output.write(json.dumps(example, ensure_ascii=False) + "\n")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    try:
        return build()
    except (OSError, sqlite3.Error, ValueError, KeyError, TypeError) as error:
        print(f"Não foi possível criar o dataset ({type(error).__name__}).", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
