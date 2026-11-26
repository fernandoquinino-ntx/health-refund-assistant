"""Tarefa de revisão consultiva da imagem e dos dados extraídos."""

import json
from typing import Any

from ..core.prompt_library import carregar_prompt
from .structured_ai import request_structured_json


def review_document(
    question: str, image: str, document: dict[str, Any],
    assessment: dict[str, Any], prompt_version: str = "v1.0",
) -> dict[str, Any]:
    prompt, _ = carregar_prompt("revisao_documental", prompt_version)
    content = [
        {
            "type": "text",
            "text": json.dumps(
                {"pergunta": question, "documento": document, "conciliacao": assessment},
                ensure_ascii=False,
            ),
        },
        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image}"}},
    ]
    review = request_structured_json(prompt, content, "document_review.schema.json")
    if not review["justificativa"].strip():
        raise ValueError("A revisão da IA não apresentou justificativa.")
    if (
        review["situacao_documental"] == "sem_inconsistencias_identificadas"
        and review["campos_para_revisao"]
    ):
        raise ValueError("A revisão da IA contém resultados contraditórios.")
    essential_fields = (
        "registro_profissional", "descricao_servico", "cnpj_cpf_prestador",
        "data_emissao", "valor_total",
    )
    incomplete = any(
        document.get(field) is None or document.get(field) == ""
        for field in essential_fields
    )
    if (
        incomplete or document.get("imagem_legivel") is not True
    ) and review["situacao_documental"] != "nao_e_possivel_avaliar":
        raise ValueError(
            "A revisão da IA contradiz os dados extraídos ou a legibilidade; "
            "não é possível concluir a análise."
        )
    return review
