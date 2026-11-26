"""Objetivo: exportar um dataset visual anonimizado para o fluxo GitHub Actions.

Entradas: dataset privado já construído, consentimento público e variável explícita.
Processamento: copia imagens aprovações e reescreve JSONL com referências públicas.
Saídas: json/training/visual/dataset e json/training/visual/images.
"""

import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any

from treinamento_visual.ingest import config


ROOT = Path(__file__).resolve().parents[3]
PRIVATE_DATASET = ROOT / "data" / "treinamento" / "dataset"
PUBLIC_ROOT = ROOT / "json" / "training" / "visual"
PUBLIC_DATASET = PUBLIC_ROOT / "dataset"
PUBLIC_IMAGES = PUBLIC_ROOT / "images"
CONSENT = PUBLIC_ROOT / "consentimento_publicacao.json"


def export_public(private: Path = PRIVATE_DATASET, public: Path = PUBLIC_ROOT) -> int:
    if os.getenv("PUBLICAR_DATASET") != "1":
        print("Exportação bloqueada: defina PUBLICAR_DATASET=1 após revisão.", file=sys.stderr)
        return 1
    if not CONSENT.is_file():
        print("Exportação bloqueada: consentimento não encontrado.", file=sys.stderr)
        return 1
    consent = json.loads(CONSENT.read_text(encoding="utf-8"))
    if not (
        consent.get("aprovado") is True
        and consent.get("anonimizacao_revisada") is True
    ):
        print("Exportação bloqueada: consentimento não aprovado ou anonimização não marcada.", file=sys.stderr)
        return 1
    if not private.is_dir():
        print("Dataset privado ausente. Execute build_dataset primeiro.", file=sys.stderr)
        return 1
    if (public / "dataset").exists():
        print("Dataset público já existe; remova manualmente após revisão.", file=sys.stderr)
        return 1

    dataset = public / "dataset"
    images = public / "images"
    dataset.mkdir(mode=0o700)
    images.mkdir(mode=0o700)
    counts = {}

    for name in ("train", "valid", "test"):
        source = private / f"{name}.jsonl"
        if not source.is_file():
            raise ValueError(f"Conjunto privado ausente: {name}.jsonl")
        exported = []
        for line in source.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row: dict[str, Any] = json.loads(line)
            public_images = []
            for image in row["images"]:
                parts = Path(image).parts
                document = next((part for part in parts if part.startswith("doc_")), None)
                if document is None:
                    raise ValueError("Imagem sem identificador de documento.")
                source_image = config.PAGINAS / document / "pagina_0001.png"
                if not source_image.is_file():
                    raise ValueError("Imagem privada não encontrada.")
                target = images / f"{document}_pagina_0001.png"
                if not target.exists():
                    shutil.copy2(source_image, target)
                public_images.append(target.name)
            row["images"] = public_images
            exported.append(row)
        (dataset / f"{name}.jsonl").write_text(
            "\n".join(json.dumps(row, ensure_ascii=False) for row in exported) + "\n",
            encoding="utf-8",
        )
        counts[name] = len(exported)
    print(json.dumps(counts, ensure_ascii=False, sort_keys=True))
    return 0


def main() -> int:
    try:
        return export_public()
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        print(f"Não foi possível exportar o dataset público ({type(error).__name__}).", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
