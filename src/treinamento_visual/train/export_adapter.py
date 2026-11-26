"""Objetivo: fundir um adaptador LoRA em uma pasta de modelo MLX independente.

Entradas: modelo base MLX e adapter.safetensors.
Processamento: carrega o adaptador, funde os pesos e exporta um modelo standalone.
Saídas: diretório local com pesos, configuração e processador.
"""

import argparse
import shutil
import sys
from pathlib import Path

from mlx_vlm import load
from mlx_vlm.export import export_model
from mlx_vlm.trainer.peft import apply_lora_layers


ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "models" / "base-smol"
ADAPTER = ROOT / "adapters" / "smolvlm-teste" / "adapters.safetensors"
OUTPUT = ROOT / "models" / "smolvlm-fused"


def export_fused(base: Path, adapter: Path, output: Path) -> int:
    if not base.is_dir() or not (base / "config.json").is_file():
        raise ValueError("Modelo base indisponível.")
    if not adapter.is_file():
        raise ValueError("Adaptador indisponível.")
    if output.exists():
        raise ValueError("O destino já existe.")

    model, processor = load(str(base), adapter_path=None)
    model = apply_lora_layers(model, str(adapter.parent))
    result = export_model(
        model,
        processor,
        str(output),
        model_path=str(base),
        quantize=False,
    )
    print(result)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=BASE)
    parser.add_argument("--adapter", type=Path, default=ADAPTER)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    try:
        return export_fused(args.base, args.adapter, args.output)
    except (OSError, ValueError, RuntimeError) as error:
        print(f"Não foi possível exportar o adaptador ({type(error).__name__}).", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
