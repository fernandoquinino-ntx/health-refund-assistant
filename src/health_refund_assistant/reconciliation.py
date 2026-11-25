"""
Reconciliador — Verificação de Existência na Exportação

OBJETIVO:
  Busca correspondência da nota fiscal extraída na exportação do plano de saúde.
  Aplica janela temporal D-2 e regras de elegibilidade.

ENTRADA:
  - Dados extraídos (JSON do VLMExtractor)
  - Exportação do plano (JSON)
  - Data de corte (D-1)

SAÍDA:
  - Status de reconciliação:
    * ENCONTRADO_PAGO_INTEGRAL
    * ENCONTRADO_PAGO_PARCIAL (com glosa/diferença)
    * ENCONTRADO_RECUSADO
    * ENCONTRADO_EM_ANALISE
    * NAO_ENCONTRADO (motivo: fora janela D-2 ou nunca submetido)
    * FORA_DA_JANELA_IMPORTACAO

PROCESSO (ETAPA 2 DO FLUXO):
  JSON extraído → Reconciliador → Status + motivo

REGRA D-2 (Crítica):
  - Exportação possui corte em D-1
  - Notas emitidas APÓS D-2 são inelegíveis
  - Reduz falsos negativos de "nunca foi submetido"

DOCUMENTO:
  Veja docs/caderno_projeto.md (R1 - Regra D-1/D-2) para detalhes

LÓGICA:
  1. Normaliza dados (remover acentos, case-insensitive)
  2. Busca por CNPJ + valor no plano
  3. Aplica similaridade fuzzy para descrição
  4. Verifica janela D-2
  5. Retorna status encontrado ou motivo da não-encontrabilidade
"""

import argparse
import json
import re
import unicodedata
from collections import Counter
from datetime import date, datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .json_contracts import validar_contrato_json
from .paths import (
    MAPPING_CONFIG_PATH,
    NOTES_STATE_PATH,
    PLAN_EXPORTS_DIR,
    RECONCILIATION_REPORTS_DIR,
)


DEFAULT_NOTES = NOTES_STATE_PATH
DEFAULT_EXPORT_DIR = PLAN_EXPORTS_DIR
DEFAULT_MAPPING = MAPPING_CONFIG_PATH
DEFAULT_JSON_REPORT = RECONCILIATION_REPORTS_DIR / "conciliacao.json"


def load_json(path: Path) -> Dict[str, Any]:
    with path.open(encoding="utf-8") as file:
        content = json.load(file)
    if not isinstance(content, dict):
        raise ValueError(f"O arquivo deve conter um objeto JSON: {path}")
    return content


def load_mapping(path: Path = DEFAULT_MAPPING) -> Dict[str, Any]:
    mapping = load_json(path)
    validar_contrato_json(
        mapping,
        "mapping_config.schema.json",
        path.name,
    )
    return mapping


def get_path(value: Any, path: str) -> Any:
    current = value
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def mapped_value(record: Dict[str, Any], paths: Any) -> Any:
    if paths is None:
        return None
    candidates = paths if isinstance(paths, list) else [paths]
    for path in candidates:
        value = get_path(record, path)
        if value is not None and value != "":
            return value
    return None


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    text = unicodedata.normalize("NFKD", str(value))
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = re.sub(r"[^A-Z0-9]+", " ", text.upper())
    ignored = {"LTDA", "LIMITADA", "ME", "EPP", "EIRELI", "SA"}
    return " ".join(word for word in text.split() if word not in ignored)


def text_similarity(left: Any, right: Any) -> float:
    normalized_left = normalize_text(left)
    normalized_right = normalize_text(right)
    if not normalized_left or not normalized_right:
        return 0.0
    left_tokens = set(normalized_left.split())
    right_tokens = set(normalized_right.split())
    token_overlap = len(left_tokens & right_tokens) / max(
        len(left_tokens), len(right_tokens)
    )
    return max(
        SequenceMatcher(None, normalized_left, normalized_right).ratio(),
        token_overlap,
    )


def parse_amount(value: Any) -> Optional[float]:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return round(float(value), 2)
    text = re.sub(r"[^\d,.\-]", "", str(value)).strip()
    if not text:
        return None
    if "," in text and "." in text:
        text = text.replace(".", "").replace(",", ".")
    elif "," in text:
        text = text.replace(",", ".")
    try:
        return round(float(text), 2)
    except ValueError:
        return None


