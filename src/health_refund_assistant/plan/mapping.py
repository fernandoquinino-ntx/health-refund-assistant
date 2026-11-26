"""Objetivo: propor o mapeamento dos campos das exportações.

Entradas: estruturas dos dados, prompt, schema e configuração de API.
Processamento: descreve estruturas, solicita proposta à IA e valida caminhos.
Saídas: proposta JSON para revisão humana ou erro de validação.
"""

import argparse
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Set
from urllib.parse import urlparse

from openai import OpenAI

from ..core.json_contracts import contexto_schema_para_prompt, validar_contrato_json
from ..documents.vlm_extractor import OPENAI_TOKEN_ENV
from .plan_exports import load_selected_exports
from ..core.paths import CONFIG_DIR, PROMPTS_DIR
from .reconciliation import (
    DEFAULT_MAPPING,
    DEFAULT_NOTES,
    DEFAULT_EXPORT_DIR,
    latest_export,
    load_json,
    load_mapping,
    write_json,
)


DEFAULT_PROMPT = PROMPTS_DIR / "reembolso_status" / "v1.2.md"
DEFAULT_PROPOSAL = CONFIG_DIR / "mapeamento_reembolsos.proposta.json"
DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-6-luna"
REQUIRED_FIELDS = {
    "notes": (
        "provider",
        "provider_tax_id",
        "invoice_number",
        "amount",
        "issue_date",
        "service_date",
        "service",
    ),
    "portal": (
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
    ),
}


def describe_schema(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: describe_schema(child) for key, child in value.items()}
    if isinstance(value, list):
        if not value:
            return {"type": "array", "items": None}
        return {"type": "array", "items": describe_schema(value[0])}
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, (int, float)):
        return "number"
    return "string"


def collect_field_paths(schema: Any, prefix: str = "") -> Set[str]:
    paths: Set[str] = set()
    if isinstance(schema, dict) and schema.get("type") == "array":
        paths.update(collect_field_paths(schema.get("items"), prefix))
    elif isinstance(schema, dict):
        for key, value in schema.items():
            path = f"{prefix}.{key}" if prefix else key
            paths.add(path)
            paths.update(collect_field_paths(value, path))
    return paths


def extract_schemas(
    notes_document: Dict[str, Any],
    portal_document: Dict[str, Any],
    mapping: Dict[str, Any],
) -> Dict[str, Any]:
    notes_records = notes_document.get(mapping["notes"]["records_path"])
    if not isinstance(notes_records, dict) or not notes_records:
        raise ValueError("Não há registros de notas para extrair o schema.")
    note_record = next(iter(notes_records.values()))
    if not isinstance(note_record, dict):
        raise ValueError("Registro de nota inválido.")
    note_result = note_record.get(mapping["notes"]["result_path"])
    if not isinstance(note_result, dict):
        raise ValueError("O registro de nota não contém um resultado em objeto.")

    portal_records = portal_document.get(mapping["portal"]["records_path"])
    if not isinstance(portal_records, list) or not portal_records:
        raise ValueError("A exportação não contém registros de reembolso.")
    portal_record = portal_records[0]
    if not isinstance(portal_record, dict):
        raise ValueError("Registro do portal inválido.")

    return {
        "notes": describe_schema(note_result),
        "portal": describe_schema(portal_record),
    }


def parse_model_json(content: str) -> Dict[str, Any]:
    cleaned = content.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        result = json.loads(cleaned)
    except json.JSONDecodeError as error:
        raise ValueError(f"O modelo não retornou JSON válido: {error}") from error
    if not isinstance(result, dict):
        raise ValueError("O modelo deve retornar um objeto JSON.")
    return result


