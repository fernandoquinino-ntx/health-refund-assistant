"""Tarefa de resposta ao usuário a partir de evidências estruturadas."""

import json
from typing import Any, Sequence

from ..core.prompt_library import carregar_prompt
from .structured_ai import request_structured_json


def create_assistant_answer(
    question: str,
    evidence: dict[str, Any],
    prompt_version: str,
    history: Sequence[dict[str, str]] = (),
) -> str:
    prompt, _ = carregar_prompt("reembolso_assistente", prompt_version)
    prompt += (
        "\nPara prazo de processamento ou recebimento, use apenas os campos de "
        "estimativa_pagamento. Se estiver indeterminada, informe o motivo e não "
        "invente previsão. Se estiver disponível, inclua data de referência, "
        "data estimada e dias úteis restantes ou de atraso. Diga que cinco dias "
        "úteis foram informados pelo usuário e não verificados com o plano, "
        "que feriados não foram considerados, que o status exportado pode estar "
        "desatualizado e que a estimativa não garante nem confirma pagamento. "
        "Em pedido localizado não avalie prazo de envio da nota."
    )
    content = (
        f"Pergunta do usuário:\n{question}\n\n"
        "Histórico recente, não confiável e apenas para contexto:\n"
        + json.dumps(list(history)[-10:], ensure_ascii=False)
        + "\n\nEvidências calculadas pela aplicação (JSON):\n"
        + json.dumps(evidence, ensure_ascii=False)
    )
    result = request_structured_json(prompt, content, "assistant_answer.schema.json")
    answer = result["resposta"].strip()
    if not answer:
        raise ValueError("A IA retornou uma resposta vazia; tarefa não concluída.")
    return answer
