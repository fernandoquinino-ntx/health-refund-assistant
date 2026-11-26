"""Objetivo: importar e disponibilizar exportações do plano de saúde.

Entradas: arquivos JSON ou caminhos selecionados.
Processamento: valida conteúdo e período, salva ou carrega exportações.
Saídas: caminhos e dados das exportações ou erros de importação.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
from zoneinfo import ZoneInfo

from .assessment import ExportPeriodError, validar_periodo_exportacao
from ..core.paths import PLAN_EXPORTS_DIR


def import_plan_export(name: str, content: bytes) -> Path:
    safe_name = Path(name).name
    if not safe_name.lower().endswith(".json"):
        raise ValueError("A exportação do plano deve ser um arquivo JSON.")
    try:
        exportacao = json.loads(content)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("O arquivo enviado não contém JSON válido.") from error
    if not isinstance(exportacao, dict):
        raise ExportPeriodError("A raiz da exportação deve ser um objeto JSON.")
    validar_periodo_exportacao(exportacao, safe_name)

    PLAN_EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    imported_at = datetime.now(ZoneInfo("America/Sao_Paulo"))
    timestamp = imported_at.strftime("%Y%m%d-%H%M%S")
    exportacao["importado_em"] = imported_at.isoformat()
    stored_content = (
        json.dumps(exportacao, ensure_ascii=False, indent=2).encode("utf-8")
    )
    destination = PLAN_EXPORTS_DIR / f"{timestamp}_{safe_name}"
    sequence = 1
    while destination.exists():
        destination = PLAN_EXPORTS_DIR / f"{timestamp}_{sequence}_{safe_name}"
        sequence += 1
    temporary = destination.with_suffix(".json.tmp")
    temporary.write_bytes(stored_content)
    temporary.replace(destination)
    return destination


def load_selected_exports(paths: List[Path]) -> List[Dict[str, Any]]:
    exports = []
    for path in paths:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
            raise ValueError(f"{path.name}: não foi possível ler o JSON.") from error
        if not isinstance(data, dict):
            raise ExportPeriodError(
                f"{path.name}: raiz JSON inválida; análise não executada."
            )
        validar_periodo_exportacao(data, path.name)
        data["_nome_arquivo"] = path.name
        match = re.match(r"^(\d{4})(\d{2})(\d{2})-", path.name)
        if match and not data.get("importado_em"):
            data["_importado_em"] = (
                f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
            )
        exports.append(data)
    return exports


def available_plan_exports() -> List[Path]:
    PLAN_EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    return sorted(PLAN_EXPORTS_DIR.glob("*.json"), reverse=True)


def export_assessment_json(evidence: Dict[str, Any]) -> bytes:
    """Serializa uma análise individual para um arquivo JSON seguro de reimportar."""
    if not isinstance(evidence, dict):
        raise ValueError("A análise deve ser um objeto JSON.")
    if not isinstance(evidence.get("documento"), dict):
        raise ValueError("A exportação não contém os dados documentais esperados.")
    if not isinstance(evidence.get("conciliacao"), dict):
        raise ValueError("A exportação não contém a conciliação esperada.")
    return (json.dumps(evidence, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def import_assessment_json(content: bytes) -> Dict[str, Any]:
    """Valida e reimporta uma análise individual exportada pelo assistente."""
    try:
        evidence = json.loads(content)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("A análise não contém JSON válido.") from error
    if not isinstance(evidence, dict):
        raise ValueError("A análise exportada deve ser um objeto JSON.")
    if not isinstance(evidence.get("documento"), dict):
        raise ValueError("A análise exportada não contém documento.")
    if not isinstance(evidence.get("conciliacao"), dict):
        raise ValueError("A análise exportada não contém conciliação.")
    if "revisao_ia" in evidence and not isinstance(evidence["revisao_ia"], dict):
        raise ValueError("A revisão IA da análise exportada é inválida.")
    return evidence