def validate_proposal(
    proposal: Dict[str, Any], schemas: Dict[str, Any]
) -> Dict[str, Any]:
    validated = {}
    for source in ("notes", "portal"):
        source_mapping = proposal.get(source)
        if not isinstance(source_mapping, dict):
            raise ValueError(f"O mapeamento de '{source}' está ausente ou inválido.")
        fields = source_mapping.get("fields")
        if not isinstance(fields, dict):
            raise ValueError(f"Os campos de '{source}' estão ausentes ou inválidos.")

        valid_paths = collect_field_paths(schemas[source])
        validated_fields = {}
        for canonical_field in REQUIRED_FIELDS[source]:
            value = fields.get(canonical_field)
            candidates = value if isinstance(value, list) else [value]
            for candidate in candidates:
                if candidate is not None and (
                    not isinstance(candidate, str) or candidate not in valid_paths
                ):
                    raise ValueError(
                        f"Caminho inválido em {source}.{canonical_field}: {candidate!r}"
                    )
            validated_fields[canonical_field] = value
        validated[source] = {"fields": validated_fields}

    caveats = proposal.get("caveats", [])
    if not isinstance(caveats, list) or any(
        not isinstance(item, str) for item in caveats
    ):
        raise ValueError("O campo 'caveats' deve ser uma lista de textos.")
    validated["caveats"] = caveats
    return validated


def build_proposal(
    notes_document: Dict[str, Any],
    portal_document: Dict[str, Any],
    active_mapping: Dict[str, Any],
    prompt: str,
    model: str,
    base_url: str,
    timeout: float,
    prompt_version: str | None = None,
) -> Dict[str, Any]:
    schemas = extract_schemas(notes_document, portal_document, active_mapping)
    token = os.getenv(OPENAI_TOKEN_ENV)
    if not token and urlparse(base_url).hostname not in ("localhost", "127.0.0.1", "::1"):
        raise ValueError(f"Configure {OPENAI_TOKEN_ENV} para usar um provedor remoto.")
    client = OpenAI(base_url=base_url, api_key=token or "lm-studio", timeout=timeout)
    prompt_com_schema = (
        f"{prompt.rstrip()}\n\n"
        f"{contexto_schema_para_prompt('mapping_proposal.schema.json')}\n\n"
    )
    response = client.chat.completions.create(
        model=model,
        temperature=0.0,
        top_p=0.9,
        max_tokens=4096,
        messages=[
            {
                "role": "system",
                "content": (
                    f"{prompt_com_schema}\n\n"
                ),
            },
            {
                "role": "user",
                "content": json.dumps(schemas, ensure_ascii=False),
            },
        ],
    )
    content = response.choices[0].message.content
    if not content:
        finish_reason = response.choices[0].finish_reason
        raise ValueError(
            "O modelo não retornou conteúdo utilizável "
            f"(finish_reason={finish_reason!r})."
        )
    raw_proposal = parse_model_json(content)
    validar_contrato_json(
        raw_proposal,
        "mapping_proposal.schema.json",
        "proposta do modelo",
    )
    proposal = validate_proposal(raw_proposal, schemas)

    result = json.loads(json.dumps(active_mapping))
    for source in ("notes", "portal"):
        result[source]["fields"] = proposal[source]["fields"]
    result["mapping_method"] = {
        "type": "local_model_proposal",
        "model": model,
        "prompt_version": prompt_version,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "human_review_required": True,
    }
    result["caveats"] = proposal["caveats"]
    validar_contrato_json(
        result,
        "mapping_config.schema.json",
        "proposta de mapeamento",
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Gera uma proposta local de mapeamento sem enviar valores dos registros."
    )
    parser.add_argument("--notas", type=Path, default=DEFAULT_NOTES)
    parser.add_argument("--exportacao", type=Path)
    parser.add_argument("--mapeamento-base", type=Path, default=DEFAULT_MAPPING)
    parser.add_argument("--prompt", type=Path, default=DEFAULT_PROMPT)
    parser.add_argument("--saida", type=Path, default=DEFAULT_PROPOSAL)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--timeout", type=float, default=180.0)
    args = parser.parse_args()

    export_path = args.exportacao or latest_export(DEFAULT_EXPORT_DIR)
    prompt = args.prompt.read_text(encoding="utf-8")
    proposal = build_proposal(
        load_json(args.notas),
        load_selected_exports([export_path])[0],
        load_mapping(args.mapeamento_base),
        prompt,
        args.model,
        args.base_url,
        args.timeout,
        prompt_version=args.prompt.stem if re.fullmatch(r"v\d+\.\d+", args.prompt.stem) else None,
    )
    write_json(args.saida, proposal)
    print(f"Proposta validada salva em {args.saida}; revise antes de ativá-la.")


if __name__ == "__main__":
    main()
