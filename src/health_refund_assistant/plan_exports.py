import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
from zoneinfo import ZoneInfo

from .assessment import ExportPeriodError, validar_periodo_exportacao
from .paths import PLAN_EXPORTS_DIR


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
    timestamp = datetime.now(ZoneInfo("America/Sao_Paulo")).strftime("%Y%m%d-%H%M%S")
    destination = PLAN_EXPORTS_DIR / f"{timestamp}_{safe_name}"
    sequence = 1
    while destination.exists():
        destination = PLAN_EXPORTS_DIR / f"{timestamp}_{sequence}_{safe_name}"
        sequence += 1
    temporary = destination.with_suffix(".json.tmp")
    temporary.write_bytes(content)
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
        exports.append(data)
    return exports


def available_plan_exports() -> List[Path]:
    PLAN_EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    return sorted(PLAN_EXPORTS_DIR.glob("*.json"), reverse=True)
