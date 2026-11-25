import json
import os
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Dict, Sequence

from openai import OpenAI

from .assessment import DEADLINE_DAYS, ExportPeriodError, avaliar_documento
from .paths import PROMPTS_DIR
from .reconciliation import DEFAULT_MAPPING, load_mapping
from .pdf_converter import converter_pdf_bytes_primeira_pagina_base64
from .plan_exports import load_selected_exports
from .vlm_extractor import (
    DEFAULT_MODEL,
    DEFAULT_OPENAI_BASE_URL,
    OPENAI_BASE_URL_ENV,
    OPENAI_TOKEN_ENV,
    VLMExtractor,
)


class ExtractionError(RuntimeError):
    def __init__(self, status: str):
        self.status = status
        super().__init__(f"A extração do documento falhou: {status}.")


@dataclass(frozen=True)
class AssistantRequest:
    pdf_bytes: bytes
    question: str
    export_paths: Sequence[Path]
    extraction_prompt_version: str
    response_prompt_version: str
    reference_date: date
    deadline_days: int = DEADLINE_DAYS


@dataclass(frozen=True)
class AssistantResponse:
    document_fields: Dict[str, Any]
    assessment: Dict[str, Any]
    answer: str


def create_assistant_answer(
    question: str, evidence: Dict[str, Any], prompt_version: str
) -> str:
    token = os.getenv(OPENAI_TOKEN_ENV)
    if not token:
        raise ValueError(
            f"Configure {OPENAI_TOKEN_ENV} antes de usar o assistente."
        )
    prompt_path = PROMPTS_DIR / "reembolso_assistente" / f"{prompt_version}.txt"
    if not prompt_path.is_file():
        raise FileNotFoundError(f"Prompt de resposta não encontrado: {prompt_path}")
    system_prompt = prompt_path.read_text(encoding="utf-8").strip()
    base_url = os.getenv(OPENAI_BASE_URL_ENV) or DEFAULT_OPENAI_BASE_URL
    client = OpenAI(api_key=token, base_url=base_url, timeout=120.0)
    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": (
                    f"Pergunta do usuário:\n{question}\n\n"
                    "Evidências calculadas pela aplicação (JSON):\n"
                    + json.dumps(evidence, ensure_ascii=False)
                ),
            },
        ],
        max_completion_tokens=1200,
        reasoning_effort="none",
    )
    content = response.choices[0].message.content
    if not content:
        raise RuntimeError("A API não retornou uma resposta textual.")
    return content.strip()


def handle_request(request: AssistantRequest) -> AssistantResponse:
    if not request.question.strip():
        raise ValueError("Escreva uma pergunta para o assistente.")
    if not request.pdf_bytes:
        raise ValueError("O PDF enviado está vazio.")
    if not request.export_paths:
        raise ExportPeriodError(
            "Nenhuma exportação do plano selecionada; análise não executada."
        )

    exports = load_selected_exports(list(request.export_paths))
    mapping = load_mapping(DEFAULT_MAPPING)
    image = converter_pdf_bytes_primeira_pagina_base64(request.pdf_bytes)
    extractor = VLMExtractor(
        model=DEFAULT_MODEL,
        prompt_version=request.extraction_prompt_version,
    )
    extraction = extractor.extrair_dados_nf_visual(image)
    status = extraction.get("_meta", {}).get("status")
    if status != "OK":
        raise ExtractionError(str(status or "status_desconhecido"))

    document_fields = {
        key: value for key, value in extraction.items() if key != "_meta"
    }
    assessment = avaliar_documento(
        extraction,
        exports,
        mapping,
        request.reference_date,
        request.deadline_days,
    )
    answer = create_assistant_answer(
        request.question,
        {"documento": document_fields, "conciliacao": assessment},
        request.response_prompt_version,
    )
    return AssistantResponse(
        document_fields=document_fields,
        assessment=assessment,
        answer=answer,
    )