def parse_date(value: Any) -> Optional[date]:
    if not value:
        return None
    text = str(value).strip()
    for date_format in ("%d/%m/%Y", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(text[:19], date_format).date()
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).date()
    except ValueError:
        return None


def status_category(status: Any, paid_amount: Optional[float], payment_date: Any) -> str:
    normalized = normalize_text(status)
    if "NAO LIBERADO" in normalized or "RECUS" in normalized or "NEGAD" in normalized:
        return "nao_liberado"
    if "PEND" in normalized or "DOCUMENT" in normalized:
        return "pendencia_documental"
    if "ANALISE" in normalized:
        return "em_analise"
    if paid_amount is not None and paid_amount > 0 and parse_date(payment_date):
        if "PARCIAL" in normalized:
            return "reembolsado_parcial"
        if "INTEGRAL" in normalized:
            return "reembolsado_integral"
        return "reembolsado"
    if "PARCIAL" in normalized:
        return "liberado_parcial_aguardando_pagamento"
    if "INTEGRAL" in normalized:
        return "liberado_integral_aguardando_pagamento"
    return "status_desconhecido"


def payment_difference(
    requested_amount: Optional[float], paid_amount: Optional[float]
) -> Optional[float]:
    if requested_amount is None or paid_amount is None:
        return None
    return round(requested_amount - paid_amount, 2)


def load_notes(document: Dict[str, Any], mapping: Dict[str, Any]) -> List[Dict[str, Any]]:
    source = mapping["notes"]
    records = get_path(document, source["records_path"])
    if not isinstance(records, dict):
        raise ValueError("O caminho de registros das notas deve apontar para um objeto.")

    notes = []
    for filename, record in records.items():
        if not isinstance(record, dict):
            continue
        result = record.get(source.get("result_path", "resultado"), {})
        if not isinstance(result, dict):
            result = {}
        fields = source["fields"]
        notes.append(
            {
                "source_id": filename,
                "filename": record.get("nome_arquivo", filename),
                "processed": record.get("processado") is True,
                "successful": record.get("sucesso") is True,
                "provider": mapped_value(result, fields["provider"]),
                "provider_tax_id": mapped_value(result, fields.get("provider_tax_id")),
                "invoice_number": mapped_value(result, fields.get("invoice_number")),
                "amount": parse_amount(mapped_value(result, fields["amount"])),
                "issue_date": mapped_value(result, fields.get("issue_date")),
                "service_date": mapped_value(result, fields.get("service_date")),
                "service": mapped_value(result, fields.get("service")),
            }
        )
    return notes


def load_claims(document: Dict[str, Any], mapping: Dict[str, Any]) -> List[Dict[str, Any]]:
    source = mapping["portal"]
    records = get_path(document, source["records_path"])
    if not isinstance(records, list):
        raise ValueError("O caminho de registros do plano deve apontar para uma lista.")

    claims = []
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            continue
        fields = source["fields"]
        claims.append(
            {
                "source_id": str(mapped_value(record, fields.get("claim_id")) or index),
                "provider": mapped_value(record, fields.get("provider")),
                "beneficiary": mapped_value(record, fields.get("beneficiary")),
                "status": mapped_value(record, fields.get("status")),
                "requested_amount": parse_amount(
                    mapped_value(record, fields.get("requested_amount"))
                ),
                "paid_amount": parse_amount(mapped_value(record, fields.get("paid_amount"))),
                "service_date": mapped_value(record, fields.get("service_date")),
                "request_date": mapped_value(record, fields.get("request_date")),
                "payment_date": mapped_value(record, fields.get("payment_date")),
                "service": mapped_value(record, fields.get("service")),
            }
        )
    return claims


