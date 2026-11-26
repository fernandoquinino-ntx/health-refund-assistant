"""Objetivo: coordenar a análise consultiva de reembolso.

Entradas: PDF, pergunta, exportações selecionadas, histórico e opções.
Processamento: extrai a primeira página, concilia, revisa e gera resposta.
Saídas: campos, avaliação, revisão, resposta e erros quando a análise falha.
"""

from dataclasses import dataclass
from datetime import date
import os
from pathlib import Path
from typing import Any, Dict, Sequence

from ..plan.assessment import DEADLINE_DAYS, ExportPeriodError, avaliar_documento
from ..plan.reconciliation import DEFAULT_MAPPING, load_mapping
from ..documents.pdf_converter import converter_pdf_bytes_primeira_pagina_base64
from ..plan.plan_exports import load_selected_exports
from ..documents.vlm_extractor import (
    DEFAULT_MODEL,
    LocalGGUFExtractor,
    LocalVLMExtractor,
    VLMExtractor,
)
from .revisao_documental import review_document
from .resposta_assistente import create_assistant_answer
from .estimativa_pagamento import estimar_pagamento


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
    review_prompt_version: str = "v1.0"
    payment_prompt_version: str = "v1.0"
    image_bytes: bytes = b""


@dataclass(frozen=True)
class AssistantResponse:
    document_fields: Dict[str, Any]
    assessment: Dict[str, Any]
    review: Dict[str, Any]
    answer: str


def handle_request(
    request: AssistantRequest, history: Sequence[Dict[str, str]] = ()
) -> AssistantResponse:
    if not request.question.strip():
        raise ValueError("Escreva uma pergunta para o assistente.")
    if not request.pdf_bytes and not request.image_bytes:
        raise ValueError("O documento enviado está vazio.")
    if not request.export_paths:
        raise ExportPeriodError(
            "Nenhuma exportação do plano selecionada; análise não executada."
        )

    exports = load_selected_exports(list(request.export_paths))
    mapping = load_mapping(DEFAULT_MAPPING)
    if request.image_bytes:
        import base64
        image = base64.b64encode(request.image_bytes).decode("ascii")
    else:
        image = converter_pdf_bytes_primeira_pagina_base64(request.pdf_bytes)
    local_base_url = os.getenv("LOCAL_VLM_BASE_URL")
    if local_base_url:
        extractor = LocalGGUFExtractor(
            base_url=local_base_url,
            model=os.getenv("LOCAL_VLM_MODEL", "smolvlm-health-refund"),
            prompt_version=request.extraction_prompt_version,
        )
    else:
        local_model = os.getenv("LOCAL_VLM_MODEL")
        if local_model:
            local_adapter = os.getenv("LOCAL_VLM_ADAPTER")
            extractor = LocalVLMExtractor(
                model_path=Path(local_model),
                adapter_path=Path(local_adapter) if local_adapter else None,
                prompt_version=request.extraction_prompt_version,
            )
        else:
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
    assessment["elegibilidade"] = {
        "status": "nao_e_possivel_avaliar",
        "motivo": "As regras contratuais do plano não foram verificadas na aplicação.",
    }
    review = review_document(
        request.question, image, document_fields, assessment, request.review_prompt_version
    )
    assessment = atualizar_estimativa(
        assessment, request.reference_date, request.payment_prompt_version
    )
    answer = create_assistant_answer(
        request.question,
        {"documento": document_fields, "conciliacao": assessment, "revisao_ia": review},
        request.response_prompt_version,
        history,
    )
    return AssistantResponse(
        document_fields=document_fields,
        assessment=assessment,
        review=review,
        answer=answer,
    )


def atualizar_estimativa(
    assessment: Dict[str, Any], reference_date: date, prompt_version: str
) -> Dict[str, Any]:
    updated = dict(assessment)
    if updated.get("candidatos"):
        updated.update({
            "prazo_simulado_dias": None,
            "data_base_prazo": None,
            "origem_data_base_prazo": None,
            "dias_desde_atendimento_ou_emissao": None,
            "situacao_prazo": "nao_aplicavel_pedido_localizado",
            "aviso_prazo": "Prazo de envio não analisado para pedido localizado.",
        })
    updated["estimativa_pagamento"] = estimar_pagamento(updated, reference_date, prompt_version)
    return updated
