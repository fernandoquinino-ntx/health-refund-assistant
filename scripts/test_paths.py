"""Caminhos dos dados, contratos e relatórios usados nas avaliações."""

from health_refund_assistant.paths import DATA_DIR, JSON_ROOT

TEST_FIXTURES_DIR = JSON_ROOT / "tests" / "templates"
SYNTHETIC_DATA_DIR = JSON_ROOT / "tests" / "synthetic"
SYNTHETIC_DOCUMENTS_DIR = DATA_DIR / "sinteticos" / "documentos"
EVALUATION_REPORTS_DIR = JSON_ROOT / "evaluation" / "reports"
TEST_SCHEMAS = {
    "test_cases.schema.json": JSON_ROOT / "tests" / "schemas" / "test_cases.schema.json",
    "test_gold.schema.json": JSON_ROOT / "tests" / "schemas" / "test_gold.schema.json",
    "vlm_evaluation_report.schema.json": JSON_ROOT / "evaluation" / "schemas" / "vlm_evaluation_report.schema.json",
}