def compare_note_claim(
    note: Dict[str, Any], claim: Dict[str, Any], rules: Dict[str, Any]
) -> Dict[str, Any]:
    provider_score = text_similarity(note["provider"], claim["provider"])
    service_score = text_similarity(note["service"], claim["service"])
    amount_difference = None
    if note["amount"] is not None and claim["requested_amount"] is not None:
        amount_difference = round(
            abs(note["amount"] - claim["requested_amount"]), 2
        )
    amount_matches = (
        amount_difference is not None
        and amount_difference <= rules["amount_tolerance"]
    )
    relative_amount_difference = (
        amount_difference / note["amount"]
        if amount_difference is not None and note["amount"] not in (None, 0)
        else None
    )

    note_service_date = parse_date(note.get("service_date"))
    invoice_date = parse_date(note["issue_date"])
    service_date = parse_date(claim["service_date"])
    comparison_date = note_service_date or invoice_date
    date_difference = (
        abs((comparison_date - service_date).days)
        if comparison_date and service_date
        else None
    )
    date_near = (
        date_difference is not None
        and date_difference <= rules["date_window_days"]
    )

    strong_candidate = (
        provider_score >= rules["provider_min_similarity"]
        and amount_matches
        and (date_near or service_score >= rules["service_min_similarity"])
    )
    weak_candidate = (
        provider_score >= rules["provider_weak_similarity"]
        and date_near
        and relative_amount_difference is not None
        and relative_amount_difference <= rules["relative_amount_tolerance"]
    )
    candidate = strong_candidate or weak_candidate
    strong = (
        strong_candidate
        and provider_score >= rules["provider_strong_similarity"]
        and date_near
    )
    evidence = []
    if provider_score >= rules["provider_min_similarity"]:
        evidence.append("prestador_semelhante")
    if amount_matches:
        evidence.append("valor_solicitado_igual_ao_valor_da_nota")
    if date_near:
        evidence.append(
            "data_de_atendimento_proxima_da_realizacao"
            if note_service_date
            else "data_de_emissao_proxima_da_realizacao"
        )
    if service_score >= rules["service_min_similarity"]:
        evidence.append("descricao_do_servico_semelhante")

    return {
        "candidate": candidate,
        "strong": strong,
        "provider_similarity": round(provider_score, 3),
        "service_similarity": round(service_score, 3),
        "amount_difference": amount_difference,
        "relative_amount_difference": (
            round(relative_amount_difference, 3)
            if relative_amount_difference is not None
            else None
        ),
        "days_between_note_and_service": date_difference,
        "match_confidence": "alta" if strong else "possivel",
        "evidence": evidence,
    }


def reconcile(
    notes: List[Dict[str, Any]],
    claims: List[Dict[str, Any]],
    mapping: Dict[str, Any],
) -> List[Dict[str, Any]]:
    rules = mapping["matching"]
    report_notes = []
    for note in notes:
        if not note["successful"]:
            report_notes.append(
                {
                    **note,
                    "reconciliation_status": "extracao_com_erro",
                    "candidates": [],
                    "alternatives": [],
                }
            )
            continue

        candidates = []
        alternatives = []
        for claim in claims:
            comparison = compare_note_claim(note, claim, rules)
            if comparison["candidate"]:
                target = candidates
            elif (
                comparison["provider_similarity"] >= rules["provider_weak_similarity"]
                or comparison["days_between_note_and_service"]
                is not None
                and comparison["days_between_note_and_service"]
                <= rules["date_window_days"]
                or comparison["service_similarity"]
                >= rules["service_min_similarity"]
            ):
                target = alternatives
            else:
                continue
            target.append(
                {
                    "claim_number": claim["source_id"],
                    "beneficiary": claim["beneficiary"],
                    "provider": claim["provider"],
                    "portal_status": claim["status"],
                    "financial_status": status_category(
                        claim["status"], claim["paid_amount"], claim["payment_date"]
                    ),
                    "requested_amount": claim["requested_amount"],
                    "paid_amount": claim["paid_amount"],
                    "requested_minus_paid": payment_difference(
                        claim["requested_amount"], claim["paid_amount"]
                    ),
                    "service_date": claim["service_date"],
                    "request_date": claim["request_date"],
                    "payment_date": claim["payment_date"],
                    **comparison,
                }
            )
        def sort_candidates(item: Dict[str, Any]) -> Tuple[float, float, int]:
            return (
                -item["provider_similarity"],
                item["relative_amount_difference"]
                if item["relative_amount_difference"] is not None
                else 1,
                item["days_between_note_and_service"]
                if item["days_between_note_and_service"] is not None
                else 10000,
            )

        candidates.sort(key=sort_candidates)
        alternatives.sort(key=sort_candidates)
        alternatives = alternatives[:3]
        if not candidates:
            result_status = "sem_correspondencia_nesta_exportacao"
        elif len(candidates) == 1 and candidates[0]["strong"]:
            result_status = "correspondencia_forte_revisar"
        else:
            result_status = "possiveis_correspondencias_revisar"

        report_notes.append(
            {
                **note,
                "reconciliation_status": result_status,
                "candidates": candidates,
                "alternatives": alternatives,
            }
        )
    return report_notes


