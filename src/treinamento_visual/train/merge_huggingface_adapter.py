"""Objetivo: fundir um adaptador PEFT SmolVLM em pesos Hugging Face.

Entradas: modelo base Hugging Face e diretório com adapter_config/adaptador.
Processamento: carrega PEFT, funde os pesos e salva um modelo standalone.
Saídas: diretório com pesos Hugging Face fusos para conversão GGUF.
"""

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def merge(base: Path, adapter: Path, output: Path) -> int:
    if not base.is_dir():
        raise ValueError("Diretório do modelo base ausente.")
    if not adapter.is_dir():
        raise ValueError("Diretório do adaptador ausente.")
    if output.exists():
        raise ValueError("O destino já existe.")

    import torch
    from peft import PeftModel
    from transformers import AutoModelForImageTextToText, AutoProcessor

    model = AutoModelForImageTextToText.from_pretrained(
        str(base),
        dtype=torch.float32,
        low_cpu_mem_usage=True,
    )
    model = PeftModel.from_pretrained(model, str(adapter))
    model = model.merge_and_unload()
    processor = AutoProcessor.from_pretrained(str(base), local_files_only=True)
    output.mkdir(parents=True)
    model.save_pretrained(output)
    processor.save_pretrained(output)
    print(output)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=ROOT / "models" / "smolvlm-hf")
    parser.add_argument("--adapter", type=Path, default=ROOT / "models" / "adapters" / "smolvlm_ci")
    parser.add_argument("--output", type=Path, default=ROOT / "models" / "smolvlm-hf-fused")
    args = parser.parse_args()
    try:
        return merge(args.base, args.adapter, args.output)
    except (OSError, ValueError, ImportError, RuntimeError) as error:
        print(f"Falha ao fundir o adaptador ({type(error).__name__}).", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
