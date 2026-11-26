"""Objetivo: ativar somente um adaptador que passou na avaliação reservada.

Entradas: relatório de avaliação e limites mínimos.
Processamento: exige melhora sobre a base e quantidade mínima de documentos.
Saídas: modelo_aprovado.json ou bloqueio explícito.
"""

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
REPORT = ROOT / "json" / "training" / "visual" / "avaliacao_adaptador.json"
OUTPUT = ROOT / "json" / "training" / "visual" / "modelo_aprovado.json"


def approve(report: Path, output: Path, minimum_documents: int, minimum_gain: float) -> int:
    if not report.is_file():
        raise ValueError("Relatório de avaliação ausente.")
    data = json.loads(report.read_text(encoding="utf-8"))
    gain = data["adaptado_taxa_acerto"] - data["base_taxa_acerto"]
    approved = (
        data["documentos_testados"] >= minimum_documents
        and gain >= minimum_gain
        and data["adaptado_taxa_acerto"] >= 0.70
    )
    record = {
        "aprovado": approved,
        "documentos_testados": data["documentos_testados"],
        "base_taxa_acerto": data["base_taxa_acerto"],
        "adaptado_taxa_acerto": data["adaptado_taxa_acerto"],
        "ganho": round(gain, 4),
        "limites": {
            "documentos_minimos": minimum_documents,
            "ganho_minimo": minimum_gain,
            "taxa_minima_adaptado": 0.70,
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(record, ensure_ascii=False))
    return 0 if approved else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=REPORT)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--minimum-documents", type=int, default=10)
    parser.add_argument("--minimum-gain", type=float, default=0.10)
    args = parser.parse_args()
    try:
        return approve(args.report, args.output, args.minimum_documents, args.minimum_gain)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        print(f"Falha ao aprovar adaptador ({type(error).__name__}).", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