def build_report(
    notes_document: Dict[str, Any],
    portal_document: Dict[str, Any],
    notes_path: Path,
    portal_path: Path,
    mapping: Dict[str, Any],
) -> Dict[str, Any]:
    notes = load_notes(notes_document, mapping)
    claims = load_claims(portal_document, mapping)
    results = reconcile(notes, claims, mapping)
    matched_claim_ids = {
        candidate["claim_number"]
        for note in results
        for candidate in note["candidates"]
    }
    claims_without_note = [
        {
            "claim_number": claim["source_id"],
            "provider": claim["provider"],
            "beneficiary": claim["beneficiary"],
            "portal_status": claim["status"],
            "financial_status": status_category(
                claim["status"], claim["paid_amount"], claim["payment_date"]
            ),
            "requested_amount": claim["requested_amount"],
            "paid_amount": claim["paid_amount"],
            "requested_minus_paid": payment_difference(
                claim["requested_amount"], claim["paid_amount"]
            ),
            "service_date": claim["service_date"],
            "request_date": claim["request_date"],
            "payment_date": claim["payment_date"],
        }
        for claim in claims
        if claim["source_id"] not in matched_claim_ids
    ]
    paid_claims = [
        claim
        for claim in claims
        if status_category(
            claim["status"], claim["paid_amount"], claim["payment_date"]
        ).startswith("reembolsado")
    ]
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "mapping_version": mapping["version"],
        "sources": {
            "notes": str(notes_path),
            "portal_export": str(portal_path),
        },
        "summary": {
            "notes_total": len(results),
            "claims_total": len(claims),
            "notes_without_correspondence_in_export": sum(
                item["reconciliation_status"] == "sem_correspondencia_nesta_exportacao"
                for item in results
            ),
            "notes_requiring_review": sum(
                item["reconciliation_status"]
                in {
                    "correspondencia_forte_revisar",
                    "possiveis_correspondencias_revisar",
                }
                for item in results
            ),
            "claims_without_note_match": len(claims_without_note),
            "claims_paid": len(paid_claims),
            "total_paid_amount": round(
                sum(claim["paid_amount"] or 0 for claim in paid_claims), 2
            ),
            "portal_statuses": dict(
                Counter(str(claim["status"] or "sem_status") for claim in claims)
            ),
        },
        "notes": results,
        "claims_without_note_match": claims_without_note,
    }


def write_json(path: Path, content: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    with temporary_path.open("w", encoding="utf-8") as file:
        json.dump(content, file, ensure_ascii=False, indent=2)
        file.write("\n")
    temporary_path.replace(path)


def latest_export(directory: Path) -> Path:
    exports = sorted(directory.glob("*.json"), key=lambda path: path.stat().st_mtime)
    if not exports:
        raise FileNotFoundError(f"Nenhuma exportação JSON encontrada em {directory}")
    return exports[-1]


def run(
    notes_path: Path,
    portal_path: Path,
    mapping_path: Path,
    json_output: Path,
) -> Dict[str, Any]:
    portal_document = load_json(portal_path)
    from .assessment import validar_periodo_exportacao
    validar_periodo_exportacao(portal_document, portal_path.name)
    notes_document = load_json(notes_path)
    mapping = load_mapping(mapping_path)
    report = build_report(
        notes_document, portal_document, notes_path, portal_path, mapping
    )
    validar_contrato_json(
        report,
        "reconciliation_report.schema.json",
        json_output.name,
    )
    write_json(json_output, report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Concilia notas extraídas com uma exportação do plano."
    )
    parser.add_argument("--notas", type=Path, default=DEFAULT_NOTES)
    parser.add_argument("--exportacao", type=Path)
    parser.add_argument("--mapeamento", type=Path, default=DEFAULT_MAPPING)
    parser.add_argument("--saida", type=Path, default=DEFAULT_JSON_REPORT)
    args = parser.parse_args()

    portal_path = args.exportacao or latest_export(DEFAULT_EXPORT_DIR)
    report = run(
        args.notas,
        portal_path,
        args.mapeamento,
        args.saida,
    )
    print(
        f"Conciliação concluída: {report['summary']['notes_total']} notas, "
        f"{report['summary']['claims_total']} pedidos. "
        f"Relatório JSON: {args.saida}"
    )


if __name__ == "__main__":
    main()
