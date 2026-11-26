"""Objetivo: centralizar caminhos operacionais e contratos do assistente.

Entradas: localização do projeto e nome de schema solicitado.
Processamento: define diretórios e resolve nomes conhecidos de schemas.
Saídas: constantes de caminhos, caminho resolvido ou erro para schema inválido.
"""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
JSON_ROOT = PROJECT_ROOT / "json"
CONFIG_DIR = JSON_ROOT / "config"
DATA_DIR = PROJECT_ROOT / "data"
INCOMING_DIR = DATA_DIR / "incoming"
PROCESSED_DIR = DATA_DIR / "processed"
FAILED_DIR = DATA_DIR / "failed"
PLAN_EXPORTS_DIR = JSON_ROOT / "plan" / "imports"
STATE_DIR = JSON_ROOT / "documents" / "state"
RECONCILIATION_REPORTS_DIR = JSON_ROOT / "reconciliation" / "reports"
NOTES_STATE_PATH = STATE_DIR / "notas_extraidas.json"
CONVERSATION_STATE_PATH = STATE_DIR / "conversa_local.json"
MAPPING_CONFIG_PATH = CONFIG_DIR / "mapeamento_reembolsos.json"
PROMPTS_DIR = PROJECT_ROOT / "prompts"

SCHEMA_LOCATIONS = {
    "vlm_extraction.schema.json": JSON_ROOT / "extraction" / "schemas" / "vlm_extraction.schema.json",
    "vlm_extraction_v4.schema.json": JSON_ROOT / "extraction" / "schemas" / "vlm_extraction_v4.schema.json",
    "vlm_extraction_v4_2.schema.json": JSON_ROOT / "extraction" / "schemas" / "vlm_extraction_v4_2.schema.json",
    "mapping_config.schema.json": JSON_ROOT / "reconciliation" / "schemas" / "mapping_config.schema.json",
    "mapping_proposal.schema.json": JSON_ROOT / "reconciliation" / "schemas" / "mapping_proposal.schema.json",
    "reconciliation_report.schema.json": JSON_ROOT / "reconciliation" / "schemas" / "reconciliation_report.schema.json",
    "plan_export.schema.json": JSON_ROOT / "plan" / "schemas" / "plan_export.schema.json",
    "notes_state.schema.json": JSON_ROOT / "documents" / "schemas" / "notes_state.schema.json",
    "document_review.schema.json": JSON_ROOT / "reconciliation" / "schemas" / "document_review.schema.json",
    "assistant_answer.schema.json": JSON_ROOT / "documents" / "schemas" / "assistant_answer.schema.json",
    "payment_estimate.schema.json": JSON_ROOT / "plan" / "schemas" / "payment_estimate.schema.json",
}


def resolve_schema(nome_schema: str) -> Path:
    """Resolve schema path by name. Raises FileNotFoundError if not found."""
    if nome_schema not in SCHEMA_LOCATIONS:
        raise ValueError(f"Schema não encontrado: {nome_schema}. Schemas disponíveis: {list(SCHEMA_LOCATIONS.keys())}")
    path = SCHEMA_LOCATIONS[nome_schema]
    if not path.exists():
        raise FileNotFoundError(f"Schema não existe: {path}")
    return path
