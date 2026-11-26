"""Objetivo: verificar conciliação e mapeamento de reembolsos.

Entradas: dados de teste, configurações e dependências substituídas.
Processamento: exercita normalização, comparação e relatórios.
Saídas: asserções de sucesso ou falha para o runner de testes.
"""

import unittest
import json
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from health_refund_assistant.plan.reconciliation import (
    DEFAULT_MAPPING,
    build_report,
    parse_amount,
    parse_date,
    payment_difference,
    reconcile,
    run,
    status_category,
)
from health_refund_assistant.plan.reconciliation import load_json
from health_refund_assistant.plan.mapping import (
    DEFAULT_PROMPT,
    REQUIRED_FIELDS,
    build_proposal,
    collect_field_paths,
    describe_schema,
    extract_schemas,
    validate_proposal,
)


class ConciliarReembolsosTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mapping = load_json(DEFAULT_MAPPING)

    def make_note(self):
        return {
            "source_id": "nota.pdf",
            "filename": "nota.pdf",
            "processed": True,
            "successful": True,
            "provider": "Clínica Saúde Ltda",
            "provider_tax_id": None,
            "invoice_number": "NF-123",
            "amount": 375.0,
            "issue_date": "15/01/2025",
            "service": "Consulta médica",
        }

    def make_claim(self, **overrides):
        claim = {
            "source_id": "SIN-123",
            "provider": "Clinica Saude",
            "beneficiary": "Beneficiário",
            "status": "Em Análise",
            "requested_amount": 375.0,
            "paid_amount": None,
            "service_date": "14/01/2025",
            "request_date": "20/01/2025",
            "payment_date": None,
            "service": "Consulta médica",
        }
        claim.update(overrides)
        return claim

    def test_parses_brazilian_amount_and_supported_dates(self):
        self.assertEqual(parse_amount("R$ 1.250,50"), 1250.5)
        self.assertEqual(parse_amount(375), 375.0)
        self.assertIsNone(parse_amount("não informado"))
        self.assertEqual(parse_date("15/01/2025").isoformat(), "2025-01-15")
        self.assertEqual(parse_date("2025-01-15").isoformat(), "2025-01-15")

    def test_strong_unique_candidate_is_flagged_for_review(self):
        result = reconcile(
            [self.make_note()], [self.make_claim()], self.mapping
        )[0]
        self.assertEqual(result["reconciliation_status"], "correspondencia_forte_revisar")
        self.assertEqual(len(result["candidates"]), 1)

    def test_multiple_candidates_are_not_auto_confirmed(self):
        result = reconcile(
            [self.make_note()],
            [self.make_claim(), self.make_claim(source_id="SIN-456")],
            self.mapping,
        )[0]
        self.assertEqual(
            result["reconciliation_status"], "possiveis_correspondencias_revisar"
        )
        self.assertEqual(len(result["candidates"]), 2)

    def test_loose_amount_date_and_provider_match_is_only_a_candidate(self):
        claim = self.make_claim(
            provider="Clinica Saude",
            requested_amount=350.0,
            service_date="10/02/2025",
        )
        note = self.make_note()
        note["provider"] = "Clinica Saude Consultoria"
        note["issue_date"] = "15/02/2025"
        result = reconcile([note], [claim], self.mapping)[0]
        self.assertEqual(
            result["reconciliation_status"], "possiveis_correspondencias_revisar"
        )
        self.assertEqual(result["candidates"][0]["match_confidence"], "possivel")

    def test_no_candidate_is_scoped_to_the_current_export(self):
        result = reconcile(
            [self.make_note()],
            [self.make_claim(provider="Outro prestador")],
            self.mapping,
        )[0]
        self.assertEqual(
            result["reconciliation_status"],
            "sem_correspondencia_nesta_exportacao",
        )

    def test_approval_without_payment_details_is_not_reported_as_paid(self):
        self.assertEqual(
            status_category("Liberado Integral", 375.0, None),
            "liberado_integral_aguardando_pagamento",
        )
        self.assertEqual(
            status_category("Liberado Integral", 375.0, "22/01/2025"),
            "reembolsado_integral",
        )
        self.assertEqual(
            status_category("Liberado Parcial", 200.0, "22/01/2025"),
            "reembolsado_parcial",
        )
        self.assertEqual(
            status_category("Não Liberado", None, None),
            "nao_liberado",
        )

    def test_requested_minus_paid_difference(self):
        self.assertEqual(payment_difference(375.0, 250.0), 125.0)
        self.assertIsNone(payment_difference(375.0, None))

    def test_paid_totals_require_payment_status_and_date(self):
        notes = {
            "pdfs": {
                "note.pdf": {
                    "nome_arquivo": "note.pdf",
                    "processado": True,
                    "sucesso": True,
                    "resultado": {
                        "prestador": "Clinic",
                        "valor_total": 375,
                    },
                }
            }
        }
        claims = {
            "reembolsos": [
                {
                    "numeroSinistro": "SIN-1",
                    "prestador": "Other provider",
                    "status": "Liberado Parcial",
                    "valorSolicitadoNum": 375,
                    "valorFinalReembolsadoNum": 100,
                },
                {
                    "numeroSinistro": "SIN-2",
                    "prestador": "Another provider",
                    "status": "Liberado Parcial",
                    "valorSolicitadoNum": 375,
                    "valorFinalReembolsadoNum": 200,
                    "dataPagamento": "22/01/2025",
                },
            ]
        }
        report = build_report(
            notes, claims, DEFAULT_MAPPING, DEFAULT_MAPPING, self.mapping
        )
        self.assertEqual(report["summary"]["claims_paid"], 1)
        self.assertEqual(report["summary"]["total_paid_amount"], 200.0)

    def test_schema_description_contains_types_not_record_values(self):
        private_record = {
            "prestador": "Nome Confidencial",
            "valor_total": 375.0,
            "detalhe": {"registro_profissional": None},
        }
        schema = describe_schema(private_record)
        serialized = str(schema)
        self.assertNotIn("Nome Confidencial", serialized)
        self.assertEqual(
            collect_field_paths(schema),
            {"prestador", "valor_total", "detalhe", "detalhe.registro_profissional"},
        )

    def test_extract_schemas_omits_dynamic_record_keys_and_values(self):
        notes = {
            "pdfs": {
                "person-name-confidential.pdf": {
                    "resultado": {"prestador": "Nome Confidencial"}
                }
            }
        }
        portal = {
            "reembolsos": [
                {"prestador": "Outro Nome Confidencial", "beneficiario": "Pessoa"}
            ]
        }
        schemas = extract_schemas(notes, portal, self.mapping)
        serialized = str(schemas)
        self.assertNotIn("person-name-confidential", serialized)
        self.assertNotIn("Nome Confidencial", serialized)
        self.assertNotIn("Pessoa", serialized)

    def test_mapping_proposal_rejects_unknown_field_paths(self):
        schemas = {
            "notes": {"prestador": "string"},
            "portal": {"prestador": "string"},
        }
        proposal = {
            "notes": {
                "fields": {
                    field: ("campo_inexistente" if field == "provider" else None)
                    for field in (
                        "provider",
                        "provider_tax_id",
                        "invoice_number",
                        "amount",
                        "issue_date",
                        "service_date",
                        "service",
                    )
                }
            },
            "portal": {
                "fields": {
                    field: None
                    for field in (
                        "claim_id",
                        "provider",
                        "beneficiary",
                        "status",
                        "requested_amount",
                        "paid_amount",
                        "service_date",
                        "request_date",
                        "payment_date",
                        "service",
                    )
                }
            },
            "caveats": [],
        }
        with self.assertRaisesRegex(ValueError, "Caminho inválido"):
            validate_proposal(proposal, schemas)

    def test_mapping_request_includes_loaded_output_schema_and_json_template(self):
        proposal = {
            source: {
                "fields": {
                    field: None for field in REQUIRED_FIELDS[source]
                }
            }
            for source in ("notes", "portal")
        }
        proposal["caveats"] = []
        response = SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(
                        content=json.dumps(proposal),
                    )
                )
            ]
        )
        notes = {"pdfs": {"nota.pdf": {"resultado": {"prestador": "Clínica"}}}}
        portal = {"reembolsos": [{"prestador": "Clínica"}]}

        with patch("health_refund_assistant.plan.mapping.OpenAI") as openai_client:
            openai_client.return_value.chat.completions.create.return_value = response
            result = build_proposal(
                notes,
                portal,
                self.mapping,
                "Instruções do prompt",
                "modelo-teste",
                "http://localhost/v1",
                10.0,
                prompt_version="v1.1",
            )

        self.assertEqual(result["mapping_method"]["prompt_version"], "v1.1")
        system_prompt = openai_client.return_value.chat.completions.create.call_args.kwargs[
            "messages"
        ][0]["content"]
        self.assertIn(
            "`reconciliation/schemas/mapping_proposal.schema.json`",
            system_prompt,
        )
        self.assertIn('"$defs"', system_prompt)
        self.assertIn("Template JSON correspondente", system_prompt)
        self.assertIn('"provider": null', system_prompt)
        self.assertNotIn('{"notes":{"fields":{...}}', system_prompt)
        user_content = openai_client.return_value.chat.completions.create.call_args.kwargs["messages"][1]["content"]
        self.assertEqual(json.loads(user_content), {"notes": {"prestador": "string"}, "portal": {"prestador": "string"}})
        self.assertNotIn("Clínica", user_content)

    def test_default_mapping_prompt_is_available_and_versioned(self):
        self.assertEqual(DEFAULT_PROMPT.name, "v1.2.md")
        self.assertIn("dados não confiáveis", DEFAULT_PROMPT.read_text(encoding="utf-8").lower())

    def test_remote_mapping_requires_explicit_api_credential(self):
        notes = {"pdfs": {"nota.pdf": {"resultado": {"prestador": "Clínica"}}}}
        portal = {"reembolsos": [{"prestador": "Clínica"}]}
        with (
            patch.dict("os.environ", {"OPENAPI_TOKEN": ""}),
            patch("health_refund_assistant.plan.mapping.OpenAI") as client,
        ):
            with self.assertRaisesRegex(ValueError, "OPENAPI_TOKEN"):
                build_proposal(
                    notes, portal, self.mapping, "Instruções", "modelo-teste",
                    "https://api.openai.com/v1", 10.0,
                )
            client.assert_not_called()

    def test_cli_pipeline_refuses_export_without_a_valid_period(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            notes_path = root / "notes.json"
            portal_path = root / "portal.json"
            report_path = root / "report.json"
            notes_path.write_text(json.dumps({"pdfs": {}}), encoding="utf-8")
            portal_path.write_text(
                json.dumps({"reembolsos": []}),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "período ausente"):
                run(notes_path, portal_path, DEFAULT_MAPPING, report_path)

            self.assertFalse(report_path.exists())


if __name__ == "__main__":
    unittest.main()
