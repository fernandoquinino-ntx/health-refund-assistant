"""Objetivo: treinar SmolVLM no GitHub Actions com dataset explicitamente aprovado.

Entradas: JSONL train/valid/test, imagens anonimizadas e consentimento JSON.
Processamento: aplica LoRA ao modelo SmolVLM com PyTorch no runner Linux.
Saídas: adaptador local, relatório privado do runner e artefato de Actions.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
CONSENT = ROOT / "json" / "training" / "visual" / "consentimento_publicacao.json"
DATASET = ROOT / "json" / "training" / "visual" / "dataset"
IMAGES = ROOT / "json" / "training" / "visual" / "images"
OUTPUT = ROOT / "models" / "adapters" / "smolvlm_ci"


def consentimento_aprovado(path: Path = CONSENT) -> bool:
    if not path.is_file():
        return False
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return data.get("aprovado") is True


def validate_dataset(dataset_root: Path, images_root: Path) -> dict[str, int]:
    counts = {}
    for name in ("train", "valid", "test"):
        path = dataset_root / f"{name}.jsonl"
        if not path.is_file():
            raise ValueError(f"Conjunto ausente: {name}.jsonl")
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        if not rows:
            raise ValueError(f"Conjunto vazio: {name}.jsonl")
        for row in rows:
            if not isinstance(row.get("images"), list) or not row["images"]:
                raise ValueError("Exemplo sem imagem.")
            for image in row["images"]:
                image_path = (images_root / image).resolve()
                if not image_path.is_file():
                    raise ValueError("Imagem do dataset não encontrada.")
        counts[name] = len(rows)
    return counts


def dry_run(dataset_root: Path, images_root: Path) -> int:
    if not consentimento_aprovado():
        print("Treino bloqueado: consentimento_publicacao.json não foi aprovado.", file=sys.stderr)
        return 1
    try:
        counts = validate_dataset(dataset_root, images_root)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"Dataset inválido: {error}", file=sys.stderr)
        return 1
    print(json.dumps(counts, ensure_ascii=False, sort_keys=True))
    return 0


def train(dataset_root: Path, images_root: Path, output: Path) -> int:
    if not consentimento_aprovado():
        print("Treino bloqueado: consentimento não aprovado.", file=sys.stderr)
        return 1
    validate_dataset(dataset_root, images_root)

    import torch
    from peft import LoraConfig, get_peft_model
    from PIL import Image
    from transformers import AutoModelForImageTextToText, AutoProcessor
    from huggingface_hub import snapshot_download

    model_id = "HuggingFaceTB/SmolVLM-256M-Instruct"
    base_path = ROOT / "models" / "smolvlm-hf"
    snapshot_download(
        repo_id=model_id,
        local_dir=str(base_path),
        local_dir_use_symlinks=False,
    )
    processor = AutoProcessor.from_pretrained(str(base_path), local_files_only=True)
    model = AutoModelForImageTextToText.from_pretrained(
        str(base_path),
        dtype=torch.float32,
        low_cpu_mem_usage=True,
        local_files_only=True,
    )
    lora = LoraConfig(
        r=8,
        lora_alpha=16,
        lora_dropout=0.05,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        bias="none",
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora)
    model.train()
    optimizer = torch.optim.AdamW(model.parameters(), lr=2e-5)

    train_rows = [
        json.loads(line)
        for line in (dataset_root / "train.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    losses = []
    for step, row in enumerate(train_rows * 3):
        image_path = (images_root / row["images"][0]).resolve()
        messages = row["messages"]
        text = processor.apply_chat_template(messages, add_generation_prompt=False)
        batch = processor(
            text=text,
            images=[Image.open(image_path).convert("RGB")],
            return_tensors="pt",
            truncation=True,
            max_length=2048,
        )
        labels = batch["input_ids"].clone()
        batch["labels"] = labels
        batch = {key: value for key, value in batch.items()}
        optimizer.zero_grad()
        result = model(**batch)
        loss = result.loss
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        losses.append(float(loss.detach()))
        if len(losses) >= 12:
            break

    output.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(output)
    processor.save_pretrained(output)
    report = {
        "model": model_id,
        "iterations": len(losses),
        "train_rows": len(train_rows),
        "losses": losses,
        "output": str(output),
    }
    (output / "training_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--dataset-root", type=Path, default=DATASET)
    parser.add_argument("--images-root", type=Path, default=IMAGES)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    if args.dry_run:
        return dry_run(args.dataset_root, args.images_root)
    try:
        return train(args.dataset_root, args.images_root, args.output)
    except (OSError, ValueError, KeyError, json.JSONDecodeError, ImportError) as error:
        print(f"Falha no treino visual ({type(error).__name__}): {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
