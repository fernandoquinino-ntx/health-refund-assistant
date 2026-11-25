from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
JSON_ROOT = PROJECT_ROOT / "json"
CONFIG_DIR = JSON_ROOT / "config"
TEST_FIXTURES_DIR = JSON_ROOT / "tests" / "templates"
DATA_DIR = PROJECT_ROOT / "data"
INCOMING_DIR = DATA_DIR / "incoming"
PROCESSED_DIR = DATA_DIR / "processed"
FAILED_DIR = DATA_DIR / "failed"
PLAN_EXPORTS_DIR = JSON_ROOT / "plan" / "imports"
STATE_DIR = JSON_ROOT / "documents" / "state"
EVALUATION_REPORTS_DIR = JSON_ROOT / "evaluation" / "reports"
RECONCILIATION_REPORTS_DIR = JSON_ROOT / "reconciliation" / "reports"
SYNTHETIC_DATA_DIR = JSON_ROOT / "tests" / "synthetic"
SYNTHETIC_DOCUMENTS_DIR = DATA_DIR / "sinteticos" / "documentos"
NOTES_STATE_PATH = STATE_DIR / "notas_extraidas.json"
MAPPING_CONFIG_PATH = CONFIG_DIR / "mapeamento_reembolsos.json"
PROMPTS_DIR = PROJECT_ROOT / "prompts"

SCHEMA_LOCATIONS = {
    "vlm_extraction.schema.json": JSON_ROOT / "extraction" / "schemas" / "vlm_extraction.schema.json",
    "vlm_extraction_v4.schema.json": JSON_ROOT / "extraction" / "schemas" / "vlm_extraction_v4.schema.json",
    "mapping_config.schema.json": JSON_ROOT / "reconciliation" / "schemas" / "mapping_config.schema.json",
    "mapping_proposal.schema.json": JSON_ROOT / "reconciliation" / "schemas" / "mapping_proposal.schema.json",
    "reconciliation_report.schema.json": JSON_ROOT / "reconciliation" / "schemas" / "reconciliation_report.schema.json",
    "plan_export.schema.json": JSON_ROOT / "plan" / "schemas" / "plan_export.schema.json",
    "notes_state.schema.json": JSON_ROOT / "documents" / "schemas" / "notes_state.schema.json",
    "vlm_evaluation_report.schema.json": JSON_ROOT / "evaluation" / "schemas" / "vlm_evaluation_report.schema.json",
    "test_cases.schema.json": JSON_ROOT / "tests" / "schemas" / "test_cases.schema.json",
    "test_gold.schema.json": JSON_ROOT / "tests" / "schemas" / "test_gold.schema.json",
}


def resolve_schema(nome_schema: str) -> Path:
    """Resolve schema path by name. Raises FileNotFoundError if not found."""
    if nome_schema not in SCHEMA_LOCATIONS:
        raise ValueError(f"Schema não encontrado: {nome_schema}. Schemas disponíveis: {list(SCHEMA_LOCATIONS.keys())}")
    path = SCHEMA_LOCATIONS[nome_schema]
    if not path.exists():
        raise FileNotFoundError(f"Schema não existe: {path}")
    return path
