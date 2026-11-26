"""Objetivo: comparar modelo base e adaptador em um conjunto reservado.

Entradas: JSONL test, imagens, modelo Hugging Face e adaptador PEFT.
Processamento: gera JSON por campo e calcula acertos exatos e JSON válido.
Saídas: relatório JSON local; não ativa o adaptador automaticamente.
"""

import argparse
import json
import sys
from pathlib import Path

from anotacao_documentos.cli import ROTULOS


ROOT = Path(__file__).resolve().parents[3]
DATASET = ROOT / "json" / "training" / "visual" / "dataset"
IMAGES = ROOT / "json" / "training" / "visual" / "images"
BASE = ROOT / "models" / "smolvlm-hf"
ADAPTER = ROOT / "models" / "adapters" / "smolvlm_ci"
REPORT = ROOT / "json" / "training" / "visual" / "avaliacao_adaptador.json"


def gerar(processor, model, image_path: Path, prompt: str) -> dict:
    from PIL import Image

    image = Image.open(image_path).convert("RGB")
    messages = [{"role": "user", "content": prompt}]
    text = processor.apply_chat_template(messages, add_generation_prompt=True)
    inputs = processor(text=text, images=[image], return_tensors="pt")
    inputs = {key: value.to(model.device) for key, value in inputs.items()}
    output = model.generate(**inputs, max_new_tokens=600, temperature=0.0)
    text_output = processor.batch_decode(output, skip_special_tokens=True)[0]
    inicio, fim = text_output.find("{"), text_output.rfind("}")
    if inicio < 0 or fim <= inicio:
        return {}
    try:
        return json.loads(text_output[inicio:fim + 1])
    except json.JSONDecodeError:
        return {}


def evaluate(dataset: Path, images: Path, base: Path, adapter: Path, report: Path) -> int:
    test_path = dataset / "test.jsonl"
    if not test_path.is_file():
        raise ValueError("Conjunto test.jsonl ausente.")

    import torch
    from peft import PeftModel
    from transformers import AutoModelForImageTextToText, AutoProcessor

    processor = AutoProcessor.from_pretrained(str(base), local_files_only=True)
    base_model = AutoModelForImageTextToText.from_pretrained(
        str(base),
        dtype=torch.float32,
        low_cpu_mem_usage=True,
    )
    tuned_model = PeftModel.from_pretrained(base_model, str(adapter))

    rows = [
        json.loads(line)
        for line in test_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    expected_total = valid_json = 0
    base_hits = tuned_hits = 0
    exemplos = []

    from health_refund_assistant.core.prompt_library import carregar_prompt
    prompt, _ = carregar_prompt("avaliacao_visual", "v1.0")

    for row in rows:
        expected = json.loads(row["messages"][2]["content"])
        image_path = (images / row["images"][0]).resolve()
        base_result = gerar(processor, base_model, image_path, prompt)
        tuned_result = gerar(processor, tuned_model, image_path, prompt)
        base_ok = tuned_ok = 0
        for field in ROTULOS:
            expected_value = expected.get(field)
            if expected_value is not None:
                expected_total += 1
                if isinstance(base_result, dict) and base_result.get(field) == expected_value:
                    base_hits += 1
                if isinstance(tuned_result, dict) and tuned_result.get(field) == expected_value:
                    tuned_hits += 1
            if isinstance(base_result, dict):
                base_ok += 1
            if isinstance(tuned_result, dict):
                tuned_ok += 1
        valid_json += 1 if isinstance(base_result, dict) and set(base_result) else 0
        valid_json += 1 if isinstance(tuned_result, dict) and set(tuned_result) else 0
        exemplos.append({
            "base_valid_json": bool(base_result),
            "adaptado_valid_json": bool(tuned_result),
        })

    result = {
        "documentos_testados": len(rows),
        "campos_esperados": expected_total,
        "base_acertos": base_hits,
        "adaptado_acertos": tuned_hits,
        "base_taxa_acerto": round(base_hits / expected_total, 4) if expected_total else 0,
        "adaptado_taxa_acerto": round(tuned_hits / expected_total, 4) if expected_total else 0,
        "exemplos": exemplos,
    }
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=DATASET)
    parser.add_argument("--images", type=Path, default=IMAGES)
    parser.add_argument("--base", type=Path, default=BASE)
    parser.add_argument("--adapter", type=Path, default=ADAPTER)
    parser.add_argument("--report", type=Path, default=REPORT)
    args = parser.parse_args()
    try:
        return evaluate(args.dataset, args.images, args.base, args.adapter, args.report)
    except (OSError, ValueError, ImportError, RuntimeError) as error:
        print(f"Falha na avaliação ({type(error).__name__}).", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
