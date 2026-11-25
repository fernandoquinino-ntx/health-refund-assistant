import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

from health_refund_assistant.json_contracts import validar_contrato_json
from health_refund_assistant.paths import (
    CONFIG_DIR,
    JSON_ROOT,
    SCHEMA_LOCATIONS,
    SYNTHETIC_DATA_DIR,
    TEST_FIXTURES_DIR,
)
from health_refund_assistant.reconciliation import DEFAULT_MAPPING, load_mapping


class JsonSchemasTests(unittest.TestCase):
    def test_all_project_json_schemas_are_valid_draft_2020_12(self):
        schemas = []
        for schema_path in SCHEMA_LOCATIONS.values():
            if schema_path.exists():
                schemas.append(schema_path)
        self.assertGreaterEqual(len(schemas), 10)
        for path in schemas:
            with self.subTest(schema=path.name):
                schema = json.loads(path.read_text(encoding="utf-8"))
                Draft202012Validator.check_schema(schema)

    def test_checked_in_json_inputs_match_their_contracts(self):
        datasets = (
            (CONFIG_DIR / "mapeamento_reembolsos.json", "mapping_config.schema.json"),
            (
                TEST_FIXTURES_DIR / "casos_teste.template.json",
                "test_cases.schema.json",
            ),
            (
                TEST_FIXTURES_DIR / "gabarito.template.json",
                "test_gold.schema.json",
            ),
            (
                SYNTHETIC_DATA_DIR / "casos_teste.json",
                "test_cases.schema.json",
            ),
            (
                SYNTHETIC_DATA_DIR / "gabarito.json",
                "test_gold.schema.json",
            ),
            (
                SYNTHETIC_DATA_DIR / "exportacao_ficticia.json",
                "plan_export.schema.json",
            ),
        )
        for path, schema in datasets:
            with self.subTest(file=path.name):
                data = json.loads(path.read_text(encoding="utf-8"))
                validar_contrato_json(data, schema, path.name)

    def test_mapping_loader_checks_the_config_contract(self):
        self.assertEqual(load_mapping(DEFAULT_MAPPING)["version"], "v1.0")

    def test_validator_reports_the_invalid_field_path(self):
        with self.assertRaisesRegex(ValueError, "periodo"):
            validar_contrato_json(
                {
                    "periodo": {"de": 123, "ate": "31/03/2026"},
                    "reembolsos": [],
                },
                "plan_export.schema.json",
                "exportacao.json",
            )

    def test_mapping_proposal_schema_requires_every_canonical_path(self):
        fields = {
            "provider": None,
            "provider_tax_id": None,
            "invoice_number": None,
            "amount": None,
            "issue_date": None,
            "service_date": None,
            "service": None,
        }
        proposal = {
            "notes": {"fields": fields},
            "portal": {
                "fields": {
                    "claim_id": None,
                    "provider": None,
                    "beneficiary": None,
                    "status": None,
                    "requested_amount": None,
                    "paid_amount": None,
                    "service_date": None,
                    "request_date": None,
                    "payment_date": None,
                    "service": None,
                }
            },
            "caveats": [],
        }
        validar_contrato_json(
            proposal,
            "mapping_proposal.schema.json",
            "proposta de teste",
        )

        del proposal["notes"]["fields"]["service_date"]
        with self.assertRaisesRegex(ValueError, "service_date"):
            validar_contrato_json(
                proposal,
                "mapping_proposal.schema.json",
                "proposta de teste",
            )


if __name__ == "__main__":
    unittest.main()
